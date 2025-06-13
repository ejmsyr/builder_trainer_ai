#!/usr/bin/env python3
"""
trainer/analyze_builder.py

This module provides functionality for analyzing the Builder agent's profile and performance
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
logger = logging.getLogger("trainer.analyze_builder")

class BuilderAnalyzer:
    """
    A class that provides methods for analyzing the Builder agent's profile and performance.
    """
    
    @staticmethod
    def analyze_builder_profile() -> Dict:
        """
        Analyze the Builder agent's profile and performance.
        
        Returns:
            Dictionary with analysis results
        """
        logger.info("Analyzing builder profile")
        
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
            
            # Load skill map
            skill_map = MemoryManager.load("memory/core/skill_map.json", default={"skills": {}})
            
            # Load score log
            score_log = MemoryManager.load("memory/core/score_log.json", default=[])
            
            # Analyze performance trend
            performance_trend = ScoreEngine.get_performance_trend(n=10)
            
            # Identify skill gaps
            skill_gaps = BuilderAnalyzer._identify_skill_gaps(skill_map)
            
            # Identify style issues
            style_issues = BuilderAnalyzer._identify_style_issues(profile)
            
            # Identify learning opportunities
            learning_opportunities = BuilderAnalyzer._identify_learning_opportunities(
                profile, skill_map, score_log
            )
            
            # Create analysis result
            analysis = {
                "profile_summary": {
                    "task_count": profile.get("task_count", 0),
                    "average_score": profile.get("average_score", 0),
                    "skills_mastered_count": len(profile.get("skills_mastered", [])),
                    "weak_skills_count": len(profile.get("weak_skills", []))
                },
                "performance_trend": performance_trend,
                "skill_gaps": skill_gaps,
                "style_issues": style_issues,
                "learning_opportunities": learning_opportunities,
                "recommended_focus": BuilderAnalyzer._determine_recommended_focus(
                    skill_gaps, style_issues, learning_opportunities
                ),
                "timestamp": datetime.now().isoformat()
            }
            
            # Save analysis to memory
            analysis_path = f"memory/advanced/builder_analysis_{int(datetime.now().timestamp())}.json"
            MemoryManager.save(analysis_path, analysis)
            
            logger.info("Builder profile analysis completed")
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing builder profile: {e}")
            
            # Create basic analysis with error information
            basic_analysis = {
                "profile_summary": {
                    "task_count": 0,
                    "average_score": 0,
                    "skills_mastered_count": 0,
                    "weak_skills_count": 0
                },
                "performance_trend": {"trend": "neutral", "average": 0},
                "skill_gaps": [],
                "style_issues": [],
                "learning_opportunities": [],
                "recommended_focus": "error_recovery",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            return basic_analysis
    
    @staticmethod
    def _identify_skill_gaps(skill_map: Dict) -> List[Dict]:
        """
        Identify skill gaps in the Builder agent's skill map.
        
        Args:
            skill_map: The Builder agent's skill map
            
        Returns:
            List of skill gaps
        """
        skill_gaps = []
        
        # Get all skills
        skills = skill_map.get("skills", {})
        
        # Check for low-level skills
        for skill_name, skill_data in skills.items():
            level = skill_data.get("level", 0)
            tasks_completed = skill_data.get("tasks_completed", 0)
            
            if level < 0.3 and tasks_completed > 0:
                # This is a skill gap
                skill_gaps.append({
                    "skill": skill_name,
                    "level": level,
                    "tasks_completed": tasks_completed,
                    "priority": "high" if level < 0.2 else "medium"
                })
        
        # Sort by priority (high first) and then by level (lowest first)
        skill_gaps.sort(
            key=lambda x: (0 if x["priority"] == "high" else 1, x["level"])
        )
        
        return skill_gaps
    
    @staticmethod
    def _identify_style_issues(profile: Dict) -> List[Dict]:
        """
        Identify style issues in the Builder agent's profile.
        
        Args:
            profile: The Builder agent's profile
            
        Returns:
            List of style issues
        """
        style_issues = []
        
        # Get style flags
        style_flags = profile.get("style_flags", {})
        
        # Check for style issues
        for flag_name, count in style_flags.items():
            if count >= 3:
                # This is a significant style issue
                style_issues.append({
                    "issue": flag_name,
                    "count": count,
                    "priority": "high" if count >= 5 else "medium"
                })
        
        # Sort by priority (high first) and then by count (highest first)
        style_issues.sort(
            key=lambda x: (0 if x["priority"] == "high" else 1, -x["count"])
        )
        
        return style_issues
    
    @staticmethod
    def _identify_learning_opportunities(
        profile: Dict, skill_map: Dict, score_log: List
    ) -> List[Dict]:
        """
        Identify learning opportunities for the Builder agent.
        
        Args:
            profile: The Builder agent's profile
            skill_map: The Builder agent's skill map
            score_log: The Builder agent's score log
            
        Returns:
            List of learning opportunities
        """
        learning_opportunities = []
        
        # Get all skills
        skills = skill_map.get("skills", {})
        
        # Check for skills with no recent practice
        now = datetime.now()
        for skill_name, skill_data in skills.items():
            level = skill_data.get("level", 0)
            tasks_completed = skill_data.get("tasks_completed", 0)
            last_used_str = skill_data.get("last_used", "")
            
            if last_used_str and tasks_completed > 0:
                try:
                    last_used = datetime.fromisoformat(last_used_str)
                    days_since_last_use = (now - last_used).days
                    
                    if days_since_last_use > 7 and level > 0.3:
                        # This is a learning opportunity (skill regression prevention)
                        learning_opportunities.append({
                            "skill": skill_name,
                            "level": level,
                            "days_since_last_use": days_since_last_use,
                            "type": "regression_prevention",
                            "priority": "high" if days_since_last_use > 14 else "medium"
                        })
                except:
                    pass
        
        # Check for skills that need advancement
        for skill_name, skill_data in skills.items():
            level = skill_data.get("level", 0)
            tasks_completed = skill_data.get("tasks_completed", 0)
            
            if 0.4 <= level <= 0.7 and tasks_completed >= 3:
                # This is a learning opportunity (skill advancement)
                learning_opportunities.append({
                    "skill": skill_name,
                    "level": level,
                    "tasks_completed": tasks_completed,
                    "type": "skill_advancement",
                    "priority": "medium"
                })
        
        # Sort by priority (high first) and then by type
        learning_opportunities.sort(
            key=lambda x: (0 if x["priority"] == "high" else 1, x["type"])
        )
        
        return learning_opportunities
    
    @staticmethod
    def _determine_recommended_focus(
        skill_gaps: List[Dict], style_issues: List[Dict], learning_opportunities: List[Dict]
    ) -> str:
        """
        Determine the recommended focus for the Builder agent.
        
        Args:
            skill_gaps: List of skill gaps
            style_issues: List of style issues
            learning_opportunities: List of learning opportunities
            
        Returns:
            The recommended focus
        """
        # Check for high-priority skill gaps
        high_priority_skill_gaps = [gap for gap in skill_gaps if gap["priority"] == "high"]
        if high_priority_skill_gaps:
            return f"skill_gap:{high_priority_skill_gaps[0]['skill']}"
        
        # Check for high-priority style issues
        high_priority_style_issues = [issue for issue in style_issues if issue["priority"] == "high"]
        if high_priority_style_issues:
            return f"style_issue:{high_priority_style_issues[0]['issue']}"
        
        # Check for high-priority learning opportunities
        high_priority_learning_opportunities = [
            opp for opp in learning_opportunities if opp["priority"] == "high"
        ]
        if high_priority_learning_opportunities:
            return f"learning:{high_priority_learning_opportunities[0]['type']}:{high_priority_learning_opportunities[0]['skill']}"
        
        # If no high-priority items, check for medium-priority skill gaps
        if skill_gaps:
            return f"skill_gap:{skill_gaps[0]['skill']}"
        
        # If no skill gaps, check for medium-priority style issues
        if style_issues:
            return f"style_issue:{style_issues[0]['issue']}"
        
        # If no style issues, check for medium-priority learning opportunities
        if learning_opportunities:
            return f"learning:{learning_opportunities[0]['type']}:{learning_opportunities[0]['skill']}"
        
        # If no specific focus, return general improvement
        return "general_improvement"


# Alias for backward compatibility
analyze_builder_profile = BuilderAnalyzer.analyze_builder_profile


if __name__ == "__main__":
    # Simple test
    try:
        # Ensure directories exist
        os.makedirs("memory/logs", exist_ok=True)
        os.makedirs("memory/core", exist_ok=True)
        os.makedirs("memory/advanced", exist_ok=True)
        
        # Create test profile
        test_profile = {
            "id": "builder_v0.1",
            "task_count": 10,
            "average_score": 75.5,
            "skills_mastered": ["python", "json_parsing"],
            "weak_skills": ["error_handling", "testing"],
            "style_flags": {
                "hardcoded_paths": 5,
                "missing_error_handling": 3,
                "poor_documentation": 2
            },
            "last_updated": datetime.now().isoformat()
        }
        MemoryManager.save("memory/core/builder_profile.json", test_profile)
        
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
        
        # Create test score log
        test_score_log = [
            {
                "task_id": f"task_{i}",
                "score": 70 + i * 2,
                "difficulty": 0.5,
                "source": "trainer",
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat()
            }
            for i in range(10)
        ]
        MemoryManager.save("memory/core/score_log.json", test_score_log)
        
        # Analyze builder profile
        analysis = BuilderAnalyzer.analyze_builder_profile()
        
        print(f"Analysis: {json.dumps(analysis, indent=2)}")
        
        print("Test passed")
    except Exception as e:
        print(f"Test failed: {e}")

