# 70城房价趋势

抓取国家统计局《70个大中城市商品住宅销售价格变动情况》月度数据，用图表展示 2021 年 7 月至今的新建商品住宅与二手住宅价格环比走势。

**在线访问：https://xueyongwu.github.io/housing-price-trends/**

数据来源：[国家统计局](https://www.stats.gov.cn/sj/zxfb/)。环比指数以上月 = 100 为基准，>100 表示价格上涨。城市分级采用统计局口径：一线 4 城、二线 31 城（省会及计划单列市）、三线 35 城。

## 功能

- 全时段堆叠柱状图：每月 70 城拆分为上涨 / 持平 / 下跌，可切换新房与二手房
- 年度折线图：单年各月上涨城市数量，点击数据点定位到下方明细表
- 明细表：按城市分级列出各月环比指数，可切换「仅上涨城市」与「全部城市」
- KPI 卡片：最新月份上涨城市数、环比变化、最强 / 最弱城市

## 项目结构

数据是单向的三段管道，前端不请求接口，数据在构建时静态编译进 bundle：

```
统计局网页
   │  scrape_housing_data.py        抓取 + 解析
   ▼
data/70城房价.json                   汇总数据（按年月去重合并）
data/raw/YYYY-MM.html.gz             原始 HTML 存档，供离线重解析
   │  generate_js_data.py           转换为前端数据
   ▼
housing-app/src/data/housingData.generated.js
   │  vite build
   ▼
静态站点
```

| 文件 | 作用 |
| --- | --- |
| `scrape_housing_data.py` | 抓取与解析主脚本，含 CLI |
| `scrape_history.py` | 批量补抓 2021–2024 历史数据 |
| `generate_js_data.py` | JSON → 前端 JS 数据文件，含城市分级定义 |
| `test_parse.py` | parser 回归自检，跑存档 HTML，不联网 |
| `housing-app/` | React + Vite + ECharts 前端 |

## 环境准备

```bash
python3 -m venv .venv
.venv/bin/pip install requests beautifulsoup4 lxml

cd housing-app && pnpm install
```

## 使用

### 抓取数据

```bash
.venv/bin/python scrape_housing_data.py --year 2026   # 抓某年（默认 2026）
.venv/bin/python scrape_housing_data.py --all         # 抓全部年份
.venv/bin/python scrape_housing_data.py --url <URL>   # 抓指定文章页
.venv/bin/python scrape_housing_data.py --reparse     # 离线重解析存档，零网络请求
.venv/bin/python scrape_housing_data.py --force       # 重抓已有月份
.venv/bin/python scrape_history.py                    # 批量补抓历史数据
```

**抓取是增量的**：已抓过的月份直接跳过，不重复下载文章页（每篇约 1.4MB）。判断依据是「数据文件里有该月 + `data/raw/` 里有对应存档」，两个条件都满足才算已有 —— 存档丢了的月份会重抓，避免永久跳过再也补不回来。要强制重抓加 `--force`。

原始 HTML 会存档到 `data/raw/`，解析失败也照样存 —— 统计局改版或撤稿后，靠它离线复现问题、修完 parser 用 `--reparse` 重跑，不必重新联网抓。

### 生成前端数据并预览

```bash
.venv/bin/python test_parse.py      # 先跑 parser 自检
.venv/bin/python generate_js_data.py

cd housing-app
pnpm dev      # 开发服务器
pnpm build    # 构建到 dist/
pnpm lint
```

### 更新数据

**自动**：`.github/workflows/update-data.yml` 每月 15–25 日每天跑一次（统计局约每月 15 日起发布上月数据，偶有延迟）。抓到新数据才提交并触发重新部署，没有新数据就什么都不做。平时不用管。

**手动**：`./update.sh` 一把跑完抓取 → parser 自检 → 生成前端数据，改动留在工作区由你 review：

```bash
./update.sh          # 抓当年（1 月时连上一年一起抓）
./update.sh 2025     # 抓指定年份
```

确认无误后 `git add -A && git commit -m "data: 更新数据" && git push`，推送到 `main` 会自动构建部署（见 `.github/workflows/deploy.yml`）。

## 实现要点

**主指数表必须解析出 70 城，否则报错。** 统计局的主指数表是双栏并排（左 35 城 + 右 35 城），列数（6 列或 8 列）需从表格首行推断。推断错误会只读到左半栏，静默产出 35 城的残缺数据 —— 这曾真实发生过。因此解析后强制断言城市数为 70，不满足就 raise，宁可失败也不让脏数据落盘。`test_parse.py` 用全部存档 HTML 回归这条断言。

**生成数据与手写代码分离。** `housingData.generated.js` 由脚本覆盖写入，`housingData.js` 是手写的辅助函数并 re-export 前者。两者早前混在一个文件，重跑生成脚本会把手写函数全部冲掉。

**ECharts 按需引入。** `src/echarts.js` 只注册用到的图表和组件（柱状图、折线图、标题、提示框、图例、网格、dataZoom、markLine）。加新图表时若用到未注册的功能，ECharts 不报错而是静默不渲染，「配置写了但没效果」优先检查这里。

## 部署

GitHub Pages，推送 `main` 自动部署。`housing-app/vite.config.js` 中的 `base` 指向仓库子路径 `/housing-price-trends/`，若改用根域名托管需改回 `/`。
