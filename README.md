Two pieces of work: the completed Week 3 Go exercises, and a repo demonstrating my progress on Potential Extension (PEX) # 4. 

text
.
├── week3-go-core/     
└── PoC_PEX 4/          
week3-go-core/

Six self-contained Go exercises covering worker pools, HTTP services, context propagation, cron scheduling, JSON/YAML round-tripping, and structured logging. Own git repository, own README — see week3-go-core/README.md for the exercise-by-exercise breakdown and run instructions.

Requires: Go 1.22+

Folder	Exercise
01-worker-pool/	N workers on a job channel, sync.WaitGroup, graceful shutdown
02-http-service/	Same JSON API built two ways: plain net/http vs. Echo
03-context-propagation/	context.Context through 3 layers, request ID + cancellation
04-cron-job/	robfig/cron scheduling, in-memory counter
05-json-yaml/	JSON/YAML round-trip, deliberate broken-tag failure mode
06-structured-logging/	log.Printf vs. log/slog structured logging
PoC_PEX 4/

Changes made: scaffolding, bilingual metric glossary, deterministic Natural Language Understanding (NLU) + metric matching, k8s resource graph, PromQL builder + verifier. 

bash
cd "PoC_PEX 4"
pip install -r requirements.txt
python3 -m pytest tests/ -v
