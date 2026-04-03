# polimi_THESIS_2026

### English

Master thesis repository: **Lombardy heat environment and heat exposure / risk mapping** using remote sensing (Google Earth Engine) and population data.

### 中文

硕士论文代码仓库：**伦巴第大区**热环境与**热暴露/热风险**制图（遥感 + 人口栅格）。

---

## Repository contents / 仓库内容

| Path | Description |
|------|-------------|
| [`notebooks/lombardy_heat_risk_2020_2022.ipynb`](notebooks/lombardy_heat_risk_2020_2022.ipynb) | **EN:** Jupyter + **geemap** (recommended): same workflow as JS; export via `ee.batch.Export` to Drive. **中文：** Jupyter + geemap（推荐）：与 JS 流程一致，导出至 Google Drive。 |
| [`src/lombardy_heat_risk_gee.py`](src/lombardy_heat_risk_gee.py) | **EN:** Python EE helpers (`build_stack`, `export_image_to_drive`). **中文：** Earth Engine Python 封装（构建图层、导出任务）。 |
| [`gee/heat_risk_lombardy_2020_2022.js`](gee/heat_risk_lombardy_2020_2022.js) | **EN:** Earth Engine **JavaScript** for Code Editor (legacy but equivalent). **中文：** 适用于 Code Editor 的 **JavaScript** 脚本（与 Python 逻辑等价）。 |
| [`gee/heat_risk_lombardy_2020_2022.md`](gee/heat_risk_lombardy_2020_2022.md) | **EN:** JS script embedded in Markdown. **中文：** 同上 JS，便于复制。 |
| [`docs/methodology.md`](docs/methodology.md) | **EN:** Methods, equations, data sources. **中文：** 方法、公式与数据源说明。 |
| [`src/plot_risk.py`](src/plot_risk.py) | **EN:** Optional local plotting of exported GeoTIFFs. **中文：** 本地读取 GeoTIFF 出图（可选）。 |
| [`requirements.txt`](requirements.txt) | **EN:** Python dependencies. **中文：** Python 依赖列表。 |

---

## Run: Python + Jupyter / 运行：Python + Jupyter

### English

1. Install dependencies and authenticate once:
   ```bash
   pip install -r requirements.txt
   earthengine authenticate
   ```
2. From the **repository root**, start Jupyter:
   ```bash
   jupyter notebook notebooks/lombardy_heat_risk_2020_2022.ipynb
   ```
3. Run all cells: the map renders in the notebook; the last cell **starts** export tasks to Google Drive (default folder `GEE_Lombardy_HeatRisk`). Track jobs on [Earth Engine Tasks](https://code.earthengine.google.com/tasks).

If your EE account uses a **Google Cloud project**, replace `ee.Initialize()` with `ee.Initialize(project='your-project-id')`.

### 中文

1. 安装依赖并**一次性**完成 Earth Engine 认证：
   ```bash
   pip install -r requirements.txt
   earthengine authenticate
   ```
2. 在**仓库根目录**启动 Jupyter：
   ```bash
   jupyter notebook notebooks/lombardy_heat_risk_2020_2022.ipynb
   ```
3. 依次运行单元格：地图在笔记本中显示；最后一个单元格会**启动**导出到 Google Drive 的任务（默认文件夹 `GEE_Lombardy_HeatRisk`）。任务进度见 [Earth Engine 任务页](https://code.earthengine.google.com/tasks)。

若账号需绑定 **Google Cloud 项目**，请将 `ee.Initialize()` 改为 `ee.Initialize(project='你的项目ID')`。

---

## Run: JavaScript Code Editor / 运行：JavaScript 代码编辑器

### English

1. Open [Earth Engine Code Editor](https://code.earthengine.google.com/).
2. Paste [`gee/heat_risk_lombardy_2020_2022.js`](gee/heat_risk_lombardy_2020_2022.js).
3. Click **Run**, then **Tasks** → **Run** each export to Drive (folder `GEE_Lombardy_HeatRisk` by default).

### 中文

1. 打开 [Earth Engine 代码编辑器](https://code.earthengine.google.com/)。
2. 粘贴 [`gee/heat_risk_lombardy_2020_2022.js`](gee/heat_risk_lombardy_2020_2022.js)。
3. 点击 **Run**，在 **Tasks** 中逐个 **Run** 导出到网盘（默认文件夹 `GEE_Lombardy_HeatRisk`）。

**Exports / 输出栅格** (100 m, EPSG:32632):

| File prefix | English | 中文 |
|-------------|---------|------|
| `lombardy_deltaT_mean_2020_2022` | Mean annual \(\Delta T\) (°C) | 三年平均热异常 \(\Delta T\)（°C） |
| `lombardy_H_norm_2020_2022` | Min–max normalized hazard in Lombardy | 伦巴第区内 min–max 归一化热危害 \(H_{\mathrm{norm}}\) |
| `lombardy_pop_density_2020` | Population density (people/km²) | 人口密度（人/km²） |
| `lombardy_heat_risk_2020_2022` | Risk raster \(H_{\mathrm{norm}} \times\) density | 风险栅格（归一化危害 × 人口密度） |

---

## Optional: plot GeoTIFF locally / 可选：本地绘制 GeoTIFF

```bash
pip install -r requirements.txt
python src/plot_risk.py --risk path/to/lombardy_heat_risk_2020_2022.tif --out outputs/risk_map.png
```

---

## Literature alignment / 文献对应说明

### English

Thermal anomaly \(\Delta T\) follows the **non-urban reference / pins** idea (Gianquintieri et al., Padua case). This repository uses a **simplified risk** map: **no elderly vulnerability layer**, only **population density exposure**.

### 中文

热异常 \(\Delta T\) 参照文献中**非城市参考区 / pins** 思路（Gianquintieri 等，帕多瓦案例）。本仓库采用**简化风险**制图：**不含老年脆弱性图层**，仅使用**人口密度暴露**。

---

## License / 许可证

See [LICENSE](LICENSE). **中文：** 见 [LICENSE](LICENSE)。
