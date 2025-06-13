# Builder-Trainer Cognitive Loop - System Analysis

## System Overview

The Builder-Trainer Cognitive Loop is a self-evolving code agent system that operates within a Docker environment. The system consists of two main agents:

1. **Builder Agent**: Executes coding tasks, reflects on outcomes, and logs metrics
2. **Trainer Agent**: Analyzes the Builder's performance, generates new tasks, and adjusts difficulty

The system maintains persistent memory through a JSON-based file system and uses a local LLM (DeepSeek-Coder 7B) via LM Studio for code generation and analysis.

## Key Components

### 1. Builder Agent

- **loop.py**: Master orchestrator that manages the overall execution flow
- **builder/run_project.py**: Executes tasks using LLM and shell commands
- **builder/reflect.py**: Summarizes task results and logs metrics
- **executor/run_cmd.py**: Subprocess shell executor for running commands
- **executor/run_code.py**: Executes generated Python or scripts

### 2. Trainer Agent

- **trainer/analyze_builder.py**: Loads and analyzes Builder's memory and profile
- **trainer/generate_task.py**: Creates task JSON with goal, difficulty, and constraints
- **trainer/adjust_difficulty.py**: Tunes the difficulty curve based on Builder's performance
- **trainer/strategy_manager.py**: Manages skill diversity and regression protection
- **trainer/task_taxonomizer.py**: Classifies and balances task types

### 3. Memory System

- **memory/core/*.json**: Profile, skill map, score log, reflections
- **memory/advanced/*.json**: Internal biases, learned concepts, motivation log
- **memory/task_memory/**: All task metadata and outcomes
- **memory/code_archive/**: Saved versions of all generated code
- **memory/logs/**: Shell logs, system logs, runtime usage

### 4. LLM Interface

- Uses LM Studio exposed at: http://host.docker.internal:1234/v1
- Accessed via OpenAI-compatible ChatCompletion API
- Primary model: DeepSeek-Coder 7B (GGUF via LM Studio)
- Optional fallback to Mistral 7B

## System Flow

1. The Trainer agent generates a task (or retrieves a user-submitted task)
2. The Builder agent executes the task using the LLM and shell commands
3. The Builder agent reflects on the outcome and logs metrics
4. The system updates the Builder's profile based on the results
5. The loop continues with the Trainer generating a new task

## Identified Gaps and Improvements

1. **loop.py needs enhancement**:
   - Add execution control and crash protection
   - Implement clear loop stages (get_task, execute_task, postprocess)
   - Add try/except handling with skip/stall/resume logic

2. **memory_manager.py is missing**:
   - Create a unified memory management system
   - Implement load, save, and append functions

3. **Scoring system is undefined**:
   - Create score_engine.py to calculate and track scores
   - Define metrics for performance evaluation

4. **LLM interface is missing**:
   - Create llm_interface.py to handle communication with LM Studio
   - Implement query function with appropriate parameters

5. **Shell sandbox logic is needed**:
   - Implement run_cmd with timeout, logging, and safety features
   - Add blacklist for destructive commands

6. **Trainer components need implementation**:
   - Create analyze_builder.py, generate_task.py, and adjust_difficulty.py
   - Set up trainer_log.json for tracking Trainer decisions

7. **Retry/failure mechanism is missing**:
   - Add logic to requeue failed tasks
   - Track retry count in task memory

8. **CLI for user tasks is needed**:
   - Create utils/cli.py for injecting high-priority tasks
   - Implement task queue management

## Docker Environment

- Uses Python 3.10 slim image
- Installs necessary system packages
- Sets up a non-root user (agent)
- Mounts volumes for persistent memory
- Connects to LM Studio via host.docker.internal

## Implementation Priorities

1. Core system components (loop.py, memory_manager.py, llm_interface.py, score_engine.py)
2. Builder agent components
3. Trainer agent components
4. Memory system setup
5. Docker environment configuration
6. Testing and debugging
7. Documentation and delivery

