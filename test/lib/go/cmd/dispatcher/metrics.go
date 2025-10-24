package main

import (
	"fmt"
	"strings"
	"sync"
	"time"

	"github.com/prometheus/client_golang/prometheus"
)

type metricRegistry struct {
	file     string
	mu       sync.Mutex
	registry *prometheus.Registry
	timers   map[string]prometheus.Summary
}

func newMetricRegistry(file string) *metricRegistry {
	return &metricRegistry{
		file:     file,
		registry: prometheus.NewRegistry(),
		timers:   make(map[string]prometheus.Summary),
	}
}

func (m *metricRegistry) Observe(topic string, duration time.Duration) {
	if m == nil {
		return
	}

	summary := m.summaryForTopic(topic)
	if summary == nil {
		return
	}

	summary.Observe(duration.Seconds())
}

func (m *metricRegistry) summaryForTopic(topic string) prometheus.Summary {
	m.mu.Lock()
	defer m.mu.Unlock()

	if summary, ok := m.timers[topic]; ok {
		return summary
	}

	name := sanitizeMetricName(topic)
	metric := prometheus.NewSummary(prometheus.SummaryOpts{
		Name: name,
		Help: fmt.Sprintf("Latency summary for topic %s", topic),
	})

	if err := m.registry.Register(metric); err != nil {
		return nil
	}

	m.timers[topic] = metric
	return metric
}

func (m *metricRegistry) WriteToFile() error {
	if m == nil || m.file == "" {
		return nil
	}

	m.mu.Lock()
	defer m.mu.Unlock()

	return prometheus.WriteToTextfile(m.file, m.registry)
}

func sanitizeMetricName(topic string) string {
	replacer := strings.NewReplacer(
		".", "_",
		"-", "_",
		":", "_",
		"/", "_",
		" ", "_",
	)

	sanitized := replacer.Replace(topic)
	sanitized = strings.Map(func(r rune) rune {
		if (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') || (r >= '0' && r <= '9') || r == '_' {
			return r
		}
		return '_'
	}, sanitized)

	if sanitized == "" {
		sanitized = "telepact_metric"
	}
	if sanitized[0] >= '0' && sanitized[0] <= '9' {
		sanitized = "telepact_" + sanitized
	}

	return sanitized
}
