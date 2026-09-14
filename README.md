# inference-engineering-learning-journal

# ToDo
> three lab
> -tinyLLLM
> -minisglang
> -nanovllm

# Pending
> CS336 Lab1

# Goal
> Build mental model first

# Learning approach
> I use small inference systems to build a systems-level mental model before going deep into theory.
> I trace the end-to-end request lifecycle, identify core state transitions, and test my understanding by asking where the system can fail.
> I also map unfamiliar inference mechanisms to systems I already know, such as Kafka, Spring, producer-consumer patterns, and distributed state management.
The detailed notes below are written in Chinese for learning speed.





# Mini-SGLang 主链路 · 第一周阅读计划 + 懂/不懂/坏点笔记 (v2)

> 源码根目录:`python/minisgl/`
> 全程在本地读代码即可,不用配 GPU 环境。
> 每天读完,填四栏:✅ 我懂了 / ❓ 我卡住的具体函数或概念 / 🔗 我查了什么 / 🔥 故障假设。
>
> ⚠️ 四栏是原料,不是成品。真正给 hiring manager / 群里的人看的,是每周末的
> **「本周认知转变」**和**「与我熟悉系统的类比」**(见每周末的合成区)。
> 写「我原来以为…,后来发现…,因为…」和「这块本质上和 Kafka/Cassandra 的 X 是同一类问题」,
> 这两种东西 agent 生成不出、别人 copy 不走,是你唯一的真壁垒。

> **关于新加的 🔥 故障假设栏(v2 新增)**:
> "能读懂"和"能预判"之间的距离,比主观感觉大得多。读代码没有反馈机制——每行都认识
> 就会产生"懂了"的错觉,而这个错觉测的是语法流畅度,不是机制理解。
> 以后判断自己懂不懂,标准换成:**能不能说出它在什么情况下坏掉**。
> 这一栏不要求你现在就能答对——记录"我猜会坏在哪,但不确定"就是有效产出,
> 比"我看懂了作者意图"更接近你实际要练的能力。

---

## 贯穿全周的锚:一个请求的生命周期

```
HTTP 进来 → 分词(tokenize)→ 调度(匹配缓存、分页)
   → prefill(算首 token)→ decode(逐 token 生成)
   → 反分词(detokenize)→ 流式返回
```

对应文件:

1. Request Reception —— `server/api_server.py`(`FrontendManager`)
2. Tokenization —— `tokenizer.py`(`tokenize_worker`)
3. Scheduling —— `scheduler/scheduler.py`(`Scheduler`)
4. Prefill —— `scheduler/prefill_manager.py`
5. Decode —— `scheduler/decode_manager.py`
6. Detokenization —— `tokenizer.py`(`detokenize_worker`)
7. Response Streaming —— `server/api_server.py`

**每天读的模块,都往这条链上挂,别孤立地看。**

---

## Day 0(半天,预热)

**读什么**

- `README.md`
- `docs/structures.md`
- clone 到本地,用编辑器打开 `python/minisgl/`

**目标**:对着上面的生命周期,能说出每一步落在哪个文件。

- ✅ 我懂了:
- ❓ 我卡住的:
- 🔗 我查了:
- 🔥 故障假设:(这天先不强求,建立整体地图为主)

---

## Day 1 — 入口与消息(强项区,先建立信心)

**读什么**

- `server/api_server.py` —— FastAPI 入口、`FrontendManager`
- `message.py` —— ZMQ 消息定义:`TokenizeMsg` / `UserMsg` / `DetokenizeMsg` / `UserReply` / `AbortMsg`

**目标**:一个请求进来后被包成了什么消息、发给了谁。

**对比你熟的**:这就是 Web 入口 + 进程间消息传递。

- ✅ 我懂了:
- ❓ 我卡住的:
- 🔗 我查了:
- 🔥 故障假设:
  - 如果客户端在请求发出后立刻断连,`AbortMsg` 是谁负责发出的?后续消息还会不会继续处理?
  - 如果同一个请求的消息在链路中重复投递一次,会不会被处理两次?(对照 Spring webhook 里 `eventId` 去重那道题)

---

## Day 2 — 进程编排与通信骨架(本周重点,兼补并发基础)

**读什么**

- `server/`(`launch_server`)—— 怎么 spawn 出 API / tokenizer / scheduler 三类进程,用 `ack_queue` 同步
- `utils`(`ZmqPushQueue` / `ZmqPullQueue`)

**目标**:搞懂它为什么用多进程 + ZMQ,而不是单进程。

**对比你熟的**:Kafka 生产者-消费者、微服务拆分。← 这段是笔记里最有差异化亮点的地方,多写。

**这天顺带练的**:这本质上是个跨进程的生产者-消费者队列,和 Spring 项目里
"消息会不会丢/会不会乱序/需不需要幂等"是同一类问题,只是换了个马甲。
把这天当成补并发/分布式基础的落地练习,比抽象学 `ExecutorService` 效率更高。

