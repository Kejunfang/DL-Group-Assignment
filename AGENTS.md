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
| D | 代码（Coding Component） | `code/`（最终提交：`code/Group_8_Image_Recognition.ipynb`）+ `code/Group_8_Image_Recognition_local.ipynb`（本地 CPU 长跑备份，自动生成）。旧版 ver1 已移到 `old_code/`，**存在缺陷，仅作参考，不得作为提交物**，已被 `.gitignore` 排除。 | **唯一代码来源**：新代码由用户从零编写，全部 Python 代码只放在 `code/` 下的 notebook，不在仓库其他位置零散存放副本。`code/` 只允许这两个 `.ipynb`（文件名固定，`scripts/check-config.sh` 强制检查）：交付 notebook 是唯一提交物；本地跑分 notebook 由 `scripts/build_local_runner.py` 从交付 notebook 自动生成（单元内容一致，只多 3 个"本地运行设置"单元），**禁止手改**，改了交付 notebook 必须重新生成，自检脚本会校验两者是否同步。最终提交为单文件 `Group_8_Image_Recognition.ipynb`（`NO`=组号 8）并复查注释完整性。 |

补充约束：

- 文档 A 中的 `Due date: 08th November 2026` 是组员把各自完成的部分交给组长的**内部截止日期**，**不是** assignment 的最终提交日期。assignment 的最终截止日期以文档 C 为准，且每次都以实时读取的文档为准。
- 文档 C 的写入权限由用户掌握：agent 默认维持只读，只给建议（改动点、理由、可直接粘贴的英文段落）；只有用户明确授权后才可以协助写入。
- A 与 C 可公开只读，取全文用：`curl -sL "https://docs.google.com/document/d/<DOC_ID>/export?format=txt"`。核对 A 是强制门禁，不是可选项。
- 若 A 无法访问或内容不明确：立即告知用户，不要凭记忆假设要求，也不要继续 commit。
- A 是需求的实时来源，禁止在仓库里缓存/复制一份需求文本当依据（会过期）。
- B 只在最终提交前整体核对，避免日常按局部 guideline 误判范围。
- **项目可整体搬移**：仓库内一律使用相对项目根目录的路径，不得写入个人主目录的绝对路径（即 `~` 展开后的路径）；整个文件夹可移动到任意目录，移动后必须复核 `git status`（应为 clean）与 `bash scripts/check-config.sh`（应 PASS）。`data/`、`old_code/`、`outputs/` 不在 git 里，搬移或换机器时必须单独拷贝 `data/`，否则 notebook 找不到数据集。
- **技术栈（已定）**：Part 2 统一使用 TensorFlow / Keras 单一栈（本地 `conda dev` 已安装，TensorFlow 2.21 / Keras 3.15），不写 PyTorch 训练代码；文档 A 2.2 提到的 `requires_grad / backward()` 只在报告中作文字对比，不作为实现路径。
- **数据集与标签方案（已定）**：使用两个数据集。ISIC 2018（HAM10000，Task 3，10,015 张图 + `HAM10000_metadata.csv`）= 训练/验证/测试（7 类，病灶级切分）；ISIC 2019（25,331 张图 + `ISIC_2019_Training_GroundTruth.csv`，8 类，AKIEC 列名为 `AK`）= 外部验证（8→7 类映射，排除 SCC，须与 2018 做 hash 去重）。文档 A 的数据集清单中，`SIIM-ISIC 2020` 已被用户标注为 `Not Use`，`Skin Cancer HAM10000` 就是本文的 ISIC 2018 数据（同一批 10,015 张图，不重复计数），因此本方案与文档 A **一致、无偏离**；report 只需简述第三个数据集因体量原因未使用。全项目统一 7 类标签空间：`MEL, NV, BCC, AKIEC, BKL, DF, VASC`。

## 6. 运行环境：Google Colab（训练）+ 本地 conda dev（开发/冒烟）

