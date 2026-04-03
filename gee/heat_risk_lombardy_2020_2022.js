/**
 * Lombardy heat exposure / risk mapping (2020-2022 summer)
 *
 * Hazard H: thermal anomaly dT ~ LST_p95 - LST_ref
 *   - LST_p95: per-pixel 95th percentile of clear-sky LST (deg C) from Landsat 8/9 C2 L2 (ST_B10)
 *   - LST_ref: mean LST over rural land cover (ESA WorldCover tree/shrub/grass/crop)
 *              within a 15-20 km annulus around the Lombardy geometry centroid (paper-style pins region)
 *
 * Aggregation: mean of annual dT for 2020, 2021, 2022 -> hazardMean
 * Normalization: min-max of hazardMean within Lombardy -> H_norm in [0,1]
 *
 * Exposure: WorldPop GP 100m (2020) population density (people/km2)
 * Risk: Risk = H_norm * PopDensity
 */

var REF_RING_INNER_M = 15000;
var REF_RING_OUTER_M = 20000;

var CRS_EXPORT = 'EPSG:32632';
var SCALE_EXPORT_M = 100;

var EXPORT_RISK = true;
var EXPORT_HAZARD = true;
var EXPORT_H_NORM = true;
var EXPORT_POP_DENSITY = true;

var DRIVE_FOLDER = 'GEE_Lombardy_HeatRisk';

var lombardyFC = ee.FeatureCollection('FAO/GAUL/2015/level1')
  .filter(ee.Filter.eq('ADM0_NAME', 'Italy'))
  .filter(
    ee.Filter.or(
      ee.Filter.eq('ADM1_NAME', 'Lombardia'),
      ee.Filter.eq('ADM1_NAME', 'Lombardy')
    )
  );

var aoi = lombardyFC.geometry();
Map.centerObject(aoi, 8);
Map.addLayer(aoi, {color: 'white'}, 'Lombardy AOI', false);

function maskLandsatL2sr(image) {
  var qa = image.select('QA_PIXEL');
  var mask = qa
    .bitwiseAnd(1 << 1).eq(0)
    .and(qa.bitwiseAnd(1 << 2).eq(0))
    .and(qa.bitwiseAnd(1 << 3).eq(0))
    .and(qa.bitwiseAnd(1 << 4).eq(0));
  return image.updateMask(mask);
}

function lstFromL2(image) {
  var lstK = image.select('ST_B10').multiply(0.00341802).add(149.0);
  var lstC = lstK.subtract(273.15).rename('LST');
  return lstC.copyProperties(image, ['system:time_start']);
}

function summerRange(year) {
  var y = ee.Number(year);
  var start = ee.Date.fromYMD(y, 6, 1);
  var end = ee.Date.fromYMD(y, 8, 31);
  return {start: start, end: end};
}

function landsatSummerLstP95(year, region) {
  var sr = summerRange(year);
  var l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    .filterBounds(region)
    .filterDate(sr.start, sr.end);
  var l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
    .filterBounds(region)
    .filterDate(sr.start, sr.end);
  var col = l8.merge(l9).map(maskLandsatL2sr).map(lstFromL2);
  var p95 = col.select('LST').reduce(ee.Reducer.percentile([95])).rename('LST');
  return p95.clip(region);
}

function ruralMaskFromWorldCover(region) {
  var wc = ee.ImageCollection('ESA/WorldCover/v200/2021').first().select('Map');
  var m = wc
    .eq(10)
    .or(wc.eq(20))
    .or(wc.eq(30))
    .or(wc.eq(40))
    .rename('rural');
  return m.clip(region);
}

function referenceRingGeometry(regionGeom) {
  var c = regionGeom.centroid(ee.ErrorMargin(1));
  var outer = c.buffer(REF_RING_OUTER_M);
  var inner = c.buffer(REF_RING_INNER_M);
  return outer.difference(inner);
}

