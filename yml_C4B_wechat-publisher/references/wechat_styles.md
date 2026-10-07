# 公众号样式参考（yml_C4B 版）

本文件记录 `convert_to_wechat.py` 中 4 套主题的 inline CSS 取值，方便微调。
所有样式均以内联形式写入 HTML，因为公众号编辑器只接受 inline CSS。

## 主题一览

| 主题 | 主色 | 适用场景 |
|------|------|----------|
| `default` | 深灰 `#333` + 红 `#d73a49` | 通用、技术向 |
| `green` | 墨绿 `#1e6f50` + 绿 `#1a7f37` | 学习心得、成长类 |
| `blue` | 深蓝 `#1d4ed8` | 产品介绍、科技向 |
| `dark` | 浅灰文字 `#c9d1d9` + 深底 | 深色质感（注意可读性） |

## 各元素样式取值

### 标题 h2 / h3

- h2：`font-size: 22px; font-weight: bold; line-height: 1.6; color: <主色>; margin: 22px 0 10px 0;`
- h3：`font-size: 18px; font-weight: bold; line-height: 1.6; color: <主色>; margin: 16px 0 8px 0;`

> 注意：公众号禁止 `<h1>`，转换时自动降级为 `<h2>`。

### 正文 p / 列表 li

- p：`font-size: 16px; line-height: 1.8; color: <文字色>; margin: 12px 0;`
- li：`font-size: 16px; line-height: 1.8; color: <文字色>; margin: 6px 0;`

### 链接 a

- `color: <链接色>; text-decoration: underline;`

### 行内代码 code_inline

- `background-color: #f5f5f5; color: <强调色>; font-size: 14px; padding: 2px 5px; border-radius: 3px;`

### 代码块 code_block

- `background-color: <代码底>; color: #24292e; font-size: 14px; line-height: 1.6; padding: 14px; margin: 12px 0;`

### 引用 blockquote

- `background-color: #f9f9f9; color: #666; padding: 12px 16px; margin: 12px 0; border-left: 4px solid <强调色>;`

### 表格 table / th / td

- table：`border-collapse: collapse; margin: 12px 0; font-size: 14px; width: 100%;`
- th：`background-color: <代码底>; color: #24292e; font-weight: bold; padding: 8px; text-align: left; border: 1px solid #ddd;`
- td：`padding: 8px; border: 1px solid #ddd; color: <文字色>;`

## Callout 高亮框配色

| emoji | 标签 | 背景色 | 边框色 | 文字色 |
|-------|------|--------|--------|--------|
| 📘 | 知识点 | `#eef3fb` | `#1d4ed8` | `#1e3a5f` |
| 💡 | 建议 | `#fff8e6` | `#d97706` | `#5c4a00` |
| ✅ | 实践 | `#eef8f1` | `#1a7f37` | `#14532d` |
| ⚠️ | 注意 | `#fff0f0` | `#dc2626` | `#7f1d1d` |
| ❌ | 避坑 | `#fdf2f2` | `#b91c1c` | `#7f1d1d` |

callout 通用：`padding: 12px 16px; margin: 12px 0; border-left: 4px solid <边框色>; line-height: 1.75;`

## 目录块（--toc）

- `background-color: #f8f9fa; padding: 14px 16px; margin: 16px 0; border-left: 4px solid #0366d6; color: #333; font-size: 15px; line-height: 1.9;`
- 标题「📑 目录」：`font-weight: bold; font-size: 16px; color: #0366d6;`

## 元数据块（--title/--author/--date/--abstract）

- `background-color: #f0f6ff; padding: 12px 16px; margin: 16px 0; border-left: 4px solid #0366d6; color: #444; font-size: 14px; line-height: 1.7;`

## 页脚（--footer）

- `text-align: center; color: #999; font-size: 13px; margin: 24px 0 8px 0; padding-top: 12px; border-top: 1px solid #eee; line-height: 1.6;`

## 微调方法

1. 编辑 `scripts/convert_to_wechat.py` 里的 `THEMES` / `CALLOUTS` 字典。
2. 本文件同步更新，保持「代码 = 文档」一致。
3. 改完跑一次示例转换验证效果。
