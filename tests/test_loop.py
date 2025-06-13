#!/usr/bin/env python3
"""
tests/test_loop.py

This module contains tests for the main loop.
"""

import os
import sys
import json
import shutil
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import system components
import loop
from memory_manager import MemoryManager

class TestLoop(unittest.TestCase):
    """
    Test case for the main loop.
    """
    
    def setUp(self):
        """
        Set up the test case.
        """
        # Create test directory
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_loop')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create test memory directories
        os.makedirs(os.path.join(self.test_dir, 'core'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'task_memory'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'advanced'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'logs'), exist_ok=True)
        
        # Create test task queue
        self.queue_path = os.path.join(self.test_dir, 'task_memory', 'task_queue.json')
        MemoryManager.save(self.queue_path, {'queue': []})
        
        # Create test task
        self.task = {
            'id': 'test_task',
            'goal': 'Test task',
            'difficulty': 0.5,
            'constraints': ['Test constraint'],
            'skills_required': ['python'],
            'expected_outcome': 'Test outcome',
            'source': 'trainer',
            'created_at': datetime.now().isoformat()
        }
        self.task_path = os.path.join(self.test_dir, 'task_memory', f"task_{self.task['id']}.json")
        MemoryManager.save(self.task_path, self.task)
    
    def tearDown(self):
        """
        Clean up after the test case.
        """
        # Remove test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @patch('loop.BuilderAgent')
    @patch('loop.BuilderReflection')
    def test_process_task(self, mock_reflection, mock_builder):
        """
        Test processing a task.
        """
        # Mock builder result
        mock_result = {
            'success': True,
            'score': 85.5,
            'metrics': {
                'correctness': 0.9,
                'efficiency': 0.8,
                'elegance': 0.7,
                'robustness': 0.6
            },
            'code_path': '/path/to/code.py',
            'execution_result': {'success': True}
        }
        mock_builder.run_project.return_value = mock_result
        
        # Mock reflection result
        mock_reflection_result = {
            'strengths': ['Test strength'],
            'weaknesses': ['Test weakness'],
            'lessons_learned': ['Test lesson'],
            'skill_improvements': {'python': 0.1}
        }
        mock_reflection.reflect_on_task.return_value = mock_reflection_result
        
        # Process task
        result = loop.process_task(self.task)
        
        # Check that builder was called
        mock_builder.run_project.assert_called_once_with(self.task)
        
        # Check that reflection was called
        mock_reflection.reflect_on_task.assert_called_once()
        
        # Check result
        self.assertTrue(result['success'])
        self.assertEqual(result['score'], 85.5)
    
    @patch('loop.process_task')
    @patch('loop.MemoryManager')
    def test_run_loop_with_task(self, mock_memory, mock_process):
        """
        Test running the loop with a task in the queue.
        """
        # Mock get_next_task
        mock_memory.get_next_task.return_value = self.task
        
        # Mock process_task
        mock_process.return_value = {
            'success': True,
            'score': 85.5
        }
        
        # Run loop once
        loop.run_loop_once(queue_path=self.queue_path)
        
        # Check that get_next_task was called
        mock_memory.get_next_task.assert_called_once()
        
        # Check that process_task was called
        mock_process.assert_called_once_with(self.task)
    
    @patch('loop.process_task')
    @patch('loop.MemoryManager')
    @patch('loop.TaskGenerator')
    def test_run_loop_without_task(self, mock_generator, mock_memory, mock_process):
        """
        Test running the loop without a task in the queue.
        """
        # Mock get_next_task
        mock_memory.get_next_task.return_value = None
        
        # Mock generate_task
        generated_task = {
            'id': 'generated_task',
            'goal': 'Generated task',
            'difficulty': 0.5
        }
        mock_generator.generate_task.return_value = generated_task
        
        # Mock process_task
        mock_process.return_value = {
            'success': True,
            'score': 85.5
        }
        
        # Run loop once
        loop.run_loop_once(queue_path=self.queue_path)
        
        # Check that get_next_task was called
        mock_memory.get_next_task.assert_called_once()
        
        # Check that generate_task was called
        mock_generator.generate_task.assert_called_once()
        
        # Check that process_task was called with generated task
        mock_process.assert_called_once_with(generated_task)
    
    @patch('loop.process_task')
    @patch('loop.MemoryManager')
    def test_run_loop_with_error(self, mock_memory, mock_process):
        """
        Test running the loop with an error.
        """
        # Mock get_next_task
        mock_memory.get_next_task.return_value = self.task
        
        # Mock process_task to raise exception
        mock_process.side_effect = Exception("Test error")
        
        # Run loop once
        loop.run_loop_once(queue_path=self.queue_path)
        
        # Check that get_next_task was called
        mock_memory.get_next_task.assert_called_once()
        
        # Check that process_task was called
        mock_process.assert_called_once_with(self.task)
        
        # Check that log_system_event was called
        mock_memory.log_system_event.assert_called()


if __name__ == '__main__':
    unittest.main()

