# Daily discovery

The primary trigger remains 09:00 Asia/Kolkata (03:30 UTC). Hourly backup triggers run at 09:47 through 23:47 IST. GitHub scheduling is best-effort: backup triggers improve recovery from a missing primary event but cannot guarantee a run during a GitHub outage.

The existing workflow concurrency lock serializes scan and deployment work. Checkout explicitly reads current `main` after acquiring the lock, so queued runs see the latest recorded scan. The daily gate uses the IST date saved by the scanner. Before 09:00 IST, scheduled events wait; after a scan is recorded that day, scheduled events skip tests, search calls, build and deployment. Push events still publish changes. Manual discovery also respects the daily limit; publish-only dispatches still deploy.

A limited scan counts for the day to avoid repeatedly using the shared API quota. A job that fails before committing its scan record can retry on a later trigger; calls made before such a failure may consume additional credits. A recorded scan followed by a deployment failure should be recovered with a publish-only dispatch.

Verification covers the 09:00 boundary, IST versus UTC dates, legacy records, later backups, next-day recovery, limited results, and manual/push behavior. New leads still require full-description review before appearing as scored recommendations.
