# Notes — cron job

`cron.WithSeconds()` is required to use `@every 2s` — without it,
robfig/cron's default schedule spec only supports minute-level
granularity (5-field cron, like standard crontab). Real output:
3 ticks in ~7 seconds at a 2-second interval, exactly as expected.

`tickCount` is protected by a `sync.Mutex` even though this program
only ever schedules one job — worth doing anyway because `cron` runs
each triggered job on its own goroutine by default, so a job that
overruns its interval (or multiple different jobs sharing one counter)
would otherwise race, same as any other shared-state-from-multiple-
goroutines case from Week 2.

This is the same shape as a Celery periodic task: a schedule string,
a function to run, and an in-memory (or Redis-backed) counter/state
that gets updated each tick.
