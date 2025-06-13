"""
trainer package

This package provides functionality for analyzing the Builder agent's performance,
generating tasks, and managing training strategies in the Builder-Trainer Cognitive Loop system.
"""

from trainer.analyze_builder import BuilderAnalyzer, analyze_builder_profile
from trainer.generate_task import TaskGenerator, generate_task
from trainer.adjust_difficulty import DifficultyAdjuster, adjust_difficulty
from trainer.strategy_manager import StrategyManager, get_next_skill_focus

__all__ = [
    'BuilderAnalyzer',
    'analyze_builder_profile',
    'TaskGenerator',
    'generate_task',
    'DifficultyAdjuster',
    'adjust_difficulty',
    'StrategyManager',
    'get_next_skill_focus'
]

