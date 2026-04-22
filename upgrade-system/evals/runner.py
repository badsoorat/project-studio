#!/usr/bin/env python3
"""
upgrade-system eval runner — 5-tier regime (plan §3).

Entry point for CI and local runs. Each tier lives under `tiers/<T>/`
and exposes a `run(args) -> TierResult` function.

Usage:
    python upgrade-system/evals/runner.py --tier T1
    python upgrade-system/evals/runner.py --tier all
    python upgrade-system/evals/runner.py --tier T3 --atom atom-017-classifier

Exit codes:
    0   all requested tiers passed
    1   one or more tiers failed
    2   runner error (bad args, missing tier, etc.)

Stage of record: F1 skeleton. F4 fleshes out the tier contents.
Plan §3, §11 (F4 exit criteria).
"""
from __future__ import annotations

import argparse
import importlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
TIERS_DIR = Path(__file__).resolve().parent / "tiers"

# Canonical tier order — CI enforces that T(n) runs only after T(n-1) passes.
TIER_ORDER = ["T1-lint", "T2-structural", "T3-behavioral", "T4-integration", "T5-compat"]


@dataclass
class TierResult:
    name: str
    passed: bool
    summary: str
    failures: List[str] = field(default_factory=list)


def _resolve_tier(tier_name: str) -> str:
    # Accept both "T1" and "T1-lint"
    if tier_name in TIER_ORDER:
        return tier_name
    for canonical in TIER_ORDER:
        if canonical.startswith(tier_name + "-") or canonical.split("-")[0] == tier_name:
            return canonical
    raise SystemExit(f"error: unknown tier '{tier_name}'. valid: {', '.join(TIER_ORDER)}")


def run_tier(tier: str, atom: Optional[str] = None) -> TierResult:
    """Dynamically import `tiers.<tier>.entrypoint` and delegate.

    Each tier MUST expose a module-level `run(atom: Optional[str]) -> TierResult`
    function. In F1 this is a skeleton; tiers are stub-only.
    """
    canonical = _resolve_tier(tier)
    tier_path = TIERS_DIR / canonical
    entry = tier_path / "entrypoint.py"

    if not entry.exists():
        # F1 skeleton — no tiers implemented yet. Return a passing stub so
        # the scaffold's own CI can exercise the runner.
        return TierResult(
            name=canonical,
            passed=True,
            summary=f"{canonical} — stub (no entrypoint.py yet; F4 delivers implementations)",
        )

    # Import tiers.<canonical>.entrypoint
    sys.path.insert(0, str(TIERS_DIR))
    try:
        mod = importlib.import_module(f"{canonical}.entrypoint")
    finally:
        sys.path.pop(0)

    return mod.run(atom=atom)


def main() -> int:
    p = argparse.ArgumentParser(description="upgrade-system eval runner")
    p.add_argument("--tier", required=True, help="tier name (T1..T5, or 'all')")
    p.add_argument("--atom", default=None, help="limit to one atom ID (T3+ only)")
    args = p.parse_args()

    if args.tier == "all":
        tiers_to_run = TIER_ORDER
    else:
        tiers_to_run = [_resolve_tier(args.tier)]

    overall_pass = True
    for t in tiers_to_run:
        r = run_tier(t, atom=args.atom)
        status = "PASS" if r.passed else "FAIL"
        print(f"[{status}] {r.name} — {r.summary}")
        for f in r.failures:
            print(f"    - {f}")
        overall_pass = overall_pass and r.passed

    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
