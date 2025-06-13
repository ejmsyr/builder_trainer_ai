#!/usr/bin/env python3
"""
loop.py

This is the main orchestrator for the Builder-Trainer Cognitive Loop system.
It manages the overall execution flow, including task retrieval, execution, and postprocessing.
"""

import os
import sys
import time
import json
import logging
import traceback
import argparse
from typing import Dict, Optional
from datetime import datetime

# Import system components
from memory_manager import MemoryManager
from llm_interface import LLMInterface
from score_engine import ScoreEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("memory/logs/loop.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("loop")

class BuilderTrainerLoop:
    """
    The main orchestrator for the Builder-Trainer Cognitive Loop system.
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the BuilderTrainerLoop.
        
        Args:
            config_path: Path to the configuration file
        """
        # Ensure directories exist
        self._ensure_directories()
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize state
        self.current_task = None
        self.running = False
        self.pause_requested = False
        self.stop_requested = False
        
        logger.info("BuilderTrainerLoop initialized")
    
    def _ensure_directories(self) -> None:
        """
        Ensure that all required directories exist.
        """
        directories = [
            "memory/core",
            "memory/advanced",
            "memory/task_memory",
            "memory/code_archive",
            "memory/logs"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        logger.debug("Directories created")
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load the configuration file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            The configuration as a dictionary
        """
        default_config = {
            "loop_interval": 5,  # seconds
            "max_consecutive_errors": 3,
            "error_cooldown": 60,  # seconds
            "task_timeout": 600,  # seconds
            "enable_trainer": True,
            "enable_user_tasks": True,
            "default_difficulty": 0.5
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded configuration from {config_path}")
                
                # Merge with default config to ensure all keys are present
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                
                return config
            except Exception as e:
                logger.error(f"Error loading configuration: {e}")
                return default_config
        else:
            logger.warning(f"Configuration file {config_path} not found, using defaults")
            
            # Save default config
            try:
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info(f"Created default configuration at {config_path}")
            except Exception as e:
                logger.error(f"Error creating default configuration: {e}")
            
            return default_config
    
    def get_task(self) -> Optional[Dict]:
        """
        Get the next task to execute.
        
        Returns:
            The next task, or None if no task is available
        """
        # Check for user tasks first (higher priority)
        if self.config["enable_user_tasks"]:
            user_task = MemoryManager.get_next_task_from_queue()
            if user_task:
                logger.info(f"Retrieved user task: {user_task['id']}")
                return user_task
        
        # If no user task and trainer is enabled, generate a task
        if self.config["enable_trainer"]:
            try:
                # Load builder profile
                profile = MemoryManager.load("memory/core/builder_profile.json", default={
                    "id": "builder_v0.1",
                    "task_count": 0,
                    "average_score": 0,
                    "skills_mastered": [],
                    "weak_skills": [],
                    "style_flags": {},
                    "last_updated": datetime.now().isoformat()
                })
                
                # Get performance trend
                trend = ScoreEngine.get_performance_trend()
                
                # Adjust difficulty
                difficulty = ScoreEngine.adjust_difficulty(
                    self.config["default_difficulty"],
                    trend
                )
                
                # Generate task
                task = LLMInterface.generate_task(profile, difficulty)
                
                logger.info(f"Generated trainer task: {task['id']} (difficulty: {difficulty})")
                return task
            except Exception as e:
                logger.error(f"Error generating task: {e}")
                return None
        
        logger.info("No tasks available")
        return None
    
    def execute_task(self, task: Dict) -> Dict:
        """
        Execute a task using the Builder agent.
        
        Args:
            task: The task to execute
            
        Returns:
            The result of the task execution
        """
        logger.info(f"Executing task: {task['id']}")
        
        # Log the start of task execution
        MemoryManager.log_system_event(
            "INFO",
            "loop.py",
            f"Started task execution for {task['id']}"
        )
        
        # Save task to memory
        task_path = f"memory/task_memory/task_{task['id']}.json"
        MemoryManager.save(task_path, task)
        
        try:
            # Import builder components (lazy import to avoid circular dependencies)
            from builder.run_project import run_project
            
            # Set task status to running
            MemoryManager.update(task_path, "status", "running")
            
            # Execute task with timeout
            start_time = time.time()
            result = run_project(task)
            end_time = time.time()
            
            # Add execution time to result
            result["execution_time"] = end_time - start_time
            
            logger.info(f"Task {task['id']} executed: success={result.get('success', False)}")
            
            return result
        except Exception as e:
            logger.error(f"Error executing task {task['id']}: {e}")
            traceback.print_exc()
            
            # Create error result
            error_result = {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            
            return error_result
    
    def postprocess(self, task: Dict, result: Dict) -> None:
        """
        Postprocess a task execution.
        
        Args:
            task: The task that was executed
            result: The result of the task execution
        """
        logger.info(f"Postprocessing task: {task['id']}")
        
        try:
            # Import builder components (lazy import to avoid circular dependencies)
            from builder.reflect import reflect_on_task
            
            # Get the generated code
            code_path = result.get("code_path", "")
            code = ""
            if code_path and os.path.exists(code_path):
                with open(code_path, 'r') as f:
                    code = f.read()
            
            # Generate reflection
            reflection = reflect_on_task(task, result, code)
            
            # Update task with reflection
            task_path = f"memory/task_memory/task_{task['id']}.json"
            MemoryManager.update(task_path, "reflection", reflection)
            
            # Update task status
            status = "completed" if result.get("success", False) else "failed"
            MemoryManager.update(task_path, "status", status)
            
            # Update builder profile
            MemoryManager.update_builder_profile(result)
            
            # Update skill levels
            ScoreEngine.update_skill_levels(task, reflection)
            
            logger.info(f"Task {task['id']} postprocessed")
        except Exception as e:
            logger.error(f"Error postprocessing task {task['id']}: {e}")
            traceback.print_exc()
    
    def handle_error(self, e: Exception) -> None:
        """
        Handle an error in the main loop.
        
        Args:
            e: The exception that was raised
        """
        logger.error(f"Error in main loop: {e}")
        traceback.print_exc()
        
        # Log the error
        MemoryManager.log_system_event(
            "ERROR",
            "loop.py",
            "Error in main loop",
            {"error": str(e), "traceback": traceback.format_exc()}
        )
        
        # Sleep for a short time to avoid rapid error loops
        time.sleep(self.config["error_cooldown"])
    
    def run(self) -> None:
        """
        Run the main loop.
        """
        logger.info("Starting main loop")
        self.running = True
        consecutive_errors = 0
        
        while self.running:
            try:
                # Check for stop request
                if self.stop_requested:
                    logger.info("Stop requested, exiting loop")
                    break
                
                # Check for pause request
                if self.pause_requested:
                    logger.info("Pause requested, waiting")
                    time.sleep(self.config["loop_interval"])
                    continue
                
                # Get task
                task = self.get_task()
                if not task:
                    logger.info("No task available, waiting")
                    time.sleep(self.config["loop_interval"])
                    continue
                
                # Set current task
                self.current_task = task
                
                # Execute task
                result = self.execute_task(task)
                
                # Postprocess task
                self.postprocess(task, result)
                
                # Reset error counter
                consecutive_errors = 0
                
                # Clear current task
                self.current_task = None
                
                # Sleep for a short time
                time.sleep(self.config["loop_interval"])
            except Exception as e:
                consecutive_errors += 1
                self.handle_error(e)
                
                # If too many consecutive errors, exit
                if consecutive_errors >= self.config["max_consecutive_errors"]:
                    logger.error(f"Too many consecutive errors ({consecutive_errors}), exiting loop")
                    self.running = False
        
        logger.info("Main loop exited")
    
    def pause(self) -> None:
        """
        Pause the main loop.
        """
        logger.info("Pause requested")
        self.pause_requested = True
    
    def resume(self) -> None:
        """
        Resume the main loop.
        """
        logger.info("Resume requested")
        self.pause_requested = False
    
    def stop(self) -> None:
        """
        Stop the main loop.
        """
        logger.info("Stop requested")
        self.stop_requested = True


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Builder-Trainer Cognitive Loop")
    parser.add_argument("--config", default="config.json", help="Path to configuration file")
    parser.add_argument("--no-trainer", action="store_true", help="Disable trainer")
    parser.add_argument("--no-user-tasks", action="store_true", help="Disable user tasks")
    args = parser.parse_args()
    
    try:
        # Create loop
        loop = BuilderTrainerLoop(args.config)
        
        # Apply command-line overrides
        if args.no_trainer:
            loop.config["enable_trainer"] = False
        if args.no_user_tasks:
            loop.config["enable_user_tasks"] = False
        
        # Run loop
        loop.run()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, exiting")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

