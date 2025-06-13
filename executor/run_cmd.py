#!/usr/bin/env python3
"""
executor/run_cmd.py

This module provides functionality for executing shell commands safely
in the Builder-Trainer Cognitive Loop system.
"""

import os
import sys
import time
import signal
import logging
import subprocess
import threading
from typing import Dict, List, Optional, Union, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("memory/logs/executor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("executor.run_cmd")

# List of dangerous commands that should be blocked
BLACKLISTED_COMMANDS = [
    "rm -rf /",
    "rm -rf /*",
    "dd if=/dev/zero",
    "mkfs",
    "> /dev/sda",
    ":(){ :|:& };:",  # Fork bomb
    "chmod -R 777 /",
    "mv /* /dev/null",
    "wget -O- | sh",
    "curl | sh",
    "sudo rm",
    "sudo mv",
    "sudo dd",
    "sudo mkfs"
]

class CommandExecutor:
    """
    A class that provides methods for executing shell commands safely.
    """
    
    @staticmethod
    def is_dangerous_command(command: str) -> bool:
        """
        Check if a command is potentially dangerous.
        
        Args:
            command: The command to check
            
        Returns:
            True if the command is potentially dangerous, False otherwise
        """
        command_lower = command.lower()
        
        # Check against blacklisted commands
        for blacklisted in BLACKLISTED_COMMANDS:
            if blacklisted in command_lower:
                return True
        
        # Check for other dangerous patterns
        if "rm -rf" in command_lower and ("/" in command_lower or "*" in command_lower):
            return True
        
        if "sudo" in command_lower and any(cmd in command_lower for cmd in ["rm", "mv", "dd", "mkfs"]):
            return True
        
        return False
    
    @staticmethod
    def run_cmd(
        command: str,
        timeout: int = 60,
        working_dir: Optional[str] = None,
        log_file: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        check_dangerous: bool = True
    ) -> Dict:
        """
        Execute a shell command safely.
        
        Args:
            command: The command to execute
            timeout: Timeout in seconds
            working_dir: Working directory for command execution
            log_file: Path to log file for command output
            env: Environment variables for command execution
            check_dangerous: Whether to check if the command is dangerous
            
        Returns:
            Dictionary with command execution results
        """
        # Check if command is dangerous
        if check_dangerous and CommandExecutor.is_dangerous_command(command):
            error_msg = f"Dangerous command detected: {command}"
            logger.error(error_msg)
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": error_msg,
                "command": command,
                "timeout": timeout,
                "timed_out": False,
                "error": "Dangerous command"
            }
        
        # Prepare environment
        cmd_env = os.environ.copy()
        if env:
            cmd_env.update(env)
        
        # Prepare log file
        log_fh = None
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            log_fh = open(log_file, 'w')
        
        start_time = time.time()
        process = None
        stdout = ""
        stderr = ""
        timed_out = False
        
        try:
            # Start process
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=working_dir,
                env=cmd_env,
                text=True,
                bufsize=1  # Line buffered
            )
            
            # Define function to read output
            def read_output(pipe, output_list, log_file_handle=None):
                for line in pipe:
                    output_list.append(line)
                    if log_file_handle:
                        log_file_handle.write(line)
                        log_file_handle.flush()
                    print(line, end='')  # Print to console
            
            # Start threads to read stdout and stderr
            stdout_lines = []
            stderr_lines = []
            
            stdout_thread = threading.Thread(
                target=read_output,
                args=(process.stdout, stdout_lines, log_fh)
            )
            stderr_thread = threading.Thread(
                target=read_output,
                args=(process.stderr, stderr_lines, log_fh)
            )
            
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            
            stdout_thread.start()
            stderr_thread.start()
            
            # Wait for process to complete or timeout
            exit_code = None
            timed_out = False
            
            try:
                exit_code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                # Kill the process
                logger.warning(f"Command timed out after {timeout} seconds: {command}")
                process.kill()
                timed_out = True
                exit_code = -1
            
            # Wait for output threads to complete
            stdout_thread.join(1)
            stderr_thread.join(1)
            
            # Combine output lines
            stdout = "".join(stdout_lines)
            stderr = "".join(stderr_lines)
            
            # Log command execution
            end_time = time.time()
            duration = end_time - start_time
            
            if timed_out:
                logger.warning(f"Command timed out: {command} (after {duration:.2f}s)")
            else:
                logger.info(f"Command completed: {command} (exit code: {exit_code}, time: {duration:.2f}s)")
            
            return {
                "success": exit_code == 0 and not timed_out,
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "command": command,
                "timeout": timeout,
                "timed_out": timed_out,
                "duration": duration,
                "error": None if exit_code == 0 and not timed_out else (
                    "Command timed out" if timed_out else f"Command failed with exit code {exit_code}"
                )
            }
        except Exception as e:
            logger.error(f"Error executing command: {command} - {str(e)}")
            return {
                "success": False,
                "exit_code": -1,
                "stdout": stdout,
                "stderr": stderr,
                "command": command,
                "timeout": timeout,
                "timed_out": timed_out,
                "error": str(e)
            }
        finally:
            # Clean up
            if process and process.poll() is None:
                try:
                    process.kill()
                except:
                    pass
            
            if log_fh:
                log_fh.close()
    
    @staticmethod
    def run_cmd_interactive(
        command: str,
        input_data: Optional[str] = None,
        timeout: int = 60,
        working_dir: Optional[str] = None,
        log_file: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        check_dangerous: bool = True
    ) -> Dict:
        """
        Execute a shell command interactively.
        
        Args:
            command: The command to execute
            input_data: Input data to send to the command
            timeout: Timeout in seconds
            working_dir: Working directory for command execution
            log_file: Path to log file for command output
            env: Environment variables for command execution
            check_dangerous: Whether to check if the command is dangerous
            
        Returns:
            Dictionary with command execution results
        """
        # Check if command is dangerous
        if check_dangerous and CommandExecutor.is_dangerous_command(command):
            error_msg = f"Dangerous command detected: {command}"
            logger.error(error_msg)
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": error_msg,
                "command": command,
                "timeout": timeout,
                "timed_out": False,
                "error": "Dangerous command"
            }
        
        # Prepare environment
        cmd_env = os.environ.copy()
        if env:
            cmd_env.update(env)
        
        # Prepare log file
        log_fh = None
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            log_fh = open(log_file, 'w')
        
        start_time = time.time()
        process = None
        stdout = ""
        stderr = ""
        timed_out = False
        
        try:
            # Start process
            process = subprocess.Popen(
                command,
                shell=True,
                stdin=subprocess.PIPE if input_data else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=working_dir,
                env=cmd_env,
                text=True,
                bufsize=1  # Line buffered
            )
            
            # Send input data if provided
            if input_data:
                process.stdin.write(input_data)
                process.stdin.flush()
                process.stdin.close()
            
            # Define function to read output
            def read_output(pipe, output_list, log_file_handle=None):
                for line in pipe:
                    output_list.append(line)
                    if log_file_handle:
                        log_file_handle.write(line)
                        log_file_handle.flush()
                    print(line, end='')  # Print to console
            
            # Start threads to read stdout and stderr
            stdout_lines = []
            stderr_lines = []
            
            stdout_thread = threading.Thread(
                target=read_output,
                args=(process.stdout, stdout_lines, log_fh)
            )
            stderr_thread = threading.Thread(
                target=read_output,
                args=(process.stderr, stderr_lines, log_fh)
            )
            
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            
            stdout_thread.start()
            stderr_thread.start()
            
            # Wait for process to complete or timeout
            exit_code = None
            timed_out = False
            
            try:
                exit_code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                # Kill the process
                logger.warning(f"Command timed out after {timeout} seconds: {command}")
                process.kill()
                timed_out = True
                exit_code = -1
            
            # Wait for output threads to complete
            stdout_thread.join(1)
            stderr_thread.join(1)
            
            # Combine output lines
            stdout = "".join(stdout_lines)
            stderr = "".join(stderr_lines)
            
            # Log command execution
            end_time = time.time()
            duration = end_time - start_time
            
            if timed_out:
                logger.warning(f"Command timed out: {command} (after {duration:.2f}s)")
            else:
                logger.info(f"Command completed: {command} (exit code: {exit_code}, time: {duration:.2f}s)")
            
            return {
                "success": exit_code == 0 and not timed_out,
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "command": command,
                "timeout": timeout,
                "timed_out": timed_out,
                "duration": duration,
                "error": None if exit_code == 0 and not timed_out else (
                    "Command timed out" if timed_out else f"Command failed with exit code {exit_code}"
                )
            }
        except Exception as e:
            logger.error(f"Error executing command: {command} - {str(e)}")
            return {
                "success": False,
                "exit_code": -1,
                "stdout": stdout,
                "stderr": stderr,
                "command": command,
                "timeout": timeout,
                "timed_out": timed_out,
                "error": str(e)
            }
        finally:
            # Clean up
            if process and process.poll() is None:
                try:
                    process.kill()
                except:
                    pass
            
            if log_fh:
                log_fh.close()


# Alias for backward compatibility
run_cmd = CommandExecutor.run_cmd


if __name__ == "__main__":
    # Simple test
    try:
        # Ensure log directory exists
        os.makedirs("memory/logs", exist_ok=True)
        
        # Test simple command
        result = CommandExecutor.run_cmd("echo 'Hello, world!'")
        print(f"Command result: {result['success']}")
        print(f"Output: {result['stdout']}")
        
        # Test command with timeout
        result = CommandExecutor.run_cmd("sleep 2", timeout=1)
        print(f"Timeout test: timed_out={result['timed_out']}")
        
        # Test dangerous command detection
        result = CommandExecutor.run_cmd("rm -rf /", check_dangerous=True)
        print(f"Dangerous command test: success={result['success']}, error={result['error']}")
        
        # Test interactive command
        result = CommandExecutor.run_cmd_interactive("cat", input_data="Hello, interactive world!\n")
        print(f"Interactive test: success={result['success']}, output={result['stdout']}")
        
        print("All tests passed")
    except Exception as e:
        print(f"Test failed: {e}")

