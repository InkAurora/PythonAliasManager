"""
Dependency management for Python Alias Manager.
Handles parsing requirements files, checking installed packages, and installing dependencies.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Set, Optional, Union


class DependencyManager:
    """Manages dependencies for Python script aliases."""
    
    def parse_requirements_txt(self, requirements_file: str) -> List[str]:
        """Parse requirements.txt file and return list of package names."""
        packages = []
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Handle different requirement formats
                    # package==1.2.3, package>=1.0, package~=1.0, etc.
                    # Extract just the package name
                    match = re.match(r'^([a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]|[a-zA-Z0-9])', line)
                    if match:
                        package_name = match.group(1)
                        packages.append(package_name)
        except Exception as e:
            print(f"Error reading requirements file: {e}")
        
        return packages

    def parse_pyproject_toml(self, pyproject_file: str) -> List[str]:
        """Parse pyproject.toml file and return list of package names."""
        packages = []
        try:
            # Basic TOML parsing for dependencies section
            with open(pyproject_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for [tool.poetry.dependencies] or [project] dependencies
            in_dependencies = False
            in_project_dependencies = False
            
            for line in content.split('\n'):
                line = line.strip()
                
                # Check for poetry dependencies section
                if line == '[tool.poetry.dependencies]':
                    in_dependencies = True
                    continue
                elif line.startswith('[') and in_dependencies:
                    in_dependencies = False
                    continue
                
                # Check for PEP 621 project dependencies
                if 'dependencies = [' in line:
                    in_project_dependencies = True
                    # Handle single-line dependencies
                    deps_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', line)
                    if deps_match:
                        deps_str = deps_match.group(1)
                        for dep in re.findall(r'"([^"]+)"', deps_str):
                            match = re.match(r'^([a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]|[a-zA-Z0-9])', dep)
                            if match:
                                packages.append(match.group(1))
                        in_project_dependencies = False
                    continue
                elif line == ']' and in_project_dependencies:
                    in_project_dependencies = False
                    continue
                
                # Parse individual dependency lines
                if in_dependencies and '=' in line and not line.startswith('#'):
                    # Poetry format: package = "^1.0.0" or package = {version = "^1.0.0"}
                    match = re.match(r'^([a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]|[a-zA-Z0-9])\s*=', line)
                    if match and match.group(1) != 'python':  # Skip python version requirement
                        packages.append(match.group(1))
                elif in_project_dependencies and '"' in line:
                    # PEP 621 format: "package>=1.0.0",
                    dep_match = re.search(r'"([^"]+)"', line)
                    if dep_match:
                        dep = dep_match.group(1)
                        match = re.match(r'^([a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]|[a-zA-Z0-9])', dep)
                        if match:
                            packages.append(match.group(1))
                            
        except Exception as e:
            print(f"Error reading pyproject.toml file: {e}")
        
        return packages

    def parse_conda_env_dependencies(self, conda_env_file: str) -> List[str]:
        """Parse dependencies from a conda environment.yml file."""
        packages = []
        try:
            with open(conda_env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            in_dependencies = False
            in_pip_section = False
            
            for line in content.split('\n'):
                line = line.strip()
                
                # Check for dependencies section
                if line.startswith('dependencies:'):
                    in_dependencies = True
                    continue
                elif line and not line.startswith(' ') and not line.startswith('-') and in_dependencies:
                    in_dependencies = False
                    in_pip_section = False
                
                if in_dependencies and line.startswith('- '):
                    dep = line[2:].strip()
                    if dep == 'pip:':
                        in_pip_section = True
                        continue
                    elif not in_pip_section:
                        # Regular conda package
                        match = re.match(r'^([a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]|[a-zA-Z0-9])', dep)
                        if match and match.group(1) != 'python':
                            packages.append(match.group(1))
                elif in_dependencies and in_pip_section and line.startswith('  - '):
                    # pip package under dependencies
                    dep = line[4:].strip()
                    match = re.match(r'^([a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]|[a-zA-Z0-9])', dep)
                    if match:
                        packages.append(match.group(1))
                        
        except Exception as e:
            print(f"Error parsing conda environment file: {e}")
        
        return packages

    def get_installed_packages(self, python_executable: str) -> Set[str]:
        """Get list of installed packages in the given Python environment."""
        packages = set()
        try:
            result = subprocess.run([python_executable, "-m", "pip", "list", "--format=freeze"], 
                                 capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if '==' in line:
                        package_name = line.split('==')[0].lower()
                        packages.add(package_name)
        except Exception as e:
            print(f"Error getting installed packages: {e}")
        
        return packages

    def install_missing_dependencies(self, python_exe: str, missing_packages: List[str]) -> bool:
        """Install missing dependencies using pip."""
        if not missing_packages:
            return True
        
        try:
            cmd = [python_exe, "-m", "pip", "install"] + missing_packages
            print(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=False, text=True)
            
            if result.returncode == 0:
                print(f"✅ Successfully installed {len(missing_packages)} packages!")
                return True
            else:
                print(f"❌ Installation failed with return code {result.returncode}")
                return False
                
        except Exception as e:
            print(f"❌ Error during installation: {e}")
            return False

    def install_conda_dependencies(self, conda_env_name: str, missing_packages: List[str]) -> bool:
        """Install missing dependencies in a conda environment."""
        if not missing_packages:
            return True
        
        try:
            cmd = ['conda', 'install', '-n', conda_env_name, '-y'] + missing_packages
            print(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=False, text=True)
            
            if result.returncode == 0:
                print(f"✅ Successfully installed {len(missing_packages)} packages in conda environment!")
                return True
            else:
                print(f"❌ Conda installation failed with return code {result.returncode}")
                print("   Trying with conda-forge channel...")
                
                # Try with conda-forge channel
                cmd = ['conda', 'install', '-n', conda_env_name, '-c', 'conda-forge', '-y'] + missing_packages
                print(f"Running: {' '.join(cmd)}")
                
                result = subprocess.run(cmd, capture_output=False, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Successfully installed {len(missing_packages)} packages via conda-forge!")
                    return True
                else:
                    print(f"❌ Conda installation failed even with conda-forge channel")
                    return False
                
        except Exception as e:
            print(f"❌ Error during conda installation: {e}")
            return False

    def get_requirements_files(self, script_dir: Path) -> List[Path]:
        """Get list of potential requirements files in order of priority."""
        return [
            script_dir / 'environment.yml',
            script_dir / 'environment.yaml',
            script_dir / 'conda.yml',
            script_dir / 'conda.yaml',
            script_dir / 'requirements.txt',
            script_dir / 'pyproject.toml',
            script_dir / 'setup.py',
            script_dir / 'poetry.lock'
        ]

    def find_requirements_file(self, script_dir: Path) -> Optional[str]:
        """Find the first existing requirements file in the script directory."""
        for req_file in self.get_requirements_files(script_dir):
            if req_file.exists():
                return str(req_file)
        return None

    def parse_requirements_file(self, requirements_file: str) -> List[str]:
        """Parse a requirements file based on its type and return package names."""
        req_path = Path(requirements_file)
        
        if req_path.name == 'requirements.txt':
            return self.parse_requirements_txt(requirements_file)
        elif req_path.name == 'pyproject.toml':
            return self.parse_pyproject_toml(requirements_file)
        elif req_path.name in ['environment.yml', 'environment.yaml', 'conda.yml', 'conda.yaml']:
            return self.parse_conda_env_dependencies(requirements_file)
        else:
            print(f"⚠️  Requirements file format not supported for dependency checking: {req_path.name}")
            print("   Supported formats: requirements.txt, pyproject.toml, environment.yml")
            return []
