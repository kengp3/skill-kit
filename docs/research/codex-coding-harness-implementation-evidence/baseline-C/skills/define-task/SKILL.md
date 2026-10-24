---
name: define-task
description: Turn vague or high-cost work into a clear task brief before execution. Use when the user wants to define a task, write a brief, clarify handoff instructions for AI or teammates, avoid rework on complex work, decide what information is missing before starting, or convert a fuzzy request into Objective, Background, Materials, Boundaries, optional Assumptions, and Definition of Done. Do not use as the primary skill for simple prompt wording, rewriting, polishing, or style optimization unless the user explicitly wants to redefine the underlying task.
---

# Define Task

## Purpose

Help the user define the work before doing the work. Treat task definition as a thinking and communication exercise, not prompt decoration.

The goal is to make a smart collaborator understand what outcome is needed, why it matters, what evidence to use, what limits to respect, and how done will be judged.

## Workflow

### 1. Identify the task stage

Classify the request before producing output:

- **Thinking**: The user is still trying to understand the problem.
- **Exploration**: The user needs options, tradeoffs, or possible directions.
- **Decision**: The user has options and needs a recommendation or decision logic.
- **Execution**: The user is ready to hand work to AI, a teammate, or a future session.

If the request is not yet in the execution stage, do not force a full brief. Help with the current stage first:

- Thinking: restate the problem and surface assumptions. Ask exactly one critical clarifying question only when a missing detail would materially change the task and cannot be verified or safely assumed. Do not bundle multiple missing details into one question.
- Exploration: list viable options with concrete tradeoffs.
- Decision: define the decision criteria, compare options, and recommend when evidence is sufficient.
- Execution: create or refine the brief.

### 2. Estimate rework cost

Use a full brief when the user explicitly requests one, or when the task is ready for handoff and getting it wrong would be expensive. Examples of high rework cost include stakeholder handoffs, implementation, research, strategy, analysis, and reusable deliverables.

For low-cost requests without an explicit request for a full brief, include only the fields needed to communicate the task. For earlier stages, continue helping with the current stage rather than forcing a handoff document.

### 3. Build the brief

When a full brief is warranted under step 2, use these fields. Otherwise, keep the output lightweight:

```markdown
## Objective
[What the output will be used for, what decision it supports, and what success should enable.]

## Background
[Relevant context, current situation, history, constraints, prior failed attempts, audience, and stakes.]

## Materials
[Primary sources, secondary sources, files, links, datasets, examples, and source rules. State what sources must not be used or invented.]

## Boundaries
[What not to do, touch, assume, change, recommend, or include.]

## Assumptions
[Only assumptions that materially affect scope, approach, or outcome. Omit this section when there are none.]

## Definition of Done
[Concrete completion standard, expected deliverable shape, quality bar, validation checks, review checkpoints, and stopping point.]
```

Keep each field practical. Prefer specific constraints and examples over abstract advice.

### 4. Handle missing information

First check the available materials for missing details. Ask exactly one critical clarifying question before drafting only when a missing detail would materially change the task and cannot be verified or safely assumed. Do not bundle multiple missing details into one question.

If a missing detail can be safely assumed, proceed and label material assumptions clearly under `Assumptions`, or inline for a lightweight response. Omit the section when no material assumptions were needed.

If sources are missing, do not invent them. State the source gap and propose the smallest next step to obtain or confirm the material.

### 5. Separate brief writing from prompt polishing

If the user only asks to rewrite, beautify, or optimize prompt wording, treat it as a prompt editing task. Do not expand it into a full task-definition exercise unless the user also asks to clarify the underlying goal, boundaries, sources, or done criteria.

## Output Style

- Match the user's language unless they request otherwise.
- Distinguish facts, assumptions, and suggestions.
- Be concise by default.
- Use a one-page brief when possible.
- End with a clear next step only when useful.
- If the user requested only task definition, stop after delivering the brief. If they also requested execution, continue within the authorized scope; the brief itself does not authorize additional work or require a new approval gate.

## Quality Check

For a full brief, verify the following. For lightweight responses, apply only the relevant checks without adding unnecessary sections:

- The Objective states what the output is for, not just the action to perform.
- The Background gives enough context for a smart outsider to avoid the wrong direction.
- The Materials identify what evidence to use and what not to fabricate.
- The Boundaries define hard limits.
- The Assumptions section contains only material assumptions, or is omitted when none were needed.
- The Definition of Done makes success testable and gives a stopping point.
- Open questions are either resolved, asked as one critical question, or recorded as assumptions.
