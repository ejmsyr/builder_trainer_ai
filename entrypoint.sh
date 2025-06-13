#!/bin/bash

# Create necessary directories
mkdir -p memory/core
mkdir -p memory/advanced
mkdir -p memory/task_memory
mkdir -p memory/code_archive
mkdir -p memory/logs

# Check if memory files exist, create if not
if [ ! -f memory/core/builder_profile.json ]; then
    echo "Initializing builder profile..."
    cp -n memory_templates/core/builder_profile.json memory/core/
fi

if [ ! -f memory/core/skill_map.json ]; then
    echo "Initializing skill map..."
    cp -n memory_templates/core/skill_map.json memory/core/
fi

if [ ! -f memory/core/score_log.json ]; then
    echo "Initializing score log..."
    cp -n memory_templates/core/score_log.json memory/core/
fi

if [ ! -f memory/task_memory/task_queue.json ]; then
    echo "Initializing task queue..."
    cp -n memory_templates/task_memory/task_queue.json memory/task_memory/
fi

if [ ! -f memory/advanced/trainer_log.json ]; then
    echo "Initializing trainer log..."
    cp -n memory_templates/advanced/trainer_log.json memory/advanced/
fi

if [ ! -f memory/advanced/current_difficulty.json ]; then
    echo "Initializing difficulty settings..."
    cp -n memory_templates/advanced/current_difficulty.json memory/advanced/
fi

if [ ! -f memory/advanced/strategy_weights.json ]; then
    echo "Initializing strategy weights..."
    cp -n memory_templates/advanced/strategy_weights.json memory/advanced/
fi

# Start the system
echo "Starting Builder-Trainer Cognitive Loop..."
python loop.py

