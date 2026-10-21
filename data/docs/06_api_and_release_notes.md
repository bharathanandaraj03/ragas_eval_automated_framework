# Orbitly API Guide and Release Notes

> Fictional company and product, created as demo data for RAG evaluation.

## API basics

The Orbitly REST API is available at `https://api.orbitly.example/v3`. API access is included on the Business and Enterprise plans; it is not available on Starter. Requests are authenticated with a personal access token sent in the `Authorization: Bearer <token>` header. Tokens expire after 90 days and can be revoked at any time from Settings → Developer.

## Rate limits

Rate limits are applied per token:

- Business: 1,000 requests per minute.
- Enterprise: 5,000 requests per minute.

Requests above the limit receive HTTP 429 with a `Retry-After` header. Webhooks are retried up to 5 times with exponential backoff if the receiving endpoint does not return a 2xx status.

## Pagination

List endpoints use cursor-based pagination. The default page size is 50 items and the maximum is 200.

---

## Release notes

### Version 3.4 — August 2026
- Added AI task summaries in Boards (Business and Enterprise only).
- Timeline now supports baseline comparisons.
- Fixed an issue where WIP limits were ignored on swimlanes.

### Version 3.2 — March 2026
- **Raised the Business API rate limit from 600 to 1,000 requests per minute.**
- Added the GitLab integration.
- Deprecated API v2. API v2 will be shut down on 31 January 2027.

### Version 3.0 — October 2025
- Launched API v3 with cursor-based pagination (API v2 used offset pagination).
- Introduced the Automations module.
- Raised the per-file attachment limit from 100 MB to 250 MB.

### Version 2.6 — April 2025
- Added Microsoft Teams integration.
- Business API rate limit set to 600 requests per minute.
