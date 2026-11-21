# 哈绩咪 Hiscore

校园成绩工作台：单文件 HTML，纯前端运行，数据留在本机浏览器。打开网页即可导入成绩、看班级 PK、生成学生分析与家长报告。

当前版本：**v3.0**（2026-11-21）

## 在线使用

部署到 GitHub Pages 后，访问：

```text
https://<你的 GitHub 用户名>.github.io/<仓库名>/
```

建议把上面这一行替换成你的真实地址，方便自己以后点开。

## 功能

- **成绩导入**：直接选 Excel / WPS 文件，或粘贴整张成绩表；先预览再写入，支持完整 JSON / Excel 备份恢复
- **总览与班级 PK**：均分、G1/G2 线、进退步、重点关注、各科对比
- **学生画像**：趋势、雷达图、单科明细、班内与年级排名
- **家长报告**：每生一页 A4，可勾选 AI 分析写入报告，支持批量打印
- **小懂弟 & 大学姐**：接入 OpenAI 兼容接口的对话助手，首次发送前展示完整外发请求体，本次会话确认一次即可
- **本机优先**：localStorage + IndexedDB，不上传成绩；API Key 只存本机，不写入导出备份
- **手机可用**：响应式布局，手机浏览器也能查看与导出

## 部署到 GitHub Pages

### 1. 新建仓库

在 GitHub 新建一个 **Public** 仓库（例如 `hiscore`）。Private 仓库不能免费使用 GitHub Pages。

### 2. 上传文件

把本项目文件夹上传到仓库。**线上页面只需要 `docs/` 目录**：

```text
docs/
  index.html   ← 网页本体
  .nojekyll    ← 告诉 GitHub Pages 不要用 Jekyll 处理
```

其余目录（`newest-version/`、`迭代版本/`、`README.md` 等）可以一起上传，方便保留版本记录。

### 3. 打开 Pages

进入仓库的 **Settings → Pages**：

- **Source** 选 `Deploy from a branch`
- **Branch** 选 `main`，文件夹选 **`/docs`**
- 点 **Save**

等 1–2 分钟，页面顶部会出现访问地址：

```text
https://<用户名>.github.io/<仓库名>/
```

### 4. 更新线上版本

以后改了网页，只需把新的 HTML 覆盖到 `docs/index.html` 再推送。也可以在项目根目录运行：

```bash
bash scripts/sync-pages.sh
```

脚本会自动把 `newest-version/` 里版本号最新的 HTML 同步到 `docs/index.html`。

## 本地打开

不用装环境：直接双击 `docs/index.html`，或拖进浏览器即可。所有功能都在本机运行。

## 数据与隐私

- 成绩、学生档案、布局和会话默认只存在当前浏览器；换电脑或清理浏览器数据前，请先在「数据」页导出备份。
- API Key 只保存在本机浏览器，**不会**进入 JSON / Excel 备份；公共电脑不要勾选「记住 Key」。
- 对话外发前会展示实际请求体；学号永不外发，姓名、班级和背景备注按你的勾选加入。
- 本项目没有后端服务器，GitHub Pages 只负责提供静态网页。

## 项目结构

```text
docs/index.html          GitHub Pages 线上页面（发布副本）
newest-version/          最新稳定版源文件
迭代版本/                历史版本与迭代记录
scripts/sync-pages.sh    把最新稳定版同步到 docs/
CLAUDE.md                开发约定与数据安全约束
```

## 说明

- 当前为单文件应用，无构建步骤、无第三方运行时依赖；浏览器需联网才能调用 AI 接口，其余功能离线可用。
- 仓库暂未选择开源许可证；如需公开复用，请先补充 LICENSE。
