//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package stdiotransport

import (
	"bufio"
	"context"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

const protoPrefix = "@@TPSTDIO@@"

type Option func(*Transport)

func WithLabel(_ string) Option {
	return func(_ *Transport) {}
}

type wireFrame struct {
	Op           string  `json:"op"`
	LID          string  `json:"lid,omitempty"`
	CID          string  `json:"cid,omitempty"`
	Channel      string  `json:"channel,omitempty"`
	ReplyChannel *string `json:"reply_channel,omitempty"`
	TimeoutMS    int     `json:"timeout_ms,omitempty"`
	Payload      string  `json:"payload,omitempty"`
	OK           bool    `json:"ok,omitempty"`
	Error        string  `json:"error,omitempty"`
}

type callResult struct {
	payload []byte
	err     error
}

type Transport struct {
	writeMu sync.Mutex

	listenersMu sync.RWMutex
	listeners   map[string]func(*Envelope)

	pendingMu sync.Mutex
	pending   map[string]chan callResult

	lidCounter   atomic.Uint64
	cidCounter   atomic.Uint64
	closed       atomic.Bool
	readerClosed chan struct{}
}

func Open(_ string, opts ...Option) (*Transport, error) {
	transport := &Transport{
		listeners:    map[string]func(*Envelope){},
		pending:      map[string]chan callResult{},
		readerClosed: make(chan struct{}),
	}

	for _, opt := range opts {
		if opt != nil {
			opt(transport)
		}
	}

	go transport.readLoop()

	return transport, nil
}

func (t *Transport) Close() error {
	t.closed.CompareAndSwap(false, true)
	return nil
}

type Envelope struct {
	Payload      []byte
	ReplyChannel string
	transport    *Transport
}

func (m *Envelope) Respond(payload []byte) error {
	if m == nil || m.transport == nil {
		return errors.New("nil envelope")
	}
	if m.ReplyChannel == "" {
		return errors.New("no reply channel")
	}
	return m.transport.Send(m.ReplyChannel, payload)
}

type Listener struct {
	transport *Transport
	lid       string
	closed    atomic.Bool
}

func (l *Listener) Close() error {
	if l == nil {
		return nil
	}
	if !l.closed.CompareAndSwap(false, true) {
		return nil
	}
	return l.transport.unlisten(l.lid)
}

func (t *Transport) Listen(channel string, cb func(*Envelope)) (*Listener, error) {
	if t == nil {
		return nil, errors.New("nil transport")
	}
	if t.closed.Load() {
		return nil, errors.New("transport closed")
	}

	lid := "lid-" + strconv.FormatUint(t.lidCounter.Add(1), 10)
	t.listenersMu.Lock()
	t.listeners[lid] = cb
	t.listenersMu.Unlock()

	if err := t.sendFrame(wireFrame{
		Op:      "listen",
		LID:     lid,
		Channel: channel,
	}); err != nil {
		return nil, err
	}

	return &Listener{transport: t, lid: lid}, nil
}

func (t *Transport) Call(ctx context.Context, channel string, payload []byte) (*Envelope, error) {
	if t == nil {
		return nil, errors.New("nil transport")
	}
	if t.closed.Load() {
		return nil, errors.New("transport closed")
	}

	timeoutMS := 5000
	if deadline, ok := ctx.Deadline(); ok {
		timeout := time.Until(deadline)
		if timeout <= 0 {
			return nil, context.DeadlineExceeded
		}
		timeoutMS = int(timeout / time.Millisecond)
		if timeoutMS < 1 {
			timeoutMS = 1
		}
	}

	cid := "cid-" + strconv.FormatUint(t.cidCounter.Add(1), 10)
	wait := make(chan callResult, 1)

	t.pendingMu.Lock()
	t.pending[cid] = wait
	t.pendingMu.Unlock()

	err := t.sendFrame(wireFrame{
		Op:        "call",
		CID:       cid,
		Channel:   channel,
		TimeoutMS: timeoutMS,
		Payload:   base64.StdEncoding.EncodeToString(payload),
	})
	if err != nil {
		t.pendingMu.Lock()
		delete(t.pending, cid)
		t.pendingMu.Unlock()
		return nil, err
	}

	select {
	case <-ctx.Done():
		t.pendingMu.Lock()
		delete(t.pending, cid)
		t.pendingMu.Unlock()
		return nil, ctx.Err()
	case result := <-wait:
		if result.err != nil {
			return nil, result.err
		}
		return &Envelope{Payload: result.payload, transport: t}, nil
	}
}

func (t *Transport) Send(channel string, payload []byte) error {
	if t == nil {
		return errors.New("nil transport")
	}
	if t.closed.Load() {
		return errors.New("transport closed")
	}

	return t.sendFrame(wireFrame{
		Op:      "send",
		Channel: channel,
		Payload: base64.StdEncoding.EncodeToString(payload),
	})
}

func (t *Transport) unlisten(lid string) error {
	t.listenersMu.Lock()
	delete(t.listeners, lid)
	t.listenersMu.Unlock()

	return t.sendFrame(wireFrame{
		Op:  "unlisten",
		LID: lid,
	})
}

func (t *Transport) sendFrame(frame wireFrame) error {
	if t == nil {
		return errors.New("nil transport")
	}
	bytes, err := json.Marshal(frame)
	if err != nil {
		return err
	}

	line := protoPrefix + string(bytes) + "\n"

	t.writeMu.Lock()
	defer t.writeMu.Unlock()
	_, err = os.Stdout.WriteString(line)
	if err != nil {
		return err
	}
	return nil
}

func (t *Transport) readLoop() {
	defer close(t.readerClosed)

	scanner := bufio.NewScanner(os.Stdin)
	buf := make([]byte, 0, 64*1024)
	scanner.Buffer(buf, 50*1024*1024)

	for scanner.Scan() {
		line := scanner.Text()
		if !strings.HasPrefix(line, protoPrefix) {
			continue
		}

		var frame wireFrame
		if err := json.Unmarshal([]byte(strings.TrimPrefix(line, protoPrefix)), &frame); err != nil {
			continue
		}

		t.handleFrame(frame)
	}

	t.failAllPending(errors.New("stdio input closed"))
}

func (t *Transport) handleFrame(frame wireFrame) {
	switch frame.Op {
	case "event":
		lid := frame.LID
		if lid == "" {
			return
		}

		t.listenersMu.RLock()
		cb := t.listeners[lid]
		t.listenersMu.RUnlock()
		if cb == nil {
			return
		}

		payload, err := base64.StdEncoding.DecodeString(frame.Payload)
		if err != nil {
			return
		}

		reply := ""
		if frame.ReplyChannel != nil {
			reply = *frame.ReplyChannel
		}

		go cb(&Envelope{
			Payload:      payload,
			ReplyChannel: reply,
			transport:    t,
		})

	case "call_result":
		cid := frame.CID
		if cid == "" {
			return
		}

		t.pendingMu.Lock()
		wait := t.pending[cid]
		delete(t.pending, cid)
		t.pendingMu.Unlock()
		if wait == nil {
			return
		}

		if !frame.OK {
			errMsg := frame.Error
			if errMsg == "" {
				errMsg = "call failed"
			}
			wait <- callResult{err: fmt.Errorf(errMsg)}
			return
		}

		payload, err := base64.StdEncoding.DecodeString(frame.Payload)
		if err != nil {
			wait <- callResult{err: err}
			return
		}

		wait <- callResult{payload: payload}
	}
}

func (t *Transport) failAllPending(err error) {
	t.pendingMu.Lock()
	defer t.pendingMu.Unlock()

	for cid, wait := range t.pending {
		wait <- callResult{err: err}
		delete(t.pending, cid)
	}
}
