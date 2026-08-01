# Week 3 — worker pools, microservice/HTTP, cron, JSON/YAML, logging

## Layout

| Folder | Exercise | Run it |
|---|---|---|
| [`01-worker-pool/`](01-worker-pool) | N workers on a job channel, results collected via `sync.WaitGroup`, graceful shutdown via `context.WithTimeout` | `go run .` |
| [`02-http-service/`](02-http-service) | Same JSON API built two ways: `bare/` (plain `net/http`) and `framework/` (Echo) | `go run .` in each subfolder, then `curl` |
| [`03-context-propagation/`](03-context-propagation) | `context.Context` through 3 function layers, carrying a request ID and cancelling a slow downstream call | `go run .` |
| [`04-cron-job/`](04-cron-job) | `robfig/cron` scheduling a task every 2s, updating an in-memory counter | `go run .` (~7s) |
| [`05-json-yaml/`](05-json-yaml) | Struct round-tripped through JSON and YAML, then a deliberately broken tag to show the silent-zero-value failure mode | `go run .` |
| [`06-structured-logging/`](06-structured-logging) | Plain `log.Printf` vs `log/slog` structured JSON logging with fields | `go run .` |

Every folder has a `NOTES.md` explaining *why*, same format as Weeks
1–2.

## Requirements

Go 1.22+. `02-http-service/framework`, `04-cron-job`, and
`05-json-yaml` are separate modules (own `go.mod`) since they pull in
real external dependencies (Echo, robfig/cron, goccy/go-yaml) —
kept isolated so a dependency issue in one doesn't block
`go build ./...` at the repo root, which only needs the standard
library.

### A sandbox-specific note, in case you see `replace` directives

`02-http-service/framework/go.mod` has several
`replace golang.org/x/... => github.com/golang/...` lines. This repo
was built in a sandboxed environment that could only reach
`github.com`, not `golang.org` — several of Echo's transitive
dependencies live under `golang.org/x/*`, so those lines redirect them
to their official GitHub mirrors (same code, different fetch host).
Harmless on a machine with normal network access; not required there,
but doesn't break anything if left in.
