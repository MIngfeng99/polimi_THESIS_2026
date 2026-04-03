"""Plot GeoTIFF exports from GEE (risk, H_norm, deltaT, pop_density)."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--risk", type=Path, help="Path to risk GeoTIFF")
    parser.add_argument("--out", type=Path, default=Path("outputs/risk_map.png"))
    args = parser.parse_args()

    if not args.risk or not args.risk.is_file():
        raise SystemExit("Provide --risk to a valid GeoTIFF.")

    try:
        import rasterio
        from rasterio.plot import show
    except ImportError as e:
        raise SystemExit("Install dependencies: pip install -r requirements.txt") from e

    args.out.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(args.risk) as ds:
        arr = ds.read(1, masked=True)
        fig, ax = plt.subplots(figsize=(8, 10), dpi=150)
        show(arr, ax=ax, cmap="YlOrRd")
        ax.set_title("Heat exposure intensity (H_norm x pop density)")
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(args.out, bbox_inches="tight")
        print(f"Saved: {args.out.resolve()}")


if __name__ == "__main__":
    main()