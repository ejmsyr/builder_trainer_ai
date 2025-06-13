#!/usr/bin/env python3
"""
builder/run_project.py

This module provides functionality for executing coding tasks using the LLM and shell commands
in the Builder-Trainer Cognitive Loop system.
"""

import os
import sys
import time
import json
import logging
import traceback
from typing import Dict, List, Optional, Union, Any

# Import system components
from memory_manager import MemoryManager
from llm_interface import LLMInterface
from score_engine import ScoreEngine
from executor.run_cmd import CommandExecutor
from executor.run_code import CodeExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("memory/logs/builder.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("builder.run_project")

class BuilderAgent:
    """
    A class that provides methods for executing coding tasks.
    """
    
    @staticmethod
    def run_project(task: Dict) -> Dict:
        """
        Execute a coding task.
        
        Args:
            task: The task to execute
            
        Returns:
            Dictionary with task execution results
        """
        logger.info(f"Running project for task: {task['id']}")
        
        # Create task directory in code archive
        task_dir = os.path.join("memory/code_archive", task["id"])
        os.makedirs(task_dir, exist_ok=True)
        
        try:
            # Parse task
            goal = task.get("goal", "")
            constraints = task.get("constraints", [])
            skills_required = task.get("skills_required", [])
            expected_outcome = task.get("expected_outcome", "")
            
            # Log task details
            logger.info(f"Task goal: {goal}")
            logger.info(f"Task constraints: {constraints}")
            logger.info(f"Skills required: {skills_required}")
            
            # Generate code using LLM
            code = BuilderAgent._generate_code(task)
            
            # Archive the generated code
            code_path = CodeExecutor.archive_code(code, task["id"])
            
            # Execute code
            execution_result = BuilderAgent._execute_code(code, task)
            
            # Evaluate results
            evaluation = BuilderAgent._evaluate_results(task, code, execution_result)
            
            # Calculate score
            score_data = ScoreEngine.calculate_score(
                metrics=evaluation["metrics"],
                difficulty=task.get("difficulty", 0.5),
                source=task.get("source", "trainer")
            )
            
            # Track score
            ScoreEngine.track_score(task["id"], score_data)
            
            # Prepare result
            result = {
                "success": evaluation["success"],
                "score": score_data["score"],
                "metrics": evaluation["metrics"],
                "code_path": code_path,
                "execution_result": execution_result,
                "evaluation": evaluation
            }
            
            logger.info(f"Task {task['id']} completed: success={result['success']}, score={result['score']}")
            
            return result
        except Exception as e:
            logger.error(f"Error running project for task {task['id']}: {e}")
            traceback.print_exc()
            
            # Create error result
            error_result = {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            
            return error_result
    
    @staticmethod
    def _generate_code(task: Dict) -> str:
        """
        Generate code for a task using the LLM.
        
        Args:
            task: The task to generate code for
            
        Returns:
            The generated code as a string
        """
        logger.info(f"Generating code for task: {task['id']}")
        
        # Prepare prompt
        goal = task.get("goal", "")
        constraints = task.get("constraints", [])
        skills_required = task.get("skills_required", [])
        expected_outcome = task.get("expected_outcome", "")
        
        constraints_str = "\n".join([f"- {constraint}" for constraint in constraints])
        skills_str = ", ".join(skills_required)
        
        prompt = f"""Generate Python code for the following task:

GOAL:
{goal}

CONSTRAINTS:
{constraints_str}

SKILLS REQUIRED:
{skills_str}

EXPECTED OUTCOME:
{expected_outcome}

Write clean, efficient, and well-documented Python code that accomplishes the goal while adhering to the constraints.
Include comments explaining your approach and any important implementation details.
"""
        
        # Generate code
        code = LLMInterface.code_completion(prompt)
        
        logger.info(f"Generated code for task {task['id']} ({len(code)} characters)")
        
        return code
    
    @staticmethod
    def _execute_code(code: str, task: Dict) -> Dict:
        """
        Execute the generated code.
        
        Args:
            code: The code to execute
            task: The task being executed
            
        Returns:
            Dictionary with execution results
        """
        logger.info(f"Executing code for task: {task['id']}")
        
        # Create log file path
        log_file = f"memory/logs/{task['id']}_execution.log"
        
        # Create save path
        save_path = f"memory/code_archive/{task['id']}/execution_code.py"
        
        # Execute code
        result = CodeExecutor.run_python_code(
            code=code,
            timeout=300,  # 5 minutes
            log_file=log_file,
            save_path=save_path
        )
        
        logger.info(f"Code execution for task {task['id']} completed: success={result['success']}")
        
        return result
    
    @staticmethod
    def _evaluate_results(task: Dict, code: str, execution_result: Dict) -> Dict:
        """
        Evaluate the results of code execution.
        
        Args:
            task: The task being executed
            code: The code that was executed
            execution_result: The results of code execution
            
        Returns:
            Dictionary with evaluation results
        """
        logger.info(f"Evaluating results for task: {task['id']}")
        
        # Analyze code quality
        code_analysis = LLMInterface.analyze_code(code)
        
        # Determine success based on execution result and code analysis
        success = execution_result.get("success", False)
        
        # Extract metrics from code analysis
        metrics = code_analysis.get("scores", {})
        
        # If execution failed, reduce correctness score
        if not success:
            metrics["correctness"] = min(metrics.get("correctness", 0.0), 0.3)
        
        # Prepare evaluation result
        evaluation = {
            "success": success,
            "metrics": metrics,
            "analysis": code_analysis,
            "execution_success": execution_result.get("success", False),
            "execution_error": execution_result.get("error", None)
        }
        
        logger.info(f"Evaluation for task {task['id']}: success={evaluation['success']}")
        
        return evaluation


# Alias for backward compatibility
run_project = BuilderAgent.run_project


if __name__ == "__main__":
    # Simple test
    try:
        # Ensure directories exist
        os.makedirs("memory/logs", exist_ok=True)
        os.makedirs("memory/code_archive", exist_ok=True)
        
        # Create a test task
        test_task = {
            "id": "test_task_002",
            "source": "trainer",
            "goal": "Write a function to calculate the factorial of a number",
            "difficulty": 0.3,
            "constraints": ["Must handle negative numbers", "Must use recursion"],
            "skills_required": ["python", "recursion"],
            "expected_outcome": "A function that correctly calculates factorials"
        }
        
        # Run the project
        result = BuilderAgent.run_project(test_task)
        
        print(f"Project result: {json.dumps(result, indent=2)}")
        
        print("Test passed")
    except Exception as e:
        print(f"Test failed: {e}")

