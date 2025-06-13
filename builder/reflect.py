#!/usr/bin/env python3
"""
builder/reflect.py

This module provides functionality for generating reflections on task execution
in the Builder-Trainer Cognitive Loop system.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Union, Any

# Import system components
from memory_manager import MemoryManager
from llm_interface import LLMInterface

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("memory/logs/builder.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("builder.reflect")

class BuilderReflection:
    """
    A class that provides methods for generating reflections on task execution.
    """
    
    @staticmethod
    def reflect_on_task(task: Dict, result: Dict, code: str) -> Dict:
        """
        Generate a reflection on a completed task.
        
        Args:
            task: The task that was executed
            result: The result of the task execution
            code: The code that was generated
            
        Returns:
            Dictionary with reflection data
        """
        logger.info(f"Reflecting on task: {task['id']}")
        
        try:
            # Generate reflection using LLM
            reflection = LLMInterface.reflect_on_task(task, result, code)
            
            # Save reflection to memory
            reflection_path = f"memory/task_memory/reflection_{task['id']}.json"
            MemoryManager.save(reflection_path, reflection)
            
            logger.info(f"Generated reflection for task {task['id']}")
            
            return reflection
        except Exception as e:
            logger.error(f"Error reflecting on task {task['id']}: {e}")
            
            # Create basic reflection with error information
            basic_reflection = {
                "strengths": ["Task was attempted"],
                "weaknesses": ["Reflection system failed"],
                "lessons_learned": ["Need to improve reflection system"],
                "skill_improvements": {},
                "error": str(e)
            }
            
            return basic_reflection
    
    @staticmethod
    def update_builder_profile_with_reflection(reflection: Dict) -> None:
        """
        Update the builder profile based on reflection.
        
        Args:
            reflection: The reflection data
        """
        logger.info("Updating builder profile with reflection")
        
        try:
            # Load builder profile
            profile = MemoryManager.load("memory/core/builder_profile.json", default={
                "id": "builder_v0.1",
                "task_count": 0,
                "average_score": 0,
                "skills_mastered": [],
                "weak_skills": [],
                "style_flags": {},
                "last_updated": ""
            })
            
            # Extract information from reflection
            strengths = reflection.get("strengths", [])
            weaknesses = reflection.get("weaknesses", [])
            lessons_learned = reflection.get("lessons_learned", [])
            skill_improvements = reflection.get("skill_improvements", {})
            
            # Update skills mastered and weak skills
            for skill, improvement in skill_improvements.items():
                if improvement > 0.1:
                    # Significant improvement, might be mastered
                    if skill not in profile["skills_mastered"]:
                        profile["skills_mastered"].append(skill)
                    
                    # Remove from weak skills if present
                    if skill in profile["weak_skills"]:
                        profile["weak_skills"].remove(skill)
                elif improvement < -0.1:
                    # Significant decline, might be weak
                    if skill not in profile["weak_skills"]:
                        profile["weak_skills"].append(skill)
                    
                    # Remove from mastered skills if present
                    if skill in profile["skills_mastered"]:
                        profile["skills_mastered"].remove(skill)
            
            # Update style flags based on weaknesses
            for weakness in weaknesses:
                weakness_lower = weakness.lower()
                
                # Check for common style issues
                if "hardcoded" in weakness_lower or "hard-coded" in weakness_lower:
                    profile["style_flags"]["hardcoded_paths"] = profile["style_flags"].get("hardcoded_paths", 0) + 1
                
                if "error handling" in weakness_lower:
                    profile["style_flags"]["missing_error_handling"] = profile["style_flags"].get("missing_error_handling", 0) + 1
                
                if "documentation" in weakness_lower or "comment" in weakness_lower:
                    profile["style_flags"]["poor_documentation"] = profile["style_flags"].get("poor_documentation", 0) + 1
                
                if "variable name" in weakness_lower:
                    profile["style_flags"]["poor_variable_names"] = profile["style_flags"].get("poor_variable_names", 0) + 1
            
            # Save updated profile
            MemoryManager.save("memory/core/builder_profile.json", profile)
            
            logger.info("Builder profile updated with reflection")
        except Exception as e:
            logger.error(f"Error updating builder profile with reflection: {e}")
    
    @staticmethod
    def generate_learning_summary(task_id: str, reflection: Dict) -> str:
        """
        Generate a human-readable learning summary from a reflection.
        
        Args:
            task_id: The ID of the task
            reflection: The reflection data
            
        Returns:
            A human-readable learning summary
        """
        logger.info(f"Generating learning summary for task: {task_id}")
        
        try:
            # Extract information from reflection
            strengths = reflection.get("strengths", [])
            weaknesses = reflection.get("weaknesses", [])
            lessons_learned = reflection.get("lessons_learned", [])
            
            # Format strengths
            strengths_text = "\n".join([f"- {strength}" for strength in strengths])
            
            # Format weaknesses
            weaknesses_text = "\n".join([f"- {weakness}" for weakness in weaknesses])
            
            # Format lessons learned
            lessons_text = "\n".join([f"- {lesson}" for lesson in lessons_learned])
            
            # Create summary
            summary = f"""# Learning Summary for Task {task_id}

## Strengths
{strengths_text}

## Areas for Improvement
{weaknesses_text}

## Lessons Learned
{lessons_text}
"""
            
            # Save summary to file
            summary_path = f"memory/task_memory/summary_{task_id}.md"
            with open(summary_path, 'w') as f:
                f.write(summary)
            
            logger.info(f"Generated learning summary for task {task_id}")
            
            return summary
        except Exception as e:
            logger.error(f"Error generating learning summary for task {task_id}: {e}")
            return f"Error generating learning summary: {e}"


# Alias for backward compatibility
reflect_on_task = BuilderReflection.reflect_on_task


if __name__ == "__main__":
    # Simple test
    try:
        # Ensure directories exist
        os.makedirs("memory/logs", exist_ok=True)
        os.makedirs("memory/task_memory", exist_ok=True)
        os.makedirs("memory/core", exist_ok=True)
        
        # Create a test task
        test_task = {
            "id": "test_task_003",
            "source": "trainer",
            "goal": "Write a function to calculate the factorial of a number",
            "difficulty": 0.3,
            "constraints": ["Must handle negative numbers", "Must use recursion"],
            "skills_required": ["python", "recursion"],
            "expected_outcome": "A function that correctly calculates factorials"
        }
        
        # Create a test result
        test_result = {
            "success": True,
            "score": 85.5,
            "metrics": {
                "correctness": 0.9,
                "efficiency": 0.8,
                "elegance": 0.7,
                "robustness": 0.6
            }
        }
        
        # Create test code
        test_code = """
def factorial(n):
    if n < 0:
        return None
    if n == 0:
        return 1
    return n * factorial(n-1)
"""
        
        # Generate reflection
        reflection = BuilderReflection.reflect_on_task(test_task, test_result, test_code)
        
        print(f"Reflection: {json.dumps(reflection, indent=2)}")
        
        # Update builder profile
        BuilderReflection.update_builder_profile_with_reflection(reflection)
        
        # Generate learning summary
        summary = BuilderReflection.generate_learning_summary(test_task["id"], reflection)
        
        print(f"Learning summary:\n{summary}")
        
        print("Test passed")
    except Exception as e:
        print(f"Test failed: {e}")

