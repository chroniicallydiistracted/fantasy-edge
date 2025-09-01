# Findings

1. **[Minor][Cache]** `apps/api/.env.example:2-3` — Sample Redis URL uses non-TLS `redis://`, but production Upstash requires `rediss://` for encrypted connections.
2. **[Minor][Cache]** `services/worker/.env.example:2` — Worker example also uses `redis://`, which doesn't match the mandated TLS `rediss://` scheme.
