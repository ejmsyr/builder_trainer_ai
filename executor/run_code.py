#!/usr/bin/env python3
"""
executor/run_code.py

This module provides functionality for executing Python code safely
in the Builder-Trainer Cognitive Loop system.
"""

import os
import sys
import time
import uuid
import signal
import logging
import tempfile
import resource
import traceback
import threading
import subprocess
from typing import Dict, List, Optional, Union, Any, Tuple

# Import command executor
from executor.run_cmd import CommandExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("memory/logs/executor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("executor.run_code")

class CodeExecutor:
    """
    A class that provides methods for executing Python code safely.
    """
    
    @staticmethod
    def run_python_code(
        code: str,
        timeout: int = 60,
        working_dir: Optional[str] = None,
        log_file: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        args: Optional[List[str]] = None,
        save_path: Optional[str] = None
    ) -> Dict:
        """
        Execute Python code safely.
        
        Args:
            code: The Python code to execute
            timeout: Timeout in seconds
            working_dir: Working directory for code execution
            log_file: Path to log file for code output
            env: Environment variables for code execution
            args: Command-line arguments for the Python script
            save_path: Path to save the Python script (if None, a temporary file is used)
            
        Returns:
            Dictionary with code execution results
        """
        # Create a temporary file or use the provided save path
        if save_path:
            script_path = save_path
            os.makedirs(os.path.dirname(script_path), exist_ok=True)
            temp_file = False
        else:
            # Create a temporary file
            fd, script_path = tempfile.mkstemp(suffix='.py', prefix='builder_')
            os.close(fd)
            temp_file = True
        
        try:
            # Write code to file
            with open(script_path, 'w') as f:
                f.write(code)
            
            logger.info(f"Saved Python code to {script_path}")
            
            # Prepare command
            cmd = [sys.executable, script_path]
            if args:
                cmd.extend(args)
            
            # Execute the script
            result = CommandExecutor.run_cmd(
                command=" ".join(cmd),
                timeout=timeout,
                working_dir=working_dir,
                log_file=log_file,
                env=env
            )
            
            # Add script path to result
            result["script_path"] = script_path
            
            return result
        except Exception as e:
            logger.error(f"Error executing Python code: {str(e)}")
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "script_path": script_path,
                "timeout": timeout,
                "timed_out": False,
                "error": str(e)
            }
        finally:
            # Clean up temporary file if needed
            if temp_file and os.path.exists(script_path):
                try:
                    os.remove(script_path)
                except:
                    pass
    
    @staticmethod
    def run_python_function(
        func_code: str,
        func_name: str,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
        timeout: int = 60,
        memory_limit: int = 1024 * 1024 * 1024,  # 1 GB
        log_file: Optional[str] = None
    ) -> Dict:
        """
        Execute a Python function safely in a subprocess.
        
        Args:
            func_code: The Python code defining the function
            func_name: The name of the function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            timeout: Timeout in seconds
            memory_limit: Memory limit in bytes
            log_file: Path to log file for function output
            
        Returns:
            Dictionary with function execution results
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        
        # Create a temporary file for the wrapper script
        fd, script_path = tempfile.mkstemp(suffix='.py', prefix='builder_func_')
        os.close(fd)
        
        try:
            # Create a wrapper script that executes the function and returns the result
            wrapper_code = f"""
import os
import sys
import json
import traceback
import resource

# Set resource limits
def set_limits():
    # Set memory limit
    resource.setrlimit(resource.RLIMIT_AS, ({memory_limit}, {memory_limit}))

# Define the function
{func_code}

# Execute the function
try:
    set_limits()
    args = {args}
    kwargs = {kwargs}
    result = {func_name}(*args, **kwargs)
    print(json.dumps({{"success": True, "result": result}}))
except Exception as e:
    print(json.dumps({{"success": False, "error": str(e), "traceback": traceback.format_exc()}}))
