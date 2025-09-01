# Incorrect or Incomplete Items

* `apps/api/.env.example:2-3` — Redis URL uses `redis://`; should be `rediss://` for Upstash TLS.
* `services/worker/.env.example:2` — Redis URL uses `redis://`; should be `rediss://`.
