"""
Earth Engine (Python): Lombardy heat hazard / exposure stack (2020–2022).

Mirrors the logic in gee/heat_risk_lombardy_2020_2022.js.
Use after: ee.Initialize() and optional geemap.Map for display.
"""

from __future__ import annotations

import ee

REF_RING_INNER_M = 15000
REF_RING_OUTER_M = 20000


def lombardy_aoi() -> ee.Geometry:
    fc = (
        ee.FeatureCollection("FAO/GAUL/2015/level1")
        .filter(ee.Filter.eq("ADM0_NAME", "Italy"))
        .filter(
            ee.Filter.Or(
                ee.Filter.eq("ADM1_NAME", "Lombardia"),
                ee.Filter.eq("ADM1_NAME", "Lombardy"),
            )
        )
    )
    return fc.geometry()


def mask_landsat_l2sr(image: ee.Image) -> ee.Image:
    qa = image.select("QA_PIXEL")
    mask = (
        qa.bitwiseAnd(1 << 1)
        .eq(0)
        .And(qa.bitwiseAnd(1 << 2).eq(0))
        .And(qa.bitwiseAnd(1 << 3).eq(0))
        .And(qa.bitwiseAnd(1 << 4).eq(0))
    )
    return image.updateMask(mask)


def lst_from_l2(image: ee.Image) -> ee.Image:
    lst_k = image.select("ST_B10").multiply(0.00341802).add(149.0)
    lst_c = lst_k.subtract(273.15).rename("LST")
    return lst_c.copyProperties(image, ["system:time_start"])


def landsat_summer_lst_p95(year: int, region: ee.Geometry) -> ee.Image:
    y = ee.Number(year)
    start = ee.Date.fromYMD(y, 6, 1)
    end = ee.Date.fromYMD(y, 8, 31)
    l8 = (
        ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        .filterBounds(region)
        .filterDate(start, end)
    )
    l9 = (
        ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
        .filterBounds(region)
        .filterDate(start, end)
    )
    col = l8.merge(l9).map(mask_landsat_l2sr).map(lst_from_l2)
    p95 = col.select("LST").reduce(ee.Reducer.percentile([95])).rename("LST")
    return p95.clip(region)


def rural_mask_from_worldcover(region: ee.Geometry) -> ee.Image:
    wc = ee.ImageCollection("ESA/WorldCover/v200/2021").first().select("Map")
    m = (
        wc.eq(10)
        .Or(wc.eq(20))
        .Or(wc.eq(30))
        .Or(wc.eq(40))
        .rename("rural")
    )
    return m.clip(region)


def reference_ring_geometry(region_geom: ee.Geometry) -> ee.Geometry:
    c = region_geom.centroid(ee.ErrorMargin(1))
    outer = c.buffer(REF_RING_OUTER_M)
    inner = c.buffer(REF_RING_INNER_M)
    return outer.difference(inner)


def delta_t_for_year(year: int, region_geom: ee.Geometry) -> ee.Image:
    lst_p95 = landsat_summer_lst_p95(year, region_geom)
    ring = reference_ring_geometry(region_geom)
    rural = rural_mask_from_worldcover(region_geom)

    lst_proj = lst_p95.projection()
    rural_reproj = rural.reproject(crs=lst_proj, scale=30).eq(1)

    masked_ring = lst_p95.updateMask(rural_reproj).clip(ring)

    ref_dict = masked_ring.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=ring,
        scale=30,
        maxPixels=1e13,
        tileScale=2,
    )
    cnt_dict = masked_ring.reduceRegion(
        reducer=ee.Reducer.count(),
        geometry=ring,
        scale=30,
        maxPixels=1e13,
        tileScale=2,
    )

    lst_ref_ring = ee.Number(ref_dict.get("LST"))
    n_pix = ee.Number(cnt_dict.get("LST"))

    fallback_dict = lst_p95.updateMask(rural_reproj).reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=region_geom,
        scale=100,
        maxPixels=1e13,
        tileScale=2,
    )
    lst_ref_fallback = ee.Number(fallback_dict.get("LST"))

    lst_ref = ee.Number(ee.Algorithms.If(n_pix.gt(0), lst_ref_ring, lst_ref_fallback))

    return lst_p95.subtract(lst_ref).rename("deltaT").clip(region_geom)


def hazard_norm_minmax(hazard_mean: ee.Image, aoi: ee.Geometry) -> ee.Image:
    hazard_stats = hazard_mean.reduceRegion(
        reducer=ee.Reducer.minMax(),
        geometry=aoi,
        scale=100,
        maxPixels=1e13,
        tileScale=2,
    )
    h_min = ee.Number(hazard_stats.get("deltaT_min"))
    h_max = ee.Number(hazard_stats.get("deltaT_max"))
    return (
        hazard_mean.subtract(h_min)
        .divide(h_max.subtract(h_min).max(1e-6))
        .rename("H_norm")
        .clip(aoi)
    )


def worldpop_2020_pop_density(aoi: ee.Geometry) -> ee.Image:
    pop_img = (
        ee.ImageCollection("WorldPop/GP/100m/pop")
        .filterDate("2020-01-01", "2021-01-01")
        .mosaic()
        .clip(aoi)
    )
    pop_band = pop_img.bandNames().get(0)
    pop = pop_img.select([pop_band]).rename("population")
    pixel_area_km2 = ee.Image.pixelArea().divide(1e6)
    return pop.divide(pixel_area_km2).rename("pop_density")


def risk_map(hazard_norm: ee.Image, pop_density: ee.Image) -> ee.Image:
    return hazard_norm.multiply(pop_density).rename("risk")


def build_stack() -> dict:
    """
    Returns ee.Image layers and geometry for Lombardy.
    Keys: aoi, d2020, d2021, d2022, hazard_mean, hazard_norm, pop_density, risk
    """
    aoi = lombardy_aoi()
    d2020 = delta_t_for_year(2020, aoi)
    d2021 = delta_t_for_year(2021, aoi)
    d2022 = delta_t_for_year(2022, aoi)
    hazard_mean = d2020.add(d2021).add(d2022).divide(3).rename("deltaT")
    hazard_norm = hazard_norm_minmax(hazard_mean, aoi)
    pop_density = worldpop_2020_pop_density(aoi)
    risk = risk_map(hazard_norm, pop_density)
    return {
        "aoi": aoi,
        "d2020": d2020,
        "d2021": d2021,
        "d2022": d2022,
        "hazard_mean": hazard_mean,
        "hazard_norm": hazard_norm,
        "pop_density": pop_density,
        "risk": risk,
    }


def export_image_to_drive(
    image: ee.Image,
    description: str,
    file_name_prefix: str,
    region: ee.Geometry,
    folder: str = "GEE_Lombardy_HeatRisk",
    scale_m: int = 100,
    crs: str = "EPSG:32632",
):
    """Create and return a Drive export task (call .start() on it)."""
    return ee.batch.Export.image.toDrive(
        image=image.float(),
        description=description,
        folder=folder,
        fileNamePrefix=file_name_prefix,
        region=region,
        scale=scale_m,
        crs=crs,
        maxPixels=1e13,
        fileFormat="GeoTIFF",
    )
