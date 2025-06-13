#!/usr/bin/env python3
"""
trainer/adjust_difficulty.py

This module provides functionality for adjusting task difficulty based on the Builder agent's performance
in the Builder-Trainer Cognitive Loop system.
"""

import os
import sys
import json
import logging
import statistics
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta

# Import system components
from memory_manager import MemoryManager
from score_engine import ScoreEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("memory/logs/trainer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("trainer.adjust_difficulty")

class DifficultyAdjuster:
    """
    A class that provides methods for adjusting task difficulty based on the Builder agent's performance.
    """
    
    # Default difficulty levels
    DEFAULT_DIFFICULTY = 0.5
    MIN_DIFFICULTY = 0.1
    MAX_DIFFICULTY = 0.9
    
    # Adjustment factors
    ADJUSTMENT_FACTORS = {
        "strongly_improving": 0.1,   # Significant increase
        "improving": 0.05,           # Moderate increase
        "stable": 0.02,              # Small increase
        "neutral": 0.0,              # No change
        "declining": -0.05,          # Moderate decrease
        "strongly_declining": -0.1   # Significant decrease
    }
    
    # Score thresholds
    SCORE_THRESHOLDS = {
        "excellent": 90.0,
        "good": 75.0,
        "average": 60.0,
        "poor": 40.0
    }
    
    @staticmethod
    def adjust_difficulty(current_difficulty: Optional[float] = None) -> float:
        """
        Adjust difficulty based on the Builder agent's performance.
        
        Args:
            current_difficulty: Current difficulty level (0.0 to 1.0)
            
        Returns:
            New difficulty level (0.0 to 1.0)
        """
        logger.info("Adjusting task difficulty")
        
        try:
            # If no current difficulty provided, load from memory
            if current_difficulty is None:
                difficulty_path = "memory/advanced/current_difficulty.json"
                if os.path.exists(difficulty_path):
                    difficulty_data = MemoryManager.load(difficulty_path)
                    current_difficulty = difficulty_data.get("difficulty", DifficultyAdjuster.DEFAULT_DIFFICULTY)
                else:
                    current_difficulty = DifficultyAdjuster.DEFAULT_DIFFICULTY
            
            # Get performance trend
            performance_trend = ScoreEngine.get_performance_trend(n=10)
            trend = performance_trend.get("trend", "neutral")
            
            # Get adjustment factor
            adjustment_factor = DifficultyAdjuster.ADJUSTMENT_FACTORS.get(trend, 0.0)
            
            # Apply adjustment
            new_difficulty = current_difficulty + adjustment_factor
            
            # Apply additional adjustments based on recent scores
            recent_scores = performance_trend.get("scores", [])
            if recent_scores:
                avg_score = statistics.mean(recent_scores)
                
                # Adjust based on score thresholds
                if avg_score >= DifficultyAdjuster.SCORE_THRESHOLDS["excellent"]:
                    # Excellent scores, increase difficulty more
                    new_difficulty += 0.05
                elif avg_score >= DifficultyAdjuster.SCORE_THRESHOLDS["good"]:
                    # Good scores, small increase
                    new_difficulty += 0.02
                elif avg_score <= DifficultyAdjuster.SCORE_THRESHOLDS["poor"]:
                    # Poor scores, decrease difficulty more
                    new_difficulty -= 0.05
            
            # Ensure difficulty is within bounds
            new_difficulty = max(DifficultyAdjuster.MIN_DIFFICULTY, min(DifficultyAdjuster.MAX_DIFFICULTY, new_difficulty))
            
            # Round to one decimal place
            new_difficulty = round(new_difficulty, 1)
            
            # Save new difficulty
            difficulty_data = {
                "difficulty": new_difficulty,
                "previous_difficulty": current_difficulty,
                "adjustment_factor": adjustment_factor,
                "performance_trend": trend,
                "timestamp": datetime.now().isoformat()
            }
            MemoryManager.save("memory/advanced/current_difficulty.json", difficulty_data)
            
            # Log adjustment
            logger.info(f"Adjusted difficulty: {current_difficulty} -> {new_difficulty} (trend: {trend})")
            
            # Log to trainer log
            trainer_log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": "adjust_difficulty",
                "previous_difficulty": current_difficulty,
                "new_difficulty": new_difficulty,
                "adjustment_factor": adjustment_factor,
                "performance_trend": trend
            }
            MemoryManager.append("memory/advanced/trainer_log.json", trainer_log_entry)
            
            return new_difficulty
        except Exception as e:
            logger.error(f"Error adjusting difficulty: {e}")
            return current_difficulty or DifficultyAdjuster.DEFAULT_DIFFICULTY
    
    @staticmethod
    def get_difficulty_for_skill(skill: str) -> float:
        """
        Get an appropriate difficulty level for a specific skill.
        
        Args:
            skill: The skill to get difficulty for
            
        Returns:
            Difficulty level (0.0 to 1.0)
        """
        try:
            # Load skill map
            skill_map = MemoryManager.load("memory/core/skill_map.json", default={"skills": {}})
            
            # Get skill data
            skill_data = skill_map.get("skills", {}).get(skill, {})
            skill_level = skill_data.get("level", 0.0)
            
            # Calculate difficulty based on skill level
            if skill_level < 0.2:
                # Very low skill level, start with easy tasks
                difficulty = 0.2
            elif skill_level < 0.4:
                # Low skill level, moderate difficulty
                difficulty = 0.3
            elif skill_level < 0.6:
                # Medium skill level, standard difficulty
                difficulty = 0.5
            elif skill_level < 0.8:
                # High skill level, challenging difficulty
                difficulty = 0.7
            else:
                # Very high skill level, very challenging difficulty
                difficulty = 0.8
            
            logger.info(f"Calculated difficulty for skill {skill}: {difficulty} (skill level: {skill_level})")
            
            return difficulty
        except Exception as e:
            logger.error(f"Error getting difficulty for skill {skill}: {e}")
            return DifficultyAdjuster.DEFAULT_DIFFICULTY
    
    @staticmethod
    def get_difficulty_curve() -> Dict:
        """
        Get the difficulty curve over time.
        
        Returns:
            Dictionary with difficulty curve data
        """
        try:
            # Load trainer log
            trainer_log = MemoryManager.load("memory/advanced/trainer_log.json", default=[])
            
            # Filter for difficulty adjustments
            difficulty_adjustments = [
                entry for entry in trainer_log
                if entry.get("action") == "adjust_difficulty"
            ]
            
            # Sort by timestamp
            difficulty_adjustments.sort(key=lambda x: x.get("timestamp", ""))
            
            # Extract difficulty values
            timestamps = []
            difficulties = []
            
            for entry in difficulty_adjustments:
                try:
                    timestamp = datetime.fromisoformat(entry.get("timestamp", ""))
                    timestamps.append(timestamp.strftime("%Y-%m-%d %H:%M"))
                    difficulties.append(entry.get("new_difficulty", DifficultyAdjuster.DEFAULT_DIFFICULTY))
                except:
                    pass
            
            # Create curve data
            curve_data = {
                "timestamps": timestamps,
                "difficulties": difficulties,
                "count": len(timestamps)
            }
            
            return curve_data
        except Exception as e:
            logger.error(f"Error getting difficulty curve: {e}")
            return {"timestamps": [], "difficulties": [], "count": 0}


