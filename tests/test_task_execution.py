#!/usr/bin/env python3
"""
tests/test_task_execution.py

This module contains tests for task execution.
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
from builder.run_project import BuilderAgent
from executor.run_cmd import CommandExecutor
from executor.run_code import CodeExecutor

class TestTaskExecution(unittest.TestCase):
    """
    Test case for task execution.
    """
    
    def setUp(self):
        """
        Set up the test case.
        """
        # Create test directory
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_execution')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create test code
        self.test_code = """
def factorial(n):
    if n < 0:
        return None
    if n == 0:
        return 1
    return n * factorial(n - 1)

if __name__ == "__main__":
    print(factorial(5))
"""
        
        # Create test task
        self.task = {
            'id': 'test_task',
            'goal': 'Calculate factorial',
            'difficulty': 0.5,
            'constraints': ['Handle negative numbers'],
            'skills_required': ['python', 'recursion'],
            'expected_outcome': 'A function that calculates factorial'
        }
    
    def tearDown(self):
        """
        Clean up after the test case.
        """
        # Remove test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @patch('executor.run_code.subprocess.run')
    def test_run_python_code(self, mock_run):
        """
        Test running Python code.
        """
        # Mock subprocess.run
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b'120\n'
        mock_run.return_value = mock_process
        
        # Run code
        result = CodeExecutor.run_python_code(
            self.test_code,
            timeout=10,
            log_file=os.path.join(self.test_dir, 'test.log'),
            save_path=os.path.join(self.test_dir, 'test.py')
        )
        
        # Check result
        self.assertTrue(result['success'])
        self.assertEqual(result['output'], '120\n')
        self.assertEqual(result['exit_code'], 0)
        
        # Check that file was saved
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'test.py')))
    
    @patch('executor.run_cmd.subprocess.run')
    def test_run_cmd(self, mock_run):
        """
        Test running a shell command.
        """
        # Mock subprocess.run
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b'Hello, world!\n'
        mock_run.return_value = mock_process
        
        # Run command
        result = CommandExecutor.run_cmd(
            'echo "Hello, world!"',
            timeout=10,
            log_file=os.path.join(self.test_dir, 'cmd.log')
        )
        
        # Check result
        self.assertTrue(result['success'])
        self.assertEqual(result['output'], 'Hello, world!\n')
        self.assertEqual(result['exit_code'], 0)
    
    @patch('builder.run_project.LLMInterface')
    @patch('builder.run_project.CodeExecutor')
    def test_builder_agent(self, mock_executor, mock_llm):
        """
        Test the BuilderAgent.
        """
        # Mock LLMInterface
        mock_llm.code_completion.return_value = self.test_code
        mock_llm.analyze_code.return_value = {
            'scores': {
                'correctness': 0.9,
                'efficiency': 0.8,
                'elegance': 0.7,
                'robustness': 0.6
            }
        }
        
        # Mock CodeExecutor
        mock_executor.archive_code.return_value = os.path.join(self.test_dir, 'code.py')
        mock_executor.run_python_code.return_value = {
            'success': True,
            'output': '120\n',
            'exit_code': 0
        }
        
        # Create directories
        os.makedirs(os.path.join(self.test_dir, 'memory', 'logs'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'memory', 'code_archive', self.task['id']), exist_ok=True)
        
        # Run project
        with patch('os.path.join', return_value=os.path.join(self.test_dir, 'memory', 'logs', 'builder.log')):
            result = BuilderAgent._execute_code(self.test_code, self.task)
        
        # Check result
        self.assertTrue(result['success'])
        self.assertEqual(result['output'], '120\n')
        self.assertEqual(result['exit_code'], 0)


if __name__ == '__main__':
    unittest.main()

