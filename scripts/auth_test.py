"""Step 1 (BREX-100): connection test via management/brand-radar-reports (does not consume units).

Usage:  python -m scripts.auth_test
"""
import json
import logging
import sys

from brex.client import AhrefsClient

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def main() -> int:
    try:
        data = AhrefsClient().list_reports()
    except Exception as e:  # noqa: BLE001
        print(f"Connection failed: {e}", file=sys.stderr)
        return 1
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
