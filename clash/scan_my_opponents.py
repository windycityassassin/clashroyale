"""One-shot CLI: score every opponent from your last 25 battles."""

import json
import os
import sys

from dotenv import load_dotenv

from utils.api_client import ClashRoyaleAPI
from utils.bot_detector import RecentOpponentScanner


def main():
    load_dotenv()
    key = os.getenv("CLASH_ROYALE_API_KEY", "").strip()
    tag = os.getenv("PLAYER_TAG", "").strip()
    if not key or not tag:
        print("missing CLASH_ROYALE_API_KEY or PLAYER_TAG in .env", file=sys.stderr)
        sys.exit(1)

    scanner = RecentOpponentScanner(ClashRoyaleAPI(api_key=key))
    report = scanner.scan(tag, limit=25)
    if "error" in report:
        print(report["error"], file=sys.stderr)
        sys.exit(2)

    print(f"\nScanned {report['scanned']} unique opponents of {report['your_tag']}\n")
    print(f"{'tag':<11} {'name':<20} {'lvl':>4} {'troph':>6} {'score':>5}  verdict")
    print("-" * 78)
    for r in report["opponents"]:
        print(
            f"{r['tag']:<11} {(r['name'] or '')[:20]:<20} "
            f"{r['exp_level'] or 0:>4} {r['trophies'] or 0:>6} "
            f"{r['score']:>5}  {r['verdict']}  ({r['your_result']})"
        )

    suspicious = [r for r in report["opponents"] if r["score"] >= 25]
    if suspicious:
        print(f"\nFiring signals on {len(suspicious)} suspicious opponent(s):\n")
        for r in suspicious:
            print(f"  {r['tag']} {r['name']} -> {r['verdict']} (score {r['score']})")
            for s in r["signals"]:
                if s["fired"]:
                    print(f"    [+{s['weight']:>2}] {s['name']}: {s['value']}")

    out_path = "/tmp/opponent_scan.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nFull JSON: {out_path}")


if __name__ == "__main__":
    main()
