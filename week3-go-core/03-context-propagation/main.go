// context.Context threaded through 3 function layers, carrying a request ID
// and cancelling a slow downstream call with context.WithTimeout.
package main

import (
	"context"
	"errors"
	"fmt"
	"time"
)

// unexported key type — avoids collisions with other packages' context keys.
type ctxKey string

const requestIDKey ctxKey = "requestID"

func withRequestID(ctx context.Context, id string) context.Context {
	return context.WithValue(ctx, requestIDKey, id)
}

func requestIDFrom(ctx context.Context) string {
	if id, ok := ctx.Value(requestIDKey).(string); ok {
		return id
	}
	return "unknown"
}

// layer 1: handler — sets up the request-scoped context.
func handleRequest(ctx context.Context) error {
	ctx = withRequestID(ctx, "req-8421")
	return service(ctx)
}

// layer 2: service — doesn't know about HTTP, just passes ctx through and
// logs using whatever request ID it finds.
func service(ctx context.Context) error {
	fmt.Printf("[%s] service: calling downstream\n", requestIDFrom(ctx))
	ctx, cancel := context.WithTimeout(ctx, 100*time.Millisecond)
	defer cancel()
	return downstreamCall(ctx)
}

// layer 3: downstream — a slow call that respects cancellation instead of
// just running to completion regardless.
func downstreamCall(ctx context.Context) error {
	select {
	case <-time.After(300 * time.Millisecond): // simulated slow work
		fmt.Printf("[%s] downstream: finished\n", requestIDFrom(ctx))
		return nil
	case <-ctx.Done():
		fmt.Printf("[%s] downstream: cancelled (%v)\n", requestIDFrom(ctx), ctx.Err())
		return ctx.Err()
	}
}

func main() {
	err := handleRequest(context.Background())
	if err != nil && errors.Is(err, context.DeadlineExceeded) {
		fmt.Println("main: request failed due to downstream timeout, as expected")
	}
}
