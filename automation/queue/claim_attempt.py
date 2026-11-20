"""Atomically reserve a bounded worker attempt in CIPI main before compute.

A normal GitHub Actions failure/timeout cannot leave a high-priority QUEUED job
eligible forever. Contents PUT uses the previous blob SHA for CAS under the
workflow's global concurrency lock. No secret or raw research evidence is saved.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timedelta, timezone
import json
import os
import re
import time
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

REPOSITORY = "techitechi0331-svg/cipi"
MAX_ATTEMPTS = 3
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class AttemptExhausted(RuntimeError):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("retry lease must have a UTC timezone")
    return parsed.astimezone(timezone.utc)


def build_attempt(
    old: dict[str, Any] | None, job_id: str, run_id: str, at: datetime
) -> tuple[dict[str, Any], bool]:
    if not ID.fullmatch(job_id) or not ID.fullmatch(run_id):
        raise ValueError("invalid job or run identifier")
    data = dict(old or {})
    if data and (data.get("schema_version") != "1.0" or data.get("job_id") != job_id):
        raise ValueError("inconsistent existing job attempt ledger")
    old_runs = list(data.get("runs") or [])
    if run_id in (run.get("run_id") for run in old_runs if isinstance(run, dict)):
        return data, False  # idempotent after lost response
    count = data.get("attempt_count", 0)
    if type(count) is not int or count < 0 or count > MAX_ATTEMPTS:
        raise ValueError("invalid attempt_count")
    if count >= MAX_ATTEMPTS:
        raise AttemptExhausted(f"{job_id}: manual review required after {count} attempts")
    eligible = data.get("next_retry_at")
    if eligible and parse_iso(str(eligible)) > at:
        raise AttemptExhausted(f"{job_id}: retry cooldown still active")
    next_count = count + 1
    duration_minutes = 15 * (2 ** (next_count - 1))
    data.update({
        "schema_version": "1.0",
        "job_id": job_id,
        "attempt_count": next_count,
        "max_attempts": MAX_ATTEMPTS,
        "next_retry_at": (at + timedelta(minutes=duration_minutes)).isoformat(),
        "latest_claimed_run": run_id,
        "requires_review_after_limit": True,
        "authority": "AUTONOMATED_ATTEMPT_ACCOUNTING_ONLY",
        "automatic_product_decision": False,
        "automatic_knowledge_promotion": False,
        "runs": (old_runs + [{
            "run_id": run_id, "attempt": next_count,
            "claimed_at": at.isoformat(),
            "cooldown_minutes": duration_minutes,
        }])[-MAX_ATTEMPTS:],
    })
    return data, True


def api(method: str, url: str, token: str, body: dict | None = None) -> dict:
    payload = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = Request(url, data=payload, headers=headers, method=method)
    with urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def reserve(job_id: str, run_id: str, token: str) -> None:
    if not ID.fullmatch(job_id) or not ID.fullmatch(run_id):
        raise ValueError("invalid job or run identifier")
    uri = f"https://api.github.com/repos/{REPOSITORY}/contents/research/job_attempts/{job_id}.json"
    for tries in range(4):
        original_sha: str | None = None
        previous: dict | None = None
        try:
            existing = api("GET", uri + "?ref=main", token)
            original_sha = str(existing["sha"])
            if existing.get("type") != "file" or existing.get("encoding") != "base64":
                raise RuntimeError("invalid remote attempt ledger representation")
            data = base64.b64decode(existing["content"]).decode("utf-8")
            previous = json.loads(data)
        except HTTPError as exc:
            if exc.code != 404:
                raise
        record, changed = build_attempt(previous, job_id, run_id, utc_now())
        if not changed:
            print(f"research attempt already claimed: {job_id}/{run_id}")
            return
        body = {
            "message": f"reserve bounded autonomous research attempt: {job_id}",
            "branch": "main",
            "content": base64.b64encode(
                (json.dumps(record, sort_keys=True, indent=2) + "\n").encode("utf-8")
            ).decode("ascii"),
        }
        if original_sha:
            body["sha"] = original_sha
        try:
            api("PUT", uri, token, body)
            print(f"CLAIMED job={job_id} run={run_id} attempt={record['attempt_count']}/{MAX_ATTEMPTS}")
            return
        except HTTPError as exc:
            if exc.code not in {409, 422} or tries == 3:
                raise
            time.sleep(1 + tries)
    raise RuntimeError("could not reserve job attempt after bounded retries")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--job-id", required=True)
    p.add_argument("--run-id", required=True)
    args = p.parse_args()
    if os.environ.get("GITHUB_REPOSITORY") != REPOSITORY or os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise SystemExit("refusing attempt lease outside trusted CIPI/main")
    token = os.environ.get("GH_TOKEN", "").strip()
    if not token:
        raise SystemExit("missing GH_TOKEN for protected attempt reservation")
    reserve(args.job_id, args.run_id, token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
