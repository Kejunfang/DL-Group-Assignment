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
| B | Assignment guideline（最全的 guideline，最终验收标准） | 项目根目录下的 `CSC60904-Deep Learning Group Assignment 30%.pdf`（相对路径，随项目一起移动） | **平时不读**。只在准备提交最终成果前才通读，并逐条核对所有产出是否符合该 guideline。 |
| C | Report 撰写位置 | https://docs.google.com/document/d/1TewRPdkWW4jRivSg-_MLOrYXNsRWVOR0tHExsaQ_LjQ/edit?tab=t.0 | 所有 report 正文最终写进这个 Google Doc。**agent 默认只读**：只给英文草稿与修改建议，未经用户明确授权，不得写入或改动该文档。 |
| D | 代码（Coding Component） | `code/Group_8_Image_Recognition.ipynb`（唯一提交物）。用户提供的参考代码在 `references/`（不是本组代码，已被 `.gitignore` 排除，**只学思路、不得照抄**）；更早的旧版在 `old_code/`，同样不得作为提交物。 | **唯一代码来源**：全部 Python 代码只放在这一个 notebook 里，不在仓库其他位置零散存放副本。`code/` 只允许这一个 `.ipynb`（文件名固定，`scripts/check-config.sh` 强制检查）。最终提交为单文件 `Group_8_Image_Recognition.ipynb`（`NO`=组号 8）并复查注释完整性。 |

补充约束：

- 文档 A 中的 `Due date: 08th November 2026` 是组员把各自完成的部分交给组长的**内部截止日期**，**不是** assignment 的最终提交日期。assignment 的最终截止日期以文档 C 为准，且每次都以实时读取的文档为准。
- 文档 C 的写入权限由用户掌握：agent 默认维持只读，只给建议（改动点、理由、可直接粘贴的英文段落）；只有用户明确授权后才可以协助写入。
- A 与 C 可公开只读，取全文用：`curl -sL "https://docs.google.com/document/d/<DOC_ID>/export?format=txt"`。核对 A 是强制门禁，不是可选项。
- 若 A 无法访问或内容不明确：立即告知用户，不要凭记忆假设要求，也不要继续 commit。
- A 是需求的实时来源，禁止在仓库里缓存/复制一份需求文本当依据（会过期）。
- `CLAUDE.md` 是 Claude Code 的入口：它用 `@AGENTS.md` 导入本文件，只补充 Claude 专用的落实细节，不另立规则；规则只在本文件维护。
- B 只在最终提交前整体核对，避免日常按局部 guideline 误判范围。
- **项目可整体搬移**：仓库内一律使用相对项目根目录的路径，不得写入个人主目录的绝对路径（即 `~` 展开后的路径）；整个文件夹可移动到任意目录，移动后必须复核 `git status`（应为 clean）与 `bash scripts/check-config.sh`（应 PASS）。`data/`、`old_code/`、`references/`、`outputs/` 不在 git 里，搬移或换机器时必须单独拷贝 `data/`，否则 notebook 找不到数据集。
- **技术栈（已定）**：Part 2 统一使用 TensorFlow / Keras 单一栈（本地 `conda dev` 已安装，TensorFlow 2.21 / Keras 3.15），不写 PyTorch 训练代码；文档 A 2.2 提到的 `requires_grad / backward()` 只在报告中作文字对比，不作为实现路径。
- **数据集与标签方案（2026-10-29 重写版）**：使用三个数据源，全部映射到统一的 7 类标签空间 `MEL, NV, BCC, AKIEC, BKL, DF, VASC`。① HAM10000（文档 A 的 `Skin Cancer HAM10000`，10,015 张，`HAM10000_metadata.csv`）按 `lesion_id` 做病灶级分层切分 70/15/15 = 训练/验证/测试；② ISIC 2019 训练集（25,331 张，8 类，AKIEC 列名为 `AK`）里已包含全部 10,015 张 HAM10000 图（同一 `ISIC_xxxxxxx` 编号），按编号去掉这些图、再去掉 SCC 后的约 14,885 张**全部并入训练**；③ BCN20000（ISIC 2019 官方 test set 中有标签的部分，去掉 UNK 与 SCC 后 6,026 张）**全部并入训练**。验证集与测试集只来自 HAM10000，不含任何额外数据。文档 A 的数据集清单把 `ISIC 2018` 与 `SIIM-ISIC 2020` 标注为 `Not Use`，HAM10000 与 ISIC 2018 Task 3 是同一批图，本方案用的是 Kaggle HAM10000 版本，因此与文档 A **一致、无偏离**；report 需写明 ISIC 2019 与 BCN20000 的角色是“额外训练数据”。

## 6. 运行环境：本地 Anaconda `conda dev` + Jupyter Notebook，或 Kaggle Notebooks（GPU）

