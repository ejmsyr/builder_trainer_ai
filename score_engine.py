#!/usr/bin/env python3
"""
score_engine.py

This module provides functionality for calculating and tracking scores for tasks
in the Builder-Trainer Cognitive Loop system.
"""

import os
import json
import logging
import statistics
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

# Import memory manager for data operations
from memory_manager import MemoryManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("memory/logs/score_engine.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("score_engine")

class ScoreEngine:
    """
    A class that provides methods for calculating and tracking scores for tasks.
    """
    
    # Default weights for different metrics
    DEFAULT_WEIGHTS = {
        "correctness": 0.4,
        "efficiency": 0.2,
        "elegance": 0.2,
        "robustness": 0.2
    }
    
    # Difficulty multipliers
    DIFFICULTY_MULTIPLIERS = {
        0.1: 0.5,   # Very easy tasks get half points
        0.3: 0.8,   # Easy tasks get 80% points
        0.5: 1.0,   # Medium tasks get normal points
        0.7: 1.3,   # Hard tasks get 30% bonus
        0.9: 1.6    # Very hard tasks get 60% bonus
    }
    
    @staticmethod
    def calculate_score(
        metrics: Dict[str, float],
        difficulty: float = 0.5,
        source: str = "trainer",
        weights: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Calculate a score based on metrics, difficulty, and source.
        
        Args:
            metrics: Dictionary of metrics and their values (0.0 to 1.0)
            difficulty: Task difficulty (0.0 to 1.0)
            source: Task source ("trainer" or "user")
            weights: Optional custom weights for metrics
            
        Returns:
            Dictionary with score and detailed breakdown
        """
        if weights is None:
            weights = ScoreEngine.DEFAULT_WEIGHTS.copy()
        
        # Ensure all required metrics are present
        for metric in weights:
            if metric not in metrics:
                logger.warning(f"Missing metric: {metric}, defaulting to 0.0")
                metrics[metric] = 0.0
        
        # Calculate raw score (weighted average of metrics)
        raw_score = 0.0
        total_weight = 0.0
        
        for metric, value in metrics.items():
            if metric in weights:
                weight = weights[metric]
                raw_score += value * weight
                total_weight += weight
        
        if total_weight > 0:
            raw_score /= total_weight
        
        # Apply difficulty multiplier
        # Find the closest difficulty level in the multipliers
        difficulties = sorted(ScoreEngine.DIFFICULTY_MULTIPLIERS.keys())
        closest_difficulty = min(difficulties, key=lambda x: abs(x - difficulty))
        difficulty_multiplier = ScoreEngine.DIFFICULTY_MULTIPLIERS[closest_difficulty]
        
        # Apply source modifier (user tasks get a small bonus)
        source_modifier = 1.1 if source == "user" else 1.0
        
        # Calculate final score (0-100 scale)
        final_score = raw_score * difficulty_multiplier * source_modifier * 100
        
        # Round to one decimal place
        final_score = round(final_score, 1)
        
        return {
            "score": final_score,
            "raw_score": raw_score,
            "difficulty_multiplier": difficulty_multiplier,
            "source_modifier": source_modifier,
            "metrics": metrics
        }
    
    @staticmethod
    def track_score(task_id: str, score_data: Dict) -> None:
        """
        Track a score in the score log.
        
        Args:
            task_id: The ID of the task
            score_data: The score data from calculate_score
        """
        # Get task data
        task_path = f"memory/task_memory/task_{task_id}.json"
        task = MemoryManager.load(task_path, default={"id": task_id})
        
        # Create score entry
        score_entry = {
            "task_id": task_id,
            "score": score_data["score"],
            "difficulty": task.get("difficulty", 0.5),
            "source": task.get("source", "trainer"),
            "timestamp": datetime.now().isoformat(),
            "metrics": score_data.get("metrics", {})
        }
        
        # Append to score log
        MemoryManager.append("memory/core/score_log.json", score_entry)
        logger.info(f"Tracked score for task {task_id}: {score_data['score']}")
        
        # Update task with score
        task["result"] = task.get("result", {})
        task["result"]["score"] = score_data["score"]
        task["result"]["metrics"] = score_data.get("metrics", {})
        MemoryManager.save(task_path, task)
    
    @staticmethod
    def get_performance_trend(n: int = 10) -> Dict:
        """
        Get the trend of the last n scores.
        
        Args:
            n: Number of scores to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        # Load score log
        score_log = MemoryManager.load("memory/core/score_log.json", default=[])
        
        # Sort by timestamp (newest first)
        score_log.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Get the last n scores
        recent_scores = score_log[:n]
        
        if not recent_scores:
            return {
                "trend": "neutral",
                "average": 0.0,
                "min": 0.0,
                "max": 0.0,
                "count": 0
            }
        
        # Extract scores
        scores = [entry["score"] for entry in recent_scores]
        
        # Calculate statistics
        avg_score = statistics.mean(scores) if scores else 0.0
        min_score = min(scores) if scores else 0.0
        max_score = max(scores) if scores else 0.0
        
        # Determine trend
        if len(scores) >= 3:
            # Simple linear regression to determine trend
            x = list(range(len(scores)))
            y = scores
            
            # Calculate slope
            n_points = len(scores)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x_i * y_i for x_i, y_i in zip(x, y))
            sum_xx = sum(x_i * x_i for x_i in x)
            
            slope = (n_points * sum_xy - sum_x * sum_y) / (n_points * sum_xx - sum_x * sum_x)
            
            if slope > 0.5:
                trend = "strongly_improving"
            elif slope > 0.1:
                trend = "improving"
            elif slope < -0.5:
                trend = "strongly_declining"
            elif slope < -0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "neutral"  # Not enough data
        
        return {
            "trend": trend,
            "average": round(avg_score, 1),
            "min": round(min_score, 1),
            "max": round(max_score, 1),
            "count": len(scores),
            "scores": scores
        }
    
    @staticmethod
    def adjust_difficulty(current_difficulty: float, performance_trend: Dict) -> float:
        """
        Adjust difficulty based on performance trend.
        
        Args:
            current_difficulty: Current difficulty level (0.0 to 1.0)
            performance_trend: Performance trend from get_performance_trend
            
        Returns:
            New difficulty level (0.0 to 1.0)
        """
        trend = performance_trend["trend"]
        
        # Adjust difficulty based on trend
        if trend == "strongly_improving":
            # Significant increase in difficulty
            new_difficulty = current_difficulty + 0.1
        elif trend == "improving":
            # Moderate increase in difficulty
            new_difficulty = current_difficulty + 0.05
        elif trend == "strongly_declining":
            # Significant decrease in difficulty
            new_difficulty = current_difficulty - 0.1
        elif trend == "declining":
            # Moderate decrease in difficulty
            new_difficulty = current_difficulty - 0.05
        else:
            # Stable or neutral, small increase
            new_difficulty = current_difficulty + 0.02
        
        # Ensure difficulty is within bounds
        new_difficulty = max(0.1, min(0.9, new_difficulty))
        
        logger.info(f"Adjusted difficulty: {current_difficulty} -> {new_difficulty} (trend: {trend})")
        return new_difficulty
    
    @staticmethod
    def update_skill_levels(task: Dict, reflection: Dict) -> None:
        """
        Update skill levels based on task reflection.
        
        Args:
            task: The task that was executed
            reflection: The reflection on the task execution
        """
        # Load skill map
        skill_map = MemoryManager.load("memory/core/skill_map.json", default={"skills": {}})
        
        # Get skill improvements from reflection
        skill_improvements = reflection.get("skill_improvements", {})
        
        # Get required skills from task
        required_skills = task.get("skills_required", [])
        
        # Update skills
        for skill in required_skills:
            if skill not in skill_map["skills"]:
                # Initialize new skill
                skill_map["skills"][skill] = {
                    "level": 0.1,
                    "tasks_completed": 0,
                    "last_used": datetime.now().isoformat()
                }
            
            # Update tasks completed
            skill_map["skills"][skill]["tasks_completed"] += 1
            
            # Update last used
            skill_map["skills"][skill]["last_used"] = datetime.now().isoformat()
            
            # Apply improvement if available
            if skill in skill_improvements:
                improvement = skill_improvements[skill]
                current_level = skill_map["skills"][skill]["level"]
                new_level = current_level + improvement
                
                # Ensure level is within bounds
                new_level = max(0.0, min(1.0, new_level))
                
                skill_map["skills"][skill]["level"] = new_level
                logger.info(f"Updated skill level for {skill}: {current_level} -> {new_level}")
        
        # Save updated skill map
        MemoryManager.save("memory/core/skill_map.json", skill_map)


if __name__ == "__main__":
    # Simple test
    try:
        # Ensure directories exist
        os.makedirs("memory/logs", exist_ok=True)
        os.makedirs("memory/core", exist_ok=True)
        os.makedirs("memory/task_memory", exist_ok=True)
        
        # Test calculate_score
        metrics = {
            "correctness": 0.8,
            "efficiency": 0.6,
            "elegance": 0.4,
            "robustness": 0.3
        }
        
        score_data = ScoreEngine.calculate_score(metrics, difficulty=0.7, source="trainer")
        print(f"Score calculation: {json.dumps(score_data, indent=2)}")
        
        # Test track_score
        task_id = "test_task_001"
        
        # Create a test task
        test_task = {
            "id": task_id,
            "source": "trainer",
            "goal": "Test the score engine",
            "difficulty": 0.7,
            "skills_required": ["python", "testing"]
        }
        MemoryManager.save(f"memory/task_memory/task_{task_id}.json", test_task)
        
        ScoreEngine.track_score(task_id, score_data)
        print(f"Score tracked for task {task_id}")
        
        # Test get_performance_trend
        trend = ScoreEngine.get_performance_trend()
        print(f"Performance trend: {json.dumps(trend, indent=2)}")
        
        # Test adjust_difficulty
        new_difficulty = ScoreEngine.adjust_difficulty(0.5, trend)
        print(f"Adjusted difficulty: {new_difficulty}")
        
        # Test update_skill_levels
        reflection = {
            "skill_improvements": {
                "python": 0.05,
                "testing": 0.03
            }
        }
        ScoreEngine.update_skill_levels(test_task, reflection)
        print("Skill levels updated")
        
        print("All tests passed")
    except Exception as e:
        print(f"Test failed: {e}")

