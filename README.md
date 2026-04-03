# polimi_THESIS_2026

Master thesis repository: **Lombardy heat environment and heat exposure / risk mapping** using remote sensing (Google Earth Engine) and population data.

## What is in this repo

| Path | Purpose |
|------|---------|
| [`notebooks/lombardy_heat_risk_2020_2022.ipynb`](notebooks/lombardy_heat_risk_2020_2022.ipynb) | **Recommended:** Jupyter + **geemap** — same workflow as JS, export via `ee.batch.Export` to Drive |
| [`src/lombardy_heat_risk_gee.py`](src/lombardy_heat_risk_gee.py) | Python EE logic (`build_stack`, `export_image_to_drive`) used by the notebook |
| [`gee/heat_risk_lombardy_2020_2022.js`](gee/heat_risk_lombardy_2020_2022.js) | Legacy Earth Engine **JavaScript** (Code Editor) — identical logic |
| [`gee/heat_risk_lombardy_2020_2022.md`](gee/heat_risk_lombardy_2020_2022.md) | Same JS script embedded in Markdown (for copy-paste) |
| [`docs/methodology.md`](docs/methodology.md) | Method summary (equations, data sources) |
| [`src/plot_risk.py`](src/plot_risk.py) | Optional local plotting of exported GeoTIFFs |
| [`requirements.txt`](requirements.txt) | Python deps (EE, geemap, Jupyter, plotting) |

## Run Google Earth Engine (Python + Jupyter)

1. Install dependencies and authenticate once:
   ```bash
   pip install -r requirements.txt
   earthengine authenticate
   ```
2. Start Jupyter from the **repository root**:
   ```bash
   jupyter notebook notebooks/lombardy_heat_risk_2020_2022.ipynb
   ```
3. Run all cells: map layers render in the notebook; the last cell **starts** export tasks to Google Drive (folder `GEE_Lombardy_HeatRisk` by default). Check task status on [Earth Engine Tasks](https://code.earthengine.google.com/tasks).

If your account uses a **Cloud project** for Earth Engine, replace `ee.Initialize()` in the notebook with `ee.Initialize(project='your-project-id')`.

## Run Google Earth Engine (JavaScript Code Editor)

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
