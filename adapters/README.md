# 其他智能体适配(Adapters)

`skills/` 是唯一事实源(Claude Code / Cursor 原生格式);本目录全部文件由 `build.py` 从其生成,**勿手改**——改了 `skills/` 后重跑:

```bash
python adapters/build.py
```

## 支持矩阵

| 目标生态 | 取用文件 | 安装方式 |
| --- | --- | --- |
| **Claude Code / Cursor**(原生) | `skills/` 整树 | 拷入 `~/.claude/skills/`,见仓库主 README |
| **OpenAI Codex CLI / OpenCode / Amp / Jules** 等 AGENTS.md 系 | `adapters/openai-codex/AGENTS.md` | 放项目根或全局(如 `~/.codex/AGENTS.md`),连同 `adapters/generic/` 一起携带 |
| **Gemini CLI** | `adapters/gemini-cli/GEMINI.md` | 放项目根或 `~/.gemini/GEMINI.md`,连同 `adapters/generic/` 携带 |
| **Cline / Roo Code** | `adapters/cline/amphoreus.md` | 拷入项目 `.clinerules/`,连同 `adapters/generic/` 携带 |
| **任意可加载系统提示的智能体** | `adapters/generic/amphoreus-<hero>.md`(单卡便携版) | 直接把单卡文件作为 system prompt / 自定义指令加载 |

## 便携版单卡的构成

每个 `generic/amphoreus-<hero>.md` = 生成头(含来源 SHA)+ 卡文 `SKILL.md` 原文 + 家族公约 `common.md` 原文,单文件自足;台词库 `persona.md` 为可选伴读(角色说话 ≤15% 风格预算,严肃场景自动静音)。

## 忠实性说明

适配层不改写任何卡文内容,只做打包与约定壳;行为契约、缺席条款(`module_unavailable`)、移交事实包纪律与原生版逐字一致。验收结论(每卡 60/60、两线端到端 CONFIRMED)是在 Claude Code 环境下取得的,其他生态的实际表现取决于各自模型与运行时,未在本仓库验收范围内。