function deltaTForYear(year, regionGeom) {
  var lstP95 = landsatSummerLstP95(year, regionGeom);
  var ring = referenceRingGeometry(regionGeom);
  var rural = ruralMaskFromWorldCover(regionGeom);

  var lstProj = lstP95.projection();
  var ruralReproj = rural.reproject({crs: lstProj, scale: 30}).eq(1);

  var maskedRing = lstP95.updateMask(ruralReproj).clip(ring);

  var refDict = maskedRing.reduceRegion({
    reducer: ee.Reducer.mean(),
    geometry: ring,
    scale: 30,
    maxPixels: 1e13,
    tileScale: 2,
  });
  var cntDict = maskedRing.reduceRegion({
    reducer: ee.Reducer.count(),
    geometry: ring,
    scale: 30,
    maxPixels: 1e13,
    tileScale: 2,
  });

  var lstRefRing = ee.Number(refDict.get('LST'));
  var nPix = ee.Number(cntDict.get('LST'));

  var fallbackDict = lstP95.updateMask(ruralReproj).reduceRegion({
    reducer: ee.Reducer.mean(),
    geometry: regionGeom,
    scale: 100,
    maxPixels: 1e13,
    tileScale: 2,
  });
  var lstRefFallback = ee.Number(fallbackDict.get('LST'));

  var lstRef = ee.Number(ee.Algorithms.If(nPix.gt(0), lstRefRing, lstRefFallback));

  return lstP95.subtract(lstRef).rename('deltaT').clip(regionGeom);
}

var d2020 = deltaTForYear(2020, aoi);
var d2021 = deltaTForYear(2021, aoi);
var d2022 = deltaTForYear(2022, aoi);

var hazardMean = d2020.add(d2021).add(d2022).divide(3).rename('deltaT');

var hazardStats = hazardMean.reduceRegion({
  reducer: ee.Reducer.minMax(),
  geometry: aoi,
  scale: 100,
  maxPixels: 1e13,
  tileScale: 2,
});

var hMin = ee.Number(hazardStats.get('deltaT_min'));
var hMax = ee.Number(hazardStats.get('deltaT_max'));

var hazardNorm = hazardMean
  .subtract(hMin)
  .divide(hMax.subtract(hMin).max(1e-6))
  .rename('H_norm')
  .clip(aoi);

var popImg = ee
  .ImageCollection('WorldPop/GP/100m/pop')
  .filterDate('2020-01-01', '2021-01-01')
  .mosaic()
  .clip(aoi);

var popBand = popImg.bandNames().get(0);
var pop = popImg.select([popBand]).rename('population');

var pixelAreaKm2 = ee.Image.pixelArea().divide(1e6);
var popDensity = pop.divide(pixelAreaKm2).rename('pop_density');

var risk = hazardNorm.multiply(popDensity).rename('risk');

Map.addLayer(d2020, {min: -5, max: 15, palette: ['313695', '4575b4', '74add1', 'fdae61', 'd73027']}, 'dT 2020', false);
Map.addLayer(hazardMean, {min: -5, max: 15, palette: ['313695', '4575b4', '74add1', 'fdae61', 'd73027']}, 'dT mean 2020-22', true);
Map.addLayer(hazardNorm, {min: 0, max: 1, palette: ['ffffcc', 'feb24c', 'fd8d3c', 'f03b20', 'bd0026']}, 'H_norm', false);
Map.addLayer(popDensity, {min: 0, max: 8000, palette: ['ffffd4', 'fed98e', 'fe9929', 'd95f0e', '993404']}, 'Pop density (/km2)', false);
Map.addLayer(risk, {min: 0, max: 5000, palette: ['ffffcc', 'feb24c', 'fd8d3c', 'f03b20', 'bd0026']}, 'Risk (H_norm x density)', false);

function exportImg(img, description, fileNamePrefix) {
  Export.image.toDrive({
    image: img.toFloat(),
    description: description,
    folder: DRIVE_FOLDER,
    fileNamePrefix: fileNamePrefix,
    region: aoi,
    scale: SCALE_EXPORT_M,
    crs: CRS_EXPORT,
    maxPixels: 1e13,
    fileFormat: 'GeoTIFF',
  });
}

if (EXPORT_HAZARD) {
  exportImg(hazardMean, 'Lombardy_deltaT_mean_2020_2022', 'lombardy_deltaT_mean_2020_2022');
}
if (EXPORT_H_NORM) {
  exportImg(hazardNorm, 'Lombardy_H_norm_2020_2022', 'lombardy_H_norm_2020_2022');
}
if (EXPORT_POP_DENSITY) {
  exportImg(popDensity, 'Lombardy_pop_density_2020_WorldPop', 'lombardy_pop_density_2020');
}
if (EXPORT_RISK) {
  exportImg(risk, 'Lombardy_heat_risk_2020_2022', 'lombardy_heat_risk_2020_2022');
}