# Hiscore v3.5 变更说明：全面显示审查 + 打印排版重做（审阅修订版 v2）

- 交付：`Hiscore_v3.5.html`（内嵌单文件）、`hiscore_v3.5_site/`+zip（外置版）、`Hiscore_v3.5_case_en.html`（英文案例页）、`Hiscore_v3.5_打印样张_家长版.html` / `Hiscore_v3.5_打印样张_合订.html`（真实生成函数产出的静态打印样张）、`v35_print.css`
- 派生：`Hiscore_v3.4.html` → `build_v35.py` 10 处补丁 → v3.5；uploads/ 原件与 v3.2–v3.4 成品均未修改
- 日期：2026-11-25 · v2 依独立审阅补证：大学面板文本断言、三版同轮计数对比、全页签明暗复核、英文页空白根因修复、打印稿暗色表字修复

## 1. 审查发现的显示缺陷（本轮修复）

| # | 缺陷 | 影响 | 修复 |
|---|---|---|---|
| B1 | **字母 helper 作用域错误（v3.4 真实 bug）**：`LETTER_SCALES/letterScaleOf/letterInfo` 定义在 uni-core 的 IIFE 内，uni-ui / uni-entry 以自由变量引用 → 一旦存在字母课记录，大学面板渲染抛 ReferenceError，整块面板消失 | 大学·实验性面板在有字母成绩时不显示 | F01：提升到共享脚本作用域并挂到 `window.HS_UNI` 导出 |
| B2 | **学生简报 markdown 表格退化为裸管道文本**：`mdToHtml` 逐行解析不支持表格 | 打印合订可读性差 | F02：表格块解析（表头/对齐行跳过/单元格转义）输出真实 `.tb` |
| B3 | 打印样式灰底灰线、无 A4 边距/防跨页 | 打印观感 | F04：`v35_print.css` 统一打印层（§2） |
| B4 | 家长版雷达 60%/85% 参考文字压中轴 | 小字相碰 | F03：参考文字左锚离轴 |
| B5 | 合订 390px 预览宽表撑破页面（818px > 390px） | 移动端横向溢出 | F06：小屏宽表 `display:block; overflow-x:auto` |
| B6 | 学生 PDF 雷达环标小尺寸相碰 | 小字相碰 | F05：打印雷达 `ringLabels:false` |
| B7 | **打印稿在深色系统主题下表格文字变浅到不可读**（暗色令牌覆盖纸面墨字；合订班级/科目/首列数值几乎看不见） | 暗色环境打印预览不可读 | v2：打印层强制 `#print-root` 及其后代墨色 `#1F362D !important`， muted/水印色单独重申；复查暗色四视图全部可读 |
| B8 | **英文案例页 v3.5 首屏全空白**：`build_case_en.py` 抽取字母块时以「课程得分」注释为终点，v3.5 字母块前移后把未闭合 IIFE 一并注入 → 整页脚本语法错误 | 交付件不可读 | v2：抽取终点改为 `(function () {`；重建后明暗×桌面/移动四视图均有完整内容 |

其余页签本轮逐张明暗+桌面/移动复核（见 §3 覆盖清单），未发现新增缺陷。

## 2. 打印排版设计（v35_print.css）

- `@page { size: A4; margin: 16mm 15mm 18mm; }`；屏幕预览即打印样貌（#print-root 居中 186mm 纸面）。
- 标题 Georgia/宋体衬线 + 森林绿 `#265745` 左色条；正文系统 sans 12px/1.65；KPI/数字等宽。
- 表格外框 `#CFC7B4`、表头暖米 `#F1EBDC`、隔行 `#FAF7EF`、行内防断裂；简报表 10.5px。
- KPI 卡 1.5px 墨线 + 3px 硬影 + 纸底 `#FBF5E9`，四列（小屏两列）。
- 防跨页：tr/表格/KPI/雷达/分栏 `break-inside:avoid`；h2/h3/h4 `break-after:avoid`；合订每节独立页。
- 演示水印琥珀虚线条；封面左对齐衬线大标题 + 森林绿粗底线。
- **纸面墨色强制**（B7）：任何系统主题下打印稿均为白底墨字。
- 小屏宽表横向滚动容器。

## 3. 验证记录（全部本轮实测，附脚本与输出）

**A. 大学面板渲染级核验（`diagnose_full.js`，jsdom 真 DOM；输出 `verify_uni_render_output.txt`）**
- `UNI_GPA_CARD: 3.33`；`UNI_COURSE_ROWS` 含「A- · GPA 3.67」与「88 / 100」；`UNI_MODE_OPTIONS` 三项含「字母等级（A/A-/B+…）」。
- 断言 4/4 PASS：gpa=3.33；字母行 A-+3.67；百分比行 88/100；三计分选项含字母。
- GPA 3.33 = (3.67×3 + 3.0×3)/6，与引擎口径一致。
- 序列化 DOM 静态样张 `_preview/v35_uni_static.html` 明暗×桌面/移动四视图目视正常。

**B. 判定计数同轮三版对比（`verify_counts_compare.js` → `verify_counts_compare_output.txt`）**
- 同一脚本同轮运行 Hiscore_v3.3 / v3.4 / v3.5，逐字段 diff：`DIFF v3.3 vs v3.4: IDENTICAL`、`DIFF v3.3 vs v3.5: IDENTICAL`、`COUNTS_NO_REGRESSION`（32/35/27，连降 0，并集 53）。

**C. 字母引擎**：`verify_letter.js` 15/15 PASS（`verify_letter_output.txt`）。

**D. 渲染覆盖清单（本轮 inspect_artifact，明/暗 × 1440/390）**
- Hiscore_v3.5.html 总览、学生、擂台、智能体、录入、设置·计分规则：各 4 视图。
- 大学面板静态样张：4 视图。
- 打印样张·家长版：4 视图；打印样张·合订：4 视图（v2 修复 B7 后复查）。
- 英文案例页：4 视图（v2 修复 B8 后复查）。
- 自动版式检查：除「打印样张无 H1」（打印稿以 ph-title/封面 h1 承载，属提示非缺陷）外无溢出/裁切报告。

**E. 语法与构建**：`build_v35.py` 10 处锚点断言全命中；v3.5 五脚本块 `node --check` 全过；外置版 index **1,013,766 B（0.97MB）** + assets 649,393 B。

## 4. 残留与下一步

1. 0.95MB 拉伸目标未达成（0.97MB）；两校单文件上限（2MB/4MB）满足。
2. 托管发布（用户决定后执行）。
3. 真实数据小样本试点后再谈验证。
4. 大学面板在设置页位于预设面板之下需下滚（应用原有布局，非缺陷）。

## 5. 复跑命令

```
python build_v35.py && python wrap_samples.py     # v3.5 + 静态打印样张
python externalize_v34.py                        # 外置版（源 v3.5）
python build_case_en.py && python make_en_run.py # 英文案例页 + DOM 桩
python gen_print_samples.py                      # 真实打印内容
node verify_letter.js                            # 字母引擎 15 项
node verify_counts_compare.js Hiscore_v3.3.html Hiscore_v3.4.html Hiscore_v3.5.html
npm i jsdom && node diagnose_full.js             # 真 DOM 大学面板断言 + 静态样张
```
