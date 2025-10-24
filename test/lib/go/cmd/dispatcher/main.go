package main

import (
	"log"
	"os"

	"github.com/nats-io/nats.go"
)

func main() {
	logger := log.New(os.Stdout, "[telepact-go] ", log.LstdFlags|log.Lmicroseconds)

	natsURL := os.Getenv("NATS_URL")
	if natsURL == "" {
		logger.Fatal("NATS_URL env var not set")
	}

	subject := os.Getenv("TP_HARNESS_SUBJECT")
	if subject == "" {
		subject = "go"
	}

	metricsFile := "metrics.txt"

	nc, err := nats.Connect(natsURL, nats.Name("telepact-go-test-harness"))
	if err != nil {
		logger.Fatalf("failed to connect to NATS: %v", err)
	}
	defer func() {
		_ = nc.Drain()
	}()

	dispatcher := NewDispatcher(nc, logger, metricsFile)
	if err := dispatcher.Start(subject); err != nil {
		logger.Fatalf("failed to start dispatcher: %v", err)
	}

	<-dispatcher.Done()

	if err := dispatcher.Close(); err != nil {
		logger.Printf("error while shutting down dispatcher: %v", err)
	}

	if err := dispatcher.WriteMetrics(); err != nil {
		logger.Printf("failed to write metrics: %v", err)
	}
}