- **交付运行环境已改为云端免费 T4 GPU（Google Colab / Kaggle Notebooks），2026-10-27 由用户决定**；Colab GPU 额度用尽后改走 **Kaggle Notebooks**（30 h/周，单 kernel 上限 9 h）：用 Kaggle API 提交并轮询 `hillzhangjunyi/group8-isic-seed{8,42,2026}` 三个单 seed 训练 kernel（并行），再由 `hillzhangjunyi/group8-combine` 汇总成三模型集成报告；BCN20000 以私有数据集 `hillzhangjunyi/group8-bcn20000` 上传（512 px、6,026 张、约 210 MB）。
- **Colab 分支仍保留**；文档 A 原文写的是 `Local environment, using Anaconda, Jupyter Notebook`，本次属于**已获用户批准的偏离**，必须在 report 中说明（用户在 Google Doc 里同步这句：`Training: Google Colab (T4 GPU, mixed precision)`）。notebook 同时保留本地分支：检测不到 `google.colab` 时用本地 `data/` + `outputs/` + float32，便于本地冒烟与复现。
- Colab 分支：`google.colab.drive.mount` 挂载 Drive，产物写到 `MyDrive/Group_8/outputs`（逐 epoch checkpoint 到 Drive，断线可续训）；数据集用 **Kaggle API** 直接下载到 `/content/data`（需要 `kaggle.json`，notebook 启动时提示上传一次），因此不需要手工上传 6 GB 数据；GPU 策略为 `mixed_float16`。
- 本地 `conda dev` 仍用于：dev 环境内运行 notebook（CPU、float32）、静态检查、以及每轮改动前的**小样本冒烟**（subset 数据 + 1 epoch/stage，约 4 分钟）。任何 Python 执行先 `conda activate dev`。
- **本地 CPU 长跑备份（2026-10-28 由用户要求增加，云端 GPU 被限额时的保底方案）**：`code/Group_8_Image_Recognition_local.ipynb` 是交付 notebook 的自动生成副本（多 3 个可编辑的"本地运行设置"单元），可在 Jupyter 里 `Run All`，也可无头启动：`bash scripts/run-local.sh`（后台 + `caffeinate` 防休眠 + 日志 `outputs/local_run/run.log`）、`bash scripts/run-local.sh --smoke`（每类 8 张 + 每阶段 1 epoch 的连线测试）。产物写 `outputs/local_run/`，**不覆盖**交付 notebook 自己的 `outputs/`。逐 epoch 存 `model/seed<seed>/last.weights.h5` 并追加 `tables/train_history_seed<seed>.csv`，训练单元会按记录回退到最近 checkpoint 继续，因此休眠/崩溃/关 kernel 最多损失 1 个 epoch，重跑同一条命令即可续训。用户明确表示**本地 CPU 长跑时间不限，目标仍是 val accuracy ≥ 90%**。
- 缺少依赖时由 agent 直接用 conda 安装到 `dev`（优先 `-c conda-forge`），装完复跑 import 验证；安装不得破坏已装好的 tensorflow / keras / numpy。
- **算力约束（本地 M4，CPU-only，2026-10-29 实测）**：22,698 张训练集，ResNet-50 stage A（冻结主干）约 734 s/epoch；stage B @224（微调 conv4/conv5）约 1,035 s/epoch；stage C @352 约 2,347 s/epoch → v2 配方（60 epochs）单 seed 约 23 小时，v3 配方（25 epochs）单 seed 约 **9 小时**。持续满载会降频（实测 1,008 → 1,225 s/epoch），但不会停止。Colab T4 约 190 s/epoch @224、275 s/epoch @352 → v3 单 seed 约 **1.5 小时**。训练必须逐 epoch + 断点续训；时间不够时优先减少 epoch 或冻结主干，而不是降低评估口径。
- **已定训练配方（2026-10-29 第四版 v3，目标 val accuracy ≥ 90%）**：训练集 = ISIC 2018 train（7,028）+ ISIC 2019 去重后 65%（9,644）+ **BCN20000（ISIC 2019 官方 test set 中有官方标签的部分，剔除 UNK 2,047 与 SCC 165 后 6,026 张；与 2018/2019 的 md5 重叠为 0）** = **22,698 张**（MEL 4,325、NV 11,211、BCC 3,159、BKL 2,399、AKIEC 1,072、DF 254、VASC 278，NV 占比 49.4%）；验证 = ISIC 2018 validation（1,488，病灶级）；测试 = ISIC 2018 test（1,499）；外部验证 = 留出的 35% ISIC 2019（5,193）。数据切分/增强/洗牌固定 `SEED = 8`，模型初始化用 3 个 seed（8 / 42 / 2026）。
  - **v1（2026-10-28 完成，已作为对照实验保留）**：3 + 59 + 8 = 70 epochs，仅 conv4/conv5 可训练，弱增强，Adam。实测 seed 8：history best val 0.8434（epoch 62，224 px 评估）、SWA 0.8407（352 px 评估，最终选中）；**train accuracy 一路升到 1.000，验证准确率自 epoch 20 起停在 0.83–0.84** → 瓶颈是过拟合，不是容量。Colab 45 epochs 版（3+34+8）SWA val 0.8427，与 70 epochs 版基本相同 → **增加 epoch 没有收益**。
  - **v2（2026-10-29 已停止，只跑了 1 个 epoch；其增强与 AdamW 设置被 v3 继承）**：增强大幅加强（水平+垂直翻转、旋转 ±180°、缩放 15%、平移 8%、亮度 10%）；stage B/C 改用 **AdamW + `0.05` 解耦权重衰减**（stage A 仍用 Adam `1e-3`；2026-10-29 修正：Keras 的衰减是 `w -= lr·wd·w`，原先的 `1e-4` 在 `lr≈1e-5` 下整个训练只缩小约 0.005%，等于没开）；epoch 预算改为 **A 3 @224 + B 42 @224 + C 15 @352 = 60**（把预算从 224 的 B 挪到高分辨率的 C）；可训练层仍为 conv4/conv5，BatchNorm 冻结；loss = categorical cross-entropy + label smoothing 0.1；最后 5 epoch 取 SWA，与 best checkpoint 按验证集择优；预测 = 多 seed + **8 视图 TTA**（4 翻转 × {352, 320}）平均；温度缩放在验证集上拟合。
  - **v3（当前配方）**：在 v2 基础上把 epoch 预算缩短为 **A 3 @224 + B 17 @224 + C 5 @352 = 25**，SWA 取整个 stage C 的 5 个 epoch。依据：v1 的 val loss 在 epoch 8 已最低，epoch 19 之后 val acc 一直在 0.83–0.84 而 train acc 升到 1.000 → 多出来的 epoch 只在背训练集；省下的算力用来跑更多 seed 做集成。
  - **已否决的做法（有实测依据）**：解冻 conv3（可训练参数 16.1M → 23.3M，只会加重已有的过拟合）；裁掉四周暗角（用 v1 checkpoint 实测 val 0.8401 → 0.8286，−1.2 点）；类权重 / 焦点损失 / 过采样（会抬高 macro F1 但压低 accuracy，与用户目标相反）；换骨干 EfficientNet/ConvNeXt（文档 A 与 guideline B 都锁定 ResNet，属违约）；先验校正 / label-shift 校正（按 HAM train 先验 ÷ 合并训练集先验重加权 softmax，2026-10-29 用 v1 SWA checkpoint + 8 视图 TTA 实测：val acc 0.8522 → 0.8569（+7 张图，噪声内），test acc 0.8686 → 0.8679、balanced acc 0.777 → 0.755，**无收益且伤 balanced acc**）。同次实测：8 视图 TTA 本身比单视图 +1.1～1.3 点（v1 单模型 test 0.8552 → 0.8686）。
  - 运行方式：本地 CPU 无头长跑 `bash scripts/run-local.sh outputs/local_run_v3`（日志 `outputs/local_run_v3/run.log`，可续训）；Colab/Kaggle T4 跑额外 seed（约 1.5 h/seed）。最终提交的模型是 3–4 个 seed 的集成，预期 val/test **89–91%**（90% 不保证）。
