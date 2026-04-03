# polimi_THESIS_2026

Master thesis repository: **Lombardy heat environment and heat exposure / risk mapping** using remote sensing (Google Earth Engine) and population data.

## What is in this repo

| Path | Purpose |
|------|---------|
| [`gee/heat_risk_lombardy_2020_2022.js`](gee/heat_risk_lombardy_2020_2022.js) | Earth Engine script: \(\Delta T\) hazard (Landsat), **2020–2022** summer mean, **WorldPop 2020** density, **Risk = H_norm × pop density** |
| [`gee/heat_risk_lombardy_2020_2022.md`](gee/heat_risk_lombardy_2020_2022.md) | Same script embedded in Markdown (for copy-paste) |
| [`docs/methodology.md`](docs/methodology.md) | Method summary (equations, data sources) |
| [`src/plot_risk.py`](src/plot_risk.py) | Optional local plotting of exported GeoTIFFs |
| [`requirements.txt`](requirements.txt) | Python deps for `plot_risk.py` |

## Run Google Earth Engine

1. Open [Earth Engine Code Editor](https://code.earthengine.google.com/).
2. Paste the contents of [`gee/heat_risk_lombardy_2020_2022.js`](gee/heat_risk_lombardy_2020_2022.js).
3. Click **Run**. Check layers on the map.
4. Open the **Tasks** tab and **Run** each export to Google Drive (folder `GEE_Lombardy_HeatRisk` by default).

Exports (100 m, EPSG:32632):

- `lombardy_deltaT_mean_2020_2022` — mean annual \(\Delta T\) (°C)
- `lombardy_H_norm_2020_2022` — min–max normalized hazard in Lombardy
- `lombardy_pop_density_2020` — population density (people/km²)
- `lombardy_heat_risk_2020_2022` — **Risk** raster

## Optional: plot exports locally

```bash
pip install -r requirements.txt
python src/plot_risk.py --risk path/to/lombardy_heat_risk_2020_2022.tif --out outputs/risk_map.png
```

## Literature alignment

Thermal anomaly \(\Delta T\) follows the **pin / non-urban reference** idea used in Gianquintieri et al. (Padua case); this repo uses a **simplified risk** product: **no elderly vulnerability layer**, only **population density exposure**.

## License

See [LICENSE](LICENSE).
