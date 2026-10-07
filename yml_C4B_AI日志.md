# AI 日志：wechat-publisher 技能定制

> 挑战 C4B · 必交交付物（无此项无法评审）
> 作者：虞梦琳（yml）
> 命名：`yml_C4B_AI日志.md`

## 使用方式概览

多轮迭代 + 中途真实 bug 修复。不是「一句话要成品」，而是「读基座 → 明确改造点 → 分步改 → 跑通 → 发现 bug → 定位 → 修复 → 复验」的完整过程。

## 第 1 轮：读基座，确认改造边界

**给 AI 的指令**：解压 starter kit，读 `SKILL.md`、`convert_to_wechat.py`、`wechat_styles.md`、`wechat_restrictions.md`、`sample_article.md`，告诉我这个 starter 已经有什么、还缺什么。

**AI 做了什么**：读完全部基座文件，识别出 starter 已有的能力（Markdown→HTML、inline CSS、标签过滤、引用/表格/代码块样式），并指出可扩展点：主题配色写死在单一 `THEMES` 里、无 callout、无目录、无元数据、无页脚、中文排版未处理。

**我的决策**：定下 6 项新增能力——多主题、callout、目录、元数据、页脚、CJK 空格，覆盖「个性化」和「排版质量」两个评审方向。

## 第 2 轮：分步写转换脚本

**给 AI 的指令**：在 starter 的 `convert_to_wechat.py` 上扩展这 6 项能力，保持单一职责，每项一个独立函数或配置字典；先写骨架，再补实现。

**AI 做了什么**：分两步写完脚本——先 `write_file` 写主骨架（含 `THEMES` / `CALLOUTS` 配置字典和核心转换流程），再用 `edit_file` 替换 `# __PART2_MARKER__` 补上后半段（目录、元数据、页脚、CJK 处理函数）。写完后 `python convert_to_wechat.py --help` 验证 6 项参数全部就位。

**我的决策**：分两步写而不是一口气写完，是为了控制单次输出长度，也便于核对每一步的 diff。

## 第 3 轮：跑真实转换，发现 bug

**给 AI 的指令**：用示例文章跑一次完整转换，验证输出符合公众号安全规范。

**AI 做了什么**：跑通转换，依赖自动安装（markdown / beautifulsoup4 / python-docx / lxml）。用 grep 校验：`<style>`/`<h1>`/`<div>`/`class=`/`id=` 全部为 False（安全规范通过）。

**发现的问题**：read_file 直接看输出 HTML 时，发现 callout 标签文字重复了——`📘 知识点` 标题下面又跟了一个「知识点」。

## 第 4 轮：定位并修复 bug

**给 AI 的指令**：callout 标签重复，定位根因并修。

**AI 做了什么**：定位到 `convert_to_wechat.py` 第 226 行附近——callout 正文用 `text[len(emoji):].strip()` 提取，而 Markdown 写法是 `> 📘 知识点\n> 正文`，所以 emoji 剥掉后「知识点」仍留在正文里；原来的 `if body_text != label` 只挡「正文恰好等于标签」一种情况，挡不住「标签+换行+正文」。

**修复方式**：正文提取后加一步——`if body_text.startswith(label): body_text = body_text[len(label):].strip()`，把首行标签前缀剥掉。

**复验**：重新转换，grep 输出确认 5 种 callout 标题干净、无重复。

## 本轮用到的关键判断

1. **先读后改**：没读基座就动手，会重复造轮子或破坏 starter 已有逻辑。
2. **单一职责**：6 项能力各自独立，改配色不动 callout，改目录不动元数据。
3. **真跑真验**：不靠「看着对」，每次改动都 `python ...` 跑一遍 + grep 校验输出。
4. **bug 写进记录**：callout 标签重复是真实踩坑，写进本日志和 AAR，而不是藏着。

## AI 工具记录（可复核）

- `write_file` / `edit_file`：写 SKILL.md、references、示例文章、脚本
- `bash`（python）：运行转换脚本、安装依赖、跑 `--help`、grep 校验
- `read_file`：读基座文件、定位 bug 代码段
