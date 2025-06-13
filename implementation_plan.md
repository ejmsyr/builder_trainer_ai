# Builder-Trainer Cognitive Loop - Implementation Plan

This document outlines the detailed implementation plan for each component of the Builder-Trainer Cognitive Loop system.

## Phase 1: Core System Components

### 1. memory_manager.py

**Purpose**: Provide a unified interface for reading, writing, and updating JSON memory files.

**Implementation Steps**:
1. Create a `MemoryManager` class with static methods for file operations
2. Implement `load`, `save`, `append`, and `update` methods
3. Add error handling and file locking for concurrent access
4. Add utility methods for common operations (e.g., get_task_by_id)

**Dependencies**: None

**Estimated Time**: 2 hours

### 2. llm_interface.py

**Purpose**: Handle communication with the LLM via LM Studio.

**Implementation Steps**:
1. Set up OpenAI API client with environment variables
2. Implement `query` method for general-purpose LLM queries
3. Implement `code_completion` method for code generation
4. Implement `analyze_code` method for code analysis
5. Add error handling and retry logic

**Dependencies**: openai package

**Estimated Time**: 2 hours

### 3. score_engine.py

**Purpose**: Calculate and track scores for tasks.

**Implementation Steps**:
1. Define scoring metrics (correctness, efficiency, elegance, robustness)
2. Implement `calculate_score` method
3. Implement `track_score` method to update score_log.json
4. Implement `get_performance_trend` method for analyzing trends

**Dependencies**: memory_manager.py

**Estimated Time**: 2 hours

### 4. loop.py

**Purpose**: Orchestrate the overall execution flow.

**Implementation Steps**:
1. Implement `get_task` method to retrieve tasks from queue
2. Implement `execute_task` method to run tasks using Builder
3. Implement `postprocess` method for updating memory and reflection
4. Implement `handle_error` method for error recovery
5. Set up main loop with try/except handling

**Dependencies**: memory_manager.py, builder/run_project.py, builder/reflect.py

**Estimated Time**: 3 hours

## Phase 2: Builder Agent Components

### 1. executor/run_cmd.py

**Purpose**: Execute shell commands safely.

**Implementation Steps**:
1. Implement `run_cmd` method using subprocess
2. Add timeout handling
3. Add output logging
4. Implement command blacklist for security

**Dependencies**: None

**Estimated Time**: 2 hours

### 2. executor/run_code.py

**Purpose**: Execute generated Python or scripts safely.

**Implementation Steps**:
1. Implement `run_python_code` method
2. Add timeout handling
3. Add output and error logging
4. Implement resource limiting

**Dependencies**: executor/run_cmd.py

**Estimated Time**: 2 hours

### 3. builder/run_project.py

**Purpose**: Execute tasks using LLM and shell commands.

**Implementation Steps**:
1. Implement `run_project` method
2. Add task parsing logic
3. Add code generation using llm_interface.py
4. Add code execution using executor/run_code.py
5. Add result evaluation logic

**Dependencies**: llm_interface.py, executor/run_cmd.py, executor/run_code.py

**Estimated Time**: 3 hours

### 4. builder/reflect.py

**Purpose**: Generate reflections on task execution.

**Implementation Steps**:
1. Implement `reflect_on_task` method
2. Add strength and weakness identification
3. Add lessons learned generation
4. Update builder profile with new insights

**Dependencies**: llm_interface.py, memory_manager.py

**Estimated Time**: 2 hours

## Phase 3: Trainer Agent Components

### 1. trainer/analyze_builder.py

**Purpose**: Analyze Builder's profile and performance.

**Implementation Steps**:
1. Implement `analyze_builder_profile` method
2. Add skill gap identification
3. Add performance trend analysis
4. Generate recommendations for improvement

**Dependencies**: memory_manager.py

**Estimated Time**: 2 hours

### 2. trainer/generate_task.py

**Purpose**: Generate tasks based on Builder's needs.

**Implementation Steps**:
1. Implement `generate_task` method
2. Add task difficulty calculation
3. Add constraint generation
4. Add task queue management

**Dependencies**: trainer/analyze_builder.py, trainer/adjust_difficulty.py, memory_manager.py

**Estimated Time**: 3 hours

### 3. trainer/adjust_difficulty.py

**Purpose**: Adjust task difficulty based on Builder's performance.

**Implementation Steps**:
1. Implement `adjust_difficulty` method
2. Add performance trend analysis
3. Add difficulty curve calculation
4. Add regression protection

**Dependencies**: memory_manager.py

**Estimated Time**: 2 hours

### 4. trainer/strategy_manager.py

**Purpose**: Manage skill diversity and learning strategy.

**Implementation Steps**:
1. Implement `get_next_skill_focus` method
2. Add skill distribution analysis
3. Add learning path optimization
4. Add regression detection

**Dependencies**: memory_manager.py, trainer/analyze_builder.py

**Estimated Time**: 2 hours

## Phase 4: Memory System Setup

### 1. Memory JSON Templates

**Purpose**: Create initial JSON files for the memory system.

**Implementation Steps**:
1. Create builder_profile.json template
2. Create score_log.json template
3. Create skill_map.json template
4. Create task_queue.json template
5. Create system_log.json template

**Dependencies**: None

**Estimated Time**: 2 hours

### 2. Memory Directory Structure

**Purpose**: Set up the directory structure for the memory system.

**Implementation Steps**:
1. Create core directory
2. Create advanced directory
3. Create task_memory directory
4. Create code_archive directory
5. Create logs directory

