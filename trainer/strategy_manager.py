#!/usr/bin/env python3
"""
trainer/strategy_manager.py

This module provides functionality for managing training strategies
in the Builder-Trainer Cognitive Loop system.
"""

import os
import sys
import json
import logging
import random
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime, timedelta
from collections import Counter

# Import system components
from memory_manager import MemoryManager
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
logger = logging.getLogger("trainer.strategy_manager")

class StrategyManager:
    """
    A class that provides methods for managing training strategies.
    """
    
    # Strategy types
    STRATEGY_TYPES = [
        "skill_gap_filling",
        "style_improvement",
        "regression_prevention",
        "skill_advancement",
        "exploration",
        "consolidation"
    ]
    
    # Strategy weights (default)
    DEFAULT_STRATEGY_WEIGHTS = {
        "skill_gap_filling": 0.3,
        "style_improvement": 0.2,
        "regression_prevention": 0.2,
        "skill_advancement": 0.1,
        "exploration": 0.1,
        "consolidation": 0.1
    }
    
    @staticmethod
    def get_next_skill_focus() -> str:
        """
        Determine the next skill to focus on.
        
        Returns:
            The next skill to focus on
        """
        logger.info("Determining next skill focus")
        
        try:
            # Get builder analysis
            analysis = BuilderAnalyzer.analyze_builder_profile()
            
            # Get current strategy
            strategy = StrategyManager._get_current_strategy()
            
            # Determine focus based on strategy
            if strategy == "skill_gap_filling":
                focus = StrategyManager._get_skill_gap_focus(analysis)
            elif strategy == "style_improvement":
                focus = StrategyManager._get_style_improvement_focus(analysis)
            elif strategy == "regression_prevention":
                focus = StrategyManager._get_regression_prevention_focus(analysis)
            elif strategy == "skill_advancement":
                focus = StrategyManager._get_skill_advancement_focus(analysis)
            elif strategy == "exploration":
                focus = StrategyManager._get_exploration_focus(analysis)
            elif strategy == "consolidation":
                focus = StrategyManager._get_consolidation_focus(analysis)
            else:
                # Default to skill gap filling
                focus = StrategyManager._get_skill_gap_focus(analysis)
            
            # Log the focus
            logger.info(f"Next skill focus: {focus} (strategy: {strategy})")
            
            # Log to trainer log
            trainer_log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": "get_next_skill_focus",
                "strategy": strategy,
                "focus": focus
            }
            MemoryManager.append("memory/advanced/trainer_log.json", trainer_log_entry)
            
            return focus
        except Exception as e:
            logger.error(f"Error determining next skill focus: {e}")
            return "general_improvement"
    
    @staticmethod
    def _get_current_strategy() -> str:
        """
        Get the current training strategy.
        
        Returns:
            The current strategy
        """
        try:
            # Load strategy weights
            weights_path = "memory/advanced/strategy_weights.json"
            if os.path.exists(weights_path):
                weights = MemoryManager.load(weights_path)
            else:
                weights = StrategyManager.DEFAULT_STRATEGY_WEIGHTS
            
            # Check if we should update the weights
            last_update_path = "memory/advanced/strategy_last_update.json"
            if os.path.exists(last_update_path):
                last_update = MemoryManager.load(last_update_path)
                last_update_time = datetime.fromisoformat(last_update.get("timestamp", "2000-01-01T00:00:00"))
                
                # Update weights every day
                if datetime.now() - last_update_time > timedelta(days=1):
                    weights = StrategyManager._update_strategy_weights()
            else:
                # First time, update weights
                weights = StrategyManager._update_strategy_weights()
            
            # Select strategy based on weights
            strategies = list(weights.keys())
            weights_list = [weights[s] for s in strategies]
            
            # Normalize weights
            total_weight = sum(weights_list)
            if total_weight > 0:
                weights_list = [w / total_weight for w in weights_list]
            else:
                weights_list = [1.0 / len(weights_list)] * len(weights_list)
            
            # Select strategy
            strategy = random.choices(strategies, weights=weights_list, k=1)[0]
            
            return strategy
        except Exception as e:
            logger.error(f"Error getting current strategy: {e}")
            return "skill_gap_filling"  # Default strategy
    
    @staticmethod
    def _update_strategy_weights() -> Dict[str, float]:
        """
        Update the strategy weights based on the Builder agent's profile.
        
        Returns:
            Updated strategy weights
        """
        try:
            # Get builder analysis
            analysis = BuilderAnalyzer.analyze_builder_profile()
            
            # Start with default weights
            weights = StrategyManager.DEFAULT_STRATEGY_WEIGHTS.copy()
            
            # Adjust weights based on analysis
            profile_summary = analysis.get("profile_summary", {})
            performance_trend = analysis.get("performance_trend", {})
            skill_gaps = analysis.get("skill_gaps", [])
            style_issues = analysis.get("style_issues", [])
            
            # Adjust for skill gaps
            if skill_gaps:
                weights["skill_gap_filling"] += 0.1
            
            # Adjust for style issues
            if style_issues:
                weights["style_improvement"] += 0.1
            
            # Adjust for performance trend
            trend = performance_trend.get("trend", "neutral")
            if trend in ["strongly_improving", "improving"]:
                # If improving, focus more on advancement and exploration
                weights["skill_advancement"] += 0.1
                weights["exploration"] += 0.05
            elif trend in ["strongly_declining", "declining"]:
                # If declining, focus more on consolidation and regression prevention
                weights["consolidation"] += 0.1
                weights["regression_prevention"] += 0.05
            
            # Normalize weights
            total_weight = sum(weights.values())
            if total_weight > 0:
                weights = {k: v / total_weight for k, v in weights.items()}
            
            # Save weights
            MemoryManager.save("memory/advanced/strategy_weights.json", weights)
            
            # Save last update time
            MemoryManager.save("memory/advanced/strategy_last_update.json", {
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Updated strategy weights: {weights}")
            
            return weights
        except Exception as e:
            logger.error(f"Error updating strategy weights: {e}")
            return StrategyManager.DEFAULT_STRATEGY_WEIGHTS
    
    @staticmethod
    def _get_skill_gap_focus(analysis: Dict) -> str:
        """
        Get a focus for skill gap filling.
        
        Args:
            analysis: Analysis of the Builder agent's profile
            
        Returns:
            Focus for skill gap filling
        """
        skill_gaps = analysis.get("skill_gaps", [])
        
        if skill_gaps:
            # Focus on the highest priority skill gap
            skill = skill_gaps[0]["skill"]
            return f"skill_gap:{skill}"
        else:
            return "general_improvement"
    
    @staticmethod
    def _get_style_improvement_focus(analysis: Dict) -> str:
        """
        Get a focus for style improvement.
        
        Args:
            analysis: Analysis of the Builder agent's profile
            
        Returns:
            Focus for style improvement
        """
        style_issues = analysis.get("style_issues", [])
        
        if style_issues:
            # Focus on the highest priority style issue
            issue = style_issues[0]["issue"]
            return f"style_issue:{issue}"
        else:
            return "general_improvement"
    
    @staticmethod
    def _get_regression_prevention_focus(analysis: Dict) -> str:
        """
        Get a focus for regression prevention.
        
        Args:
            analysis: Analysis of the Builder agent's profile
            
        Returns:
            Focus for regression prevention
        """
        # Load skill map
        skill_map = MemoryManager.load("memory/core/skill_map.json", default={"skills": {}})
        
        # Find skills that haven't been used recently
        now = datetime.now()
        unused_skills = []
        
        for skill_name, skill_data in skill_map.get("skills", {}).items():
            level = skill_data.get("level", 0.0)
            tasks_completed = skill_data.get("tasks_completed", 0)
            last_used_str = skill_data.get("last_used", "")
            
            if last_used_str and tasks_completed > 0 and level > 0.3:
                try:
                    last_used = datetime.fromisoformat(last_used_str)
                    days_since_last_use = (now - last_used).days
                    
                    if days_since_last_use > 7:
                        unused_skills.append((skill_name, days_since_last_use))
                except:
                    pass
        
        if unused_skills:
            # Sort by days since last use (descending)
            unused_skills.sort(key=lambda x: x[1], reverse=True)
            
            # Focus on the skill that hasn't been used for the longest time
            skill = unused_skills[0][0]
            return f"learning:regression_prevention:{skill}"
        else:
            return "general_improvement"
    
    @staticmethod
    def _get_skill_advancement_focus(analysis: Dict) -> str:
        """
        Get a focus for skill advancement.
        
        Args:
            analysis: Analysis of the Builder agent's profile
            
        Returns:
            Focus for skill advancement
        """
        # Load skill map
        skill_map = MemoryManager.load("memory/core/skill_map.json", default={"skills": {}})
        
        # Find skills that are ready for advancement
        advancement_skills = []
        
        for skill_name, skill_data in skill_map.get("skills", {}).items():
            level = skill_data.get("level", 0.0)
            tasks_completed = skill_data.get("tasks_completed", 0)
            
            if 0.4 <= level <= 0.7 and tasks_completed >= 3:
                advancement_skills.append((skill_name, level))
        
        if advancement_skills:
            # Sort by level (ascending, to focus on lower levels first)
            advancement_skills.sort(key=lambda x: x[1])
            
            # Focus on the skill with the lowest level
            skill = advancement_skills[0][0]
            return f"learning:skill_advancement:{skill}"
        else:
            return "general_improvement"
    
    @staticmethod
    def _get_exploration_focus(analysis: Dict) -> str:
        """
        Get a focus for exploration.
        
        Args:
            analysis: Analysis of the Builder agent's profile
            
        Returns:
            Focus for exploration
        """
        # Load skill map
        skill_map = MemoryManager.load("memory/core/skill_map.json", default={"skills": {}})
        
        # Get all skills
        known_skills = set(skill_map.get("skills", {}).keys())
        
        # Define potential new skills
        potential_skills = {
            "python", "file_io", "error_handling", "testing", "json_parsing",
            "data_processing", "algorithms", "web_scraping", "api_client",
            "database", "concurrency", "networking", "gui", "command_line",
            "data_visualization", "machine_learning", "natural_language_processing"
        }
        
        # Find skills that haven't been explored yet
        unexplored_skills = potential_skills - known_skills
        
        if unexplored_skills:
            # Select a random unexplored skill
            skill = random.choice(list(unexplored_skills))
            return f"skill_gap:{skill}"
        else:
            return "general_improvement"
    
    @staticmethod
    def _get_consolidation_focus(analysis: Dict) -> str:
        """
        Get a focus for consolidation.
        
        Args:
            analysis: Analysis of the Builder agent's profile
            
        Returns:
            Focus for consolidation
        """
        # Load task history
        task_history = StrategyManager._get_task_history()
        
        # Count skills by frequency
        skill_counts = Counter()
        for task in task_history:
            skills = task.get("skills_required", [])
            for skill in skills:
                skill_counts[skill] += 1
        
        if skill_counts:
            # Get the most common skills
            common_skills = skill_counts.most_common()
            
            # Focus on one of the top 3 most common skills
            top_skills = [skill for skill, _ in common_skills[:3]]
            skill = random.choice(top_skills)
            
            return f"learning:consolidation:{skill}"
        else:
            return "general_improvement"
    
    @staticmethod
    def _get_task_history() -> List[Dict]:
        """
        Get the task history.
        
        Returns:
            List of tasks
        """
        try:
            # Get all task files
            task_dir = "memory/task_memory"
            task_files = [f for f in os.listdir(task_dir) if f.startswith("task_") and f.endswith(".json")]
            
            # Load tasks
            tasks = []
            for file_name in task_files:
                try:
                    task = MemoryManager.load(os.path.join(task_dir, file_name))
                    tasks.append(task)
                except:
                    pass
            
            return tasks
        except Exception as e:
            logger.error(f"Error getting task history: {e}")
            return []
    
    @staticmethod
    def get_skill_distribution() -> Dict:
        """
        Get the distribution of skills in the task history.
        
        Returns:
            Dictionary with skill distribution data
        """
        try:
            # Get task history
            task_history = StrategyManager._get_task_history()
            
            # Count skills by frequency
            skill_counts = Counter()
            for task in task_history:
                skills = task.get("skills_required", [])
                for skill in skills:
                    skill_counts[skill] += 1
            
            # Calculate percentages
            total_count = sum(skill_counts.values())
            skill_percentages = {}
            
            if total_count > 0:
                for skill, count in skill_counts.items():
                    skill_percentages[skill] = round(count / total_count * 100, 1)
            
            # Create distribution data
            distribution = {
                "counts": dict(skill_counts),
                "percentages": skill_percentages,
                "total_tasks": len(task_history),
                "unique_skills": len(skill_counts)
            }
            
            return distribution
        except Exception as e:
            logger.error(f"Error getting skill distribution: {e}")
            return {"counts": {}, "percentages": {}, "total_tasks": 0, "unique_skills": 0}


# Alias for backward compatibility
get_next_skill_focus = StrategyManager.get_next_skill_focus


if __name__ == "__main__":
    # Simple test
    try:
        # Ensure directories exist
        os.makedirs("memory/logs", exist_ok=True)
        os.makedirs("memory/core", exist_ok=True)
        os.makedirs("memory/advanced", exist_ok=True)
        os.makedirs("memory/task_memory", exist_ok=True)
        
        # Create test skill map
        test_skill_map = {
            "skills": {
                "python": {
                    "level": 0.7,
                    "tasks_completed": 8,
                    "last_used": datetime.now().isoformat()
                },
                "json_parsing": {
                    "level": 0.6,
                    "tasks_completed": 3,
                    "last_used": datetime.now().isoformat()
                },
                "error_handling": {
                    "level": 0.2,
                    "tasks_completed": 2,
                    "last_used": (datetime.now() - timedelta(days=2)).isoformat()
                },
                "testing": {
                    "level": 0.1,
                    "tasks_completed": 1,
                    "last_used": (datetime.now() - timedelta(days=5)).isoformat()
                },
                "file_io": {
                    "level": 0.5,
                    "tasks_completed": 4,
                    "last_used": (datetime.now() - timedelta(days=10)).isoformat()
                }
            }
        }
        MemoryManager.save("memory/core/skill_map.json", test_skill_map)
        
        # Create test tasks
        for i in range(5):
            test_task = {
                "id": f"test_task_{i}",
                "goal": f"Test task {i}",
                "difficulty": 0.5,
                "skills_required": ["python", "json_parsing"] if i % 2 == 0 else ["error_handling", "testing"],
                "created_at": (datetime.now() - timedelta(days=i)).isoformat()
            }
            MemoryManager.save(f"memory/task_memory/task_test_task_{i}.json", test_task)
        
        # Test get_next_skill_focus
        focus = StrategyManager.get_next_skill_focus()
        print(f"Next skill focus: {focus}")
        
        # Test get_skill_distribution
        distribution = StrategyManager.get_skill_distribution()
        print(f"Skill distribution: {json.dumps(distribution, indent=2)}")
        
        # Test different strategies
        for strategy in StrategyManager.STRATEGY_TYPES:
            focus = getattr(StrategyManager, f"_get_{strategy}_focus")({"skill_gaps": [], "style_issues": []})
            print(f"Focus for {strategy}: {focus}")
        
        print("All tests passed")
    except Exception as e:
        print(f"Test failed: {e}")

