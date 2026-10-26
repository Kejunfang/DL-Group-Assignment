# AGENTS.md — 项目协作配置

本文件是本项目内所有 AI agent 的强制配置，优先级高于任何默认习惯。
用户若要调整规则，直接编辑本文件；agent 不得自行删除、弱化或绕过其中任何一条。

## 1. 语言约定：中文交流，英文产出

- 与用户的对话、澄清提问、进度汇报、过程解释：一律使用中文。
- 报告（report）、结果（result）、交付文档、表格/图表说明：一律使用英文。
- 代码、注释、变量名、文件名、commit message：使用英文。

## 2. 每次执行先用 karpathy-guidelines 优化流程

- 每个任务开始前，先加载并应用 `karpathy-guidelines` skill。
- 固定四步：① 先思考，写出假设与可验收的成功标准 → ② 用能解决问题的最小实现 → ③ 只做必要改动，不顺手重构无关代码 → ④ 以可验证的目标驱动执行，循环到全部通过。
- 多步任务先在回复中给出「步骤 → 验证方式」的简短计划，再动手。

## 3. 任何改动都必须单独提交

- 每完成一个独立改动，立即 `git commit` 一次；不积压，不把不相关的改动混进同一个 commit。
- 提交信息使用英文，格式 `<type>: <summary>`，`type` 取 `feat` / `fix` / `docs` / `test` / `refactor` / `chore`。
- 每次提交前先看 `git status` 与 `git diff`，确认提交范围与预期完全一致。
- **重要变动必须回写本文件**：出现任何影响项目执行的重要变动（需求变化、数据集与标签方案、技术栈、代码文件结构与命名、成员分工、截止日期、交付要求等）时，必须在同一次改动中同步更新本文件对应条款；只改代码或文档、不更新本文件，视为改动未完成。

## 4. 提交前必须测试 + 模拟，全部通过才可提交

- 强制顺序：先测试（运行现有测试/校验脚本），再做一次模拟执行（dry-run 真实执行路径，检查真实产出），两者全部通过后才允许 `commit`。
- 任一步失败：修复后从头重跑，禁止用 commit 绕过失败的测试。
- 项目暂无可运行的测试时，先补一个最小自动校验脚本，并在提交说明中写清已执行了哪些检查。
- 本项目配置自检脚本：`bash scripts/check-config.sh`，退出码为 0 才算通过。

## 5. 项目资料与权威来源（按用途区分，不要混用）

| # | 资料 | 位置 | 使用时机与规则 |
|---|------|------|----------------|
| A | 客户需求文档 + 技术文档 | https://docs.google.com/document/d/1gtXetjRMJPsyf2Oy3_ry1-jAWAEhTNbjVmHc7na862s/edit?tab=t.0#heading=h.s3by5ebukh2x | **时刻关注**。每次 commit 前必须对照核对本次改动是否满足要求。发现不符合 → 先告知用户，**禁止 commit**；改好并通过核对后才允许 commit。 |
| B | Assignment guideline（最全的 guideline，最终验收标准） | `/Users/hill/Desktop/Work/DL Group Assignment/CSC60904-Deep Learning Group Assignment 30%.pdf` | **平时不读**。只在准备提交最终成果前才通读，并逐条核对所有产出是否符合该 guideline。 |
| C | Report 撰写位置 | https://docs.google.com/document/d/1TewRPdkWW4jRivSg-_MLOrYXNsRWVOR0tHExsaQ_LjQ/edit?tab=t.0 | 所有 report 正文最终写进这个 Google Doc。**agent 默认只读**：只给英文草稿与修改建议，未经用户明确授权，不得写入或改动该文档。 |
| D | 代码（Coding Component） | `code/`（最终提交：`code/Group_8_Image_Recognition.ipynb`）。旧版 ver1 已移到 `old_code/`，**存在缺陷，仅作参考，不得作为提交物**，已被 `.gitignore` 排除。 | **唯一代码来源**：新代码由用户从零编写，全部 Python 代码只放在 `code/` 下的 notebook，不在仓库其他位置零散存放副本。开发期 `code/` 可以为空，但最多只能有一份 `.ipynb`（`scripts/check-config.sh` 强制检查）；最终提交为单文件 `Group_8_Image_Recognition.ipynb`（`NO`=组号 8）并复查注释完整性。 |

补充约束：

- 文档 A 中的 `Due date: 08th November 2026` 是组员把各自完成的部分交给组长的**内部截止日期**，**不是** assignment 的最终提交日期。assignment 的最终截止日期以文档 C 为准，且每次都以实时读取的文档为准。
- 文档 C 的写入权限由用户掌握：agent 默认维持只读，只给建议（改动点、理由、可直接粘贴的英文段落）；只有用户明确授权后才可以协助写入。
- A 与 C 可公开只读，取全文用：`curl -sL "https://docs.google.com/document/d/<DOC_ID>/export?format=txt"`。核对 A 是强制门禁，不是可选项。
- 若 A 无法访问或内容不明确：立即告知用户，不要凭记忆假设要求，也不要继续 commit。
- A 是需求的实时来源，禁止在仓库里缓存/复制一份需求文本当依据（会过期）。
- B 只在最终提交前整体核对，避免日常按局部 guideline 误判范围。
- **技术栈（已定）**：Part 2 统一使用 TensorFlow / Keras 单一栈（Colab 预装），不写 PyTorch 训练代码；文档 A 2.2 提到的 `requires_grad / backward()` 只在报告中作文字对比，不作为实现路径。
- **数据集与标签方案（已定）**：三个数据集全部使用。ISIC 2018 Task 3 = 训练/验证/测试（7 类，病灶级切分）；ISIC 2019 = 外部验证（8→7 类映射，排除 SCC，须与 2018 做 hash 去重）；SIIM-ISIC 2020 = 域外测试（按病人切分，折叠为 malignant = MEL+BCC+AKIEC，报 AUC 与指定特异度下敏感度）。全项目统一 7 类标签空间：`MEL, NV, BCC, AKIEC, BKL, DF, VASC`。

## 6. 本地测试环境：conda dev

- 任何在本地执行的 Python 测试、校验或代码检查，必须先 `conda activate dev`，不要在 `base` 环境里跑项目代码。
- 缺少依赖时由 agent 直接用 conda 安装到 `dev`（优先 `-c conda-forge`），装完复跑 import 验证；安装不得破坏已装好的 tensorflow / keras / numpy。
- 本地 `dev` 仅用于自测；最终交付的运行环境以文档 A 为准（Google Colab），本地环境差异不得成为改变交付要求的理由。

## 提交前自查清单

- [ ] 本次改动对应用户的哪个请求？
- [ ] 是否已加载 karpathy-guidelines 并按其四步执行？
- [ ] 测试通过？模拟（dry-run）通过？
- [ ] 已核对需求文档 A，本次改动没有不符合项？（有不符合项时先告知用户并停止 commit）
- [ ] 若本次是最终成果提交：已通读 guideline B 并逐条核对？
- [ ] 若涉及 report：已给出英文草稿与修改建议，且未经授权没有写入文档 C？
- [ ] 是否只包含本次改动，没有无关文件？
- [ ] 若本次改动含重要变动，是否已同步更新本文件对应条款？
- [ ] commit message 为英文且格式正确？
- [ ] 给用户的结论/报告是英文，过程交流是中文？
