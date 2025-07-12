"""
Utility functions for cross-platform compatibility.
"""

import sys


def safe_print(*args, **kwargs):
    """Print with safe Unicode handling for Windows."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Replace Unicode characters with ASCII equivalents on Windows
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                # Replace common Unicode symbols with ASCII equivalents
                replacements = {
                    '✓': '[OK]',
                    '⚠': '[!]', 
                    '❌': '[X]',
                    '🎉': '[!]',
                    '🐍': '[Python]'
                }
                for unicode_char, ascii_char in replacements.items():
                    arg = arg.replace(unicode_char, ascii_char)
            safe_args.append(arg)
        print(*safe_args, **kwargs)


def safe_unicode(text):
    """Convert Unicode text to safe ASCII on Windows."""
    if isinstance(text, str):
        replacements = {
            '✓': '[OK]',
            '⚠': '[!]', 
            '❌': '[X]',
            '🎉': '[!]',
            '🐍': '[Python]'
        }
        for unicode_char, ascii_char in replacements.items():
            text = text.replace(unicode_char, ascii_char)
    return text
