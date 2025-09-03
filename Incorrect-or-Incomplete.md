# Incorrect or Incomplete Items

- `apps/api/app/settings.py` — instantiating `Settings` without required named arguments triggers mypy `call-arg` errors.
- `apps/api` — missing type stubs for `python-jose` and other modules keep `mypy` from passing project-wide.

