# Employer coverage and review — 22 October 2026

Nixon's employer coverage increased from 11 to 62 configured, verified career sources. The current release has 16 directly confirmed, reviewed roles, plus three confirmed openings whose profile-match review is pending. Sivanesh's companion engine increased from seven to 45 sources and from two to six directly confirmed, reviewed roles.

Sources include SmartRecruiters, Lever, Greenhouse, Ashby, and employer Workday career data. Workday searches use public career-site configuration, observe robots rules, and submit only read-only job-search queries. Every positive availability result requires the exact vacancy, matching requisition/application route, and affirmative application evidence. Search results, a page fetch, and a failed request cannot refresh an open timestamp.

The UI provides **More open jobs** separately from reviewed matches. It shows only fresh, eligible vacancies and explicitly labels profile review as pending. It does not invent percentages. The 48-hour expiry and deadline/closure checks apply to both views.

All newly scored roles were reviewed against their full current employer descriptions and existing candidate resume evidence. Python/automation/networking overlap is distinguished from unproven PySpark, AI evaluation, specialist hardware, C#/Java and data-warehouse requirements. Lower experience bands and unknown salaries remain explicit. Product-company and manager priorities continue to apply.

Tests cover exact Workday identity, application flags and deadlines, malformed hosts, robots denial, partial feed failures, distinct requisitions with identical titles, singular/unicode experience ranges, pending-view filtering and HTML escaping. Public build allowlist and private-field gates pass. Local preview shows the updated counts and the new view.

The workflow still targets 09:00 IST, with existing fallback behavior. Employer feeds do not consume the shared search-provider credits. New discoveries require full description review before becoming scored recommendations; employer description changes clear existing scores for re-review. No external account or private candidate data was added.

Public API references: [Ashby](https://developers.ashbyhq.com/docs/public-job-posting-api), [SmartRecruiters](https://developers.smartrecruiters.com/docs/endpoints), [Greenhouse](https://docs.greenhouse.io/job-board.html), [Lever](https://github.com/lever/postings-api).
