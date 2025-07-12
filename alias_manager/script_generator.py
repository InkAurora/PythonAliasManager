"""
Script generation for Python Alias Manager.
Handles creation of batch files and shell scripts for cross-platform alias execution.
"""

import sys
from pathlib import Path
from typing import Dict, Optional

from .venv_detector import VenvDetector


class ScriptGenerator:
    """Generates batch files and shell scripts for Python script aliases."""
    
    def __init__(self, batch_dir: Path):
        self.batch_dir = batch_dir
        self.venv_detector = VenvDetector()
    
    def create_batch_file(self, alias_name: str, script_path: str, venv_info_override: Dict[str, str] = None):
        """Create a batch file for the alias (Windows)."""
        batch_file = self.batch_dir / f"{alias_name}.bat"
        
        # Use override if provided, otherwise detect virtual environment
        venv_info = venv_info_override or self.venv_detector.detect_venv(script_path)
        
        if venv_info and venv_info.get('type') == 'venv':
            # Use virtual environment with activation-based approach
            venv_path = venv_info.get('path')
            if venv_path:
                # Create batch file that activates venv and uses the activated Python
                batch_content = f'''@echo off
if exist "{venv_path}\\Scripts\\activate.bat" (
    call "{venv_path}\\Scripts\\activate.bat" >nul 2>&1
    python "{script_path}" %*
) else (
    echo Error: Virtual environment activation script not found at {venv_path}\\Scripts\\activate.bat
    echo Falling back to system Python...
    python "{script_path}" %*
)
'''
            else:
                # Fallback to system Python
                batch_content = f'''@echo off
python "{script_path}" %*
'''
        elif venv_info and venv_info.get('type') == 'conda':
            # Use conda environment
            conda_env_name = venv_info.get('conda_env_name')
            if conda_env_name and self.venv_detector.check_conda_available():
                # Create batch file content with conda run (no initialization required)
                # Use --no-capture-output to ensure stdin/stdout/stderr are properly forwarded
                batch_content = f'''@echo off
conda run --no-capture-output -n {conda_env_name} python "{script_path}" %*
'''
            else:
                # Fallback to system Python if conda not available or no env name
                batch_content = f'''@echo off
python "{script_path}" %*
'''
        else:
            # Use system Python with dynamic detection
            batch_content = f'''@echo off
python "{script_path}" %*
'''
        
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        
        return batch_file

    def create_shell_script(self, alias_name: str, script_path: str, venv_info_override: Dict[str, str] = None):
        """Create a shell script for the alias (Linux/macOS/Bash)."""
        shell_file = self.batch_dir / alias_name
        
        # Use override if provided, otherwise detect virtual environment
        venv_info = venv_info_override or self.venv_detector.detect_venv(script_path)
        
        if venv_info and venv_info.get('type') == 'venv':
            # Use virtual environment Python
            venv_python = self.venv_detector.get_venv_python_executable(venv_info)
            activate_script = venv_info.get('activate_script', '')
            
            if venv_python and activate_script:
                # Create shell script content with venv activation
                shell_content = f'''#!/bin/bash
# Auto-detect Python executable and script path based on environment
if [[ "${{PWD}}" == /mnt/* ]] || command -v wslpath &> /dev/null; then
    # We're in WSL - use Linux Python and convert Windows paths
    if [[ "{script_path}" == [A-Za-z]:* ]]; then
        # Convert Windows path to WSL path
        SCRIPT_PATH=$(wslpath "{script_path}")
    else
        SCRIPT_PATH="{script_path}"
    fi
    
    # Try to find and activate the virtual environment
    if [[ "{activate_script}" == [A-Za-z]:* ]]; then
        ACTIVATE_SCRIPT=$(wslpath "{activate_script}")
    else
        ACTIVATE_SCRIPT="{activate_script}"
    fi
    
    # Source the activation script and run Python
    if [[ -f "$ACTIVATE_SCRIPT" ]]; then
        source "$ACTIVATE_SCRIPT"
        # Try python3 first, then python after activation
        if command -v python3 &> /dev/null; then
            python3 "$SCRIPT_PATH" "$@"
        elif command -v python &> /dev/null; then
            python "$SCRIPT_PATH" "$@"
        else
            echo "Error: No Python interpreter found after activating virtual environment"
            exit 1
        fi
    else
        # Fallback to system Python
        if command -v python3 &> /dev/null; then
            python3 "$SCRIPT_PATH" "$@"
        elif command -v python &> /dev/null; then
            python "$SCRIPT_PATH" "$@"
        else
            echo "Error: No Python interpreter found"
            exit 1
        fi
    fi
else
    # We're in regular Linux/macOS or Git Bash
    SCRIPT_PATH="{script_path}"
    
    # Activate virtual environment if available
    if [[ -f "{activate_script}" ]]; then
        source "{activate_script}"
        # Try python3 first, then python after activation
        if command -v python3 &> /dev/null; then
            python3 "$SCRIPT_PATH" "$@"
        elif command -v python &> /dev/null; then
            python "$SCRIPT_PATH" "$@"
        else
            echo "Error: No Python interpreter found after activating virtual environment"
            exit 1
        fi
    else
        # Fallback to system Python
        if command -v python3 &> /dev/null; then
            python3 "$SCRIPT_PATH" "$@"
        elif command -v python &> /dev/null; then
            python "$SCRIPT_PATH" "$@"
        else
            echo "Error: No Python interpreter found"
            exit 1
        fi
    fi
fi
'''
            else:
                # Fallback to system Python
                shell_content = self._create_system_python_shell_script(script_path)
        elif venv_info and venv_info.get('type') == 'conda':
            # Use conda environment
            conda_env_name = venv_info.get('conda_env_name')
            if conda_env_name and self.venv_detector.check_conda_available():
                # Create shell script content with conda activation
                shell_content = f'''#!/bin/bash
# Auto-detect script path based on environment
if [[ "${{PWD}}" == /mnt/* ]] || command -v wslpath &> /dev/null; then
    # We're in WSL - convert Windows paths
    if [[ "{script_path}" == [A-Za-z]:* ]]; then
        # Convert Windows path to WSL path
        SCRIPT_PATH=$(wslpath "{script_path}")
    else
        SCRIPT_PATH="{script_path}"
    fi
else
    # We're in regular Linux/macOS or Git Bash
    SCRIPT_PATH="{script_path}"
fi

# Check if conda is available
if command -v conda &> /dev/null; then
    # Use conda to run the script in the specified environment
    # Use --no-capture-output to ensure stdin/stdout/stderr are properly forwarded
    conda run --no-capture-output -n {conda_env_name} python "$SCRIPT_PATH" "$@"
else
    echo "Error: Conda is not available in PATH"
    echo "Please install Anaconda/Miniconda or ensure conda is in your PATH"
    exit 1
fi
'''
            else:
                # Fallback to system Python if conda not available or no env name
                shell_content = self._create_system_python_shell_script(script_path)
        else:
            # Create shell script content without venv
            shell_content = self._create_system_python_shell_script(script_path)
        
        with open(shell_file, 'w') as f:
            f.write(shell_content)
        
        # Make the shell script executable
        shell_file.chmod(0o755)
        
        return shell_file
    
    def _create_system_python_shell_script(self, script_path: str) -> str:
        """Create a shell script that uses system Python with cross-platform path handling."""
        return f'''#!/bin/bash
# Auto-detect Python executable and script path based on environment
if [[ "${{PWD}}" == /mnt/* ]] || command -v wslpath &> /dev/null; then
    # We're in WSL - use Linux Python and convert Windows paths
    PYTHON_CMD="python3"
    if [[ "{script_path}" == [A-Za-z]:* ]]; then
        # Convert Windows path to WSL path
        SCRIPT_PATH=$(wslpath "{script_path}")
    else
        SCRIPT_PATH="{script_path}"
    fi
else
    # We're in regular Linux/macOS or Git Bash - use system Python
    PYTHON_CMD="python3"
    SCRIPT_PATH="{script_path}"
fi

# Try python3 first, then python, then fall back to sys.executable path
if command -v python3 &> /dev/null; then
    "$PYTHON_CMD" "$SCRIPT_PATH" "$@"
elif command -v python &> /dev/null; then
    python "$SCRIPT_PATH" "$@"
else
    # Fallback to the original Python executable (may not work in WSL)
    "{sys.executable}" "{script_path}" "$@"
fi
'''
