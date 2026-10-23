# Company-first testing-role discovery — 23 October 2026

The next improvement is employer coverage, not a claim to list every company or a quota of weak matches. The catalog contains research targets. It does not assert that every company currently has a suitable Chennai role, meets the salary target, or qualifies for the product-company badge.

## References examined

- [JobSpy](https://github.com/speedyapply/JobSpy): 4,543 stars at review, MIT. Useful patterns: provider adapters, normalized outputs, concurrent collection, location/country and age filters, explicit per-provider failures. It supports India-focused Naukri discovery. Its LinkedIn and other scraper integrations remain dependent on platform access restrictions; this release adds no JobSpy dependency or proxy mechanism.
- [JobFunnel](https://github.com/PaulMcInnis/JobFunnel): 2,196 stars, MIT, last pushed December 2025 at review. Useful patterns: master inventory, deduplication, history/cache, configurable company exclusions, job-age filtering and respectful request delays. Its documented locales do not include India, so it is an architectural reference rather than a drop-in Chennai search engine.
- [MochiDay](https://github.com/MochiDay/mochiday): a smaller reference (70 stars; last pushed January 2025), Apache-2.0. Demonstrates employer ATS ingestion with a separate web client. Prefer the current official [Greenhouse](https://docs.greenhouse.io/job-board.html) and [Lever](https://github.com/lever/postings-api) contracts for implementation.

No external project code was copied and no new service/account is required.

## Implemented

- A 26-company catalog adds Chennai startup/product-company research alongside the existing employer boards. Examples include Rocketlane, SuperOps, Facilio, Kissflow, Chargebee, Zoho, Freshworks, SurveySparrow, Testsigma, Spendflo, Zuper, Disprz, Uniphore, FourKites, M2P and Yubi. Smaller company career pages are included too.
- Ten due company pages per hourly replenishment run, a persistent rotation cursor, six-hour refresh spacing for fetched pages and twelve-hour backoff for unavailable pages. At startup the full catalog fits in three bounded batches; these are attempts, not proof of successful coverage.
- Public employer-linked Greenhouse, Lever, Ashby, SmartRecruiters and Workday boards are recognized and processed by the existing exact-ID ingestion pipeline. Workday hosts explicitly linked by employers remain auditable later.
- Exact structured job pages are accepted only with matching application evidence. New postings remain unscored until full-description review; existing reviewed matches are preserved.
- The role vocabulary includes spelled-out Software Development Engineer in Test, QE and software/network/system/firmware validation or verification. Twelve additional startup, senior/staff, test architect, API/mobile and portal search phrases rotate within the existing four-query daily API budget.
- Per-company coverage distinguishes ATS links, structured vacancies, blocked/unavailable sources, explicit no-opening messages and pages needing another adapter. A fetched directory is never reported as zero available roles merely because its jobs are rendered by JavaScript.

## Remaining coverage work

Many Chennai startups use Zoho Recruit, Freshteam, Kula, Workable, Keka, custom JavaScript boards or recruiter posts. Each needs an appropriate public connector, feed or employer-indexed search route. Kula documents a public XML feed at the employer career page's `/feed`; its authenticated Job Boards API requires the employer's key and must not be treated as an unauthenticated third-party API. See [Kula feed documentation](https://support.kula.ai/articles/8061577825-publishing-an-xml-job-feed).

Add companies continuously from local startup directories, investor portfolio pages and discovered employer hiring posts, verifying their identity and primary career route before activating them. A company registry is an expandable index, not an exhaustive Chennai-company database.

Next priorities are connectors for the largest uncovered Chennai portals, company/role-focused discovery queries, and an evidence-based match-review queue that can publish suitable new roles promptly. A larger company count alone is not a larger count of relevant, currently open jobs. No salary or qualification gate is relaxed for a target count.
