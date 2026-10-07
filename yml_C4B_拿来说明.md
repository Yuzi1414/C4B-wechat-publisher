# 拿来说明：wechat-publisher 技能

> 挑战 C4B · 交付物之一
> 作者：虞梦琳（yml）
> 命名：`yml_C4B_拿来说明.md`

本挑战要求「拿来说明」：哪些是拿来的、哪些自己改了、哪些是新增的，逐项交代清楚，避免把参考来源当成原创。

## 一、拿了什么（来源与去向）

| 来源 | 拿了什么 | 用在哪里 | 状态 |
|------|----------|----------|------|
| starter kit `c4b-wechat-publisher-starter.zip` | 技能整体骨架：SKILL.md、`convert_to_wechat.py`、`references/wechat_styles.md`、`references/wechat_restrictions.md`、示例文章 | 全部作为基座保留 | 参考 |
| `wechat_restrictions.md` | 公众号编辑器安全规范（禁 `<style>`/`<h1>`/`<div>`/`class`/`id`，只留 inline CSS 和少量标签） | 原样保留，作为转换脚本的过滤白名单依据 | 拿了（原样） |
| `convert_to_wechat.py` | Markdown→HTML 核心转换流程、标签过滤逻辑、图片/引用/表格样式 | 在其上扩展，未推翻重写 | 拿了（改） |
| 中文排版「盘古之白」习惯 | 中英文之间加空格这一排版约定 | 实现为 `--no-cjk` 开关 | 参考 |

## 二、改了什么（对基座的改造）

1. **新增 4 套主题**：starter 配色写死，我改成 `--theme {default,green,blue,dark}` 四套可切换配色，绿色主题为默认示例。
2. **新增 callout 高亮框**：`> 📘 知识点`、`> 💡 建议`、`> ✅ 实践`、`> ⚠️ 注意`、`> ❌ 避坑` 五种彩色提示框，各自独立配色。
3. **新增目录**：`--toc` 自动抓取二级标题生成文章目录。
4. **新增元数据头**：`--title / --author / --date / --abstract` 生成文章头部的标题、作者、日期、摘要。
5. **新增页脚**：`--footer` 生成页脚版权行。
6. **新增 CJK 空格**：中英文/数字之间自动加空格，`--no-cjk` 可关闭。

## 三、新增了什么（基座没有的）

- `examples/sample_article.md`：重写为真实示范文章《用 AI 高效学习：我从踩坑到上手的 5 条心得》，覆盖全部 5 种 callout、表格、代码块、行内代码。
- `examples/sample_output.html`：示范文章转换后的成品 HTML。
- `yml_C4B_output.html`：交付用文章源文件的成品 HTML。
- 教学说明、AI 日志、本拿来说明等课程要求的说明文档。

## 四、为什么这样拿/改

- **拿骨架、不重造**：starter 的 Markdown→HTML 和标签过滤是正确的、可复用的，重写只会引入新 bug。
- **改在扩展点、不动核心**：所有新增能力都通过独立配置字典（`THEMES`、`CALLOUTS`）和独立函数实现，没有侵入核心转换流程，降低回归风险。
- **改了说清楚**：中途真实 bug（callout 标签重复）已记录在 AI 日志和 AAR，未隐瞒。

## 五、声明

除上述「拿了/参考」部分外，技能的能力扩展、示例文章、各说明文档均为本人（虞梦琳）在 AI 协助下独立完成。所有第三方来源均已在上表列出。
