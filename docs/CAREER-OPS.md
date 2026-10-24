# Nixon Career Ops trial — 24 October 2026

Nixon only. Nextmove's Career Ops tab is a separate, source-attributed cohort; the regular Jobs view remains unchanged.

## What actually ran

Unmodified `scan.mjs --json --quiet` from https://github.com/career-ops-hq/career-ops at commit `2d6ed587e60cbb1aaaac7e3dd4a9f5b7b46a26af` (version 1.38.0, MIT). It ran in an isolated checkout with a sanitized role/location profile, no resume, credentials, API key or authenticated browser session. Upstream dependencies were installed with lifecycle scripts disabled. Its receipt recorded 69 scanned employer boards, 25 unsupported sources skipped, 47,096 broad postings examined and 20 title/location candidates. These counts do not represent 47,096 relevant openings.

Codex assessed full employer descriptions using the upstream five-dimension rubric: CV match, North Star alignment, compensation, cultural signals and red flags. This was agent-assisted review, not the upstream API evaluator. Native 1–5 ratings are holistic judgments; Nextmove's weighted match percentage stays independent. Unknown compensation and independent culture evidence mean low confidence.

The first cohort contains Extreme Networks 10413 and YipitData 6743082, both already covered by Nextmove. Their freshly fetched descriptions matched their recorded SHA256 hashes. Other leads were excluded or not promoted: manufacturing QA/inspection, below-level roles, or material specialist/experience gaps. In particular Strategy's manager requires 12+ years and BI/AI platform experience; Arista requires RF/L1 and modern Wi-Fi lab expertise. No candidate facts were invented to fill gaps.

## Comparison limits and maintenance

This is a reviewed snapshot, not a daily autonomous Career Ops evaluator. Both methods used substantially overlapping employer sources, so the first trial measures a stricter recommendation layer, not independent discovery coverage or application outcomes. There are currently zero additional recommended vacancies. Do not infer that Career Ops cannot discover more elsewhere from this trial.

Recommendation records reference the same vacancy IDs and reviewed description hashes. Existing hourly employer checks therefore control closure/availability for both views. A closed, unconfirmed beyond 48h, unreviewed, excluded or changed-description job disappears from Career Ops, even when archived jobs are enabled. Reappearance after a description change requires explicit re-review. New Career Ops discovery and scoring are not scheduled; this is disclosed in the UI.

Shared job IDs preserve the same private Saved/tracking record. No upstream runtime, profile, original resume or credentials ship to the browser. Only the public receipt summary, source URLs and recommendation evidence ship. The public build checks both datasets for forbidden private fields.

## 25 October correction

The first adapter could only select records already in Nextmove, making additional coverage impossible by construction. The adapter now accepts a separately validated `jobs` collection in the trial dataset. Those records remain excluded from regular scored matches and compare by vacancy ID; shared tracking remains available. A regression test proves an independent vacancy increases additional coverage. No synthetic fixture is published.

A real upstream scan of two additional sources, Gigamon (Jobvite) and Gen Digital (Ashby), examined 142 postings and found four title/location candidates. The public expansion receipt records their URLs and screening status. Two Gigamon descriptions show level/specialist gaps; the cloud role also has unproven cloud/infrastructure requirements, and the Gen Digital full-description API returned HTTP 403. None has been promoted simply to raise the count. Discovery and evaluation remain manual. Future independent records require their own refreshed availability evidence; the 48-hour gate hides stale records. The original two shared recommendations continue to use existing hourly checks.
