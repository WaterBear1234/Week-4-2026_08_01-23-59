// N workers pull jobs off a shared channel, push results to another
// channel, main collects with sync.WaitGroup. context.Context cancellation
// gives graceful shutdown — workers stop taking new jobs mid-run instead of
// draining the whole queue.
package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

type Job struct{ ID int }
type Result struct {
	JobID int
	Value int
}

func worker(ctx context.Context, id int, jobs <-chan Job, results chan<- Result, wg *sync.WaitGroup) {
	defer wg.Done()
	for {
		// Check shutdown FIRST, non-blocking: without this, select picks
		// pseudo-randomly among ready cases, so a buffered job could still
		// get pulled even after ctx already expired.
		select {
		case <-ctx.Done():
			fmt.Printf("worker %d: shutting down (%v)\n", id, ctx.Err())
			return
		default:
		}

		select {
		case <-ctx.Done():
			fmt.Printf("worker %d: shutting down (%v)\n", id, ctx.Err())
			return
		case job, ok := <-jobs:
			if !ok { // channel closed, no more jobs
				return
			}
			time.Sleep(80 * time.Millisecond) // simulate work
			results <- Result{JobID: job.ID, Value: job.ID * job.ID}
		}
	}
}

func main() {
	const numWorkers = 3
	const numJobs = 10

	// Cancel after 120ms — enough time for some jobs to finish, not all of
	// them, so the graceful-shutdown path actually fires.
	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Millisecond)
	defer cancel()

	jobs := make(chan Job, numJobs)
	results := make(chan Result, numJobs)
	var wg sync.WaitGroup

	for w := 1; w <= numWorkers; w++ {
		wg.Add(1)
		go worker(ctx, w, jobs, results, &wg)
	}

	for j := 1; j <= numJobs; j++ {
		jobs <- Job{ID: j}
	}
	close(jobs)

	wg.Wait()
	close(results)

	completed := 0
	for r := range results {
		fmt.Printf("result: job %d -> %d\n", r.JobID, r.Value)
		completed++
	}
	fmt.Printf("completed %d/%d jobs before shutdown\n", completed, numJobs)
}
