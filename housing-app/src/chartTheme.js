// echarts 图表的共享视觉语言，与 index.css 的 token 保持一致。
// 编辑型风格：无网格噪音、发丝线、衬线标题、灰阶 UI + 语义色。

export const COLORS = {
  ink: "#1f1d1a",
  ink2: "#4a4640",
  ink3: "#8a8377",
  ink4: "#b3aca0",
  rule: "#e6e0d6",
  paper: "#faf8f4",
  up: "#b23b32",
  flat: "#c4bdb0",
  down: "#2f7a5c",
  series1: "#2c5f7c", // 新建商品住宅
  series2: "#c07a35", // 二手住宅
};

export const titleStyle = (text, size = 17) => ({
  text,
  left: 0,
  textStyle: {
    fontSize: size,
    fontWeight: 600,
    color: COLORS.ink,
    fontFamily: '"Songti SC", "Source Han Serif SC", Georgia, serif',
  },
});

export const axisCommon = {
  axisLine: { lineStyle: { color: COLORS.rule } },
  axisTick: { lineStyle: { color: COLORS.rule } },
  axisLabel: { color: COLORS.ink3, fontSize: 11 },
  splitLine: { lineStyle: { color: COLORS.rule, type: "dashed" } },
};

export const tooltipCommon = {
  backgroundColor: "#fffefb",
  borderColor: COLORS.rule,
  borderWidth: 1,
  textStyle: { color: COLORS.ink2, fontSize: 13 },
  extraCssText: "box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-radius: 2px;",
};
