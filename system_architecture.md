# Builder-Trainer Cognitive Loop - System Architecture

## System Architecture Overview

The Builder-Trainer Cognitive Loop is designed as a modular system with clear separation of concerns. The architecture follows these principles:

1. **Modularity**: Each component has a specific responsibility
2. **Persistence**: All data is stored in JSON files for persistence
3. **Error Resilience**: The system can recover from failures
4. **Autonomy**: The system can operate without human intervention

## Component Architecture

### Core Components

#### 1. loop.py

The main orchestrator that manages the overall execution flow.

```
def main():
    while True:
        try:
            task = get_task()
            result = execute_task(task)
            postprocess(task, result)
        except Exception as e:
            handle_error(e)
            continue
```

**Interfaces**:
- `get_task()`: Retrieves a task from the Trainer or user queue
- `execute_task(task)`: Executes the task using the Builder agent
- `postprocess(task, result)`: Updates memory and triggers reflection
- `handle_error(e)`: Logs errors and manages recovery

#### 2. memory_manager.py

Handles all read/write operations to JSON memory files.

```
class MemoryManager:
    def load(file_path):
        # Load JSON data from file
    
    def save(file_path, data):
        # Save data to JSON file
    
    def append(file_path, new_entry):
        # Append new entry to JSON array file
    
    def update(file_path, key, value):
        # Update specific key in JSON file
```

**Interfaces**:
- `load(file_path)`: Loads JSON data from file
- `save(file_path, data)`: Saves data to JSON file
- `append(file_path, new_entry)`: Appends new entry to JSON array
- `update(file_path, key, value)`: Updates specific key in JSON file

#### 3. llm_interface.py

Handles communication with the LLM via LM Studio.

```
def query(prompt, system="You're a code agent...", model="deepseek-coder"):
    # Query LLM via OpenAI-compatible API
    
def code_completion(prompt, language="python"):
    # Get code completion from LLM
    
def analyze_code(code, criteria):
    # Analyze code quality using LLM
```

**Interfaces**:
- `query(prompt, system, model)`: General-purpose LLM query
- `code_completion(prompt, language)`: Get code completion
- `analyze_code(code, criteria)`: Analyze code quality

#### 4. score_engine.py

Calculates and tracks scores for tasks.

```
def calculate_score(metrics, difficulty, source):
    # Calculate score based on metrics
    
def track_score(task_id, score):
    # Track score in score_log.json
    
def get_performance_trend(n=10):
    # Get trend of last n scores
```

**Interfaces**:
- `calculate_score(metrics, difficulty, source)`: Calculate score
- `track_score(task_id, score)`: Track score in log
- `get_performance_trend(n)`: Get trend of last n scores

### Builder Agent Components

#### 1. builder/run_project.py

Executes tasks using LLM and shell commands.

```
def run_project(task):
    # Parse task
    # Generate code using LLM
    # Execute code
    # Evaluate results
    # Return result object
```

**Interfaces**:
- `run_project(task)`: Executes a task and returns result

#### 2. builder/reflect.py

Summarizes task results and logs metrics.

```
def reflect_on_task(task, result):
    # Analyze task execution
    # Identify strengths and weaknesses
    # Generate reflection
    # Return reflection object
```

**Interfaces**:
- `reflect_on_task(task, result)`: Generates reflection on task execution

### Trainer Agent Components

#### 1. trainer/analyze_builder.py

Loads and analyzes Builder's memory and profile.

```
def analyze_builder_profile():
    # Load builder profile
    # Analyze performance
    # Identify skill gaps
    # Return analysis object
```

**Interfaces**:
- `analyze_builder_profile()`: Analyzes Builder's profile and returns analysis

#### 2. trainer/generate_task.py

Creates task JSON with goal, difficulty, and constraints.

```
def generate_task(analysis=None):
    # Generate task based on analysis
    # Set appropriate difficulty
    # Define constraints
    # Return task object
```

**Interfaces**:
- `generate_task(analysis)`: Generates a task based on analysis

#### 3. trainer/adjust_difficulty.py

Tunes the difficulty curve based on Builder's performance.

```
def adjust_difficulty(performance_trend):
    # Analyze performance trend
    # Adjust difficulty curve
    # Return new difficulty level
```

**Interfaces**:
- `adjust_difficulty(performance_trend)`: Adjusts difficulty based on performance

#### 4. trainer/strategy_manager.py

Manages skill diversity and regression protection.

```
def get_next_skill_focus():
    # Analyze skill distribution
    # Determine next skill to focus on
    # Return skill focus
```

**Interfaces**:
- `get_next_skill_focus()`: Determines next skill to focus on

### Executor Components

#### 1. executor/run_cmd.py

Subprocess shell executor for running commands.

```
def run_cmd(command, timeout=60, log_file=None):
    # Execute shell command
    # Capture output
    # Handle timeout
    # Return result
```

**Interfaces**:
- `run_cmd(command, timeout, log_file)`: Executes shell command and returns result

#### 2. executor/run_code.py

Executes generated Python or scripts.

```
def run_python_code(code, timeout=60, log_file=None):
    # Save code to temporary file
    # Execute Python code
    # Capture output
    # Return result
```

**Interfaces**:
- `run_python_code(code, timeout, log_file)`: Executes Python code and returns result

### Utils Components

#### 1. utils/cli.py

CLI for injecting high-priority tasks.

```
def add_user_task(task_description, difficulty=0.5):
    # Create task object
    # Add to task queue
    # Return task ID
```

**Interfaces**:
- `add_user_task(task_description, difficulty)`: Adds user task to queue

## Data Flow

1. **Task Generation**:
   - Trainer analyzes Builder profile
   - Trainer generates task
   - Task is added to task queue

2. **Task Execution**:
   - Builder retrieves task from queue
   - Builder generates code using LLM
   - Builder executes code using executor
   - Builder evaluates results

3. **Reflection and Learning**:
   - Builder reflects on task execution
   - System updates Builder profile
   - System logs score and metrics

4. **Feedback Loop**:
   - Trainer analyzes updated profile
   - Trainer adjusts difficulty
   - Trainer generates new task

## Memory Structure

### 1. Core Memory

- **builder_profile.json**: Builder's profile and skills
- **score_log.json**: Log of task scores
- **skill_map.json**: Map of skills and proficiency levels

### 2. Task Memory

- **task_{id}.json**: Task metadata and results
- **task_queue.json**: Queue of pending tasks

### 3. Code Archive

- **{task_id}/{timestamp}_code.py**: Archived code versions

### 4. Logs

- **shell_logs/{task_id}.log**: Shell execution logs
- **system_log.json**: System-level logs

## Error Handling and Recovery

1. **Task Failure**:
   - Log error in task memory
   - Increment retry count
   - Requeue task if retry count < max_retries

2. **System Failure**:
   - Log error in system log
   - Attempt to recover state from memory
   - Resume from last known good state

## Security Considerations

1. **Command Execution**:
   - Blacklist dangerous commands
   - Run with limited privileges
   - Sandbox execution environment

2. **Resource Limits**:
   - Set timeouts for all operations
   - Limit memory and CPU usage
   - Prevent infinite loops