**Dependencies**: None

**Estimated Time**: 1 hour

## Phase 5: Utils Components

### 1. utils/cli.py

**Purpose**: Provide a CLI for injecting user tasks.

**Implementation Steps**:
1. Implement `add_user_task` method
2. Add command-line argument parsing
3. Add task priority management
4. Add task validation

**Dependencies**: memory_manager.py

**Estimated Time**: 2 hours

## Phase 6: Docker Environment

### 1. Dockerfile

**Purpose**: Define the Docker image for the system.

**Implementation Steps**:
1. Use Python 3.10 slim as base image
2. Install system dependencies
3. Create non-root user
4. Set up working directory
5. Copy code and install Python dependencies

**Dependencies**: requirements.txt

**Estimated Time**: 1 hour

### 2. docker-compose.yml

**Purpose**: Define the Docker Compose configuration.

**Implementation Steps**:
1. Define builder_trainer service
2. Set up environment variables
3. Configure volumes for persistent memory
4. Set up network configuration

**Dependencies**: Dockerfile

**Estimated Time**: 1 hour

### 3. entrypoint.sh

**Purpose**: Define the entry point for the Docker container.

**Implementation Steps**:
1. Set up environment
2. Run loop.py
3. Add error handling and logging

**Dependencies**: None

**Estimated Time**: 1 hour

### 4. requirements.txt

**Purpose**: Define Python dependencies.

**Implementation Steps**:
1. Add openai package
2. Add psutil package
3. Add tqdm package
4. Add rich package
5. Add pyyaml package

**Dependencies**: None

**Estimated Time**: 0.5 hours

## Phase 7: Testing and Debugging

### 1. tests/test_memory_manager.py

**Purpose**: Test memory manager functionality.

**Implementation Steps**:
1. Test load method
2. Test save method
3. Test append method
4. Test update method
5. Test error handling

**Dependencies**: memory_manager.py

**Estimated Time**: 2 hours

### 2. tests/test_llm_interface.py

**Purpose**: Test LLM interface functionality.

**Implementation Steps**:
1. Test query method
2. Test code_completion method
3. Test analyze_code method
4. Test error handling and retry logic

**Dependencies**: llm_interface.py

**Estimated Time**: 2 hours

### 3. tests/test_executor.py

**Purpose**: Test executor functionality.

**Implementation Steps**:
1. Test run_cmd method
2. Test run_python_code method
3. Test timeout handling
4. Test error handling

**Dependencies**: executor/run_cmd.py, executor/run_code.py

**Estimated Time**: 2 hours

### 4. tests/test_integration.py

**Purpose**: Test full system integration.

**Implementation Steps**:
1. Test task execution flow
2. Test memory persistence
3. Test error recovery
4. Test full loop execution

**Dependencies**: All components

**Estimated Time**: 3 hours

## Phase 8: Documentation and Delivery

### 1. README.md

**Purpose**: Provide overview and usage instructions.

**Implementation Steps**:
1. Add system overview
2. Add installation instructions
3. Add usage instructions
4. Add configuration options
5. Add troubleshooting guide

**Dependencies**: None

**Estimated Time**: 2 hours

### 2. API Documentation

**Purpose**: Document component APIs.

**Implementation Steps**:
1. Document memory_manager.py API
2. Document llm_interface.py API
3. Document executor API
4. Document builder API
5. Document trainer API

**Dependencies**: All components

**Estimated Time**: 3 hours

## Implementation Timeline

| Phase | Component | Estimated Time | Dependencies |
|-------|-----------|----------------|--------------|
| 1 | memory_manager.py | 2 hours | None |
| 1 | llm_interface.py | 2 hours | openai package |
| 1 | score_engine.py | 2 hours | memory_manager.py |
| 1 | loop.py | 3 hours | memory_manager.py, builder/run_project.py, builder/reflect.py |
| 2 | executor/run_cmd.py | 2 hours | None |
| 2 | executor/run_code.py | 2 hours | executor/run_cmd.py |
| 2 | builder/run_project.py | 3 hours | llm_interface.py, executor/run_cmd.py, executor/run_code.py |
| 2 | builder/reflect.py | 2 hours | llm_interface.py, memory_manager.py |
| 3 | trainer/analyze_builder.py | 2 hours | memory_manager.py |
| 3 | trainer/generate_task.py | 3 hours | trainer/analyze_builder.py, trainer/adjust_difficulty.py, memory_manager.py |
| 3 | trainer/adjust_difficulty.py | 2 hours | memory_manager.py |
| 3 | trainer/strategy_manager.py | 2 hours | memory_manager.py, trainer/analyze_builder.py |
| 4 | Memory JSON Templates | 2 hours | None |
| 4 | Memory Directory Structure | 1 hour | None |
| 5 | utils/cli.py | 2 hours | memory_manager.py |
| 6 | Dockerfile | 1 hour | requirements.txt |
| 6 | docker-compose.yml | 1 hour | Dockerfile |
| 6 | entrypoint.sh | 1 hour | None |
| 6 | requirements.txt | 0.5 hours | None |
| 7 | tests/test_memory_manager.py | 2 hours | memory_manager.py |
| 7 | tests/test_llm_interface.py | 2 hours | llm_interface.py |
| 7 | tests/test_executor.py | 2 hours | executor/run_cmd.py, executor/run_code.py |
| 7 | tests/test_integration.py | 3 hours | All components |
| 8 | README.md | 2 hours | None |
| 8 | API Documentation | 3 hours | All components |

**Total Estimated Time**: 48.5 hours

