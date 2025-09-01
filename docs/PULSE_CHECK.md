# Pulse Check

Date: 2025-09-01

## Outstanding Issues
- **API mypy**: `app/waivers.py` conflicts with `app/routers/waivers.py`, causing duplicate-module errors.
- **Worker linting**: `black --check` wants to reformat multiple files.
- **Worker tests**: Import errors for `project_offense` from `projections` prevent test collection.
- **Web build**: `pnpm build` fails due to missing type declarations in `lib/waivers`.
- **Dependency stubs**: Missing typing stubs for `celery.schedules` and `python-jose`.

These items should be revisited after initial phase completion.
