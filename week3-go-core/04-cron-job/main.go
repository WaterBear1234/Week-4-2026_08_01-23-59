// Schedules a task every 2 seconds with robfig/cron, logs each tick, and
// updates an in-memory counter — the Celery-equivalent muscle memory for
// the Prometheus agent project's periodic tasks.
package main

import (
	"fmt"
	"sync"
	"time"

	"github.com/robfig/cron/v3"
)

func main() {
	var mu sync.Mutex // cron runs each job on its own goroutine, so the
	tickCount := 0    // shared counter needs protecting like any other

	c := cron.New(cron.WithSeconds()) // WithSeconds enables "@every 2s"-style precision
	_, err := c.AddFunc("@every 2s", func() {
		mu.Lock()
		tickCount++
		n := tickCount
		mu.Unlock()
		fmt.Printf("[%s] tick #%d\n", time.Now().Format("15:04:05"), n)
	})
	if err != nil {
		panic(err)
	}

	c.Start()
	defer c.Stop()

	fmt.Println("cron started, running for ~7s to observe a few ticks")
	time.Sleep(7 * time.Second)

	mu.Lock()
	fmt.Printf("stopped after %d ticks\n", tickCount)
	mu.Unlock()
}