# Alias for backward compatibility
adjust_difficulty = DifficultyAdjuster.adjust_difficulty


if __name__ == "__main__":
    # Simple test
    try:
        # Ensure directories exist
        os.makedirs("memory/logs", exist_ok=True)
        os.makedirs("memory/core", exist_ok=True)
        os.makedirs("memory/advanced", exist_ok=True)
        
        # Create test score log
        test_score_log = [
            {
                "task_id": f"task_{i}",
                "score": 70 + i * 2,  # Increasing scores
                "difficulty": 0.5,
                "source": "trainer",
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat()
            }
            for i in range(10)
        ]
        MemoryManager.save("memory/core/score_log.json", test_score_log)
        
        # Create test skill map
        test_skill_map = {
            "skills": {
                "python": {
                    "level": 0.7,
                    "tasks_completed": 8,
                    "last_used": datetime.now().isoformat()
                },
                "error_handling": {
                    "level": 0.2,
                    "tasks_completed": 2,
                    "last_used": datetime.now().isoformat()
                }
            }
        }
        MemoryManager.save("memory/core/skill_map.json", test_skill_map)
        
        # Create test trainer log
        test_trainer_log = [
            {
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
                "action": "adjust_difficulty",
                "previous_difficulty": 0.5 - (i * 0.05),
                "new_difficulty": 0.5 - ((i - 1) * 0.05),
                "adjustment_factor": 0.05,
                "performance_trend": "improving"
            }
            for i in range(1, 6)
        ]
        MemoryManager.save("memory/advanced/trainer_log.json", test_trainer_log)
        
        # Test adjust_difficulty
        new_difficulty = DifficultyAdjuster.adjust_difficulty(0.5)
        print(f"Adjusted difficulty: 0.5 -> {new_difficulty}")
        
        # Test get_difficulty_for_skill
        python_difficulty = DifficultyAdjuster.get_difficulty_for_skill("python")
        error_handling_difficulty = DifficultyAdjuster.get_difficulty_for_skill("error_handling")
        print(f"Difficulty for python: {python_difficulty}")
        print(f"Difficulty for error_handling: {error_handling_difficulty}")
        
        # Test get_difficulty_curve
        curve_data = DifficultyAdjuster.get_difficulty_curve()
        print(f"Difficulty curve: {json.dumps(curve_data, indent=2)}")
        
        print("All tests passed")
    except Exception as e:
        print(f"Test failed: {e}")

