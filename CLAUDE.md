# 哈绩咪 Hiscore 项目规则

## 当前版本与基底

- 最新稳定版：`newest-version/Hiscore_v3.0.html`，SHA-256 `41f0d270681d701f6c76ba0b73aa2ad5f2451ccbaf5dc1f955a7f0dbd9925b9a`。
- 当前最新成品：`newest-version/Hiscore_v3.5.html`（2026-11-27）。
- GitHub Pages 发布副本：`docs/index.html`（与最新稳定版一致，更新时运行 `scripts/sync-pages.sh`）。
- v3.1–v3.4 已归档：`迭代版本/S3/v3.1/` 至 `迭代版本/S3/v3.4/`；v3.0 已归档：`迭代版本/S3/v3.0/Hiscore_v3.0.html`。
- v3.0 迭代源文件：`迭代版本/S3/v3.0.beta/Hiscore_v3.0.beta.html`（与稳定版内容一致）。
- v2.5 已归档：`迭代版本/S2/v2.5/Hiscore_v2.5.html`，SHA-256 `524d88d5c27da3b28673a8863c498a3a0549a9d4e7e1fd9a5174f8d918dfb551`；不再覆盖，也不再作为最新版。
- v3.0.alpha 方案与实施文件：`迭代版本/S3/v3.0.alpha/Hiscore_v3.0.alpha.html`；完整方案见 `规划/Hiscore_v3.0.alpha-方案-第1版.md`。

## 旧学生 AI 保留约束（Aki 明确要求，2026-11-17）

- **新「小懂弟&大学姐」运行时完整接管前，必须保留学生页现有「AI 分析」能力**：`PANEL_DEFS.ai`、`buildAiPanel()`、`studentBriefMd()`、`buildAnalysisPrompt()`，以及 `profiles[key].aiReport / aiInParent` 的读取兼容。
- 小懂弟页在 alpha 只提供跳转到现有学生 AI 的入口；不得因新页面仍为空框架而删除、禁用或留空旧入口。
- 新运行时只有在生成、取消、保存、家长报告发布、旧数据/备份恢复和浏览器回归全部通过，并经 Aki 明确确认后，才能收编或移除旧入口。
- 修改旧 AI 的安全门时，只能增强外发预览、草稿复核和发布确认，不能借安全修补删掉原有可用能力。
- 旧 AI 面板旁也留有同义代码注释；清理旧代码前必须先查该注释和本文件。

## 数据与安全

- 不改 `LS_KEY`、`LS_WORKSPACE`、`LS_AI`、SNAP 数据库名；布局迁移必须幂等，不能重置用户自定义布局。
- 共享 API Key 不写入 HTML、浏览器存储、日志、方案文档或备份；真实共享只允许受控中转。
- alpha 不实现真实双智能体生成、智能路由、长期记忆或新 AI 偏好持久化；不做假聊天、假进度、假路由成功。
- 大学姐成绩导入是完整本地工具；完整 JSON/Excel 恢复仍留数据页。
- 不改统计公式、学生身份、历史 `cls`、赋分和年排口径；完整单班详情与 classId 迁移另立任务。
- 2026-11-17 Aki 已允许 UI 与整体视觉升级和功能同步推进；保留「校园像素 + 哈绩咪」辨识度，重点优化信息层次、数据可读性、深浅色、响应式与动效，不改成通用企业后台，也不借视觉改动改变功能或统计口径。

## 验收

- 每个阶段提取内联脚本跑 `node --check`，并做浏览器 console 与交互回归；静态检查不能代替实测。
- 重点覆盖旧 localStorage/布局、慢 XLSX 竞态、写盘与 IndexedDB 失败、导入双实例、只读绕过、JSON/Excel 往返、手机导出和离线。
- 预览使用 `.claude/launch.json` 的 `campus-pixel-preview`（8902）；最新版路径为 `/newest-version/Hiscore_v3.0.html`，迭代版路径为 `/迭代版本/S3/v3.0.beta/Hiscore_v3.0.beta.html`，刷新加 `?v=时间戳`。
