#!/usr/bin/env python3
"""
llm_interface.py

This module provides an interface for communicating with the LLM via LM Studio.
"""

import os
import time
import json
import logging
import openai
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

# Import memory manager for logging
from memory_manager import MemoryManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("memory/logs/llm_interface.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("llm_interface")

# Configure OpenAI API
openai.api_base = os.getenv("OPENAI_API_BASE", "http://host.docker.internal:1234/v1")
openai.api_key = os.getenv("OPENAI_API_KEY", "sk-local")
DEFAULT_MODEL = os.getenv("MODEL_NAME", "deepseek-coder")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "mistral")

class LLMInterface:
    """
    A class that provides methods for communicating with the LLM via LM Studio.
    """
    
    @staticmethod
    def query(
        prompt: str, 
        system: str = "You're a code agent that helps with programming tasks.",
        model: str = DEFAULT_MODEL,
        max_retries: int = 3,
        retry_delay: int = 2,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Query the LLM with a prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            system: The system message to set the context
            model: The model to use
            max_retries: Maximum number of retries on failure
            retry_delay: Delay between retries in seconds
            temperature: The temperature parameter for generation
            max_tokens: The maximum number of tokens to generate
            
        Returns:
            The LLM's response as a string
        """
        start_time = time.time()
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                messages = [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ]
                
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                content = response.choices[0].message.content
                
                # Log the interaction
                end_time = time.time()
                duration = end_time - start_time
                
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "model": model,
                    "prompt_length": len(prompt),
                    "response_length": len(content),
                    "duration_seconds": duration,
                    "success": True
                }
                
                MemoryManager.append("memory/logs/llm_interactions.json", log_entry)
                logger.debug(f"LLM query successful: {duration:.2f}s, {len(prompt)} chars -> {len(content)} chars")
                
                return content
                
            except Exception as e:
                retry_count += 1
                logger.warning(f"LLM query failed (attempt {retry_count}/{max_retries}): {e}")
                
                # Log the failure
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "model": model,
                    "prompt_length": len(prompt),
                    "error": str(e),
                    "attempt": retry_count,
                    "success": False
                }
                MemoryManager.append("memory/logs/llm_interactions.json", log_entry)
                
                if retry_count < max_retries:
                    # Try fallback model on the last retry
                    if retry_count == max_retries - 1 and model != FALLBACK_MODEL:
                        logger.info(f"Trying fallback model: {FALLBACK_MODEL}")
                        model = FALLBACK_MODEL
                    
                    time.sleep(retry_delay)
                else:
                    logger.error(f"LLM query failed after {max_retries} attempts")
                    raise
        
        # This should not be reached due to the raise in the loop
        return "Error: Failed to get response from LLM"
    
    @staticmethod
    def code_completion(
        prompt: str,
        language: str = "python",
        model: str = DEFAULT_MODEL,
        temperature: float = 0.2,
        max_tokens: int = 2048
    ) -> str:
        """
        Get code completion from the LLM.
        
        Args:
            prompt: The prompt describing the code to generate
            language: The programming language
            model: The model to use
            temperature: The temperature parameter for generation
            max_tokens: The maximum number of tokens to generate
            
        Returns:
            The generated code as a string
        """
        system_prompt = f"""You are an expert {language} programmer. 
Generate only the code without any explanations or markdown formatting.
Focus on writing clean, efficient, and well-documented code."""
        
        full_prompt = f"""Write {language} code for the following task:

{prompt}

Provide ONLY the code, no explanations or markdown formatting."""
        
        response = LLMInterface.query(
            prompt=full_prompt,
            system=system_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Clean up the response to extract just the code
        # Remove markdown code blocks if present
        code = response
        if code.startswith("```"):
            lines = code.split("\n")
            if len(lines) > 1:
                # Remove the first line (```language)
                lines = lines[1:]
                # Remove the last line if it's ```
                if lines[-1].strip() == "```":
                    lines = lines[:-1]
                code = "\n".join(lines)
        
        return code
    
    @staticmethod
    def analyze_code(
        code: str,
        criteria: List[str] = None,
        language: str = "python",
        model: str = DEFAULT_MODEL
    ) -> Dict:
        """
        Analyze code quality using the LLM.
        
        Args:
            code: The code to analyze
            criteria: The criteria to evaluate (e.g., ["correctness", "efficiency", "elegance"])
            language: The programming language
            model: The model to use
            
        Returns:
            A dictionary with analysis results
        """
        if criteria is None:
            criteria = ["correctness", "efficiency", "elegance", "robustness"]
        
        criteria_str = ", ".join(criteria)
        
        system_prompt = f"""You are an expert {language} code reviewer. 
Analyze the provided code based on the following criteria: {criteria_str}.
Provide a structured analysis with scores and explanations."""
        
        prompt = f"""Analyze the following {language} code based on these criteria: {criteria_str}

```{language}
{code}
```

For each criterion, provide:
1. A score from 0.0 to 1.0 (where 1.0 is perfect)
2. A brief explanation of the score
3. Suggestions for improvement

Format your response as a JSON object with the following structure:
{{
  "scores": {{
    "criterion1": score,
    "criterion2": score,
    ...
  }},
  "explanations": {{
    "criterion1": "explanation",
    "criterion2": "explanation",
    ...
  }},
  "suggestions": [
    "suggestion1",
    "suggestion2",
    ...
  ],
  "overall_score": overall_score
}}"""
        
        response = LLMInterface.query(
            prompt=prompt,
            system=system_prompt,
            model=model,
            temperature=0.3
        )
        
        # Extract JSON from the response
        try:
            # Find JSON in the response (it might be wrapped in markdown code blocks)
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                analysis = json.loads(json_str)
            else:
                # If no JSON found, try to parse the whole response
                analysis = json.loads(response)
            
            return analysis
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from LLM response: {response}")
            # Return a basic structure with error information
            return {
                "scores": {criterion: 0.0 for criterion in criteria},
                "explanations": {criterion: "Analysis failed" for criterion in criteria},
                "suggestions": ["Analysis failed to parse"],
                "overall_score": 0.0,
                "error": "Failed to parse analysis result"
            }
    
    @staticmethod
    def generate_task(
        builder_profile: Dict,
        difficulty: float = 0.5,
        model: str = DEFAULT_MODEL
    ) -> Dict:
        """
        Generate a coding task for the Builder agent.
        
        Args:
            builder_profile: The Builder's profile
            difficulty: The desired difficulty level (0.0 to 1.0)
            model: The model to use
            
        Returns:
            A dictionary with the generated task
        """
        system_prompt = """You are an AI trainer that creates coding tasks to improve a coding agent's skills.
Generate a well-defined coding task with clear goals and constraints."""
        
        # Convert profile to a string summary
        profile_summary = json.dumps(builder_profile, indent=2)
        
        prompt = f"""Generate a coding task for a Builder agent with the following profile:

{profile_summary}

The task should have a difficulty level of {difficulty} (on a scale from 0.0 to 1.0).

Create a task that will help the Builder improve its skills, especially in areas where it's weak.

Format your response as a JSON object with the following structure:
{{
  "id": "unique_task_id",
  "source": "trainer",
  "goal": "Clear description of the task goal",
  "difficulty": {difficulty},
  "constraints": ["constraint1", "constraint2", ...],
  "skills_required": ["skill1", "skill2", ...],
  "expected_outcome": "Description of what success looks like"
}}"""
        
        response = LLMInterface.query(
            prompt=prompt,
            system=system_prompt,
            model=model,
            temperature=0.7
        )
        
        # Extract JSON from the response
        try:
            # Find JSON in the response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                task = json.loads(json_str)
            else:
                # If no JSON found, try to parse the whole response
                task = json.loads(response)
            
            # Ensure required fields are present
            if "id" not in task:
                task["id"] = f"task_{int(time.time())}"
            
            if "source" not in task:
                task["source"] = "trainer"
            
            if "difficulty" not in task:
                task["difficulty"] = difficulty
            
            if "created_at" not in task:
                task["created_at"] = datetime.now().isoformat()
            
            return task
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from LLM response: {response}")
            # Create a basic task with error information
            return {
                "id": f"error_task_{int(time.time())}",
                "source": "trainer",
                "goal": "Debug the task generation system",
                "difficulty": difficulty,
                "constraints": ["Fix the JSON parsing issue"],
                "skills_required": ["debugging", "error_handling"],
                "expected_outcome": "Task generation works correctly",
                "error": "Failed to parse task JSON"
            }
    
    @staticmethod
    def reflect_on_task(
        task: Dict,
        result: Dict,
        code: str,
        model: str = DEFAULT_MODEL
    ) -> Dict:
        """
        Generate a reflection on a completed task.
        
        Args:
            task: The task that was executed
            result: The result of the task execution
            code: The code that was generated
            model: The model to use
            
        Returns:
            A dictionary with the reflection
        """
        system_prompt = """You are an AI that reflects on coding tasks to identify strengths, weaknesses, and lessons learned.
Provide a thoughtful analysis of the task execution."""
        
        # Convert task and result to string summaries
        task_summary = json.dumps(task, indent=2)
        result_summary = json.dumps(result, indent=2)
        
        prompt = f"""Reflect on the following coding task and its result:

TASK:
{task_summary}

CODE:
```
{code}
```

RESULT:
{result_summary}

Analyze the task execution and identify:
1. Strengths: What went well?
2. Weaknesses: What could be improved?
3. Lessons learned: What should be remembered for future tasks?

Format your response as a JSON object with the following structure:
{{
  "strengths": ["strength1", "strength2", ...],
  "weaknesses": ["weakness1", "weakness2", ...],
  "lessons_learned": ["lesson1", "lesson2", ...],
  "skill_improvements": {{
    "skill1": 0.1,
    "skill2": -0.05,
    ...
  }}
}}"""
        
        response = LLMInterface.query(
            prompt=prompt,
            system=system_prompt,
            model=model,
            temperature=0.5
        )
        
        # Extract JSON from the response
        try:
            # Find JSON in the response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                reflection = json.loads(json_str)
            else:
                # If no JSON found, try to parse the whole response
                reflection = json.loads(response)
            
            return reflection
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from LLM response: {response}")
            # Return a basic reflection with error information
            return {
                "strengths": ["Task was attempted"],
                "weaknesses": ["Reflection system failed"],
                "lessons_learned": ["Need to improve JSON parsing in reflection system"],
                "skill_improvements": {},
                "error": "Failed to parse reflection JSON"
            }


if __name__ == "__main__":
    # Simple test
    try:
        # Ensure log directory exists
        os.makedirs("memory/logs", exist_ok=True)
        
        # Test query
        response = LLMInterface.query("What is the capital of France?")
        print(f"Query response: {response}")
        
        # Test code completion
        code = LLMInterface.code_completion("Write a function to calculate the factorial of a number")
        print(f"Code completion:\n{code}")
        
        # Test code analysis
        test_code = """
def factorial(n):
    if n < 0:
        return None
    if n == 0:
        return 1
    return n * factorial(n-1)
"""
        analysis = LLMInterface.analyze_code(test_code)
        print(f"Code analysis: {json.dumps(analysis, indent=2)}")
        
        print("All tests passed")
    except Exception as e:
        print(f"Test failed: {e}")

