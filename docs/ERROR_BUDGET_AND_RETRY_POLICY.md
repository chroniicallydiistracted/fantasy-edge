# Error Budget and Retry Policy

The API client uses an exponential backoff strategy with jitter when
communicating with Yahoo. Requests are retried up to three times with
delays of `0.1 * 2^n` seconds plus a random 0–0.1 second jitter. This
helps smooth traffic spikes and guards against transient failures.

We maintain an informal error budget of 99% success over rolling seven days.
Exceeding this threshold triggers investigation and potential backoff
adjustments. Persistent failures are surfaced through structured logs and
metrics derived from those logs.
