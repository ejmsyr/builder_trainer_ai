#!/usr/bin/env python3
"""
trainer/generate_task.py

This module provides functionality for generating tasks for the Builder agent
in the Builder-Trainer Cognitive Loop system.
"""

import os
import sys
import time
import json
import logging
import random
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

# Import system components
from memory_manager import MemoryManager
from llm_interface import LLMInterface
from trainer.analyze_builder import BuilderAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("memory/logs/trainer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("trainer.generate_task")

class TaskGenerator:
    """
    A class that provides methods for generating tasks for the Builder agent.
    """
    
    # Task templates for different focus areas
    TASK_TEMPLATES = {
        "skill_gap": {
            "python": [
                "Create a Python script that {goal} using {technique}",
                "Implement a Python function to {goal} with {constraint}",
                "Build a Python class that {goal} and handles {edge_case}"
            ],
            "error_handling": [
                "Create a robust Python function that {goal} with comprehensive error handling",
                "Implement a system that {goal} and gracefully handles all potential errors",
                "Build a Python script that {goal} with try-except blocks for all edge cases"
            ],
            "testing": [
                "Create a Python module with unit tests that {goal}",
                "Implement a function and test suite that {goal}",
                "Build a testable Python class that {goal} with 100% test coverage"
            ],
            "file_io": [
                "Create a Python script that {goal} by reading and writing files",
                "Implement a file processing system that {goal}",
                "Build a data pipeline that {goal} using file operations"
            ],
            "json_parsing": [
                "Create a JSON parser that {goal} and handles nested structures",
                "Implement a system that {goal} by processing JSON data",
                "Build a JSON validation tool that {goal}"
            ],
            "default": [
                "Create a Python script that {goal}",
                "Implement a function that {goal}",
                "Build a system that {goal}"
            ]
        },
        "style_issue": {
            "hardcoded_paths": [
                "Create a configurable system that {goal} without hardcoded paths",
                "Implement a Python script that {goal} using configuration files",
                "Build a flexible tool that {goal} with dynamic path resolution"
            ],
            "missing_error_handling": [
                "Create a robust Python function that {goal} with comprehensive error handling",
                "Implement a system that {goal} and gracefully handles all potential errors",
                "Build a Python script that {goal} with try-except blocks for all edge cases"
            ],
            "poor_documentation": [
                "Create a well-documented Python module that {goal}",
                "Implement a function with clear docstrings that {goal}",
                "Build a Python class with comprehensive documentation that {goal}"
            ],
            "poor_variable_names": [
                "Create a Python script with clear, descriptive variable names that {goal}",
                "Implement a function with self-documenting variable names that {goal}",
                "Build a system with consistent naming conventions that {goal}"
            ],
            "default": [
                "Create a Python script that {goal} with good coding practices",
                "Implement a function that {goal} following best practices",
                "Build a system that {goal} with clean code principles"
            ]
        },
        "learning": {
            "regression_prevention": [
                "Create a Python script that {goal} using {skill}",
                "Implement a function that {goal} with {skill}",
                "Build a system that {goal} leveraging {skill}"
            ],
            "skill_advancement": [
                "Create an advanced Python script that {goal} using {skill}",
                "Implement a sophisticated function that {goal} with {skill}",
                "Build a complex system that {goal} leveraging {skill}"
            ],
            "default": [
                "Create a Python script that {goal}",
                "Implement a function that {goal}",
                "Build a system that {goal}"
            ]
        },
        "general_improvement": [
            "Create a Python script that {goal}",
            "Implement a function that {goal}",
            "Build a system that {goal}",
            "Develop a tool that {goal}",
            "Design an algorithm that {goal}"
        ]
    }
    
    # Goal templates for different focus areas
    GOAL_TEMPLATES = {
        "skill_gap": {
            "python": [
                "processes data from multiple sources",
                "implements a custom data structure",
                "solves a complex algorithmic problem",
                "automates a repetitive task"
            ],
            "error_handling": [
                "processes user input with validation",
                "handles network requests with timeouts and retries",
                "validates and processes external data",
                "manages system resources safely"
            ],
            "testing": [
                "implements a feature with comprehensive tests",
                "refactors legacy code with test coverage",
                "creates a testable API",
                "validates input data with test cases"
            ],
            "file_io": [
                "processes large files efficiently",
                "manages a directory of files",
                "implements a file-based database",
                "handles concurrent file access"
            ],
            "json_parsing": [
                "validates and transforms JSON data",
                "converts between JSON and other formats",
                "implements a JSON schema validator",
                "processes nested JSON structures"
            ]
        },
        "style_issue": {
            "hardcoded_paths": [
                "processes files from configurable locations",
                "manages resources with dynamic paths",
                "loads configuration from multiple sources",
                "implements a plugin system with dynamic loading"
            ],
            "missing_error_handling": [
                "processes external data with validation",
                "handles network requests robustly",
                "manages system resources with error recovery",
                "implements a fault-tolerant service"
            ],
            "poor_documentation": [
                "implements a public API with documentation",
                "creates a library with usage examples",
                "develops a command-line tool with help text",
                "builds a framework with developer guides"
            ],
            "poor_variable_names": [
                "implements a complex algorithm with clear naming",
                "processes data with self-documenting code",
                "builds a state machine with descriptive states",
                "creates a configuration system with meaningful options"
            ]
        }
    }
    
    # Constraint templates
    CONSTRAINT_TEMPLATES = [
        "Must handle invalid input gracefully",
        "Must be memory efficient",
        "Must be thread-safe",
        "Must include comprehensive error handling",
        "Must include unit tests",
        "Must use object-oriented design",
        "Must be extensible for future requirements",
        "Must include clear documentation",
        "Must follow PEP 8 style guidelines",
        "Must handle edge cases",
        "Must be optimized for performance",
        "Must use appropriate design patterns",
        "Must minimize external dependencies",
        "Must include logging",
        "Must be configurable without code changes"
    ]
    
    @staticmethod
    def generate_task(analysis: Optional[Dict] = None) -> Dict:
        """
        Generate a task for the Builder agent.
        
        Args:
            analysis: Optional analysis of the Builder agent's profile
            
        Returns:
            Dictionary with the generated task
        """
        logger.info("Generating task for Builder agent")
        
        try:
            # If no analysis provided, generate one
            if analysis is None:
                analysis = BuilderAnalyzer.analyze_builder_profile()
            
            # Get recommended focus
            recommended_focus = analysis.get("recommended_focus", "general_improvement")
            logger.info(f"Recommended focus: {recommended_focus}")
            
            # Parse focus
            focus_parts = recommended_focus.split(":")
            focus_type = focus_parts[0]
            
            # Generate task based on focus
            if focus_type == "skill_gap" and len(focus_parts) > 1:
                skill = focus_parts[1]
                task = TaskGenerator._generate_skill_gap_task(skill, analysis)
            elif focus_type == "style_issue" and len(focus_parts) > 1:
                issue = focus_parts[1]
                task = TaskGenerator._generate_style_issue_task(issue, analysis)
            elif focus_type == "learning" and len(focus_parts) > 2:
                learning_type = focus_parts[1]
                skill = focus_parts[2]
                task = TaskGenerator._generate_learning_task(learning_type, skill, analysis)
            else:
                task = TaskGenerator._generate_general_improvement_task(analysis)
            
            # Add metadata
            task["source"] = "trainer"
            task["created_at"] = datetime.now().isoformat()
            
            # Save task to memory
            task_path = f"memory/task_memory/task_{task['id']}.json"
            MemoryManager.save(task_path, task)
            
            # Log task generation
            logger.info(f"Generated task: {task['id']} - {task['goal']}")
            
            # Log to trainer log
            trainer_log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": "generate_task",
                "task_id": task["id"],
                "focus": recommended_focus,
                "difficulty": task["difficulty"]
            }
            MemoryManager.append("memory/advanced/trainer_log.json", trainer_log_entry)
            
            return task
        except Exception as e:
            logger.error(f"Error generating task: {e}")
            
            # Create a fallback task
            fallback_task = {
                "id": f"fallback_{int(time.time())}",
                "source": "trainer",
                "goal": "Create a simple Python function that calculates the factorial of a number",
                "difficulty": 0.3,
                "constraints": [
                    "Must handle negative numbers",
                    "Must include error handling",
                    "Must include docstrings"
                ],
                "skills_required": ["python", "error_handling"],
                "expected_outcome": "A function that correctly calculates factorials",
                "created_at": datetime.now().isoformat()
            }
            
            return fallback_task
    
    @staticmethod
    def _generate_skill_gap_task(skill: str, analysis: Dict) -> Dict:
        """
        Generate a task to address a skill gap.
        
        Args:
            skill: The skill to focus on
            analysis: Analysis of the Builder agent's profile
            
        Returns:
            Dictionary with the generated task
        """
        # Get skill templates
        templates = TaskGenerator.TASK_TEMPLATES["skill_gap"].get(
            skill, TaskGenerator.TASK_TEMPLATES["skill_gap"]["default"]
        )
        
        # Get goal templates
        goal_templates = TaskGenerator.GOAL_TEMPLATES["skill_gap"].get(
            skill, ["solves a specific problem", "implements a useful feature", "automates a task"]
        )
        
        # Select random templates
        task_template = random.choice(templates)
        goal = random.choice(goal_templates)
        
        # Generate technique or constraint
        techniques = [
            "object-oriented programming",
            "functional programming",
            "recursion",
            "iteration",
            "list comprehensions",
            "generators",
            "decorators",
            "context managers"
        ]
        technique = random.choice(techniques)
        
        # Generate edge case
        edge_cases = [
            "invalid input",
            "missing data",
            "network failures",
            "resource constraints",
            "concurrent access",
            "large datasets"
        ]
        edge_case = random.choice(edge_cases)
        
        # Format task template
        task_goal = task_template.format(
            goal=goal,
            technique=technique,
            constraint=random.choice(TaskGenerator.CONSTRAINT_TEMPLATES),
            edge_case=edge_case
        )
        
        # Generate constraints
        constraints = TaskGenerator._generate_constraints(skill)
        
        # Generate task ID
        task_id = f"{skill}_{int(time.time())}"
        
        # Determine difficulty (start low for skill gaps)
        difficulty = 0.3
        
        # Create task
        task = {
            "id": task_id,
            "goal": task_goal,
            "difficulty": difficulty,
            "constraints": constraints,
            "skills_required": [skill],
            "expected_outcome": f"A solution that demonstrates proficiency in {skill}"
        }
        
        return task
    
    @staticmethod
    def _generate_style_issue_task(issue: str, analysis: Dict) -> Dict:
        """
        Generate a task to address a style issue.
        
        Args:
            issue: The style issue to focus on
            analysis: Analysis of the Builder agent's profile
            
        Returns:
            Dictionary with the generated task
        """
        # Get issue templates
        templates = TaskGenerator.TASK_TEMPLATES["style_issue"].get(
            issue, TaskGenerator.TASK_TEMPLATES["style_issue"]["default"]
        )
        
        # Get goal templates
        goal_templates = TaskGenerator.GOAL_TEMPLATES["style_issue"].get(
            issue, ["solves a specific problem", "implements a useful feature", "automates a task"]
        )
        
        # Select random templates
        task_template = random.choice(templates)
        goal = random.choice(goal_templates)
        
        # Format task template
        task_goal = task_template.format(goal=goal)
        
        # Generate constraints based on the issue
        constraints = []
        if issue == "hardcoded_paths":
            constraints.append("Must use configuration files for all paths")
            constraints.append("Must support changing paths without code modifications")
        elif issue == "missing_error_handling":
            constraints.append("Must include comprehensive error handling")
            constraints.append("Must log all errors with appropriate context")
            constraints.append("Must recover gracefully from failures")
        elif issue == "poor_documentation":
            constraints.append("Must include docstrings for all functions and classes")
            constraints.append("Must include usage examples")
            constraints.append("Must include type hints")
        elif issue == "poor_variable_names":
            constraints.append("Must use descriptive variable and function names")
            constraints.append("Must follow consistent naming conventions")
            constraints.append("Must avoid abbreviations unless widely understood")
        
        # Add general constraints
        constraints.extend(random.sample(TaskGenerator.CONSTRAINT_TEMPLATES, 2))
        
        # Generate task ID
        task_id = f"{issue}_{int(time.time())}"
        
        # Determine difficulty (medium for style issues)
        difficulty = 0.5
        
        # Determine required skills
        skills_required = ["python"]
        if issue == "hardcoded_paths":
            skills_required.append("configuration_management")
        elif issue == "missing_error_handling":
            skills_required.append("error_handling")
        elif issue == "poor_documentation":
            skills_required.append("documentation")
        
        # Create task
        task = {
            "id": task_id,
            "goal": task_goal,
            "difficulty": difficulty,
            "constraints": constraints,
            "skills_required": skills_required,
            "expected_outcome": f"A solution that demonstrates good practices regarding {issue.replace('_', ' ')}"
        }
        
        return task
    
    @staticmethod
    def _generate_learning_task(learning_type: str, skill: str, analysis: Dict) -> Dict:
        """
        Generate a task for learning.
        
        Args:
            learning_type: The type of learning (regression_prevention or skill_advancement)
            skill: The skill to focus on
            analysis: Analysis of the Builder agent's profile
            
        Returns:
            Dictionary with the generated task
        """
        # Get learning templates
        templates = TaskGenerator.TASK_TEMPLATES["learning"].get(
            learning_type, TaskGenerator.TASK_TEMPLATES["learning"]["default"]
        )
        
        # Select random template
        task_template = random.choice(templates)
        
        # Generate goal
        goals = [
            "processes data efficiently",
            "implements a useful algorithm",
            "solves a practical problem",
            "automates a common task",
            "creates a reusable component",
            "builds a useful tool"
        ]
        goal = random.choice(goals)
        
        # Format task template
        task_goal = task_template.format(goal=goal, skill=skill)
        
        # Generate constraints
        constraints = TaskGenerator._generate_constraints(skill)
        
        # Generate task ID
        task_id = f"{skill}_{learning_type}_{int(time.time())}"
        
        # Determine difficulty
        if learning_type == "regression_prevention":
            difficulty = 0.4  # Moderate difficulty for regression prevention
        else:  # skill_advancement
            difficulty = 0.7  # Higher difficulty for skill advancement
        
        # Create task
        task = {
            "id": task_id,
            "goal": task_goal,
            "difficulty": difficulty,
            "constraints": constraints,
            "skills_required": [skill],
            "expected_outcome": f"A solution that demonstrates proficiency in {skill}"
        }
        
        return task
    
    @staticmethod
    def _generate_general_improvement_task(analysis: Dict) -> Dict:
        """
        Generate a task for general improvement.
        
        Args:
            analysis: Analysis of the Builder agent's profile
            
        Returns:
            Dictionary with the generated task
        """
        # Select random template
        task_template = random.choice(TaskGenerator.TASK_TEMPLATES["general_improvement"])
        
        # Generate goal
        goals = [
            "processes and analyzes data from CSV files",
            "implements a simple web scraper",
            "creates a command-line tool for file operations",
            "builds a text-based game",
            "develops a simple API client",
            "implements a caching system",
            "creates a data visualization tool",
            "builds a simple database interface",
            "implements a configuration management system",
            "develops a logging framework"
        ]
        goal = random.choice(goals)
        
        # Format task template
        task_goal = task_template.format(goal=goal)
        
        # Generate constraints
        constraints = random.sample(TaskGenerator.CONSTRAINT_TEMPLATES, 3)
        
        # Generate task ID
        task_id = f"general_{int(time.time())}"
        
        # Determine difficulty (random for general improvement)
        difficulty = round(random.uniform(0.3, 0.7), 1)
        
        # Determine required skills (random selection)
        all_skills = [
            "python", "file_io", "error_handling", "testing",
            "json_parsing", "data_processing", "algorithms"
        ]
        skills_required = random.sample(all_skills, min(3, len(all_skills)))
        
        # Create task
        task = {
            "id": task_id,
            "goal": task_goal,
            "difficulty": difficulty,
            "constraints": constraints,
            "skills_required": skills_required,
            "expected_outcome": "A working solution that meets all constraints"
        }
        
        return task
    
    @staticmethod
    def _generate_constraints(skill: str) -> List[str]:
        """
        Generate constraints for a task based on the skill.
        
        Args:
            skill: The skill to focus on
            
        Returns:
            List of constraints
        """
        # Base constraints
        base_constraints = [
            "Must include clear documentation",
            "Must handle edge cases"
        ]
        
        # Skill-specific constraints
        skill_constraints = {
            "python": [
                "Must follow PEP 8 style guidelines",
                "Must use appropriate data structures",
                "Must be efficient in terms of time and space complexity"
            ],
            "error_handling": [
                "Must include comprehensive error handling",
                "Must log all errors with appropriate context",
                "Must recover gracefully from failures"
            ],
            "testing": [
                "Must include unit tests",
                "Must achieve at least 80% test coverage",
                "Must include tests for edge cases"
            ],
            "file_io": [
                "Must handle file not found errors",
                "Must close files properly",
                "Must handle large files efficiently"
            ],
            "json_parsing": [
                "Must handle malformed JSON",
                "Must validate JSON against a schema",
                "Must handle nested structures"
            ]
        }
        
        # Get skill-specific constraints
        specific_constraints = skill_constraints.get(skill, [])
        
        # Combine constraints
        all_constraints = base_constraints + specific_constraints
        
        # Select a subset of constraints
        num_constraints = min(4, len(all_constraints))
        return random.sample(all_constraints, num_constraints)


