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

package stdionats

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

type Option func(*Conn)

func Name(_ string) Option {
	return func(_ *Conn) {}
}

type wireFrame struct {
	Op        string  `json:"op"`
	SID       string  `json:"sid,omitempty"`
	RID       string  `json:"rid,omitempty"`
	Subject   string  `json:"subject,omitempty"`
	Reply     *string `json:"reply,omitempty"`
	TimeoutMS int     `json:"timeout_ms,omitempty"`
	Data      string  `json:"data,omitempty"`
	OK        bool    `json:"ok,omitempty"`
	Error     string  `json:"error,omitempty"`
}

type requestResult struct {
	data []byte
	err  error
}

type Conn struct {
	writeMu sync.Mutex

	subsMu sync.RWMutex
	subs   map[string]func(*Msg)

	pendingMu sync.Mutex
	pending   map[string]chan requestResult

	sidCounter   atomic.Uint64
	ridCounter   atomic.Uint64
	closed       atomic.Bool
	readerClosed chan struct{}
}

func Connect(_ string, opts ...Option) (*Conn, error) {
	conn := &Conn{
		subs:         map[string]func(*Msg){},
		pending:      map[string]chan requestResult{},
		readerClosed: make(chan struct{}),
	}

	for _, opt := range opts {
		if opt != nil {
			opt(conn)
		}
	}

	go conn.readLoop()

	return conn, nil
}

func (c *Conn) Drain() error {
	c.closed.CompareAndSwap(false, true)
	return nil
}

type Msg struct {
	Data  []byte
	Reply string
	conn  *Conn
}

func (m *Msg) Respond(data []byte) error {
	if m == nil || m.conn == nil {
		return errors.New("nil message")
	}
	if m.Reply == "" {
		return errors.New("no reply subject")
	}
	return m.conn.Publish(m.Reply, data)
}

type Subscription struct {
	conn   *Conn
	sid    string
	closed atomic.Bool
}

func (s *Subscription) Drain() error {
	if s == nil {
		return nil
	}
	if !s.closed.CompareAndSwap(false, true) {
		return nil
	}
	return s.conn.unsubscribe(s.sid)
}

func (c *Conn) Subscribe(subject string, cb func(*Msg)) (*Subscription, error) {
	if c == nil {
		return nil, errors.New("nil connection")
	}
	if c.closed.Load() {
		return nil, errors.New("connection closed")
	}

	sid := "sid-" + strconv.FormatUint(c.sidCounter.Add(1), 10)
	c.subsMu.Lock()
	c.subs[sid] = cb
	c.subsMu.Unlock()

	if err := c.send(wireFrame{
		Op:      "subscribe",
		SID:     sid,
		Subject: subject,
	}); err != nil {
		return nil, err
	}

	return &Subscription{
		conn: c,
		sid:  sid,
	}, nil
}

func (c *Conn) RequestWithContext(ctx context.Context, subject string, data []byte) (*Msg, error) {
	if c == nil {
		return nil, errors.New("nil connection")
	}
	if c.closed.Load() {
		return nil, errors.New("connection closed")
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

	rid := "rid-" + strconv.FormatUint(c.ridCounter.Add(1), 10)
	wait := make(chan requestResult, 1)

	c.pendingMu.Lock()
	c.pending[rid] = wait
	c.pendingMu.Unlock()

	err := c.send(wireFrame{
		Op:        "request",
		RID:       rid,
		Subject:   subject,
		TimeoutMS: timeoutMS,
		Data:      base64.StdEncoding.EncodeToString(data),
	})
	if err != nil {
		c.pendingMu.Lock()
		delete(c.pending, rid)
		c.pendingMu.Unlock()
		return nil, err
	}

	select {
	case <-ctx.Done():
		c.pendingMu.Lock()
		delete(c.pending, rid)
		c.pendingMu.Unlock()
		return nil, ctx.Err()
	case result := <-wait:
		if result.err != nil {
			return nil, result.err
		}
		return &Msg{Data: result.data, conn: c}, nil
	}
}

func (c *Conn) Publish(subject string, data []byte) error {
	if c == nil {
		return errors.New("nil connection")
	}
	if c.closed.Load() {
		return errors.New("connection closed")
	}

	return c.send(wireFrame{
		Op:      "publish",
		Subject: subject,
		Reply:   nil,
		Data:    base64.StdEncoding.EncodeToString(data),
	})
}

func (c *Conn) unsubscribe(sid string) error {
	c.subsMu.Lock()
	delete(c.subs, sid)
	c.subsMu.Unlock()

	return c.send(wireFrame{
		Op:  "unsubscribe",
		SID: sid,
	})
}

func (c *Conn) send(frame wireFrame) error {
	if c == nil {
		return errors.New("nil connection")
	}
	bytes, err := json.Marshal(frame)
	if err != nil {
		return err
	}

	line := protoPrefix + string(bytes) + "\n"

	c.writeMu.Lock()
	defer c.writeMu.Unlock()
	_, err = os.Stdout.WriteString(line)
	if err != nil {
		return err
	}
	return nil
}

func (c *Conn) readLoop() {
	defer close(c.readerClosed)

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

		c.handleFrame(frame)
	}

	c.failAllPending(errors.New("stdio input closed"))
}

func (c *Conn) handleFrame(frame wireFrame) {
	switch frame.Op {
	case "message":
		sid := frame.SID
		if sid == "" {
			return
		}

		c.subsMu.RLock()
		cb := c.subs[sid]
		c.subsMu.RUnlock()
		if cb == nil {
			return
		}

		payload, err := base64.StdEncoding.DecodeString(frame.Data)
		if err != nil {
			return
		}

		reply := ""
		if frame.Reply != nil {
			reply = *frame.Reply
		}

		go cb(&Msg{
			Data:  payload,
			Reply: reply,
			conn:  c,
		})

	case "request_result":
		rid := frame.RID
		if rid == "" {
			return
		}

		c.pendingMu.Lock()
		wait := c.pending[rid]
		delete(c.pending, rid)
		c.pendingMu.Unlock()
		if wait == nil {
			return
		}

		if !frame.OK {
			errMsg := frame.Error
			if errMsg == "" {
				errMsg = "request failed"
			}
			wait <- requestResult{err: fmt.Errorf(errMsg)}
			return
		}

		payload, err := base64.StdEncoding.DecodeString(frame.Data)
		if err != nil {
			wait <- requestResult{err: err}
			return
		}

		wait <- requestResult{data: payload}
	}
}

func (c *Conn) failAllPending(err error) {
	c.pendingMu.Lock()
	defer c.pendingMu.Unlock()

	for rid, wait := range c.pending {
		wait <- requestResult{err: err}
		delete(c.pending, rid)
	}
}
