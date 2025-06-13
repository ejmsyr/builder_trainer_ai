#!/usr/bin/env python3
"""
memory_manager.py

This module provides a unified interface for reading, writing, and updating JSON memory files
for the Builder-Trainer Cognitive Loop system.
"""

import os
import json
import time
import logging
import fcntl
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("memory/logs/memory_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("memory_manager")

class MemoryManager:
    """
    A class that provides methods for reading, writing, and updating JSON memory files.
    """
    
    @staticmethod
    def ensure_directory_exists(file_path: str) -> None:
        """
        Ensure that the directory for the given file path exists.
        
        Args:
            file_path: The path to the file
        """
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    @staticmethod
    def load(file_path: str, default: Optional[Any] = None) -> Any:
        """
        Load JSON data from a file.
        
        Args:
            file_path: The path to the JSON file
            default: The default value to return if the file doesn't exist
            
        Returns:
            The loaded JSON data, or the default value if the file doesn't exist
        """
        try:
            if not os.path.exists(file_path):
                if default is not None:
                    logger.info(f"File {file_path} not found, returning default value")
                    return default
                else:
                    logger.error(f"File {file_path} not found and no default value provided")
                    raise FileNotFoundError(f"File {file_path} not found")
            
            with open(file_path, 'r') as f:
                # Acquire a shared lock for reading
                fcntl.flock(f, fcntl.LOCK_SH)
                try:
                    data = json.load(f)
                    logger.debug(f"Loaded data from {file_path}")
                    return data
                finally:
                    # Release the lock
                    fcntl.flock(f, fcntl.LOCK_UN)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {file_path}: {e}")
            if default is not None:
                return default
            raise
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            if default is not None:
                return default
            raise
    
    @staticmethod
    def save(file_path: str, data: Any) -> None:
        """
        Save data to a JSON file.
        
        Args:
            file_path: The path to the JSON file
            data: The data to save
        """
        try:
            MemoryManager.ensure_directory_exists(file_path)
            
            # Create a temporary file
            temp_file = f"{file_path}.tmp"
            with open(temp_file, 'w') as f:
                # Acquire an exclusive lock for writing
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    json.dump(data, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                finally:
                    # Release the lock
                    fcntl.flock(f, fcntl.LOCK_UN)
            
            # Atomically replace the original file
            os.rename(temp_file, file_path)
            logger.debug(f"Saved data to {file_path}")
        except Exception as e:
            logger.error(f"Error saving to {file_path}: {e}")
            # Clean up the temporary file if it exists
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise
    
    @staticmethod
    def append(file_path: str, new_entry: Any) -> None:
        """
        Append a new entry to a JSON array file.
        
        Args:
            file_path: The path to the JSON file
            new_entry: The new entry to append
        """
        try:
            # Load existing data or create an empty array
            data = MemoryManager.load(file_path, default=[])
            
            # Ensure data is a list
            if not isinstance(data, list):
                logger.error(f"Cannot append to {file_path}: file does not contain a JSON array")
                raise TypeError(f"Cannot append to {file_path}: file does not contain a JSON array")
            
            # Append the new entry
            data.append(new_entry)
            
            # Save the updated data
            MemoryManager.save(file_path, data)
            logger.debug(f"Appended entry to {file_path}")
        except Exception as e:
            logger.error(f"Error appending to {file_path}: {e}")
            raise
    
    @staticmethod
    def update(file_path: str, key: str, value: Any) -> None:
        """
        Update a specific key in a JSON object file.
        
        Args:
            file_path: The path to the JSON file
            key: The key to update
            value: The new value
        """
        try:
            # Load existing data or create an empty object
            data = MemoryManager.load(file_path, default={})
            
            # Ensure data is a dictionary
            if not isinstance(data, dict):
                logger.error(f"Cannot update {file_path}: file does not contain a JSON object")
                raise TypeError(f"Cannot update {file_path}: file does not contain a JSON object")
            
            # Update the key
            data[key] = value
            
            # Save the updated data
            MemoryManager.save(file_path, data)
            logger.debug(f"Updated key '{key}' in {file_path}")
        except Exception as e:
            logger.error(f"Error updating {file_path}: {e}")
            raise
    
    @staticmethod
    def get_task_by_id(task_id: str) -> Dict:
        """
        Get a task by its ID.
        
        Args:
            task_id: The ID of the task
            
        Returns:
            The task data
        """
        file_path = f"memory/task_memory/task_{task_id}.json"
        return MemoryManager.load(file_path)
    
    @staticmethod
    def get_next_task_from_queue() -> Optional[Dict]:
        """
        Get the next task from the task queue.
        
        Returns:
            The next task, or None if the queue is empty
        """
        queue_path = "memory/task_memory/task_queue.json"
        queue_data = MemoryManager.load(queue_path, default={"queue": []})
        
        if not queue_data["queue"]:
            logger.info("Task queue is empty")
            return None
        
        # Get the highest priority task (lower number = higher priority)
        queue_data["queue"].sort(key=lambda x: x.get("priority", 999))
        next_task = queue_data["queue"].pop(0)
        
        # Save the updated queue
        MemoryManager.save(queue_path, queue_data)
        
        logger.info(f"Retrieved task {next_task['id']} from queue")
        return next_task
    
    @staticmethod
    def add_task_to_queue(task: Dict, priority: int = 10) -> None:
        """
        Add a task to the task queue.
        
        Args:
            task: The task to add
            priority: The priority of the task (lower number = higher priority)
        """
        queue_path = "memory/task_memory/task_queue.json"
        queue_data = MemoryManager.load(queue_path, default={"queue": []})
        
        # Add priority if not present
        if "priority" not in task:
            task["priority"] = priority
        
        # Add timestamp if not present
        if "created_at" not in task:
            task["created_at"] = datetime.now().isoformat()
        
        queue_data["queue"].append(task)
        MemoryManager.save(queue_path, queue_data)
        logger.info(f"Added task {task['id']} to queue with priority {priority}")
    
    @staticmethod
    def log_system_event(level: str, component: str, message: str, details: Optional[Dict] = None) -> None:
        """
        Log a system event.
        
        Args:
            level: The log level (INFO, WARNING, ERROR, etc.)
            component: The component that generated the event
            message: The event message
            details: Additional details about the event
        """
        log_path = "memory/logs/system_log.json"
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "component": component,
            "message": message
        }
        
        if details:
            event["details"] = details
        
        MemoryManager.append(log_path, event)
        
        # Also log to Python's logging system
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(f"{component}: {message}")
    
    @staticmethod
    def update_builder_profile(result: Dict) -> None:
        """
        Update the builder profile based on task results.
        
        Args:
            result: The task result
        """
        profile_path = "memory/core/builder_profile.json"
        profile = MemoryManager.load(profile_path, default={
            "id": "builder_v0.1",
            "task_count": 0,
            "average_score": 0,
            "skills_mastered": [],
            "weak_skills": [],
            "style_flags": {},
            "last_updated": datetime.now().isoformat()
        })
        
        # Update task count
        profile["task_count"] += 1
        
        # Update average score
        if "score" in result:
            old_avg = profile["average_score"]
            task_count = profile["task_count"]
            profile["average_score"] = (old_avg * (task_count - 1) + result["score"]) / task_count
        
        # Update last updated timestamp
        profile["last_updated"] = datetime.now().isoformat()
        
        MemoryManager.save(profile_path, profile)
        logger.info(f"Updated builder profile: task_count={profile['task_count']}, average_score={profile['average_score']}")
    
    @staticmethod
    def save_task_result(task_id: str, result: Dict) -> None:
        """
        Save a task result.
        
        Args:
            task_id: The ID of the task
            result: The task result
        """
        task_path = f"memory/task_memory/task_{task_id}.json"
        task = MemoryManager.load(task_path, default={
            "id": task_id,
            "status": "unknown",
            "attempts": 0,
            "max_attempts": 3,
            "created_at": datetime.now().isoformat()
        })
        
        # Update task with result
        task["status"] = "completed" if result.get("success", False) else "failed"
        task["attempts"] += 1
        task["result"] = result
        task["updated_at"] = datetime.now().isoformat()
        
        MemoryManager.save(task_path, task)
        logger.info(f"Saved result for task {task_id}: status={task['status']}, attempts={task['attempts']}")
        
        # If the task failed and has not reached max attempts, requeue it
        if task["status"] == "failed" and task["attempts"] < task["max_attempts"]:
            task_copy = task.copy()
            task_copy["priority"] = 5  # Higher priority for retry
            MemoryManager.add_task_to_queue(task_copy)
            logger.info(f"Requeued failed task {task_id} for retry (attempt {task['attempts']} of {task['max_attempts']})")
        
        # Log the score if available
        if "score" in result:
            score_entry = {
                "task_id": task_id,
                "score": result["score"],
                "difficulty": task.get("difficulty", 0.5),
                "source": task.get("source", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
            
            if "metrics" in result:
                score_entry["metrics"] = result["metrics"]
            
            MemoryManager.append("memory/core/score_log.json", score_entry)
            logger.info(f"Logged score for task {task_id}: {result['score']}")


if __name__ == "__main__":
    # Simple test
    try:
        # Ensure log directory exists
        os.makedirs("memory/logs", exist_ok=True)
        
        # Test saving and loading
        test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
        MemoryManager.save("memory/test.json", test_data)
        loaded_data = MemoryManager.load("memory/test.json")
        assert loaded_data["test"] == "data"
        print("Save/load test passed")
        
        # Test appending
        MemoryManager.append("memory/test_array.json", {"item": 1})
        MemoryManager.append("memory/test_array.json", {"item": 2})
        array_data = MemoryManager.load("memory/test_array.json")
        assert len(array_data) == 2
        assert array_data[1]["item"] == 2
        print("Append test passed")
        
        # Test updating
        MemoryManager.update("memory/test.json", "updated", True)
        updated_data = MemoryManager.load("memory/test.json")
        assert updated_data["updated"] is True
        print("Update test passed")
        
        # Test logging
        MemoryManager.log_system_event("INFO", "test", "Test message")
        print("Logging test passed")
        
        print("All tests passed")
    except Exception as e:
        print(f"Test failed: {e}")

