# Incorrect or Incomplete Items

- `apps/api/app/session.py` — cookie helpers still mis-type `samesite` and require stricter `int` parsing.
- `apps/api/app/yahoo_oauth.py` and scripts — `mypy` reports argument/assignment type mismatches.

