# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

抓取国家统计局「70个大中城市商品住宅销售价格变动情况」月度数据，生成前端数据文件，用 React + ECharts 展示环比走势。

数据流是单向的三段管道，改任何一段都要考虑下游：

```
统计局网页 --scrape_housing_data.py--> data/70城房价.json + data/raw/YYYY-MM.html.gz
         --generate_js_data.py--> housing-app/src/data/housingData.generated.js
         --HomePage.jsx--> 图表
```

## Commands

```bash
# Python 侧（用仓库自带 venv）
.venv/bin/python scrape_housing_data.py --year 2026   # 抓某年（默认 2026）
.venv/bin/python scrape_housing_data.py --all         # 抓全部年份
.venv/bin/python scrape_housing_data.py --reparse     # 离线重解析 data/raw/，零网络请求
.venv/bin/python scrape_history.py                    # 批量补 2021-2024 历史数据
.venv/bin/python test_parse.py                        # parser 回归自检（唯一的测试）
.venv/bin/python generate_js_data.py                  # JSON → 前端 JS 数据

# 前端
cd housing-app && pnpm dev      # 开发服务器
cd housing-app && pnpm build    # 构建
cd housing-app && pnpm lint     # eslint
```

改完 parser 的标准闭环：`--reparse` → `test_parse.py` → `generate_js_data.py`。不用重新联网抓。

## 约束（踩过坑，别再踩）

**主指数表必须解析出 70 城，少了就 raise。** 表格是双栏并排（左 35 城 + 右 35 城），列数靠 `parse_main_index_table` 从首行推断（6 列 / 8 列）。推断错会只吃到左半栏，静默落盘 35 城残缺数据 —— 2026-01 真发生过。`EXPECT_CITIES` 断言就是防这个，不要为了「让它先跑通」把断言放宽。

**原始 HTML 必须存档，解析失败也要存。** `data/raw/YYYY-MM.html.gz`（gzip，1.4MB → ~140KB，才进得了 git）。统计局改版或撤稿后，靠它离线复现 + `--reparse`，不用重抓。

**`housingData.generated.js`（生成）和 `housingData.js`（手写辅助函数）必须分开。** 早前混在一个文件里，重跑 generator 把手写函数全冲掉了。generated 文件只导出数据，js 文件 re-export 数据 + 加函数。

**数据文件只有一份 `data/70城房价.json`，按 (年, 月) 去重合并写入**（`merge_save`），不带时间戳。多份带时间戳的文件会让下游按 glob 顺序随机选中版本。

**城市分级只有三档：一线 4 / 二线 31 / 三线 35**（`generate_js_data.py` 的 `CITY_TIERS`，国家统计局口径）。不要自造四线/五线，那对不上公报也无法对外解释。

## 数据形状

`data/70城房价.json`：list of entry，每 entry 一个月：
```
{year, month, pub_date, url, title,
 new_house: {城市: {环比, 同比, 平均}},      # 指数，上月=100
 second_hand: {...},
 new_house_by_area: {城市: {"90m²及以下": {...}, "90-144m²": {...}, "144m²以上": {...}}},
 second_hand_by_area: {...}}
```

前端只用「环比」。`dataByYear[year] = { months, newHouse: {城市: [每月环比]}, secondHand: {...} }`。

## 前端

单页应用，只有 `pages/HomePage.jsx` 一个页面，直接用 echarts 命令式 API（`useRef` + `useEffect`）。图表视觉统一走 `chartTheme.js` 的 `COLORS` / `titleStyle` / `axisCommon` / `tooltipCommon`，和 `index.css` 的 token 对齐 —— 加新图表复用这些，别各写各的颜色。

**echarts 按需引入**：从 `src/echarts.js` 导入，不要 `import * as echarts from "echarts"`（那是全量，bundle 会大 500KB+）。用到新的图表类型或组件时，必须先在 `src/echarts.js` 的 `echarts.use([...])` 里注册 —— 漏注册时 echarts **不报错**，而是静默不渲染那部分。「option 写了但没效果」先查这里。
