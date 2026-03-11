---
name: read-arxiv-paper
description: Use this skill when asked to read, analyze, or summarize an arxiv paper given an arxiv URL or paper ID. Also triggered when processing papers from daily research reports. **每次只精读一篇论文**，严禁批量精读。
---

# Read & Analyze arXiv Paper

This skill deeply reads an arXiv paper and produces a structured knowledge card, tailored for a PhD researcher in **Generative Recommendation & LLM** fields.

> **🌐 语言要求**：知识卡片中所有自然语言内容（TL;DR、贡献总结、方法描述、实验分析、评论等）**必须使用中文**撰写。仅 BibTeX、论文标题原文、专有术语等保留英文。

---

## ⚠️ 关键规则：严格单篇精读 & 质量守卫

### 规则 1：一次只精读一篇论文

- **每次对话只处理一篇论文**。如果用户要求批量精读多篇论文，**必须拒绝**并建议用户逐篇提交。
- 回复示例："为保证精读质量，建议每次对话只精读一篇论文。请先告诉我要精读哪一篇，其余论文可以在后续对话中逐一精读。"
- 唯一例外：用户明确只需要"速览/快速总结"（非精读）时，可以处理多篇，但此时不生成完整知识卡片。

### 规则 2：反省略质量守卫

- **禁止跳过或省略论文的任何关键章节**。必须完整阅读 Abstract、Introduction、Method、Experiments、Conclusion 五个核心部分。
- **禁止因上下文空间不足而默默降低输出质量**。如果发现论文内容过长（如单文件 > 100KB），应主动告知用户并采取以下策略：
  1. 优先完整读取 Method 和 Experiments 部分
  2. 对 Related Work 可以略读
  3. 但**绝不能跳过实验结果表格和消融实验**
- 知识卡片的每个章节都必须包含**具体的、有实质内容的信息**，禁止使用笼统的概括性语句代替具体描述。
- 如果某个章节确实无法填充（如论文没有消融实验），显式标注"论文未提供"，而不是默默跳过。

---

## Part 1: Identify the Paper

You will receive one of:
- A full arXiv URL: `https://arxiv.org/abs/2501.07372`
- A short arXiv ID: `2501.07372`
- A paper entry from a daily report (which already contains title, authors, abstract)

Normalize to extract the `arxiv_id` (e.g., `2501.07372`).

**Detect if it's a top-lab paper** (auto deep-read regardless of score):
- Top labs include: Google DeepMind, Google Brain, OpenAI, Meta AI (FAIR), Microsoft Research, Apple ML, Anthropic, Mistral, Cohere, Amazon Science, Alibaba DAMO/Tongyi, Tencent AI Lab, ByteDance Research, Baidu Research, Huawei Noah's Ark, Salesforce Research, Adobe Research, NVIDIA Research, CMU, MIT, Stanford, Berkeley, Oxford, Cambridge, ETH Zurich, Tsinghua, PKU, Zhejiang University, SJTU, Fudan, RUC, USTC, NUS, NTU
- If the paper is from any of the above, mark it as `[TOP-LAB]` and proceed to full deep-read unconditionally.

---

## Part 2: Download the Paper Source

### Step 2a: Try TeX source first (preferred)

```bash
# Download TeX source
ARXIV_ID="2501.07372"
CACHE_DIR="/data/workspace/research/cache/${ARXIV_ID}"
mkdir -p "${CACHE_DIR}"

# Check if already downloaded
if [ ! -f "${CACHE_DIR}/source.tar.gz" ]; then
    curl -L "https://arxiv.org/src/${ARXIV_ID}" -o "${CACHE_DIR}/source.tar.gz"
fi

# Unpack
cd "${CACHE_DIR}" && tar -xzf source.tar.gz 2>/dev/null || true
```

### Step 2b: Fallback to PDF if TeX source unavailable

```bash
# If TeX source extraction fails or yields no .tex files, download PDF
if [ ! -f "${CACHE_DIR}/paper.pdf" ]; then
    curl -L "https://arxiv.org/pdf/${ARXIV_ID}" -o "${CACHE_DIR}/paper.pdf"
fi
```

**Cache location**: `/data/workspace/research/cache/{arxiv_id}/`
- If the directory already exists and contains files, skip downloading.

---

## Part 3: Read the Paper

### For TeX source:
1. Find the entrypoint: look for `main.tex`, or the `.tex` file that contains `\documentclass`
2. Read the entrypoint file fully
3. Recursively follow `\input{}` and `\include{}` directives to read all sections
4. Pay special attention to: Abstract, Introduction, Related Work, Method/Model, Experiments, Conclusion

### For PDF:
- Use the pdf skill or direct text extraction to read the content
- Focus on the same sections as above

