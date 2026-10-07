---
name: wechat-publisher
description: 把 Markdown 或 Word 文档一键转成微信公众号「复制即用」的 HTML。支持多主题配色、callout 高亮框、自动目录、文章元数据、页脚版权、中文排版优化（盘古之白）。输入 .md/.docx/.html，输出公众号安全的内联样式 HTML。
---

# wechat-publisher（yml_C4B 版）

把 Markdown / Word 文档转成**微信公众号编辑器可直接粘贴**的 HTML。
输出只使用 inline CSS，自动过滤公众号禁止的标签，并做排版美化。

## 触发条件

- 用户说「把这篇 md / Word 转成公众号文章」「生成公众号排版」
- 用户要发布公众号文章，需要 copy-paste ready 的 HTML
- 用户提到公众号排版、WeChat 文章格式转换

## 输入 / 输出

| 方向 | 说明 |
|------|------|
| 输入 | Markdown（`.md`）、Word（`.docx`）、HTML（`.html`） |
| 输出 | 微信公众号安全的 HTML 文件（inline CSS，无 class/id，无 `<style>`） |
| 副产品 | 无（不写临时文件，不改动源文件） |

## 一条命令

```bash
python scripts/convert_to_wechat.py 输入.md 输出.html --theme green --toc \
  --title "文章标题" --author "虞梦琳" --date "2026-10-07" \
  --abstract "一句话摘要" --footer "© 2026 yml"
```

转换成功后，在浏览器打开输出 HTML → Ctrl+A/C 全选复制 → 粘贴到 mp.weixin.qq.com 编辑器 → 上传图片 → 预览 → 发布。

## 技能能力（6 项，starter kit 之上新增）

1. **多主题配色** `--theme {default|green|blue|dark}` — 4 套 inline CSS 配色，默认 default。
2. **Callout 高亮框** — blockquote 以 emoji 开头即转高亮框：
   - `> 📘 知识点` `> 💡 建议` `> ✅ 实践` `> ⚠️ 注意` `> ❌ 避坑`
3. **自动目录** `--toc` — 从 h2/h3 自动生成内嵌目录块。
4. **文章元数据** `--title/--author/--date/--abstract` — 生成头部元信息块。
5. **页脚版权** `--footer` — 末尾追加版权声明（默认文案兜底）。
6. **中文排版优化** `--cjk`（默认开，`--no-cjk` 关闭）— 中文与英文/数字间自动加半角空格（盘古之白）。

## 参考文件

- `references/wechat_styles.md` — 4 套主题的 inline CSS 取值，想微调配色看这里。
- `references/wechat_restrictions.md` — 公众号 HTML 限制规则（为什么 h1/div/style 不能用）。
- `examples/sample_article.md` + `examples/sample_output.html` — 输入/输出对照示例。

## 测试用例（eval）

运行 `python scripts/convert_to_wechat.py examples/sample_article.md /tmp/out.html --theme green --toc --title "测试" --author "yml"`，然后断言：

1. 输出 HTML 不含 `<style>`、`<script>`、`<iframe>`、`<h1>`、`<div>`、`class=`、`id=`。
2. `📘` 开头的 blockquote 被转成带背景色的 callout 块。
3. `--toc` 生成了「📑 目录」块。
4. 中文与英文/数字之间有半角空格（如「AI 时代」「第 3 章」）。
5. 页脚版权文案出现在文末。

## 修改指引

- 改配色：编辑 `scripts/convert_to_wechat.py` 里的 `THEMES` 字典，或改 `references/wechat_styles.md` 后同步。
- 加新 callout：编辑 `CALLOUTS` 字典（emoji → 标签/背景色/边框色/文字色）。
- 加新能力：在 `sanitize()` / `convert()` 之间插入独立函数，保持单一职责。
