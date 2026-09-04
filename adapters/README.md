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
| **Cline / Roo Code** | `adapters/cline/amphoreus.md` | Cline 拷入 `.clinerules/`;Roo Code 拷入 `.roo/rules/`(Roo 不读目录形态的 `.clinerules/`);连同 `adapters/generic/` 携带 |
| **GitHub Copilot** | `adapters/github-copilot/copilot-instructions.md` | 拷为项目 `.github/copilot-instructions.md`,连同 `adapters/generic/` 携带 |
| **Windsurf(Cascade)** | `adapters/windsurf/amphoreus.md` | 拷入项目 `.windsurf/rules/`,连同 `adapters/generic/` 携带 |
| **Aider** | `adapters/aider/CONVENTIONS.md` | 放项目根,`aider --read CONVENTIONS.md` 加载(或写入 `.aider.conf.yml` 的 `read:`) |
| **Trae** | `adapters/trae/project_rules.md` | 拷为项目 `.trae/rules/project_rules.md`,连同 `adapters/generic/` 携带 |
| **Qwen Code** | `adapters/qwen-code/QWEN.md` | 放项目根或 `~/.qwen/QWEN.md`,连同 `adapters/generic/` 携带 |
| **iFlow CLI** | `adapters/iflow-cli/IFLOW.md` | 放项目根或 `~/.iflow/IFLOW.md`,连同 `adapters/generic/` 携带 |
| **任意可加载系统提示的智能体** | `adapters/generic/amphoreus-<hero>.md`(单卡便携版) | 直接把单卡文件作为 system prompt / 自定义指令加载 |

> 约定型生态(AGENTS.md / GEMINI.md / Copilot / Windsurf / Aider / Trae / QWEN / IFLOW / Cline)共用同一份约定正文,只是落点与安装方式不同;它们负责"何时召唤哪张卡",实际卡文一律回读 `adapters/generic/` 便携版。

## 便携版单卡的构成

每个 `generic/amphoreus-<hero>.md` = 生成头(含来源 SHA)+ 卡文 `SKILL.md` 原文 + 家族公约 `common.md` 原文(含〈沙龙与陪聊〉与〈圆桌〉、工艺词防火墙、台词 / 台账分离),单文件自足;`amphoreus-router.md` 另附关系单源 `relations.md` 原文;台词库 `persona.md` 为可选伴读(工作场角色说话 ≤15% 风格预算,陪聊 / 沙龙场不计税,严肃场景自动静音)。

## 忠实性说明

适配层不改写任何卡文内容,只做打包与约定壳;行为契约、缺席条款(`module_unavailable`)、移交事实包纪律与原生版逐字一致。验收结论(行为 65/65、两线端到端 CONFIRMED)是在 Claude Code 环境下取得的,其他生态的实际表现取决于各自模型与运行时,未在本仓库验收范围内。