### Reading priority order:
1. **Abstract** — core contribution in one paragraph
2. **Introduction** — motivation, problem statement, key claims
3. **Method / Model** — architecture, training strategy, key innovations
4. **Experiments** — datasets, baselines, metrics, key results
5. **Related Work** — positioning in the field
6. **Conclusion / Future Work** — limitations and open problems

---

## Part 4: Generate Knowledge Card

Save the knowledge card to **two locations**:

### Location 1: Local project knowledge base
```
/data/workspace/research/papers/{sub_field}/{arxiv_id}_{tag}/
├── card.md          # The knowledge card (main output)
└── source/          # Symlink or copy of downloaded source
```

### Location 2: Cache reference
The downloaded source stays at `/data/workspace/research/cache/{arxiv_id}/`

**Determine `sub_field`** based on paper content:

### Track A — Generative Recommendation Core
- `generative_rec` — end-to-end generative recommendation, sequential generation of item IDs
- `tokenization_and_decoding` — item tokenization (RQ-VAE, RQ-KMeans, Semantic IDs), constrained decoding, trie-based decoding, hallucination mitigation in generation
- `alignment_and_sft_rec` — aligning LLMs to recommendation objectives via SFT, RLHF, DPO, GRPO; reward modeling for rec
- `hybrid_id_text_rec` — fusing collaborative CF signals (ID embeddings) with LLMs via soft prompts, cross-attention, graph+LLM; bridging traditional rec and generative rec
- `llm_as_ranker` — LLM-based listwise/pairwise reranking over candidate sets, position bias elimination, discriminative rec

### Track B — Breakout Technologies
- `agentic_and_simulation` — recommendation as interactive agent, LLM-based user behavior simulation, data augmentation via LLM
- `rag_for_rec` — retrieval-augmented recommendation, knowledge injection for cold-start and freshness; focus on information retrieval side (distinct from agentic)
- `llm_reasoning_core` — pure LLM advances: architecture evolution, o1-style CoT, long-context, efficiency (MoE, quantization); potential to transfer into rec
- `other_exploratory` — multimodal recommendation, diffusion-based rec, early-stage emerging directions

**Generate `tag`**: a short snake_case descriptor of the paper's core idea, e.g., `llm_as_reranker`, `diffusion_rec`, `chain_of_thought_rec`. Make sure the tag doesn't already exist in the target directory.

---

## Part 5: Knowledge Card Template

The card must follow this exact structure:

