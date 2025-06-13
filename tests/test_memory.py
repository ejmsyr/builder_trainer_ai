#!/usr/bin/env python3
"""
tests/test_memory.py

This module contains tests for the memory manager.
"""

import os
import sys
import json
import shutil
import unittest
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import system components
from memory_manager import MemoryManager

class TestMemoryManager(unittest.TestCase):
    """
    Test case for the memory manager.
    """
    
    def setUp(self):
        """
        Set up the test case.
        """
        # Create test directory
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_memory')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create test file
        self.test_file = os.path.join(self.test_dir, 'test.json')
        self.test_data = {
            'id': 'test',
            'value': 42,
            'nested': {
                'key': 'value'
            },
            'list': [1, 2, 3]
        }
    
    def tearDown(self):
        """
        Clean up after the test case.
        """
        # Remove test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_save_and_load(self):
        """
        Test saving and loading data.
        """
        # Save data
        MemoryManager.save(self.test_file, self.test_data)
        
        # Check that file exists
        self.assertTrue(os.path.exists(self.test_file))
        
        # Load data
        loaded_data = MemoryManager.load(self.test_file)
        
        # Check that data is correct
        self.assertEqual(loaded_data, self.test_data)
    
    def test_load_nonexistent(self):
        """
        Test loading a nonexistent file.
        """
        # Load nonexistent file with default
        default_data = {'default': True}
        loaded_data = MemoryManager.load('nonexistent.json', default=default_data)
        
        # Check that default data is returned
        self.assertEqual(loaded_data, default_data)
    
    def test_append(self):
        """
        Test appending data to a file.
        """
        # Create list file
        list_file = os.path.join(self.test_dir, 'list.json')
        initial_list = [{'id': 1}]
        MemoryManager.save(list_file, initial_list)
        
        # Append item
        new_item = {'id': 2}
        MemoryManager.append(list_file, new_item)
        
        # Load data
        loaded_data = MemoryManager.load(list_file)
        
        # Check that data is correct
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0], initial_list[0])
        self.assertEqual(loaded_data[1], new_item)
    
    def test_add_task_to_queue(self):
        """
        Test adding a task to the queue.
        """
        # Create queue file
        queue_file = os.path.join(self.test_dir, 'task_queue.json')
        initial_queue = {'queue': []}
        MemoryManager.save(queue_file, initial_queue)
        
        # Create task
        task = {
            'id': 'test_task',
            'goal': 'Test task',
            'priority': 1
        }
        
        # Add task to queue
        MemoryManager.add_task_to_queue(task, priority=1, queue_path=queue_file)
        
        # Load queue
        loaded_queue = MemoryManager.load(queue_file)
        
        # Check that task is in queue
        self.assertEqual(len(loaded_queue['queue']), 1)
        self.assertEqual(loaded_queue['queue'][0]['id'], task['id'])
    
    def test_get_next_task(self):
        """
        Test getting the next task from the queue.
        """
        # Create queue file
        queue_file = os.path.join(self.test_dir, 'task_queue.json')
        initial_queue = {
            'queue': [
                {
                    'id': 'task1',
                    'priority': 2
                },
                {
                    'id': 'task2',
                    'priority': 1  # Higher priority (lower number)
                }
            ]
        }
        MemoryManager.save(queue_file, initial_queue)
        
        # Get next task
        next_task = MemoryManager.get_next_task(queue_path=queue_file)
        
        # Check that task is correct (highest priority)
        self.assertEqual(next_task['id'], 'task2')
        
        # Check that task is removed from queue
        loaded_queue = MemoryManager.load(queue_file)
        self.assertEqual(len(loaded_queue['queue']), 1)
        self.assertEqual(loaded_queue['queue'][0]['id'], 'task1')
    
    def test_log_system_event(self):
        """
        Test logging a system event.
        """
        # Create log file
        log_file = os.path.join(self.test_dir, 'system_log.json')
        initial_log = []
        MemoryManager.save(log_file, initial_log)
        
        # Log event
        MemoryManager.log_system_event(
            'INFO',
            'test_component',
            'Test message',
            {'key': 'value'},
            log_path=log_file
        )
        
        # Load log
        loaded_log = MemoryManager.load(log_file)
        
        # Check that event is logged
        self.assertEqual(len(loaded_log), 1)
        self.assertEqual(loaded_log[0]['level'], 'INFO')
        self.assertEqual(loaded_log[0]['component'], 'test_component')
        self.assertEqual(loaded_log[0]['message'], 'Test message')
        self.assertEqual(loaded_log[0]['details'], {'key': 'value'})
        self.assertTrue('timestamp' in loaded_log[0])


if __name__ == '__main__':
    unittest.main()

