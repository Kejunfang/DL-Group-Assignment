# CLAUDE.md — Claude Code 入口

@AGENTS.md

`AGENTS.md` 是本项目唯一的规则来源，上面一行把它整份导入。本文件只写 Claude Code 如何落实这些规则，
不重复、不改写其中任何条款；两者冲突时以 `AGENTS.md` 为准，规则要改就改 `AGENTS.md`。

## 规则落地方式

- **规则 1（语言）**：对话、提问、进度汇报用中文；report / result / 表格与图表说明用英文；代码、注释、
  文件名、commit message 用英文。
- **规则 2（流程）**：每个任务开始先调用 skill `andrej-karpathy-skills:karpathy-guidelines`；多步任务用任务
  列表写出「步骤 → 验证方式」再动手。
- **规则 3 / 4（提交门禁）**，每次 commit 按顺序执行，任一步失败就修好后从头再来：
  1. `git status` + `git diff`，确认只包含本次改动；
  2. `bash scripts/check-config.sh`，退出码必须为 0；
  3. 改了 notebook 时做冒烟测试：把 `code/Group_8_Image_Recognition.ipynb` 用 `jupyter nbconvert --to script`
     导出到 scratchpad，设 `G8_SMOKE=1 G8_OUT_DIR=<全新的临时目录>` 后用 `conda run -n dev` 前台运行，检查日志里
     两个训练阶段、测试评估和所有图表单元都完成。每次用全新的 `G8_OUT_DIR`：旧的 checkpoint 会让训练单元直接
     续训或跳过，测不到改动；
  4. 用 `curl -sL "https://docs.google.com/document/d/<DOC_ID>/export?format=txt"` 重新读文档 A，核对本次改动；
  5. commit 格式 `<type>: <summary>`，正文写清跑过哪些检查。
- **改 notebook**：`code/` 下只有交付 notebook `code/Group_8_Image_Recognition.ipynb` 一个文件。保持原有 JSON 格式（`indent=1`、非 ASCII 字符不转义），否则 diff 会被格式噪声淹没。
- **Python 环境**：一律在 conda `dev` 中运行（`conda run -n dev python ...`）。`conda run` 不转发 stdin，
  heredoc 形式的脚本要先写成文件再运行。
- **临时代码**：一次性的验证脚本、推理检查放在会话的 scratchpad 目录，不进仓库（规则 5 D：项目的 Python
  代码只放在 `code/` 下的 notebook）。
- **文档 C**：默认只读，只给英文草稿与修改建议；用户明确授权后才写入。
