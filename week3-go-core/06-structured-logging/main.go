// Swaps log.Println for structured logging (log/slog, stdlib since 1.21) —
// leveled logs with fields instead of a plain sentence, compared side by
// side with the plain-text equivalent.
package main

import (
	"log"
	"log/slog"
	"os"
)

func main() {
	orderID := 4821
	amount := 129.99

	log.Printf("processing order: order_id=%d amount=%.2f", orderID, amount)

	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	logger.Info("processing order", "order_id", orderID, "amount", amount)

	logger.Warn("payment retry", "order_id", orderID, "attempt", 2)
	logger.Error("payment failed", "order_id", orderID, "reason", "card declined")

	// a logger with fields baked in once, reused across calls — avoids
	// repeating order_id on every log line for one request's lifetime.
	requestLogger := logger.With("order_id", orderID)
	requestLogger.Info("validating")
	requestLogger.Info("charging card")
	requestLogger.Info("done")
}