# Alias for backward compatibility
generate_task = TaskGenerator.generate_task


if __name__ == "__main__":
    # Simple test
    try:
        # Ensure directories exist
        os.makedirs("memory/logs", exist_ok=True)
        os.makedirs("memory/core", exist_ok=True)
        os.makedirs("memory/advanced", exist_ok=True)
        os.makedirs("memory/task_memory", exist_ok=True)
        
        # Create a test analysis
        test_analysis = {
            "profile_summary": {
                "task_count": 10,
                "average_score": 75.5,
                "skills_mastered_count": 2,
                "weak_skills_count": 2
            },
            "performance_trend": {
                "trend": "improving",
                "average": 75.5
            },
            "skill_gaps": [
                {
                    "skill": "error_handling",
                    "level": 0.2,
                    "tasks_completed": 2,
                    "priority": "high"
                }
            ],
            "style_issues": [
                {
                    "issue": "hardcoded_paths",
                    "count": 5,
                    "priority": "high"
                }
            ],
            "learning_opportunities": [],
            "recommended_focus": "skill_gap:error_handling"
        }
        
        # Generate task
        task = TaskGenerator.generate_task(test_analysis)
        
        print(f"Generated task: {json.dumps(task, indent=2)}")
        
        # Generate tasks for different focus areas
        focus_areas = [
            "skill_gap:python",
            "style_issue:poor_documentation",
            "learning:regression_prevention:file_io",
            "learning:skill_advancement:json_parsing",
            "general_improvement"
        ]
        
        for focus in focus_areas:
            test_analysis["recommended_focus"] = focus
            task = TaskGenerator.generate_task(test_analysis)
            print(f"\nTask for {focus}: {task['goal']}")
            print(f"Constraints: {task['constraints']}")
        
        print("\nAll tests passed")
    except Exception as e:
        print(f"Test failed: {e}")