- **2026-10-29 用户决定推翻旧代码、从零重写**：旧的三份 notebook（交付版 + 本地副本 + Colab 副本）、`scripts/build_local_runner.py`、`scripts/build_colab_runner.py`、`scripts/run-local.sh` 已删除，只在 git 历史里可查；Colab / Kaggle 云端训练分支随之取消。运行环境回到文档 A 写的 `Local Environment, Using Anaconda, Jupyter Notebook`，**与文档 A 一致，无偏离**。
- **Kaggle GPU 运行（2026-10-29 由用户要求增加，本地 CPU 太慢）**：不另建 notebook，同一份交付 notebook 检测到 `/kaggle/input` 时自动切换：数据从 Kaggle 挂载的数据集读取（按标签文件 `HAM10000_metadata.csv` / `ISIC_2019_Training_GroundTruth.csv` / `ISIC_2019_Test_GroundTruth.csv` 定位文件夹），产物写 `/kaggle/working/outputs`。用户在 Kaggle 上 Import Notebook，Add Input 三个数据集 `kmader/skin-cancer-mnist-ham10000`、`andrewmvd/isic-2019`、`hillzhangjunyi/group8-bcn20000`（私有，512 px，6,026 张），Accelerator 选 GPU、Internet 打开，再 `Save & Run All (Commit)`。训练配方与本地完全相同（float32，不加混合精度）。文档 A 写的是 `Local Environment, Using Anaconda, Jupyter Notebook`：在 Kaggle 上训练属于**用户批准的偏离**，report 必须说明（本地分支仍保留，代码在本地照样能跑）。
- 本地机器：Apple M4，16 GB 内存，TensorFlow 只用 CPU（float32）。任何 Python 执行先 `conda activate dev`（agent 用 `conda run -n dev ...`）。
- **正式训练由用户在 Jupyter 中亲自运行**：用户需要 notebook 里内嵌的训练过程与可视化输出交给老师，因此 agent **不得**在后台代跑正式训练（`nohup`、后台 `python` 等）。agent 只负责改代码、跑分钟级的冒烟测试与小规模推理验证、交代运行方法、分析用户跑出的结果。
- **冒烟测试**：notebook 读两个环境变量，只用于测试——`G8_SMOKE=1`（每类每个 split 只取 8 张、每阶段 1 epoch）、`G8_OUT_DIR=<目录>`（产物写到别处，不碰 `outputs/`）。在 Jupyter 里正常 `Run All` 时两者都不设。
- **代码风格（用户要求）**：参考 `references/` 的思路（两段式迁移学习、224 输入、ImageNet 归一化、混淆矩阵、逐图预测可视化），但**不照抄**；写法保持简单易懂，不用太专业的技巧（不做多 seed 集成、TTA、SWA、Mixup、温度缩放、多分辨率阶段）。每个单元前用 markdown 标注对应的 guideline 条目（2.1–2.20）。
- **训练配方（2026-10-29 重写版）**：Keras `ResNet50`（ImageNet 权重）+ GlobalAveragePooling + Dropout 0.3 + Dense(7) logits + Softmax；输入 224×224；Stage 1 冻结主干只训分类头 3 epochs（Adam 1e-3）；Stage 2 解冻 `conv4`/`conv5`（BatchNorm 保持冻结）再训 12 epochs（Adam，学习率从 1e-4 余弦退火到 1e-6）；loss = categorical cross-entropy；按 val accuracy 保存最佳权重，测试只用一次。增强：水平/垂直翻转、旋转、缩放、亮度/对比度（只在训练时生效）。`SEED = 8`。
- **断点续训**：Stage 1 完成后存 `head.weights.h5`，重跑时直接载入跳过；Stage 2 用 `keras.callbacks.BackupAndRestore`，kernel 中断后重新 `Run All` 会从最近一个 epoch 继续。
- **预缩放缓存**：第一次运行时把全部图片缩放成 224×224 JPEG 写到 `outputs/resized_224/`（一次性，约 10–20 分钟），之后每个 epoch 直接读小图，省掉解码大图的时间。
- **算力预估（旧代码 2026-10-29 实测推算）**：约 28k 张训练图，CPU 上 Stage 1 约 15 min/epoch、Stage 2 约 21 min/epoch，整个训练约 **5 小时**。
- **已有实测经验（来自旧代码，仍有参考价值）**：旧版 ResNet-50 在 HAM10000 病灶级切分上 val/test 约 83–85%；train accuracy 会升到接近 100% 而 val 停住，瓶颈是过拟合，多加 epoch 没有收益；类权重 / 焦点损失 / 过采样会抬高 macro F1 但压低 accuracy；换骨干违反文档 A（锁定 ResNet）。
- 缺少依赖时由 agent 直接用 conda 安装到 `dev`（优先 `-c conda-forge`），装完复跑 import 验证；安装不得破坏已装好的 tensorflow / keras / numpy。
- **数据路径**：`data/` 由用户手动下载并解压（已 git 忽略）：`data/ISIC 2018/` = HAM10000（`HAM10000_metadata.csv` + 10,015 张 jpg，分在两个子目录）；`data/ISIC 2019/` = 8 类训练集（`ISIC_2019_Training_GroundTruth.csv` + 25,331 张 jpg，按类分子目录）；`data/BCN20000/` = ISIC 2019 官方 test set（`ISIC_2019_Test_GroundTruth.csv` + `ISIC_2019_Test_Input/` 8,238 张 jpg，CC BY-NC 4.0）。notebook 一律用 `DATA_ROOT` / `OUT_DIR` 变量拼路径并用 `rglob` 递归查找文件，禁止硬编码个人绝对路径；生成物写入 `outputs/`（已 git 忽略）。

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
