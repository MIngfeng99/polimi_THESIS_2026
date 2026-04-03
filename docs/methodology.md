# Methodology: Lombardy heat exposure / risk (2020–2022)

This note matches the Earth Engine workflow implemented as:

- Python: [`src/lombardy_heat_risk_gee.py`](../src/lombardy_heat_risk_gee.py) and [`notebooks/lombardy_heat_risk_2020_2022.ipynb`](../notebooks/lombardy_heat_risk_2020_2022.ipynb)
- JavaScript (Code Editor): [`gee/heat_risk_lombardy_2020_2022.js`](../gee/heat_risk_lombardy_2020_2022.js)

## Study area and period

- **Region**: Lombardy, Italy (`FAO/GAUL/2015/level1`, Italy, `Lombardia` / `Lombardy`).
- **Years**: 2020, 2021, 2022 (summers only: 1 June–31 August).
- **Output CRS / scale**: `EPSG:32632`, **100 m** (resampled from Landsat ~30 m LST).

## Hazard: thermal anomaly \(\Delta T\) (Landsat)

For each summer:

1. **LST from Landsat 8/9 Collection 2 Level-2** (`LANDSAT/LC08/C02/T1_L2`, `LANDSAT/LC09/C02/T1_L2`), band `ST_B10`.
2. **Cloud / shadow mask** using `QA_PIXEL` (exclude dilated cloud, cirrus, cloud, cloud shadow bits).
3. Convert to °C (Collection 2 scaling):

   \[
   T_K = \mathrm{ST\_B10} \times 0.00341802 + 149.0,\quad T_C = T_K - 273.15
   \]

4. **Per-pixel summer composite**: \( \mathrm{LST}_{p95} \) = pixel-wise **95th percentile** of clear \(T_C\) across all summer acquisitions.

5. **Rural reference \(T_{\mathrm{ref}}\)** (pins-style region, inspired by Gianquintieri et al.):

   - Build a **15–20 km annulus** around the **Lombardy polygon centroid**.
   - Use **ESA WorldCover v200 2021** “rural” classes: tree (10), shrub (20), grass (30), crop (40).
   - \(T_{\mathrm{ref}}\) = **mean** of \(\mathrm{LST}_{p95}\) over masked rural pixels **inside the annulus**.
   - If the annulus contains **zero** valid rural pixels (pixel count \(=0\)), fall back to the **mean** of \(\mathrm{LST}_{p95}\) over rural pixels across the **full Lombardy AOI** (robustness).

6. **Thermal anomaly** (hazard layer):

   \[
   \Delta T = \mathrm{LST}_{p95} - T_{\mathrm{ref}}
   \]

7. **Three-year hazard**: \(\overline{\Delta T} = \mathrm{mean}(\Delta T_{2020}, \Delta T_{2021}, \Delta T_{2022})\).

8. **Normalization within Lombardy** (min–max):

   \[
   H_{\mathrm{norm}} = \frac{\overline{\Delta T} - \min(\overline{\Delta T})}{\max(\overline{\Delta T}) - \min(\overline{\Delta T})}
   \]

## Exposure: population density (WorldPop)

- **Dataset**: `WorldPop/GP/100m/pop`, filtered to **2020** (`filterDate('2020-01-01','2021-01-01')`).
- **Density**: population count per pixel divided by pixel area (km²), yielding **people/km²**.

## Risk (continuous)

\[
\mathrm{Risk} = H_{\mathrm{norm}} \times \mathrm{PopDensity}
\]

This is a **continuous exposure–intensity** product (not a full HERI, which also weights vulnerability).

## Relation to Gianquintieri et al. (Padua)

Their hazard uses **urban thermal anomaly** \(\Delta T\) relative to non-urban “pins”, and they combine **exposure** (population density) and **vulnerability** (e.g. elderly share) into **HERI** with fixed weights. Here we keep the **\(\Delta T\)** hazard logic (simplified reference region) but **only multiply by population density** as agreed for your thesis scope.

## Uncertainty (brief)

- **LST vs air temperature**: \(\Delta T\) is **surface** thermal contrast; interpret as hazard proxy, not 2 m air temperature.
- **Temporal sampling**: Landsat revisit limits how many clear observations enter \(\mathrm{LST}_{p95}\); cloudy summers can bias composites.
- **WorldPop**: 2020 population held constant for all three hazard years by design.
