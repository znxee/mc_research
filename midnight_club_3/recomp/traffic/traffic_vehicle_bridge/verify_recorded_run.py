"""Revalidate recorded telemetry without changing the original run result."""
import argparse
import json
import re
from pathlib import Path

from probe_arcade_traffic import measure_routes


def verify(run: Path) -> dict:
    log = (run / "game.log").read_text(encoding="utf-8", errors="replace")
    metrics = measure_routes(log)
    actors = json.loads((run / "actors.json").read_text(encoding="utf-8"))
    after = json.loads((run / "after_pause_state.json").read_text(encoding="utf-8"))
    binary = json.loads((run / "binary.json").read_text(encoding="utf-8"))
    times = [float(x) for x in re.findall(r"\[\s*([\d.]+)\].*MC3TRAFFIC actor ", log)]
    checks = {
        "six_complete_actors": len(actors) == 6 and all(
            all(int(actor[key], 16) for key in ("owner", "entity", "car", "sim", "input"))
            for actor in actors),
        "ten_minute_telemetry": bool(times) and max(times) - min(times) >= 590,
        "no_exception": "exception " not in log and "KeBugCheck " not in log,
        "heap_valid": "MC3TRAFFIC heap BAD" not in log and
                      log.count("heap phase=after-destroy") == 6,
        "all_routes_moved": len(metrics) == 6 and all(
            row["actor_path_length"] >= 10 and row["oracle_path_length"] >= 10
            for row in metrics.values()),
        "tracking_error_bounded": bool(metrics) and all(
            row["max_tracking_error"] <= 100 for row in metrics.values()),
        "six_owners_released": "MC3TRAFFIC released 6 extra owners" in log,
        "returned_to_frontend": after["state"] == 7 and after["menu_active"],
    }
    return {
        "result": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
        "telemetry_span_seconds": max(times) - min(times) if times else 0,
        "route_metrics": metrics, "binary": binary,
        "original_result_preserved": True,
        "measurement_change": "Use traveled path length, not net displacement, so a closed traffic loop counts as movement.",
        "limits": "Stationary player; no ambient retire/respawn stress; independent Cruise pool still pending.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    report = verify(args.run)
    (args.run / "verified_result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    raise SystemExit(report["result"] != "PASS")
