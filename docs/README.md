# Fantasy Edge Docs

Refer to the root `README.md` for the canonical architecture, env vars, and dev instructions.

## Dev quickstart
```bash
cp .env.example .env
docker compose -f infra/docker-compose.dev.yml up --build
```

- API: http://localhost:8000/health
- Web: http://localhost:3000

## Frontend tests
```bash
cd apps/web
pnpm test
```
