"""Merge WTI shard JSON files into wti_data.json."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from worldthreatindex import WTIAnalyzer


def main():
    root = Path(__file__).resolve().parents[1]
    shard_files = sorted(root.glob("wti_shard_*.json"))
    if not shard_files:
        print("No shard files found")
        return 1

    combined = {}
    for shard_file in shard_files:
        data = json.loads(shard_file.read_text(encoding="utf-8"))
        combined.update(data.get("countries", {}))
        print(f"Merged {shard_file.name}: {len(data.get('countries', {}))} countries")

    analyzer = WTIAnalyzer(output_path=str(root))
    analyzer._write_dashboard(combined)
    print(f"Published wti_data.json with {len(combined)} country blocks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())