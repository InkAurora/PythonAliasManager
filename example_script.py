#!/usr/bin/env python3
"""
Example Python script to demonstrate the alias system.
This script shows various features that can be aliased.
"""

import argparse
import sys
from datetime import datetime

def greet(name, times=1, enthusiastic=False):
    """Greet someone."""
    greeting = "Hello" if not enthusiastic else "HELLO!!!"
    for i in range(times):
        print(f"{greeting} {name}!")

def calculate(operation, a, b):
    """Perform basic calculations."""
    operations = {
        'add': lambda x, y: x + y,
        'subtract': lambda x, y: x - y,
        'multiply': lambda x, y: x * y,
        'divide': lambda x, y: x / y if y != 0 else "Cannot divide by zero"
    }
    
    if operation not in operations:
        return f"Unknown operation: {operation}"
    
    return operations[operation](a, b)

def show_info():
    """Show system information."""
    print(f"Current time: {datetime.now()}")
    print(f"Python version: {sys.version}")
    print(f"Script path: {__file__}")

def main():
    parser = argparse.ArgumentParser(description="Example script for Python alias system")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Greet command
    greet_parser = subparsers.add_parser('greet', help='Greet someone')
    greet_parser.add_argument('name', help='Name to greet')
    greet_parser.add_argument('--times', type=int, default=1, help='Number of times to greet')
    greet_parser.add_argument('--enthusiastic', action='store_true', help='Be enthusiastic')
    
    # Calculate command
    calc_parser = subparsers.add_parser('calc', help='Perform calculations')
    calc_parser.add_argument('operation', choices=['add', 'subtract', 'multiply', 'divide'])
    calc_parser.add_argument('a', type=float, help='First number')
    calc_parser.add_argument('b', type=float, help='Second number')
    
    # Info command
    subparsers.add_parser('info', help='Show system information')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'greet':
        greet(args.name, args.times, args.enthusiastic)
    elif args.command == 'calc':
        result = calculate(args.operation, args.a, args.b)
        print(f"Result: {result}")
    elif args.command == 'info':
        show_info()

if __name__ == "__main__":
    main()
