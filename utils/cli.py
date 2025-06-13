#!/usr/bin/env python3
"""
utils/cli.py

This module provides a command-line interface for interacting with the Builder-Trainer Cognitive Loop system.
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import system components
from memory_manager import MemoryManager

def add_user_task(task_description, difficulty=0.5, constraints=None, skills=None, priority=1):
    """
    Add a user task to the task queue.
    
    Args:
        task_description: Description of the task
        difficulty: Task difficulty (0.0 to 1.0)
        constraints: List of constraints
        skills: List of required skills
        priority: Task priority (lower number = higher priority)
        
    Returns:
        The task ID
    """
    # Generate task ID
    task_id = f"user_{int(time.time())}"
    
    # Create task
    task = {
        "id": task_id,
        "source": "user",
        "goal": task_description,
        "difficulty": difficulty,
        "constraints": constraints or [],
        "skills_required": skills or ["python"],
        "expected_outcome": "A solution that meets the user's requirements",
        "created_at": datetime.now().isoformat(),
        "priority": priority
    }
    
    # Add task to queue
    MemoryManager.add_task_to_queue(task, priority)
    
    # Save task to memory
    task_path = f"memory/task_memory/task_{task_id}.json"
    MemoryManager.save(task_path, task)
    
    # Log the action
    MemoryManager.log_system_event(
        "INFO",
        "utils/cli.py",
        f"Added user task: {task_id}",
        {"task": task_description, "priority": priority}
    )
    
    return task_id

def list_tasks(count=10, status=None):
    """
    List recent tasks.
    
    Args:
        count: Number of tasks to list
        status: Filter by status (completed, failed, pending, running)
        
    Returns:
        List of tasks
    """
    # Get all task files
    task_dir = "memory/task_memory"
    task_files = [f for f in os.listdir(task_dir) if f.startswith("task_") and f.endswith(".json")]
    
    # Load tasks
    tasks = []
    for file_name in task_files:
        try:
            task = MemoryManager.load(os.path.join(task_dir, file_name))
            if status is None or task.get("status") == status:
                tasks.append(task)
        except:
            pass
    
    # Sort by creation time (newest first)
    tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Limit to count
    tasks = tasks[:count]
    
    return tasks

def get_task_details(task_id):
    """
    Get details of a specific task.
    
    Args:
        task_id: The task ID
        
    Returns:
        The task details
    """
    task_path = f"memory/task_memory/task_{task_id}.json"
    
    if not os.path.exists(task_path):
        print(f"Task {task_id} not found")
        return None
    
    task = MemoryManager.load(task_path)
    
    # Get reflection if available
    reflection_path = f"memory/task_memory/reflection_{task_id}.json"
    if os.path.exists(reflection_path):
        reflection = MemoryManager.load(reflection_path)
        task["reflection"] = reflection
    
    # Get code if available
    code_dir = f"memory/code_archive/{task_id}"
    if os.path.exists(code_dir):
        code_files = os.listdir(code_dir)
        if code_files:
            # Get the latest code file
            code_files.sort()
            latest_code_file = code_files[-1]
            code_path = os.path.join(code_dir, latest_code_file)
            
            with open(code_path, 'r') as f:
                code = f.read()
            
            task["code"] = code
            task["code_path"] = code_path
    
    return task

def get_builder_profile():
    """
    Get the Builder agent's profile.
    
    Returns:
        The Builder agent's profile
    """
    profile_path = "memory/core/builder_profile.json"
    return MemoryManager.load(profile_path)

def get_skill_map():
    """
    Get the skill map.
    
    Returns:
        The skill map
    """
    skill_map_path = "memory/core/skill_map.json"
    return MemoryManager.load(skill_map_path)

def get_performance_trend():
    """
    Get the performance trend.
    
    Returns:
        The performance trend
    """
    return ScoreEngine.get_performance_trend()

def main():
    """
    Main entry point for the CLI.
    """
    parser = argparse.ArgumentParser(description="Builder-Trainer CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Add task command
    add_parser = subparsers.add_parser("add-task", help="Add a user task")
    add_parser.add_argument("description", help="Task description")
    add_parser.add_argument("--difficulty", type=float, default=0.5, help="Task difficulty (0.0 to 1.0)")
    add_parser.add_argument("--constraints", nargs="+", help="Task constraints")
    add_parser.add_argument("--skills", nargs="+", help="Required skills")
    add_parser.add_argument("--priority", type=int, default=1, help="Task priority (lower number = higher priority)")
    
    # List tasks command
    list_parser = subparsers.add_parser("list-tasks", help="List recent tasks")
    list_parser.add_argument("--count", type=int, default=10, help="Number of tasks to list")
    list_parser.add_argument("--status", choices=["completed", "failed", "pending", "running"], help="Filter by status")
    
    # Get task details command
    get_parser = subparsers.add_parser("get-task", help="Get task details")
    get_parser.add_argument("task_id", help="Task ID")
    
    # Get builder profile command
    subparsers.add_parser("get-profile", help="Get builder profile")
    
    # Get skill map command
    subparsers.add_parser("get-skills", help="Get skill map")
    
    # Get performance trend command
    subparsers.add_parser("get-trend", help="Get performance trend")
    
    args = parser.parse_args()
    
    if args.command == "add-task":
        task_id = add_user_task(
            args.description,
            args.difficulty,
            args.constraints,
            args.skills,
            args.priority
        )
        print(f"Added task: {task_id}")
    
    elif args.command == "list-tasks":
        tasks = list_tasks(args.count, args.status)
        print(f"Found {len(tasks)} tasks:")
        for task in tasks:
            print(f"  {task['id']}: {task.get('goal', '')} (status: {task.get('status', 'unknown')})")
    
    elif args.command == "get-task":
        task = get_task_details(args.task_id)
        if task:
            print(json.dumps(task, indent=2))
    
    elif args.command == "get-profile":
        profile = get_builder_profile()
        print(json.dumps(profile, indent=2))
    
    elif args.command == "get-skills":
        skill_map = get_skill_map()
        print(json.dumps(skill_map, indent=2))
    
    elif args.command == "get-trend":
        trend = get_performance_trend()
        print(json.dumps(trend, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

