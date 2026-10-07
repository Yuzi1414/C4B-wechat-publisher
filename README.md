# C4B · 公众号文章生成技能（wechat-publisher）

> EduSeed「Elite 20」挑战 C4B 交付物仓库
> 作者：虞梦琳（yml）

## 挑战目标

从官方 starter kit `c4b-wechat-publisher-starter.zip` 出发，用 `skill-creator` 技能把它改造成一个个性化的公众号文章生成技能，产出一篇结构与观点俱佳的文章，完成真实发布，并用数据复盘传播效果。

## 已发布文章

- 链接：<https://mp.weixin.qq.com/s/7MTO7s0j7BB1LyAW8MzY5Q>
- 标题：用 AI 高效学习：我从踩坑到上手的 5 条心得
- 公众号：余赴遇 · 作者：虞梦琳 · 发布时间：2026-10-07

## 交付物清单（7 件，全部齐全）

| # | 交付物 | 本仓库路径 |
|---|--------|-----------|
| 1 | 定制后的技能包 | `yml_C4B_wechat-publisher/`（SKILL.md + scripts/ + references/ + examples/） |
| 2 | 公众号文章链接 | `yml_C4B_文章链接.md` |
| 3 | 文章源文件 | `yml_C4B_文章源文件.md` |
| 4 | 转换后 HTML | `yml_C4B_output.html` |
| 5 | 教学说明 | `yml_C4B_教学说明.md` |
| 6 | AI 日志 | `yml_C4B_AI日志.md` |
| 7 | 拿来说明 | `yml_C4B_拿来说明.md` |

## 技能能力（相对 starter 的增量）

1. 多主题配色（THEMES）
2. callout 提示块（5 种）
3. 自动生成目录
4. 元数据与页脚
5. 中文（CJK）排版空格处理

## 使用方式

```bash
cd yml_C4B_wechat-publisher
python scripts/convert_to_wechat.py --help
```

详见 `yml_C4B_wechat-publisher/SKILL.md` 与 `yml_C4B_教学说明.md`。
