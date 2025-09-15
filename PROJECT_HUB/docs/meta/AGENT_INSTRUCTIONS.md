---
title: "Agent Instructions"
created: "2025-09-15T00:08:01.041612Z"
author: "system-cleanup"
topics: ["meta"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# HAK/GAL System - Instructions for AI Agents

## 1. Welcome & Your Context

Welcome, agent. You have been invoked to perform a task within the HAK/GAL system.

Your execution is automatically enriched with a two-tiered context system to guide you:

1.  **Global Context (`ssot.md`):** Contains universal principles, architectural facts, and goals for the entire system. This is your foundational knowledge.
2.  **Specific Context (`claude.md`, `deepseek.md`, etc.):** Contains information about your specific role, strengths, and unique instructions. This defines your "niche".

You must adhere to the principles and roles defined in the context provided with your task prompt.

## 2. Your Primary Tool: The Gemini Bridge

You do not have direct access to a shell. Your primary interface for interacting with the system and the user is the `gemini_bridge.py` script. It provides the essential functionalities you need.

### Available Commands:

**A) Sending a Message / Asking a Question:**
To communicate, ask for clarification, or deliver a text-based result, use the `--message` flag.

*Example:*
```bash
python gemini_bridge.py --message "I have analyzed the code and here is my report: ..."
```

**B) Executing Code:**
To test a hypothesis, run a calculation, or verify a piece of code, use the `--execute` flag. The bridge can execute Python, JavaScript, Bash, and PowerShell.

*Example:*
```bash
python gemini_bridge.py --execute "for i in range(5): print(i)"
```
The bridge will return a JSON object containing the `stdout`, `stderr`, and `returncode` of the execution.

## 3. Standard Operating Procedure

1.  **Analyze:** Carefully read the user's request and the entire context provided to you.
2.  **Plan:** Formulate a step-by-step plan. Decide if you need to execute code to gather more information or if you can answer directly.
3.  **Execute:** Use the `gemini_bridge.py` tool to carry out your plan. Use `--execute` for tests and `--message` for communication.
4.  **Report:** Deliver your final, complete answer using the `--message` command.
