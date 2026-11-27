# DSCI5800 期末项目 — HPU 学业成功辅导员系统提示词设计与评估

本文件夹是这次期末项目的**全部材料**，自包含、可独立归档或提交。

## 要交的文件

| 文件 | 说明 |
|---|---|
| [`submission/DSCI5800_王_路_期末项目.pdf`](submission/DSCI5800_王_路_期末项目.pdf) | **提交件**：23 页，简体中文，Letter 纸 1 英寸页边距、宋体 / Times New Roman 12 磅、单倍行距 |

## 作业原件

| 文件 | 说明 |
|---|---|
| [`assignment/[5800][30分]期末项目.pdf`](assignment/[5800][30分]期末项目.pdf) | 中文版作业说明，9 页 |
| [`assignment/[5800][30points]Take-Home_Final_Project_HPU_Academic_Success_Coach.pdf`](assignment/[5800][30points]Take-Home_Final_Project_HPU_Academic_Success_Coach.pdf) | 英文版作业说明，9 页 |

两份均为原始文件副本，未作任何改动，便于对照评分标准与提交要求。

## 目录结构

```
DSCI5800_期末项目/
├── assignment/          作业原件（中英两版，未改动，MD5 与下载件一致）
├── submission/          提交件（PDF）
├── prompts/             所有提示词与脚本输入
│   ├── sp_v1.txt        系统提示词 v1（主记录，第一节）
│   ├── sp_v2.txt        修订版 v2（附录 A）
│   ├── sp_base.txt      对照组：无角色设定的通用助手
│   ├── turns.json       10 轮学生台词脚本
│   ├── probes.json      8 类对抗探针的输入
│   └── judge_prompt.txt LLM 评审提示词（作业规定原文）
├── runs/                原始请求与响应存档（每段对话一个 JSON）
├── scripts/             实验脚本
│   ├── run_chat.py      10 轮对话（含重复运行、v2、对照组）
│   ├── run_probes.py    8 类对抗探针 × 2 版本
│   └── run_judge.py     LLM-as-a-Judge
└── build/               报告构建脚本
    ├── make_report.py   报告正文（内容源）
    ├── mdconv.py        Markdown → HTML
    └── add_pagenum.py   加页脚页码
```

## 实验规模

共 **78 次**成功的模型调用，全部存档在 `runs/`：

| 类型 | 数量 | 说明 |
|---|---|---|
| 10 轮主对话 | 1 段 | v1，即报告第二节 |
| 补充对话 | 3 段 | v1 重复运行、v2 复测、无角色对照组 |
| 对抗探针 | 16 段 | 8 类攻击 × 2 个版本，各自独立上下文 |
| LLM 评审 | 6 次 | DeepSeek（主）与 Kimi（交叉）各评 v1、v2；DeepSeek 另评重复运行与对照组 |

**评审模型**：DeepSeek-V4-Pro（主评审）、Kimi-K3.1-Pro（交叉评审）；**被测助手**：ChatGPT（GPT-5.5）。

## 复现

脚本用 `ROOT = dirname(脚本)` 定位项目根目录，在本文件夹内任意位置运行都可以。

```bash
PY=/Users/wanglu/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3

# 10 轮对话（已有存档会跳过）
$PY scripts/run_chat.py v1

# 对抗探针
$PY scripts/run_probes.py v1

# LLM 评审（注意：sp_file 只写文件名，脚本内部会拼 prompts/）
$PY scripts/run_judge.py deepseek-v4-pro v1 sp_v1.txt

# 重建报告 PDF
$PY build/make_report.py
cd build && "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-sandbox --user-data-dir=/tmp/chrome-pdf \
  --no-pdf-header-footer --print-to-pdf=report_raw.pdf report.html
PYTHONPATH=/tmp/rl2 $PY add_pagenum.py report_raw.pdf "../submission/DSCI5800_王_路_期末项目.pdf"
```

## 说明

- **平台差异**：作业要求用 ChatGPT。本次通过 API 调用 GPT-5.5（`system` 角色承载提示词、每轮重发全历史），未使用 ChatGPT 网页版或 Custom GPT 界面。此差异在报告附录 E 中已如实说明。
- **数据合规**：对话中的林嘉怡、张伟、学号 FICT-2026-0731、工号 A-119 / T-2201 及所有成绩均为虚构。
- **API 密钥**：脚本从 `~/.dsh/.credentials.yaml` 读取，未写入本文件夹。
- **报告结论**：报告的判定口径较严格，未按“六项全过”来写。v1 有两条补充项未通过，并记录了两处对结论不利的发现：对照组在无角色设定时仍拒绝了第 6、7 轮，说明该两项通过主要来自基座模型而非提示词；LLM 评审对弱提示词会给出饱和的 40/40。
