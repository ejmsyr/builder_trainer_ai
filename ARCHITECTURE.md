# Builder-Trainer Cognitive Loop: System Architecture

## Overview

The Builder-Trainer Cognitive Loop is a self-evolving AI system designed to improve its coding abilities through continuous practice, reflection, and targeted learning. The system consists of two main agents—the Builder and the Trainer—that work together in a feedback loop to generate, execute, and learn from coding tasks.

## System Components

### 1. Builder Agent

The Builder Agent is responsible for executing coding tasks. It uses a local Large Language Model (LLM) to generate code based on task requirements, executes the code in a safe environment, and evaluates the results.

#### Key Components:

- **run_project.py**: The main module for executing tasks. It takes a task definition as input and returns the execution results.
  - `BuilderAgent.run_project()`: Executes a coding task
  - `BuilderAgent._generate_code()`: Generates code using the LLM
  - `BuilderAgent._execute_code()`: Executes the generated code
  - `BuilderAgent._evaluate_results()`: Evaluates the execution results

- **reflect.py**: Generates reflections on task execution and updates the Builder Agent's profile.
  - `BuilderReflection.reflect_on_task()`: Generates a reflection on a completed task
  - `BuilderReflection.update_builder_profile_with_reflection()`: Updates the Builder profile based on reflection
  - `BuilderReflection.generate_learning_summary()`: Generates a human-readable learning summary

### 2. Trainer Agent

The Trainer Agent analyzes the Builder Agent's performance and generates new tasks to help it improve. It identifies skill gaps, style issues, and learning opportunities, and adjusts task difficulty based on the Builder Agent's progress.

#### Key Components:

- **analyze_builder.py**: Analyzes the Builder Agent's profile and performance.
  - `BuilderAnalyzer.analyze_builder_profile()`: Analyzes the Builder Agent's profile
  - `BuilderAnalyzer._identify_skill_gaps()`: Identifies skill gaps
  - `BuilderAnalyzer._identify_style_issues()`: Identifies style issues
  - `BuilderAnalyzer._identify_learning_opportunities()`: Identifies learning opportunities

- **generate_task.py**: Generates tasks for the Builder Agent.
  - `TaskGenerator.generate_task()`: Generates a task
  - `TaskGenerator._generate_skill_gap_task()`: Generates a task to address a skill gap
  - `TaskGenerator._generate_style_issue_task()`: Generates a task to address a style issue
  - `TaskGenerator._generate_learning_task()`: Generates a task for learning

- **adjust_difficulty.py**: Adjusts task difficulty based on the Builder Agent's performance.
  - `DifficultyAdjuster.adjust_difficulty()`: Adjusts difficulty
  - `DifficultyAdjuster.get_difficulty_for_skill()`: Gets an appropriate difficulty level for a specific skill
  - `DifficultyAdjuster.get_difficulty_curve()`: Gets the difficulty curve over time

- **strategy_manager.py**: Manages training strategies.
  - `StrategyManager.get_next_skill_focus()`: Determines the next skill to focus on
  - `StrategyManager._get_current_strategy()`: Gets the current training strategy
  - `StrategyManager._update_strategy_weights()`: Updates the strategy weights

### 3. Memory System

The Memory System stores all data related to the Builder-Trainer Cognitive Loop, including task history, code archives, performance metrics, and reflections.

#### Key Components:

- **memory_manager.py**: Handles all read/write operations to JSON memory files.
  - `MemoryManager.save()`: Saves data to a file
  - `MemoryManager.load()`: Loads data from a file
  - `MemoryManager.append()`: Appends data to a file
  - `MemoryManager.add_task_to_queue()`: Adds a task to the queue
  - `MemoryManager.get_next_task()`: Gets the next task from the queue
  - `MemoryManager.log_system_event()`: Logs a system event

#### Memory Structure:

- **Core Memory**:
  - `builder_profile.json`: General profile of the Builder Agent
  - `skill_map.json`: Map of skills and proficiency levels
  - `score_log.json`: Log of task scores

- **Task Memory**:
  - `task_queue.json`: Queue of pending tasks
  - `task_*.json`: Individual task definitions
  - `reflection_*.json`: Reflections on completed tasks
  - `summary_*.json`: Human-readable learning summaries

- **Advanced Memory**:
  - `trainer_log.json`: Log of Trainer Agent actions
  - `current_difficulty.json`: Current difficulty settings
  - `strategy_weights.json`: Weights for different training strategies
  - `learned_concepts.json`: Concepts learned by the Builder Agent
  - `builder_analysis_*.json`: Analysis of Builder Agent performance

- **Code Archive**:
  - `memory/code_archive/task_id/`: Directory for each task
  - `memory/code_archive/task_id/final_code.py`: Final code for a task

- **Logs**:
  - `memory/logs/system_log.json`: System log
  - `memory/logs/task_id_execution.log`: Execution log for a task