```markdown
# {Paper Title}

**arXiv ID**: {arxiv_id}  
**Authors**: {authors}  
**Affiliation**: {affiliation} {[TOP-LAB] if applicable}  
**Published**: {date}  
**Sub-field**: {sub_field}  
**Tag**: {tag}  
**Source**: https://arxiv.org/abs/{arxiv_id}  
**Local Source**: /data/workspace/research/cache/{arxiv_id}/  

---

## TL;DR
> One sentence: what does this paper do and why does it matter?

---

## ELI5 — 通俗易懂讲解

> **写作要求**：假设读者是一名刚入学的、对该领域一无所知的博士生。用最日常的语言、类比和例子，**详细**讲清楚这篇论文在做什么、为什么要做、怎么做的。禁止使用未经解释的术语。越通俗越好，但不能丢失关键信息。长度不限，务必讲透。

### 这篇论文想解决什么问题？
{用生活化的类比解释问题背景和动机，比如"你去饭店点菜……"这种日常场景引入}

### 它提出了什么解决方案？
{用最直白的语言讲清楚方法的核心思路，避免任何公式，纯靠比喻和逻辑}

### 具体是怎么做的？
{分步骤讲清楚方法流程，每一步都用类比或实例辅助理解。如果方法分多个阶段，逐阶段讲}

### 效果怎么样？
{用最直观的方式讲清楚实验结论：比如"比之前最好的方法好了 XX%"，"在真实线上环境赚钱多了 XX%"}

### 有什么不足？
{用大白话讲清楚局限性}

---

## Core Contributions
1. {contribution 1}
2. {contribution 2}
3. {contribution 3 if any}

---

## Problem Definition
- **Task**: What exact task is being solved?
- **Input / Output**: What goes in, what comes out?
- **Key Challenge**: What makes this hard?

---

## Method & Architecture
### Overview
{High-level description of the approach}

### Key Components
- **{Component 1}**: {description}
- **{Component 2}**: {description}
- ...

### Training Strategy
- Loss function(s):
- Training data:
- Special techniques (e.g., instruction tuning, RLHF, contrastive learning):

### Key Formula — 沿方法流程的逐公式拆解

> **写作要求（极其重要）**：
> 
> **禁止**把公式一个个孤立地罗列出来。必须**按方法的执行流程分阶段组织**公式讲解，让读者始终知道"我现在在方法的哪一步"、"这个公式在这一步扮演什么角色"、"它和上一个公式是什么关系"。
> 
> 具体格式要求：
> 1. 先按方法流程划分若干**阶段**（如「阶段一：数据预处理」「阶段二：SFT 训练」「阶段三：RL 优化」「阶段四：推理」等），阶段名来自方法本身
> 2. 每个阶段开头，用 2-3 句话交代**这个阶段在做什么、目标是什么、和上一阶段的关系**
> 3. 在阶段内部，按该阶段涉及的公式逐个讲解。每个公式前，用一句话说明**这个公式在本阶段的角色**（如"这是本阶段的损失函数"、"这是奖励信号的定义"、"这个公式实现了上面提到的XXX"）
> 4. 对每个公式：(a) LaTeX 写出公式 (b) 符号说明 (c) 直觉解释 (d) 设计动机
> 5. 阶段之间用分割线隔开，保持流程的连贯性

#### 阶段一：{阶段名}
{2-3句话：这个阶段在做什么，目标是什么}

**公式 1（{角色描述，如"本阶段的核心量化公式"}）：**

$$
{formula_1}
$$

**符号说明**：
- $symbol_1$：...

**直觉解释**：{用通俗语言解释这个公式在做什么}

**设计动机**：{为什么要这样设计}

---

#### 阶段二：{阶段名}
{2-3句话：从上一阶段过渡到这个阶段，目标是什么}

**公式 2（{角色描述}）：**
...

{以此类推，直到所有核心公式覆盖完毕}

---

## Experiments
| Dataset | Baselines | Key Metric | Result |
|---------|-----------|------------|--------|
| {ds1}   | {b1, b2}  | {metric}   | {gain} |

**Key Findings**:
- {finding 1}
- {finding 2}

**Ablation Highlights**:
- {what component matters most}

---

## Limitations & Open Problems
- {limitation 1}
- {limitation 2}

---

## Relevance to Generative Recommendation Research

### Direct Connection
{How does this paper directly relate to generative recommendation or LLM-based rec?}

### Potential Baselines
{Could this paper's model serve as a baseline in your work? Which datasets/settings?}

### Transferable Techniques
{What specific techniques, losses, architectures, or training strategies could be borrowed?}

### Inspiration & Ideas
{What new research directions or hypotheses does this paper inspire?}
- Idea 1: ...
- Idea 2: ...

### Gap / Critique
{What does this paper NOT solve? What's the next step?}

---

## BibTeX
```bibtex
@{entry_type}{cite_key},
  title     = {{Paper Title}},
  author    = {Author1 and Author2 and Author3},
  journal   = {arXiv preprint arXiv:{arxiv_id}},
  year      = {YYYY},
  url       = {https://arxiv.org/abs/{arxiv_id}},
  note      = {Accepted at {Venue} {Year} if applicable},
}
```

---

## Personal Notes
<!-- Fill in manually -->

---

## Reading Date
{YYYY-MM-DD}
```

---

## Part 6: Update SOUL Files

After generating the knowledge card, **always** update the following two SOUL files:

### 6.1 Update `insights.md` — `/data/workspace/research/SOUL/insights.md`

1. Read the current file
2. If this paper introduces a genuinely new insight, technique, or perspective relevant to generative recommendation, add it to the appropriate section
3. If it reinforces or refines an existing insight, update that entry
4. Keep it as distilled wisdom — not a paper list, but your highest-level understanding

### 6.2 Update `challenge.md` — `/data/workspace/research/SOUL/challenge.md`

This file tracks **open problems, unresolved tensions, and hard challenges** in the field as revealed by your reading.

1. Read the current `challenge.md`
2. If this paper explicitly identifies an unsolved problem, or if your reading reveals a gap/contradiction not yet captured, add a new entry under the appropriate section
3. If this paper partially addresses an existing challenge, update that entry's status
4. Structure of each entry:
   - **Challenge**: one-sentence description of the open problem
   - **Why Hard**: root cause or technical barrier
   - **Current Best Attempt**: best known approach (cite paper if applicable)
   - **Status**: `Open` / `Partially Addressed` / `Solved`
   - **Source Papers**: arXiv IDs that surface this challenge

See the `research-soul` skill for full SOUL file structure details.

---

## Execution Notes

- Always check `/data/workspace/research/cache` before downloading
- If TeX source tar.gz exists but extraction fails (some papers use zip), try `unzip` as fallback
- For very long papers, prioritize reading Method + Experiments sections most carefully
- When reading TeX, skip purely formatting/style files (`.sty`, `.cls`) unless they contain algorithm definitions
- The knowledge card should be **opinionated** — don't just summarize, evaluate and connect
- **所有知识卡片的自然语言内容使用中文**，包括 TL;DR、贡献、方法描述、实验分析、局限性、与生成式推荐的关联分析等
- **单篇精读，绝不批量**：如果用户在一次对话中提出多篇精读请求，只处理第一篇，其余提示用户开新对话
- **质量优先**：宁可告诉用户"这篇论文太长，我需要分段阅读"，也不要默默省略内容