"""
            
            # Write wrapper code to file
            with open(script_path, 'w') as f:
                f.write(wrapper_code)
            
            logger.info(f"Saved Python function wrapper to {script_path}")
            
            # Execute the wrapper script
            result = CommandExecutor.run_cmd(
                command=f"{sys.executable} {script_path}",
                timeout=timeout,
                log_file=log_file
            )
            
            # Parse the JSON output
            if result["success"]:
                try:
                    output = result["stdout"].strip()
                    if output:
                        func_result = json.loads(output)
                        result.update(func_result)
                except json.JSONDecodeError:
                    result["success"] = False
                    result["error"] = "Failed to parse function output as JSON"
            
            return result
        except Exception as e:
            logger.error(f"Error executing Python function: {str(e)}")
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "error": str(e)
            }
        finally:
            # Clean up temporary file
            if os.path.exists(script_path):
                try:
                    os.remove(script_path)
                except:
                    pass
    
    @staticmethod
    def run_script(
        script_path: str,
        language: str = "python",
        timeout: int = 60,
        working_dir: Optional[str] = None,
        log_file: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        args: Optional[List[str]] = None
    ) -> Dict:
        """
        Execute a script file.
        
        Args:
            script_path: Path to the script file
            language: Script language (python, bash, etc.)
            timeout: Timeout in seconds
            working_dir: Working directory for script execution
            log_file: Path to log file for script output
            env: Environment variables for script execution
            args: Command-line arguments for the script
            
        Returns:
            Dictionary with script execution results
        """
        if not os.path.exists(script_path):
            error_msg = f"Script file not found: {script_path}"
            logger.error(error_msg)
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": error_msg,
                "script_path": script_path,
                "timeout": timeout,
                "timed_out": False,
                "error": error_msg
            }
        
        # Prepare command based on language
        if language.lower() == "python":
            cmd = [sys.executable, script_path]
        elif language.lower() == "bash":
            cmd = ["bash", script_path]
        elif language.lower() == "sh":
            cmd = ["sh", script_path]
        else:
            # For other languages, try to use the language name as the command
            cmd = [language, script_path]
        
        # Add arguments if provided
        if args:
            cmd.extend(args)
        
        # Execute the script
        result = CommandExecutor.run_cmd(
            command=" ".join(cmd),
            timeout=timeout,
            working_dir=working_dir,
            log_file=log_file,
            env=env
        )
        
        # Add script path to result
        result["script_path"] = script_path
        
        return result
    
    @staticmethod
    def archive_code(
        code: str,
        task_id: str,
        file_name: str = "code.py",
        code_archive_dir: str = "memory/code_archive"
    ) -> str:
        """
        Archive code for a task.
        
        Args:
            code: The code to archive
            task_id: The ID of the task
            file_name: The name of the file
            code_archive_dir: The directory for code archives
            
        Returns:
            The path to the archived code file
        """
        # Create archive directory for the task
        task_dir = os.path.join(code_archive_dir, task_id)
        os.makedirs(task_dir, exist_ok=True)
        
        # Add timestamp to file name
        timestamp = int(time.time())
        base_name, ext = os.path.splitext(file_name)
        archive_file_name = f"{base_name}_{timestamp}{ext}"
        archive_path = os.path.join(task_dir, archive_file_name)
        
        # Write code to archive file
        with open(archive_path, 'w') as f:
            f.write(code)
        
        logger.info(f"Archived code for task {task_id} to {archive_path}")
        
        return archive_path


# Aliases for backward compatibility
run_python_code = CodeExecutor.run_python_code
run_script = CodeExecutor.run_script
archive_code = CodeExecutor.archive_code


if __name__ == "__main__":
    # Simple test
    try:
        # Ensure log directory exists
        os.makedirs("memory/logs", exist_ok=True)
        os.makedirs("memory/code_archive", exist_ok=True)
        
        # Test running Python code
        test_code = """
print("Hello from Python code!")
for i in range(5):
    print(f"Count: {i}")
"""
        result = CodeExecutor.run_python_code(test_code)
        print(f"Python code result: {result['success']}")
        print(f"Output: {result['stdout']}")
        
        # Test running Python function
        func_code = """
def add(a, b):
    return a + b
"""
        result = CodeExecutor.run_python_function(func_code, "add", args=[2, 3])
        print(f"Function result: {result['success']}")
        if result['success']:
            print(f"Result: {result['result']}")
        
        # Test archiving code
        archive_path = CodeExecutor.archive_code(test_code, "test_task_001")
        print(f"Archived code to: {archive_path}")
        
        print("All tests passed")
    except Exception as e:
        print(f"Test failed: {e}")

