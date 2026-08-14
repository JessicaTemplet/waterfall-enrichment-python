# waterfall-enrichment-python

A lead enrichment pipeline that spends money on data providers only when it has
to. Each lead gets a **doubt score** (0.0 = fully resolved, 1.0 = no data at
all) computed from what's already known about it, and that score decides
which enrichment stage runs next. A lead that's already got a title and email
never touches a paid API. A lead with nothing gets pushed through every stage.

This is the Python implementation. A parallel Rust port of the core pipeline
logic lives in [Waterfall-Enrichment](https://github.com/JessicaTemplet/Waterfall-Enrichment).

## How the waterfall works

```
doubt score          stage        cost
-----------------------------------------
> 0.5      ----->    shallow      2c
> 0.2      ----->    waterfall    8c   (tries up to 4 vendor sources)
> 0.1      ----->    agent        15c  (deep-research fallback)
0.0        ----->    done
```

`doubt.py` computes the score from the lead's existing `Observation` rows:
missing a title costs 0.4, conflicting titles from different sources cost
0.3, missing an email costs 0.3. The pipeline only pays for a stage if the
lead's doubt is still above that stage's threshold after the previous one
ran, so a lead that resolves early exits the waterfall immediately.

## Architecture

- **`leadintel/storage/`**: SQLAlchemy models and repositories (`Lead`,
  `Observation`, `Run`) backing the doubt calculation and enrichment history.
- **`leadintel/intelligence/`**: signal scoring on top of raw observations.
- **`leadintel/integrations/`**: the async task execution glue between the
  pipeline stages and the job queue.
- **`leadintel/vendor/`**: the job execution engine, idempotency layer, and
  rate limiter, vendored in from their own standalone repos
  ([Background-Job-Processor](https://github.com/JessicaTemplet/Background-Job-Processor),
  [Idempotent-API-Layer](https://github.com/JessicaTemplet/Idempotent-API-Layer),
  [Atomic-Rate-Limiter](https://github.com/JessicaTemplet/Atomic-Rate-Limiter))
  rather than duplicated inline.
- **`leadintel/core/`**: a compact, self-contained reference implementation
  of the pipeline (config loading, stages, worker, runner) kept intentionally
  small. This is the module-for-module twin that the Rust port mirrors line
  by line. See that repo's doc comments for the side-by-side mapping.
- **Root-level `config.py` / `db.py` / `runner.py` / `stages.py` / `tasks.py`
  / `worker.py`**: the actual, fuller pipeline implementation that runs
  against real (currently mocked) vendor APIs: Apollo, Hunter, Clearbit, and
  a LinkedIn scraper, each with its own simulated latency and confidence per
  field.

## Running it

```sh
cp .env.example .env   # set REDIS_URL and DATABASE_URL
pip install sqlalchemy redis pyyaml typer rich python-dotenv
python -m leadintel.storage.init_db
python runner.py
```

No `requirements.txt` yet, the packages above cover everything currently
imported.

`pipeline.yaml` at the repo root defines the stage thresholds and costs shown
above; edit it to change the waterfall without touching code.

Defaults to SQLite for local dev; swap `DATABASE_URL` to Postgres for
production. Redis backs the job queue the vendored execution engine runs on.

## Status

The vendor integrations (Apollo/Hunter/Clearbit/LinkedIn) are mocked with
randomized responses rather than live API calls. Swapping in real clients is
the main piece left to do.