- ✅ 我懂了:
- ❓ 我卡住的:
- 🔗 我查了:
- 🔥 故障假设:
  - `ZmqPushQueue`/`ZmqPullQueue` 有没有 ack 机制?如果没有,消息丢了谁会发现?
  - 为什么单机内部的 ZMQ 通信不需要像 Kafka 那样搞幂等/去重?这个"可以不做"的假设,
    成立的边界在哪里(比如换成多机会不会立刻破功)?
  - `ack_queue` 用来同步三类进程的启动,如果某个进程起晚了/挂了,别的进程会不会卡死等待?
  - 三个进程之一(比如 scheduler)崩溃重启,内存里的状态(比如正在处理的 batch)怎么办?

---

## Day 3 — 核心数据结构(读代码的地基)

**读什么**

- `core` —— `Req`(单请求状态)、`Batch`(一批请求)、`Context`(全局推理状态,单例,持有 page_table / kv_cache / attn_backend)、`SamplingParams`

**目标**:不追流程,只搞懂"数据长什么样"。后面所有模块都在操作这几个对象。

- ✅ 我懂了:
- ❓ 我卡住的:
- 🔗 我查了:
- 🔥 故障假设:
  - `Context` 是单例、全局持有 kv_cache,如果两个不同的调度循环(或未来加并发)同时读写它,
    有没有锁保护?
  - 一个 `Req` 被放进多个 `Batch` 会不会导致状态不一致?

---

## Day 4 — 调度器主循环(全项目的心脏)

**读什么**

- `scheduler/scheduler.py` —— `run_forever()`、`normal_loop()`
- `overlap_loop()` 标记「待第二遍」,先跳过

**目标**:看懂调度器怎么不停地「取请求 → 组 batch → 交给 engine → 收结果」。

**对比你熟的**:事件循环 / 消费循环。

- ✅ 我懂了:
- ❓ 我卡住的:
- 🔗 我查了:
- 🔥 故障假设:
  - 两个请求同时被组进同一个 batch,其中一个中途被 abort,另一个会不会受影响?
  - `normal_loop()` 正在处理当前 batch 时,新请求进来了,会插队还是等下一轮?插队逻辑会不会
    导致某类请求永远排不上号(饿死问题)?
  - 如果 engine 处理某个 batch 时抛异常,整个 loop 会崩掉,还是只丢这一个 batch?

---

## Day 5 — Prefill 与 Decode 两阶段(LLM serving 的核心概念)

**读什么**

- `scheduler/prefill_manager.py` —— `add_one_req`、`schedule_next_batch`
- `scheduler/decode_manager.py`

**目标**:用自己的话讲清「为什么推理要分 prefill / decode 两个阶段」。

- prefill:并行处理整段输入,算出首 token
- decode:之后逐个 token 生成

这是 LLM serving 区别于普通后端的核心,务必在笔记里讲透。

- ✅ 我懂了:
- ❓ 我卡住的:
- 🔗 我查了:
- 🔥 故障假设:
  - 一个请求在 prefill 阶段中途被 abort,已经分配的 KV cache page 会不会泄漏(没被释放)?
  - `schedule_next_batch` 如果同时把多个长请求塞进一个 batch,显存不够会怎样——是拒绝、
    排队,还是直接 OOM?

---

## Day 6 — 引擎与一次前向(开始碰新东西)

**读什么**

- `engine/` —— `Engine.forward_batch()` → `ForwardOutput`
- `Sampler` —— 怎么从 logits 采样出下一个 token
- CUDA graph / `GraphRunner` 先跳过

**目标**:把「engine 拿到一个 batch 后做了什么」的主干串起来。
弱项区,读不顺正常,细节标进「不懂」栏即可。

- ✅ 我懂了:
- ❓ 我卡住的:
- 🔗 我查了:
- 🔥 故障假设:
  - `forward_batch()` 里如果某一个请求的输入长度异常(比如 0 长度或超长),会不会拖垮整个
    batch 的前向计算?
  - 采样阶段(`Sampler`)出现 NaN/Inf logits,后续流程会怎样处理,还是直接崩?

---

## Day 7 — 回顾 + 扫 attention/kvcache 概念(不深钻,只做一件事)

**做两件事**

1. 把整周笔记串成完整生命周期,自己讲一遍(能讲通 = 这周成功)
2. 只从概念层扫一眼:
   - `attention/` —— `BaseAttnBackend` 及 fa/fi 后端接口长啥样
   - `kvcache/` —— KV cache 是个 `[2, num_layers, num_pages, page_size, num_kv_heads, head_dim]` 的大张量 + 分页表

