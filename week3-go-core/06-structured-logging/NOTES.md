# Notes — structured logging

Plain `log.Printf` output is one sentence — fine for a human staring
at a terminal, painful to query later ("find every log line where
order_id=4821 and level=ERROR" means regex, not a field lookup).

`log/slog` (stdlib since Go 1.21, no external dependency needed) gives
structured key-value fields plus levels (`Info`/`Warn`/`Error`) and
emits real JSON here via `slog.NewJSONHandler` — directly greppable/
queryable by a log aggregator (Loki, CloudWatch Insights, etc.)
without any parsing step.

`logger.With("order_id", orderID)` returns a new logger with that
field baked in — every subsequent call on `requestLogger` includes
`order_id` automatically, instead of repeating it on every log call
for the life of one request. That's the pattern you'd use for a
per-request or per-goroutine logger.