- **BCN20000 数据来源与合规**：来自 ISIC Archive 2019 官方 test set（`data/BCN20000/`：`ISIC_2019_Test_Input.zip` + `ISIC_2019_Test_GroundTruth.csv` + `ISIC_2019_Test_Metadata.csv`，CC BY-NC 4.0；无 `lesion_id`，全量并入训练、不做切分）。它属于文档 A 数据集清单里的 "ISIC 2019"（同一挑战的 test split），不是新增数据集，但 report 必须写明其角色是"额外训练数据"。
- **PAD-UFES-20 评估结论（2026-10-27）**：`maxjen/pad-ufes-20` 版本只有 PNG 图像、无逐图标签 CSV，且为手机临床照片（域差大），**决定不使用**；如后续需要，只作为辅助预训练数据，不直接混入皮肤镜训练集。
- **数据路径与本地运行**：本地开发时 `data/` 由用户手动下载并解压（`data/` 已 git 忽略）：`data/ISIC 2018/` = HAM10000（`HAM10000_metadata.csv` + 10,015 张 jpg，允许嵌套子目录）；`data/ISIC 2019/` = 8 类训练集（`ISIC_2019_Training_GroundTruth.csv` + 25,331 张 jpg，按类分子目录）；`data/BCN20000/` = 2019 test set（zip 会被 notebook 自动解压）。notebook 一律用 `DATA_ROOT` / `OUT_DIR` 变量拼路径并用 `rglob` 递归查找文件，禁止硬编码个人绝对路径；生成物写入 `outputs/`（已 git 忽略）。

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