**这天只做一件事(v2 降低预期)**:不深入 attention 计算本身,只搞清楚
**KV cache 的分页表和"锁/竞态"有没有关系**——比如两个请求同时申请 page 会不会冲突,
`ref_count` 本质上是不是就是一个需要加锁保护的引用计数器。这部分留个印象即可,
attention 计算细节留给第二周或见朋友时问。

- ✅ 我懂了:
- ❓ 我卡住的:
- 🔗 我查了:
- 🔥 故障假设:
  - 两个请求同时申请同一批空闲 page,分配逻辑有没有加锁?如果没锁,单进程内为什么"恰好"不会出问题?
  - `ref_count` 减到 0 但忘记回收会怎样(page 泄漏)?

---

## 🧠 周末合成区(把一周的原料熬成文章素材)

> 这是全份文档最重要的部分。四栏笔记是流水账,证明你勤奋——但勤奋在 agent 时代
> 不加分。下面几栏证明你有「原理判断」和「跨领域迁移」的脑子,这才是 hiring manager
> 赌一个 0-YoE 的人时真正想买的东西,也是你在 500 人核心群里从「脸熟」变「被认可」的货币。
> **每周末强制写满,哪怕只有一条,只要是真的。**

### 本周认知转变(格式:我原来以为 X,后来发现 Y,因为 Z)

> 例:我原来以为 KV cache 就是「把算过的存下来省得重算」,后来发现它的分页设计
> 其实是为了解决「不同请求长度不一、显存碎片化」的问题,因为固定大小的 page 才能
> 像操作系统的虚拟内存一样灵活分配和复用——这一步我卡了很久,直到用 OS 分页去类比才想通。

1.
2.
3.

### 与我熟悉系统的类比(我的独家签名,别人写不出)

> 每条格式:mini-sglang 的 【X】,本质上和 【Kafka/Cassandra/Spring 的 Y】是同一类问题,
> 区别在于 【Z】。
> 这一栏同时干三件事:证明我真懂了新东西 + 证明我有可迁移的老底子 + 证明我能跨领域连接。

1.
2.
3.

### 本周从「故障假设」栏里挑出的最有价值的一条

> 这一栏是 v2 新增的合成项,专门筛选四栏笔记里"故障假设"那栏的产出。
> 格式:我猜测 【场景】 会导致 【问题】,后来验证发现 【结果】,这说明 【设计取舍】。
> 不需要每条都验证对——猜错了、去读源码或问人后发现"其实有保护机制,机制是 X",
> 本身就是有价值的记录。

1.

### 本周我形成的一个「观点」(不是知识复述,是立场)

> 例:读完调度这块,我认为 mini-sglang 把复杂度主要压在了 scheduler 上,
> 用「进程隔离 + 消息传递」换来了可读性,代价是跨进程的调试变难——这是个我认同的取舍,因为…

1.

### 诚实的边界(我目前还不懂的,及下一步计划)

> 诚实标注反而加分:展示成熟的自我认知和学习规划。假装全懂会被一眼看穿。

1.

---

## ✍️ 最终总结文章 · 骨架(边读边往里填,读完就成文)

1. **为什么读它**:从 30 万行 SGLang 到 5k 行的动机(一段)
2. **一个请求的旅程**:主链路流程图 —— 全文主线
3. **让我卡住又想通的三个点**:直接搬「本周认知转变」里最好的三条
4. **用我的分布式底子重新理解它**:搬「与我熟悉系统的类比」里最强的两三条 ← 差异化核心
5. **它什么时候会坏**:搬「故障假设」栏里验证过的一两条 ← v2 新增,体现"预判"而非"读懂"
6. **我的一个观点**:对现代 LLM 推理引擎复杂度来源的判断(搬「观点」栏)
7. **我还不懂的**:诚实收尾,列留给下一遍的问题

> 提醒:这篇文章真正发力的场景是**内推时随简历一起递**,或**面试里被引用**。
> 它让内推更有底气(朋友能说「这人认真啃了推理引擎还写了深度分析」),
> 内推让文章有机会被读到。文章 + 内推是一套,不是两件独立的事。

---

## 第二周预告(硬骨头,带着问题去见朋友后再啃)

- attention 实现(FlashAttention / FlashInfer 后端)
- KV cache 分页细节、`RadixCacheManager` 前缀树
- Tensor Parallelism(`distributed/`:all_reduce / all_gather)
- Overlap Scheduling(`overlap_loop`)、CUDA Graph
- `kernel/`:自定义 CUDA / Triton kernel

---

## 攒给「懂/不懂」文章的素材(随时往这里丢)

**可以和朋友深聊的点**(attention / KV cache / kernel / PyTorch):
-

**能和我熟悉的系统对比的点**(Kafka / Spring / 分布式):
-

**仍然完全不懂、留给下一遍的**:
-

---



### 我自己要想清楚的

- [ ] 我到底愿不愿意为 inference 转去啃 C++/CUDA/嵌入式?还是先在 Python 层(SGLang 生态)站稳?
