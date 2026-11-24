"""Summarize a local, de-identified collaboration sample; no network calls."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re


def is_alias(value, prefix):
    return isinstance(value, str) and re.fullmatch(prefix + r"[0-9]{2,8}", value) is not None


def summarize(data):
    if not isinstance(data, dict) or set(data) != {"teams", "events"}:
        raise ValueError("Expected only teams and events")
    teams, events = data["teams"], data["events"]
    if not isinstance(teams, dict) or not isinstance(events, list):
        raise ValueError("Expected a team mapping and event list")
    if any(not is_alias(p, "P") or not is_alias(t, "T") for p, t in teams.items()):
        raise ValueError("Use participant and team aliases")
    seen = set()
    directions, kinds = Counter(), Counter()
    internal = 0
    for event in events:
        if not isinstance(event, dict) or set(event) != {"id", "kind", "from", "to"}:
            raise ValueError("Unexpected event fields")
        eid, kind = event["id"], event["kind"]
        if not is_alias(eid, "E") or eid in seen:
            raise ValueError("Each event needs a distinct anonymous ID")
        seen.add(eid)
        if kind not in ("request", "handoff", "decision"):
            raise ValueError("Unknown event category")
        source, target = event["from"], event["to"]
        if not is_alias(source, "P") or source not in teams or not is_alias(target, "P") or target not in teams:
            raise ValueError("Missing participant alias")
        kinds[kind] += 1
        pair = teams[source], teams[target]
        if pair[0] == pair[1]:
            internal += 1
        else:
            directions[pair] += 1
    return {
        "events": len(events),
        "within_team": internal,
        "cross_team": len(events) - internal,
        "by_kind": dict(sorted(kinds.items())),
        "cross_team_directions": [
            {"from": pair[0], "to": pair[1], "count": count}
            for pair, count in sorted(directions.items())
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sample", type=Path)
    args = parser.parse_args()
    try:
        result = summarize(json.loads(args.sample.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(2, f"Cannot summarize sample: {exc}\n")
    print(json.dumps(result, indent=2))
