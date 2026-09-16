# Day 0916 — setup and roadmap

## Goal

重新制定了目标 6个月后找到一份inference sglang相关的junior entry level

确定了学习资料和路线（尤其确定了不学哪些）

加入了社区群

用AWS EC2租GPU，云端跑

今天先用两个材料读理论。公式部分都可以跳过

zero to sglang刚开始写，同步加入社区群

part1的公式部分暂时不用管

Random-Liu的讲述方式就没有没用的公式，但这个缺少lab

## What I Read



## 30 天具体计划

| 时间             | 主线                      | 具体材料                                                     | 你实际要做什么                                               | 到什么程度算过关                                             |
| ---------------- | ------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **Day 1–5**      | 建 inference mental model | `Random-Liu/llm-inference-principle-to-production` **Part 1 Ch1–3 + Part 2 Ch4–8** | 看 QKV、autoregressive generation、prefill/decode、KV cache、batching、memory bandwidth | 不看资料能解释：`prompt → prefill → KV → decode → next token`；能解释为什么 KV cache 存 K/V、为什么 decode memory-bound |
| **Day 1–7 同步** | 第一次进入 Mini-SGLang    | `sgl-project/mini-sglang`：`docs/structures.md`、`core.py`、server/tokenizer/message/scheduler 的入口 | 只追 **一条 request lifecycle**，不要研究优化                | 能自己画出：`API → tokenizer → scheduler → engine → detokenizer → stream`；知道 `Req / Batch / Scheduler / Engine` 大概分别是谁 |
| **Day 4–8**      | Git + upstream workflow   | Mini-SGLang repo                                             | fork、clone、设置 `origin/upstream`、branch、diff、commit、push、PR；如果阅读时自然发现真实 typo/docs error，可以作为第一 PR | 能从 mental model 解释 `HEAD / branch / origin / upstream / commit / PR`，而不是只会背命令 |
| **Day 8–14**     | 深入 Scheduler            | `python/minisgl/scheduler/scheduler.py`、`io.py`、`config.py`、`utils.py`、`prefill.py` + 理论书 **Ch13 Continuous Batching / Chunked Prefill** | 从 request 进入 scheduler 开始追：什么时候能进 batch、token budget 在控制什么、prefill 为什么要调度 | 能回答：“scheduler 每一步在优化哪几种有限资源？”、“为什么不能来一个 request 就立刻 forward？” |
| **Day 15–20**    | KV Cache 主线             | 理论书 **Ch11 PagedAttention、Ch12 RadixAttention、Ch14 Preemption/Scheduling**；Mini-SGLang `kvcache/base.py → mha_pool.py → naive_cache.py → radix_cache.py` | **先 naive，再 radix**。搞清 pool vs manager、allocation/free、prefix reuse | 能画出 request 和 KV memory 的生命周期；能说明 naive cache 和 radix cache 的根本区别。Mini-SGLang 当前 cache 目录确实分成 base、MHA pool、naive 和 radix 实现。 |
| **Day 18–22**    | Tiny-LLM 只补洞           | `skyzh/tiny-llm`：优先 **2.1 KV Cache、3.1 Continuous Batching、3.2 Chunked Prefill、3.3 Paged KV Cache** | **不是整门课做完**。Mini-SGLang 哪块仍然抽象，就去看/做相应 lab | 做完后再回 Mini-SGLang，同一概念明显能映射到源码即可。Tiny-LLM 本身的 Week 3 就是 continuous batching → chunked prefill → paged KV。 |
| **Day 21–25**    | 第二遍读 Mini-SGLang      | `core.py → scheduler → prefill → kvcache → engine`           | 这次不追“每行是什么意思”，而追 **state + invariant**         | 能预测：某个 request 长 prompt、cache 不足、新 request 插入时，大概哪一层负责处理 |
| **Day 26–28**    | 第二实现对照              | `GeeeekExplorer/nano-vllm`：`engine/sequence.py`、`scheduler.py`、`block_manager.py`、`llm_engine.py` | 只比较三个问题：request state、scheduler、KV/block management | 能写出至少 3 个“共同本质”和 3 个“implementation choice”。nano-vLLM 只有约 1,200 行 Python，而且 engine 正好把 sequence、scheduler、block manager 分开。 |
| **Day 29–30**    | 整合                      | 回到 Mini-SGLang                                             | 不看笔记，从头讲一次系统；整理一篇自己的 architecture note   | 能在 20–30 分钟内从 API request 一路讲到 scheduler/KV/model execution；明确列出下个月仍然不懂的 5 个问题 |

## ✅ What I Understand

## ❓ What I Don't Understand

## 🔥 Failure Hypotheses

## 🔗 Systems Analogy

## 🧠 Mental Model Update