### 4. Core System

The core system orchestrates the interaction between the Builder Agent, Trainer Agent, and Memory System.

#### Key Components:

- **loop.py**: The main orchestrator loop.
  - `run_loop()`: Runs the main loop
  - `run_loop_once()`: Runs one iteration of the loop
  - `process_task()`: Processes a task

- **llm_interface.py**: Communicates with the LLM.
  - `LLMInterface.code_completion()`: Generates code using the LLM
  - `LLMInterface.analyze_code()`: Analyzes code using the LLM
  - `LLMInterface.reflect_on_task()`: Generates a reflection using the LLM

- **score_engine.py**: Calculates and tracks scores.
  - `ScoreEngine.calculate_score()`: Calculates a score for a task
  - `ScoreEngine.track_score()`: Tracks a score in the score log
  - `ScoreEngine.get_performance_trend()`: Gets the performance trend

### 5. Execution Environment

The execution environment provides a safe way to run code generated by the Builder Agent.

#### Key Components:

- **run_cmd.py**: Executes shell commands.
  - `CommandExecutor.run_cmd()`: Runs a shell command

- **run_code.py**: Executes Python code.
  - `CodeExecutor.run_python_code()`: Runs Python code
  - `CodeExecutor.run_script()`: Runs a script
  - `CodeExecutor.archive_code()`: Archives code

### 6. Utilities

The system includes various utilities for interacting with the Builder-Trainer Cognitive Loop.

#### Key Components:

- **cli.py**: Command-line interface.
  - `add_user_task()`: Adds a user task to the queue
  - `list_tasks()`: Lists recent tasks
  - `get_task_details()`: Gets details of a specific task
  - `get_builder_profile()`: Gets the Builder Agent's profile
  - `get_skill_map()`: Gets the skill map
  - `get_performance_trend()`: Gets the performance trend

## Data Flow

1. **Task Selection**:
   - The system checks the task queue for pending tasks
   - If the queue is empty, the Trainer Agent generates a new task

2. **Task Execution**:
   - The Builder Agent generates code for the task
   - The code is executed in a safe environment
   - The results are evaluated and scored

3. **Reflection and Learning**:
   - The Builder Agent reflects on its performance
   - The reflection is used to update the Builder Agent's profile
   - A human-readable learning summary is generated

4. **Analysis and Planning**:
   - The Trainer Agent analyzes the Builder Agent's performance
   - The Trainer Agent identifies skill gaps, style issues, and learning opportunities
   - The Trainer Agent adjusts task difficulty and selects a training strategy
   - The Trainer Agent generates new tasks to help the Builder Agent improve

## Docker Environment

The system runs in a Docker container to provide a consistent and isolated environment.

### Key Files:

- **Dockerfile**: Defines the Docker image
- **docker-compose.yml**: Defines the Docker services
- **entrypoint.sh**: Initializes the system and starts the main loop
- **.env.example**: Example environment variables

## Cognitive Loop Process

1. **Task Selection**: The system selects a task from the queue or generates a new one
2. **Code Generation**: The Builder Agent generates code to solve the task
3. **Code Execution**: The code is executed in a safe environment
4. **Evaluation**: The results are evaluated and scored
5. **Reflection**: The Builder Agent reflects on its performance
6. **Learning**: The Builder Agent updates its skills and knowledge
7. **Analysis**: The Trainer Agent analyzes the Builder Agent's performance
8. **Task Generation**: The Trainer Agent generates new tasks to help the Builder Agent improve

## System Initialization

When the system starts, it performs the following initialization steps:

1. **Create Directories**: Creates necessary directories for memory storage
2. **Initialize Memory**: Initializes memory files with default values if they don't exist
3. **Start Loop**: Starts the main loop

## Error Handling

The system includes comprehensive error handling to ensure robustness:

1. **Task Execution Errors**: Errors during task execution are caught and logged
2. **LLM Communication Errors**: Errors communicating with the LLM are caught and logged
3. **Memory Access Errors**: Errors accessing memory files are caught and logged
4. **Loop Errors**: Errors in the main loop are caught and logged

## Testing

The system includes a comprehensive test suite:

- **test_memory.py**: Tests for the memory manager
- **test_loop.py**: Tests for the main loop
- **test_task_execution.py**: Tests for task execution

## Future Enhancements

Potential future enhancements to the system include:

1. **Web Interface**: A web interface for monitoring and interacting with the system
2. **Multi-Agent Collaboration**: Multiple Builder Agents collaborating on tasks
3. **External API Integration**: Integration with external APIs for data and services
4. **Natural Language Task Specification**: Specifying tasks in natural language
5. **Code Review**: Automated code review and feedback
6. **Visualization**: Visualization of the Builder Agent's learning progress
7. **Customizable Training Strategies**: User-defined training strategies
8. **Multi-Language Support**: Support for multiple programming languages

