# Changelog

## [1.0.1] - 2025-07-12

### Fixed

- **Critical Fix**: Interactive input now works correctly for scripts using conda environments
  - Added `--no-capture-output` flag to `conda run` commands in generated batch files and shell scripts
  - Fixes `EOFError: EOF when reading a line` when scripts use `input()` function
  - Ensures proper stdin/stdout/stderr forwarding for interactive applications
  - Affects both Windows batch files and Linux/macOS shell scripts

### Changed

- Updated script generation to preserve interactive capabilities for conda-based aliases
- Improved documentation with troubleshooting guide for interactive input issues

## [1.0.0] - 2025-07-12

### Added

- Initial release of Python Alias Manager
- Cross-platform support for Windows, Linux, and macOS
- Automatic virtual environment detection (venv and conda)
- Interactive setup and dependency management
- Comprehensive CLI interface
- PATH configuration assistance
