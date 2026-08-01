# Notes — worker pool with graceful shutdown

3 workers, 10 buffered jobs, `context.WithTimeout(120ms)`. Each job
takes ~80ms, so 3 workers finish ~2 rounds (6 jobs) before the
deadline hits — output confirms `6/10 jobs before shutdown`.

The non-obvious part: `select` picks pseudo-randomly among *all* ready
cases. A single `select{ case <-ctx.Done(): ...; case job := <-jobs: ...}`
does NOT guarantee shutdown wins the moment the context expires — if
the jobs channel still has buffered data, that case is just as likely
to fire. The fix is the first non-blocking `select` with only a
`default` — it explicitly checks "is ctx already done?" before even
considering a new job, so once the deadline passes, every worker
returns on its *next* loop iteration instead of maybe grabbing one
more job by chance.
