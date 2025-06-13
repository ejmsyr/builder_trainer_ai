# Builder-Trainer Cognitive Loop - Memory Schemas

This document defines the JSON schemas for the memory system to ensure consistent data structures across the application.

## Core Memory Schemas

### 1. builder_profile.json

```json
{
  "id": "builder_v0.1",
  "task_count": 0,
  "average_score": 0,
  "skills_mastered": [],
  "weak_skills": [],
  "style_flags": {
    "hardcoded_paths": 3,
    "missing_error_handling": 5
  },
  "last_updated": "2025-06-12T00:00:00"
}
```

### 2. score_log.json

```json
[
  {
    "task_id": "json_parser_001",
    "score": 34.5,
    "difficulty": 0.32,
    "source": "trainer",
    "timestamp": "2025-06-12T00:00:00",
    "metrics": {
      "correctness": 0.8,
      "efficiency": 0.6,
      "elegance": 0.4,
      "robustness": 0.3
    }
  }
]
```

### 3. skill_map.json

```json
{
  "skills": {
    "python": {
      "level": 0.4,
      "tasks_completed": 5,
      "last_used": "2025-06-12T00:00:00"
    },
    "json_parsing": {
      "level": 0.2,
      "tasks_completed": 1,
      "last_used": "2025-06-12T00:00:00"
    }
  },
  "categories": {
    "language_proficiency": ["python", "javascript"],
    "data_processing": ["json_parsing", "csv_handling"],
    "web_development": ["html", "css", "javascript"]
  }
}
```

## Task Memory Schemas

### 1. task_{id}.json

```json
{
  "id": "json_parser_001",
  "source": "trainer",
  "goal": "Create a JSON parser that can handle nested objects and arrays",
  "difficulty": 0.32,
  "constraints": ["Must handle malformed JSON", "Must provide detailed error messages"],
  "created_at": "2025-06-12T00:00:00",
  "status": "completed",
  "attempts": 1,
  "max_attempts": 3,
  "result": {
    "success": true,
    "score": 34.5,
    "execution_time": 12.3,
    "output": "JSON parser created successfully",
    "error": null
  },
  "reflection": {
    "strengths": ["Correctly handles nested objects", "Good error messages"],
    "weaknesses": ["Could be more efficient", "Missing edge case handling"],
    "lessons_learned": ["Need to improve error handling", "Should use more efficient algorithms"]
  },
  "code_path": "code_archive/json_parser_001/final_code.py"
}
```

### 2. task_queue.json

```json
{
  "queue": [
    {
      "id": "csv_processor_001",
      "source": "trainer",
      "goal": "Create a CSV processor that can handle large files",
      "difficulty": 0.45,
      "constraints": ["Must be memory efficient", "Must handle malformed CSV"],
      "created_at": "2025-06-12T00:00:00",
      "priority": 1
    }
  ]
}
```

## Advanced Memory Schemas

### 1. trainer_log.json

```json
[
  {
    "timestamp": "2025-06-12T00:00:00",
    "action": "generate_task",
    "task_id": "json_parser_001",
    "reasoning": "Builder needs to improve JSON parsing skills",
    "difficulty_adjustment": 0.05
  }
]
```

### 2. system_log.json

```json
[
  {
    "timestamp": "2025-06-12T00:00:00",
    "level": "INFO",
    "component": "loop.py",
    "message": "Started task execution for json_parser_001"
  },
  {
    "timestamp": "2025-06-12T00:00:00",
    "level": "ERROR",
    "component": "executor/run_cmd.py",
    "message": "Command execution timed out",
    "details": {
      "command": "python3 test.py",
      "timeout": 60
    }
  }
]
```

### 3. learned_concepts.json

```json
{
  "concepts": {
    "json_parsing": {
      "description": "Parsing JSON strings into data structures",
      "related_skills": ["python", "data_processing"],
      "confidence": 0.6,
      "last_updated": "2025-06-12T00:00:00"
    }
  }
}
```

## Memory Directory Structure

```
memory/
├── core/
│   ├── builder_profile.json
│   ├── score_log.json
│   └── skill_map.json
├── advanced/
│   ├── trainer_log.json
│   ├── learned_concepts.json
│   └── motivation_log.json
├── task_memory/
│   ├── task_queue.json
│   ├── task_json_parser_001.json
│   └── task_csv_processor_001.json
├── code_archive/
│   ├── json_parser_001/
│   │   ├── attempt_1_code.py
│   │   └── final_code.py
│   └── csv_processor_001/
│       └── attempt_1_code.py
└── logs/
    ├── shell_logs/
    │   ├── json_parser_001.log
    │   └── csv_processor_001.log
    └── system_log.json
```

## Memory Manager Usage Examples

### Loading Data

```python
from memory_manager import MemoryManager

# Load builder profile
profile = MemoryManager.load("memory/core/builder_profile.json")

# Load task
task = MemoryManager.load(f"memory/task_memory/task_{task_id}.json")
```

### Saving Data

```python
from memory_manager import MemoryManager

# Save builder profile
MemoryManager.save("memory/core/builder_profile.json", profile)

# Save task
MemoryManager.save(f"memory/task_memory/task_{task_id}.json", task)
```

### Appending Data

```python
from memory_manager import MemoryManager

# Append to score log
new_score = {
    "task_id": task_id,
    "score": 34.5,
    "difficulty": 0.32,
    "source": "trainer",
    "timestamp": "2025-06-12T00:00:00"
}
MemoryManager.append("memory/core/score_log.json", new_score)

# Append to system log
log_entry = {
    "timestamp": "2025-06-12T00:00:00",
    "level": "INFO",
    "component": "loop.py",
    "message": f"Started task execution for {task_id}"
}
MemoryManager.append("memory/logs/system_log.json", log_entry)
```

### Updating Data

```python
from memory_manager import MemoryManager

# Update builder profile
MemoryManager.update("memory/core/builder_profile.json", "task_count", profile["task_count"] + 1)
MemoryManager.update("memory/core/builder_profile.json", "average_score", new_average_score)
```

