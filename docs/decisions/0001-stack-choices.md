# 0001: Stack choices

Date: November 2026. Status: accepted.

## Decisions

- **Python 3.14 and Django 5.2 LTS.** 5.2 is supported until April 2028. The plan is to move to Django 6.2 LTS (due April 2027, supported until April 2030) in one upgrade pull request.
- **MySQL 8.4 LTS.** It matches the version on Aiven's free hosted MySQL plan, so development and production run the same major version. 9.7 LTS exists and can be adopted once the host offers it.
- **REST, not GraphQL or gRPC.** One frontend with predictable screens; REST keeps rate limiting and permissions simple per endpoint.
- **Relational database, not NoSQL.** Money and group membership need transactions and constraints.
- **Public demo runs client-side only.** It needs no backend, so it has no attack surface, cost or cold start. A shared test-vector file will keep the Python and TypeScript money logic in agreement.
- **Free-tier hosting.** Next.js on Vercel, the Django container on Cloud Run or Render, MySQL on Aiven. Rate limiting is built in so free limits are not exceeded.
