# Fantasy Edge (Scaffold)

## Dev quickstart
```bash
cp .env.example .env
docker compose -f infra/docker-compose.dev.yml up --build
```

- API: http://localhost:8000/health
- Web: http://localhost:3000

## Testing
Run frontend smoke tests with Node's built-in test runner:

```bash
cd apps/web
npm test
```
