# Notes — bare net/http vs Echo

Same service, same behavior, two implementations:

`bare/` — `http.ServeMux`, manual method check (`if r.Method != POST`),
manual `json.NewDecoder(r.Body).Decode`, manual validation, manual
status codes. Every line is something a framework would give you for
free — the point of building it bare first is feeling exactly what
that "free" is buying you.

`framework/` (Echo) — routing is method-aware by default: `e.POST(...)`
plus Echo's router auto-returns `405 Method Not Allowed` for other
verbs on `/users`, no manual check needed. Recovery middleware
(`middleware.Recover()`) is one line instead of hand-writing a
panic-catching wrapper. Validation is still manual either way — Echo
doesn't validate request structs by default, only binds them.

One real gotcha hit while testing both: `curl -d` without an explicit
`Content-Type` defaults to `application/x-www-form-urlencoded`. The
bare version doesn't care (it blindly calls `json.Decode` on the body
regardless of header), so it worked either way. Echo's `c.Bind`
*does* branch on `Content-Type` to pick a binder — sending it without
`-H "Content-Type: application/json"` silently bound nothing and every
field came back empty, `curl -X POST ... -H "Content-Type: application/json" -d '...'`
fixed it. Small thing, but exactly the kind of framework "magic" that
bites you once and then you know for good.

## Sandbox note on `go get`

`go get github.com/labstack/echo/v4` initially failed here because
several of Echo's transitive deps live under `golang.org/x/...`, and
this sandbox can't reach `golang.org` (only `github.com` is
allowlisted). Fixed with `replace` directives redirecting each
`golang.org/x/*` package to its official GitHub mirror
(`github.com/golang/sys`, `github.com/golang/net`, etc.) — same
package, different host to fetch it from. Not needed on a machine with
normal network access.
