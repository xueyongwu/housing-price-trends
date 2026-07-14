#!/usr/bin/env python3
"""
parser 自检。跑: .venv/bin/python test_parse.py

用 data/raw/ 下的存档 HTML 回归测试，不发网络请求。
"""

import glob
import os
import sys

from scrape_housing_data import extract_table_data, load_raw, EXPECT_CITIES, RAW_DIR


def test_all_archived_html_parses():
    """每份存档 HTML 都要解析出 70 城新建 + 70 城二手。"""
    files = sorted(glob.glob(os.path.join(RAW_DIR, "*.html.gz")))
    assert files, f"{RAW_DIR} 下没有存档 HTML，先跑一次抓取"

    for path in files:
        data = extract_table_data(load_raw(path))
        stem = os.path.basename(path)
        assert len(data["new_house"]) == EXPECT_CITIES, stem
        assert len(data["second_hand"]) == EXPECT_CITIES, stem
        assert data["new_house"]["北京"]["环比"] is not None, stem

    print(f"✅ {len(files)} 份存档 HTML 全部解析出 {EXPECT_CITIES} 城")


def test_half_parsed_table_raises():
    """
    主指数表是左35城+右35城双栏，列数靠推断。推断错会只吃到左半栏。
    这种残缺必须 raise，不能静默落盘 —— 历史上真发生过（2026-01 只存了 35 城）。
    """
    rows = "".join(
        f"<tr><td>城市{i}</td><td>100.1</td><td>99.5</td></tr>" for i in range(35)
    )
    table = f"<table><tr><th>表头</th></tr><tr><th>表头</th></tr>{rows}</table>"
    html = f"<html><body>{table}{table}</body></html>"

    try:
        extract_table_data(html)
    except ValueError as e:
        assert "35" in str(e), f"报错信息应说明实际城市数: {e}"
        print(f"✅ 残缺表格正确报错: {e}")
        return

    raise AssertionError("35 城的残缺表格没有报错 —— 断言失效了")


if __name__ == "__main__":
    test_half_parsed_table_raises()
    test_all_archived_html_parses()
    print("\n全部通过")
