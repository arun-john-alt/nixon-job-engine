"""Decide whether a serialized workflow should scan or publish today."""
import datetime as dt
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo

IST = ZoneInfo('Asia/Kolkata')


def decision(data, event, requested=False, now=None):
    local = (now or dt.datetime.now(dt.timezone.utc)).astimezone(IST)
    if event != 'schedule' and not (event == 'workflow_dispatch' and requested):
        return False, True, 'Publish only; discovery was not requested.'
    if event == 'schedule' and local.hour < 9:
        return False, False, 'Waiting for the 9 AM IST daily window.'
    run = data.get('run') or {}
    # Older records stored UTC dates only. During the post-9-AM window,
    # the UTC and IST calendar dates agree.
    previous = run.get('scanDateIst') or run.get('checkedOn')
    if previous == local.date().isoformat():
        return False, event != 'schedule', 'Today already has a recorded scan; no search credits used.'
    return True, True, 'Daily scan is due.'


if __name__ == '__main__':
    data = json.loads(Path('site/data/jobs.json').read_text())
    scan, publish, reason = decision(data, os.environ['GITHUB_EVENT_NAME'], os.getenv('REQUEST_SCAN') == 'true')
    with open(os.environ['GITHUB_OUTPUT'], 'a') as out:
        out.write(f'scan={str(scan).lower()}\npublish={str(publish).lower()}\n')
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as out:
        out.write(reason + '\n')
    print(reason)
