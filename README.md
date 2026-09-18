# Inference Engineering Learning Journal

This repository documents my hands-on learning process in **LLM inference engineering**.

I am using small, readable inference systems to understand how modern LLM serving works from the inside out — from attention and model execution to KV cache, batching, scheduling, and distributed serving.

## Repository Structure

### `DailyLogs`

Daily records of what I studied, implemented, debugged, and understood.

These notes preserve the **learning process**, including:

* questions I encountered
* experiments and debugging
* code-reading observations
* changes in my mental model
* connections between new concepts and systems I already know

Think of this folder as the chronological learning trace.

---

### `TopicNotes`

Structured notes organized by concept rather than by date.

This folder consolidates ideas that first appeared across different daily logs into reusable explanations, such as:

* attention
* tensor shapes
* KV cache
* batching
* scheduling
* model execution
* inference system architecture

Think of this folder as the **conceptual knowledge base** built from the DailyLogs.

---

### `Labs`

Hands-on implementations and exercises from small inference systems.

The goal is not only to read about inference mechanisms, but to implement them, run tests, inspect tensor/state transitions, and connect individual components to the end-to-end inference lifecycle.

Current / planned labs include:

* `tiny-llm`
* `Mini-SGLang`
* `nano-vLLM`

Think of this folder as the **implementation layer** of the journal.

---

## Current Focus

Build a strong systems-level mental model of LLM inference before going deep into optimization details.

I am currently focusing on understanding the path from:

`request → tokenization → model execution → attention → KV cache → decoding → scheduling → output`

and gradually connecting these components to real inference engines such as SGLang and vLLM.

## Learning Approach

I use small inference systems to build a systems-level mental model before going deep into theory.

I trace the end-to-end request lifecycle, identify core state transitions, and test my understanding by asking where the system can fail.

I also map unfamiliar inference mechanisms to systems I already know, such as Kafka, Spring, producer-consumer patterns, caching, queues, and distributed state management.

My learning loop is roughly:

`read → trace → implement → test → explain → consolidate`

`DailyLogs` capture the process, `TopicNotes` capture the resulting mental models, and `Labs` verify those models through implementation.

## Roadmap

### In Progress

* Tiny LLM
* Mini-SGLang
* nano-vLLM

### Pending

* Stanford CS336 Assignment 1

## Notes

Detailed learning notes are primarily written in Chinese so I can reason and iterate quickly.

Code, repository structure, and higher-level summaries are kept accessible for readers interested in following the learning process.
