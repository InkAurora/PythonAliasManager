# Changelog

## [1.0.3] - 2025-07-12

### Added

- **Force Recreate Virtual Environments**: New `--force` flag for `setup-deps` command
  - `pam setup-deps alias_name --force` removes existing virtual environment and recreates from scratch
  - Fixes broken virtual environments that reference non-existent Python installations
  - Automatically installs all dependencies from requirements files after recreation
  - Works with both conda environments and Python virtual environments

### Fixed

- **Dynamic Python Executable Resolution**: Fixed hardcoded Python paths in generated batch files
  - Batch files now use activation-based approach instead of hardcoded Python executable paths
  - Prevents "did not find executable at 'C:\Python313\python.exe'" errors when Python installations move
  - Improved robustness when virtual environments are created with different Python versions
  - Enhanced fallback mechanisms for broken virtual environment detection

### Changed

- Updated dependency installation to use `--no-cache-dir` flag to avoid permission issues
- Improved error handling and user feedback during environment recreation

## [1.0.2] - 2025-07-12

### Added

- **Environment Cleanup**: Enhanced `remove` command to also remove associated virtual environments
  - Interactive prompt to remove conda environments when removing an alias
  - Interactive prompt to remove venv directories when removing an alias
  - `--keep-env` flag to preserve virtual environments when removing aliases
  - `--remove-env` flag to automatically remove virtual environments without prompting
  - Supports both conda environments and Python virtual environments
  - Provides manual cleanup instructions when automated removal fails

### Changed

- Updated `remove` command behavior to detect and optionally clean up virtual environments
- Enhanced CLI help text with new virtual environment removal examples

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
