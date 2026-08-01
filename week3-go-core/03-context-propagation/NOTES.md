# Notes — context propagation

Request ID rides through 3 layers (`handleRequest` → `service` →
`downstreamCall`) via `context.WithValue`, not a function parameter —
that's the intended use case for context values: request-scoped
metadata that every layer might want (logging, tracing) without
threading an extra parameter through every signature.

The timeout is set at the `service` layer (100ms) but the slow work
is simulated in `downstreamCall` (300ms) — `downstreamCall`'s `select`
against `ctx.Done()` is what actually makes the cancellation take
effect. Without that `select`, the context would expire but the
function would just keep running anyway; a context timeout only does
something if the code holding it actually checks `ctx.Done()`.

Using an unexported `ctxKey` type (not a plain `string`) for the
context key is deliberate — it prevents a collision if some other
package also stores a value under the key `"requestID"`.
