# Builder-Trainer Cognitive Loop: Usage Guide

This document provides detailed instructions for using the Builder-Trainer Cognitive Loop system.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Running the System](#running-the-system)
4. [Command-Line Interface](#command-line-interface)
5. [Monitoring](#monitoring)
6. [Customization](#customization)
7. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Docker (version 20.10 or later)
- Docker Compose (version 2.0 or later)
- LM Studio (for local LLM)

### Setting Up LM Studio

1. Download and install LM Studio from [lmstudio.ai](https://lmstudio.ai/)
2. Download the `deepseek-coder-7b-instruct.Q4_K_M.gguf` model
3. Start the HTTP server on port 1234

### Installing the System

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/builder-trainer-ai.git
   cd builder-trainer-ai
   ```

2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file to match your LM Studio configuration:
   ```
   OPENAI_API_BASE=http://host.docker.internal:1234/v1
   OPENAI_API_KEY=sk-local
   MODEL_NAME=deepseek-coder
   ```

## Configuration

### Environment Variables

- `OPENAI_API_BASE`: URL of the LLM API (default: `http://host.docker.internal:1234/v1`)
- `OPENAI_API_KEY`: API key for the LLM API (default: `sk-local`)
- `MODEL_NAME`: Name of the LLM model (default: `deepseek-coder`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `TASK_CHECK_INTERVAL`: Interval between task checks in seconds (default: `300`)
- `MAX_RETRIES`: Maximum number of retries for failed tasks (default: `3`)

### Memory Templates

The system uses memory templates to initialize the memory system. These templates are located in the `memory_templates` directory.

- `memory_templates/core/`: Templates for core memory files
- `memory_templates/task_memory/`: Templates for task memory files
- `memory_templates/advanced/`: Templates for advanced memory files

You can customize these templates to change the initial state of the system.

## Running the System

### Starting the System

1. Build and start the Docker container:
   ```bash
   docker-compose up --build -d
   ```

2. Check the logs:
   ```bash
   docker-compose logs -f
   ```

### Stopping the System

```bash
docker-compose down
```

### Restarting the System

```bash
docker-compose restart
```

## Command-Line Interface

The system includes a command-line interface (CLI) for interacting with the Builder-Trainer Cognitive Loop.

### Adding a User Task

```bash
python utils/cli.py add-task "Build a GUI downloader" --difficulty 0.7 --priority 1
```

Options:
- `--difficulty`: Task difficulty (0.0 to 1.0, default: 0.5)
- `--constraints`: Task constraints (multiple values allowed)
- `--skills`: Required skills (multiple values allowed)
- `--priority`: Task priority (lower number = higher priority, default: 1)

### Listing Tasks

```bash
python utils/cli.py list-tasks --count 10 --status pending
```

Options:
- `--count`: Number of tasks to list (default: 10)
- `--status`: Filter by status (completed, failed, pending, running)

### Getting Task Details

```bash
python utils/cli.py get-task task_123456
```

### Getting Builder Profile

```bash
python utils/cli.py get-profile
```

### Getting Skill Map

```bash
python utils/cli.py get-skills
```

### Getting Performance Trend

```bash
python utils/cli.py get-trend
```

## Monitoring

### System Logs

The system logs are stored in the `memory/logs` directory:

- `memory/logs/system_log.json`: System log
- `memory/logs/builder.log`: Builder Agent log
- `memory/logs/trainer.log`: Trainer Agent log
- `memory/logs/task_id_execution.log`: Execution log for a task

### Memory Files

The memory files are stored in the `memory` directory:

- `memory/core/`: Core memory files
- `memory/task_memory/`: Task memory files
- `memory/code_archive/`: Code archive
- `memory/logs/`: Logs
- `memory/advanced/`: Advanced memory files

### Docker Logs

```bash
docker-compose logs -f
```

## Customization

### Task Templates

You can customize the task templates in `trainer/generate_task.py`:

- `TASK_TEMPLATES`: Templates for task descriptions
- `GOAL_TEMPLATES`: Templates for task goals
- `CONSTRAINT_TEMPLATES`: Templates for task constraints

### Difficulty Adjustment

You can customize the difficulty adjustment in `trainer/adjust_difficulty.py`:

- `DEFAULT_DIFFICULTY`: Default difficulty level
- `MIN_DIFFICULTY`: Minimum difficulty level
- `MAX_DIFFICULTY`: Maximum difficulty level
- `ADJUSTMENT_FACTORS`: Adjustment factors for different performance trends
- `SCORE_THRESHOLDS`: Score thresholds for difficulty adjustment

### Training Strategies

You can customize the training strategies in `trainer/strategy_manager.py`:

- `STRATEGY_TYPES`: Types of training strategies
- `DEFAULT_STRATEGY_WEIGHTS`: Default weights for training strategies

## Troubleshooting

### Common Issues

#### LLM Connection Issues

If the system cannot connect to the LLM:

1. Check that LM Studio is running and the HTTP server is started
2. Check that the `OPENAI_API_BASE` environment variable is set correctly
3. Check that the Docker container can access the host machine

#### Task Execution Issues

If tasks fail to execute:

1. Check the task execution logs in `memory/logs/task_id_execution.log`
2. Check the Builder Agent log in `memory/logs/builder.log`
3. Check the system log in `memory/logs/system_log.json`

#### Memory Issues

If the system cannot access memory files:

1. Check that the memory directories exist
2. Check that the memory files have the correct permissions
3. Check that the Docker container has access to the memory directory

### Getting Help

If you encounter issues not covered in this guide, please:

1. Check the [README.md](README.md) file
2. Check the [ARCHITECTURE.md](ARCHITECTURE.md) file
3. Create an issue on the GitHub repository

