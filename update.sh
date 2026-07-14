#!/usr/bin/env bash
# 更新数据：抓取 → 自检 → 生成前端数据。改动留在工作区，由你 review 后自行提交。
#
# 用法：
#   ./update.sh          抓当年（1 月时连上一年一起抓，因为 12 月数据在次年 1 月发布）
#   ./update.sh 2025     抓指定年份
#
# 统计局一般每月 16 日前后发布上月数据。
set -euo pipefail
cd "$(dirname "$0")"

PY=.venv/bin/python
[ -x "$PY" ] || { echo "❌ 没有 .venv，先跑: python3 -m venv .venv && .venv/bin/pip install requests beautifulsoup4 lxml"; exit 1; }

if [ $# -gt 0 ]; then
  years=("$@")
elif [ "$(date +%-m)" -le 2 ]; then
  # 12 月数据标题写「上一年12月」，却在次年 1 月才发布，只抓当年会漏掉它
  years=("$(($(date +%Y) - 1))" "$(date +%Y)")
else
  years=("$(date +%Y)")
fi

for y in "${years[@]}"; do
  echo "▶ 抓取 $y 年..."
  "$PY" scrape_housing_data.py --year "$y"
done

echo "▶ parser 自检..."
"$PY" test_parse.py

echo "▶ 生成前端数据..."
"$PY" generate_js_data.py

echo
echo "▶ 改动："
git status --short
echo
echo "确认无误后提交推送，GitHub Actions 会自动部署："
echo "  git add -A && git commit -m 'data: 更新数据' && git push"
