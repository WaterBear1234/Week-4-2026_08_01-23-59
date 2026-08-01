# Notes — JSON/YAML round-trip

Both formats round-trip cleanly with matching struct tags (`json:"..."`
and `yaml:"..."` on the same fields).

The important part is the broken-tag section: sending `"prt"` instead
of `"port"` produces **`err: <nil>`** — `encoding/json` doesn't treat
an unrecognized field as an error by default, it just ignores it. The
`Port` field silently stays at its zero value (`0`) instead of `8080`.
This is a real footgun for config files / API payloads: a typo in a
field name fails silently instead of loudly.

The fix is `dec.DisallowUnknownFields()` before decoding — same input,
now returns a real error (`json: unknown field "prt"`) instead of
quietly producing a half-populated struct.

Used `github.com/goccy/go-yaml` instead of the more common
`gopkg.in/yaml.v3` here — this sandbox can't reach `gopkg.in` (only
`github.com` is allowlisted for network access), and `goccy/go-yaml`
is a GitHub-hosted equivalent with the same `Marshal`/`Unmarshal` API.
On a machine with normal network access, `gopkg.in/yaml.v3` works the
same way.
