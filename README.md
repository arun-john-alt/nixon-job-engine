# Nixon Job Engine

A separate Nextmove dashboard for Chennai and fully remote India test automation, Senior SDET, networking QA and test leadership roles. Minimum target: **₹25 lakh annual total CTC**. No deadline or current compensation has been assumed.

## Status

Published with 22 reviewed roles. Each recommendation has a weighted match percentage, documented gaps and an authentic locally bundled employer mark. Sources were reviewed on 18 September 2026 via public search indexes; they are **not guaranteed live vacancies**. No reviewed role discloses a verified ₹25L+ annual total CTC budget. Salary unknown stays eligible; match does not imply salary eligibility.

Repository: https://github.com/arun-john-alt/nixon-job-engine

Live site: https://arun-john-alt.github.io/nixon-job-engine/

Initial scan and Pages deployment succeeded on 19 September 2026 (Actions run 35423204474). No search API secret is configured: the first run performed a limited employer check, found no new leads and retained the 15 reviewed records. The daily schedule is enabled; a scheduled run has not yet been observed. Never force-push.

## Use

```sh
python3 -m http.server 8005 --directory site
```

Open http://localhost:8005. The separate `nixon-private-workspace.json` imports under **Import profile**. Keep it private: it contains contact details and the resume. The source PDF is unchanged and outside this repository.

The public site offers job research. Nixon can import his profile, save jobs, record applications, approve truthful resume edits and export DOCX or print/PDF. Nothing submits applications automatically. Local changes do not change the shared public dataset. Private browser data does not sync between devices. Use encrypted backups to transfer it explicitly.

This version uses separate `nje-v2-*` storage keys and Nixon-specific backup types so it does not load another candidate’s workspace on the same GitHub Pages origin. This prevents accidental mixing, not malicious access: GitHub Pages paths under the same owner share a browser origin and are not separate security boundaries.

## Priorities

Default order follows: product companies → manager roles → employer-disclosed annual total CTC → Chennai before fully remote India → profile match. Company classification uses evidence about the hiring company, not a services client. A badge is not an endorsement or salary claim. Services roles remain available. Technical leads are not automatically treated as people managers.

Salary estimates, annual base pay and unknown pay do not masquerade as verified total CTC. None of the current roles discloses an annual total CTC budget. Select Best match to sort purely by resume fit. Fully remote filters include only reviewed India-eligible roles; hybrid jobs elsewhere do not qualify.

## Matching

Weights: responsibilities 35, tools 20, relevant seniority 20, industry 15, location 10. Scores are human-reviewed evidence heuristics, not employer ATS ratings. Search leads remain in Sources until a full description supports a score; daily discovery does not automatically review or promote them.

The supplied resume says 11+ years, but dated IT jobs total approximately 9.5 years excluding the MBA break as of September 2026. Matching uses the dated history; the candidate should reconcile the discrepancy before claiming an exact total. Advanced AI, Java, C++, Playwright, Pytest and routing-protocol expertise are not inferred from adjacent skills. Cloud/Kubernetes/GenAI familiarity is introductory.

## Daily workflow

`.github/workflows/engine.yml` schedules scans at 03:30 UTC / **9 AM IST**, with testing and Pages deployment. GitHub scheduled execution is best-effort and can be delayed. A workflow file alone does not prove execution; check Actions after setup.

Without a search secret, only existing roles on approved employer sites are rechecked. This is limited coverage and cannot check LinkedIn availability. Add `TAVILY_API_KEY` (or the supported alternative `BRAVE_SEARCH_API_KEY`) to the new repository’s Actions secrets for broader employer and LinkedIn search-index discovery. Never put a key in frontend code or commit it. GitHub cannot reveal an existing repository secret for copying; set it separately in this repository.

Twelve targeted query themes rotate across three days, covering product firms, management, salary evidence, Chennai and fully remote India. The default daily budget is four basic discovery searches plus two rotating exact-URL availability searches per run: up to six search requests/day, or 186 in a 31-day month, excluding manual runs. If sharing a provider account, count usage from all repositories. No complete LinkedIn coverage or instant closure detection is promised. Explicit closure signals hide jobs; failed requests and missing results do not prove closure. No login or anti-bot bypass is used.

The bot commits only `site/data/jobs.json` and deploys the allowlisted `dist/` output. Search failures preserve existing research. The frontend never receives credentials.

## Validation and publication

Requirements: Node 20+, Python 3.10+, Git and authenticated GitHub CLI for publication. No npm packages required.

```sh
node --test tests/*.test.js
python3 -m unittest discover -s tests -p 'test_*.py'
node scripts/validate.mjs
python3 scripts/build.py
```

Inspect the staged files before publishing. Exclude private workspace JSON, source resumes, contacts, current compensation, notes, generated resumes and credentials. The build has an exact file allowlist and rejects private dataset keys. Review free text too.

After explicit approval, publish the new public repository, push `main`, enable GitHub Actions as the Pages source and dispatch the included workflow. The guarded `scripts/publish.sh OWNER/REPO --public` helper is only for a fresh folder with no Git history and refuses an existing remote repository. Verify the Pages run and live URL before calling deployment complete.

Live URL: https://arun-john-alt.github.io/nixon-job-engine/

See `docs/QA.md` for actual checks and `docs/COMPANY_LOGOS.md` for asset provenance.
