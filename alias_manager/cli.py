"""
Command-line interface for Python Alias Manager.
Handles argument parsing and command routing.
"""

import argparse
from .core import PythonAliasManager


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Python Script Alias Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python_alias_manager.py add myapp ~/scripts/my_application.py
  python_alias_manager.py add myapp ~/scripts/my_application.py --conda-env myenv
  python_alias_manager.py list
  python_alias_manager.py remove myapp
  python_alias_manager.py run myapp --help
  python_alias_manager.py venv myapp
  python_alias_manager.py deps myapp
  python_alias_manager.py deps myapp --install
  python_alias_manager.py deps myapp --setup
  python_alias_manager.py setup-deps myapp    # Auto-setup venv/conda + deps
  python_alias_manager.py setup
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add alias command with conda environment option
    add_parser = subparsers.add_parser('add', help='Add a new alias')
    add_parser.add_argument('alias_name', help='Name for the alias')
    add_parser.add_argument('script_path', help='Path to the Python script')
    add_parser.add_argument('--conda-env', help='Specify conda environment name to use')
    
    # Remove alias command
    remove_parser = subparsers.add_parser('remove', help='Remove an alias')
    remove_parser.add_argument('alias_name', help='Name of the alias to remove')
    
    # List aliases command
    subparsers.add_parser('list', help='List all aliases')
    
    # Update alias command
    update_parser = subparsers.add_parser('update', help='Update an existing alias')
    update_parser.add_argument('alias_name', help='Name of the alias to update')
    update_parser.add_argument('script_path', help='New path to the Python script')
    update_parser.add_argument('--conda-env', help='Specify conda environment name to use')
    
    # Run script command
    run_parser = subparsers.add_parser('run', help='Run a script by alias')
    run_parser.add_argument('alias_name', help='Name of the alias to run')
    run_parser.add_argument('args', nargs='*', help='Arguments to pass to the script')
    
    # Setup command
    subparsers.add_parser('setup', help='Check and show PATH setup instructions')
    
    # Virtual environment info command
    venv_parser = subparsers.add_parser('venv', help='Check virtual environment info for an alias')
    venv_parser.add_argument('alias_name', help='Name of the alias to check')
    
    # Dependencies command
    deps_parser = subparsers.add_parser('deps', help='Check and manage dependencies for an alias')
    deps_parser.add_argument('alias_name', help='Name of the alias to check dependencies for')
    deps_parser.add_argument('--install', action='store_true', help='Install missing dependencies automatically')
    deps_parser.add_argument('--setup', action='store_true', help='Create virtual environment and install dependencies if needed')
    
    # Auto-setup command
    setup_deps_parser = subparsers.add_parser('setup-deps', help='Auto-create virtual environment or Anaconda environment and install dependencies for an alias')
    setup_deps_parser.add_argument('alias_name', help='Name of the alias to setup dependencies for')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = PythonAliasManager()
    
    if args.command == 'add':
        manager.add_alias(args.alias_name, args.script_path, args.conda_env)
        manager.check_path_setup()
    elif args.command == 'remove':
        manager.remove_alias(args.alias_name)
    elif args.command == 'list':
        manager.list_aliases()
    elif args.command == 'update':
        conda_env = getattr(args, 'conda_env', None)
        manager.update_alias(args.alias_name, args.script_path, conda_env)
    elif args.command == 'run':
        manager.run_script(args.alias_name, args.args)
    elif args.command == 'setup':
        manager.check_path_setup()
    elif args.command == 'venv':
        manager.check_venv_info(args.alias_name)
    elif args.command == 'deps':
        install_flag = args.install or args.setup
        manager.check_dependencies(args.alias_name, install_flag)
    elif args.command == 'setup-deps':
        manager.auto_setup_dependencies(args.alias_name, True)


if __name__ == "__main__":
    main()
