"""
Plot GeoTIFF exports from GEE (risk, H_norm, deltaT, pop_density).
从 GEE 导出的 GeoTIFF 制图（风险、H_norm、deltaT、人口密度等）。

Usage / 用法:
  python src/plot_risk.py --risk path/to/lombardy_heat_risk_2020_2022.tif --out outputs/risk_map.png

Requires / 依赖: rasterio, matplotlib, numpy (see requirements.txt)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot a GeoTIFF exported from Earth Engine. / 绘制 Earth Engine 导出的 GeoTIFF。"
    )
    parser.add_argument(
        "--risk",
        type=Path,
        help="Path to risk GeoTIFF / 风险栅格 GeoTIFF 路径",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("outputs/risk_map.png"),
        help="Output PNG path / 输出 PNG 路径",
    )
    args = parser.parse_args()

    if not args.risk or not args.risk.is_file():
        raise SystemExit(
            "Provide --risk to a valid GeoTIFF. / 请提供有效的 --risk GeoTIFF 路径。"
        )

    try:
        import rasterio
        from rasterio.plot import show
    except ImportError as e:
        raise SystemExit(
            "Install dependencies: pip install -r requirements.txt "
            "/ 请先安装依赖：pip install -r requirements.txt"
        ) from e

    args.out.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(args.risk) as ds:
        arr = ds.read(1, masked=True)
        fig, ax = plt.subplots(figsize=(8, 10), dpi=150)
        show(arr, ax=ax, cmap="YlOrRd")
        ax.set_title(
            "Heat exposure intensity (H_norm x pop density) "
            "/ 热暴露强度（H_norm × 人口密度）"
        )
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(args.out, bbox_inches="tight")
        print(f"Saved / 已保存: {args.out.resolve()}")


if __name__ == "__main__":
    main()
