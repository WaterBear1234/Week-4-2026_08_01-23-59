# Week 4

Two pieces of work for Week 4: the completed Week 3 Go exercises,
and a repo demonstrating progress on Potential Extension (PEX) #4 — the
deterministic core of a bilingual (English/Vietnamese) natural-language-to-
PromQL assistant.

---

## `week3-go-core` 

Six independent exercises, each in its own subfolder:

| Folder | Exercise |
|---|---|
| `01-worker-pool/` | N workers on a job channel, `sync.WaitGroup`, graceful shutdown |
| `02-http-service/` | Same JSON API built two ways: plain `net/http` vs. Echo |
| `03-context-propagation/` | `context.Context` through 3 layers, request ID + cancellation |
| `04-cron-job/` | `robfig/cron` scheduling, in-memory counter |
| `05-json-yaml/` | JSON/YAML round-trip, deliberate broken-tag failure mode |
| `06-structured-logging/` | `log.Printf` vs. `log/slog` structured logging |

---

## `PoC_PEX 4` 

Changes made:

- Bilingual (EN/VI) metric glossary as the domain model
- Regex-based NLU for slot extraction (time range, aggregation, group-by, filters)
- A k8s resource graph resolving `deployment=`/`service=` filters to real `pod=` matchers
- A PromQL builder + verifier producing structurally correct queries

Run the test suite:

```bash
cd "PoC_PEX 4"
pip install -r requirements.txt
python3 -m pytest tests/ -v
