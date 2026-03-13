# Error & Rescue Table Templates

## METHOD/CODEPATH Table

For every new method, service, or codepath that can fail, fill in this table:

```
  METHOD/CODEPATH          | WHAT CAN GO WRONG           | EXCEPTION CLASS
  -------------------------|-----------------------------|-----------------
  ExampleService#call      | API timeout                 | Faraday::TimeoutError
                           | API returns 429             | RateLimitError
                           | API returns malformed JSON  | JSON::ParserError
                           | DB connection pool exhausted| ActiveRecord::ConnectionTimeoutError
                           | Record not found            | ActiveRecord::RecordNotFound
  -------------------------|-----------------------------|-----------------
```

## EXCEPTION CLASS Table

```
  EXCEPTION CLASS              | RESCUED?  | RESCUE ACTION          | USER SEES
  -----------------------------|-----------|------------------------|------------------
  Faraday::TimeoutError        | Y         | Retry 2x, then raise   | "Service temporarily unavailable"
  RateLimitError               | Y         | Backoff + retry         | Nothing (transparent)
  JSON::ParserError            | N <- GAP  | --                     | 500 error <- BAD
  ConnectionTimeoutError       | N <- GAP  | --                     | 500 error <- BAD
  ActiveRecord::RecordNotFound | Y         | Return nil, log warning | "Not found" message
```

## Rules for This Section

- `rescue StandardError` is ALWAYS a smell. Name the specific exceptions.
- `rescue => e` with only `Rails.logger.error(e.message)` is insufficient. Log the full context: what was being attempted, with what arguments, for what user/request.
- Every rescued error must either: retry with backoff, degrade gracefully with a user-visible message, or re-raise with added context. "Swallow and continue" is almost never acceptable.
- For each GAP (unrescued error that should be rescued): specify the rescue action and what the user should see.

## LLM/AI Failure Modes

For LLM/AI service calls specifically: what happens when the response is malformed? When it's empty? When it hallucinates invalid JSON? When the model returns a refusal? Each of these is a distinct failure mode.
