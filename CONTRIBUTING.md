# Contributing to NRGkick Home Assistant Integration

Thank you for your interest in contributing to the NRGkick Home Assistant integration! This document provides guidelines and information for contributors.

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to create a welcoming environment for all contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

1. **Clear title** describing the problem
2. **Steps to reproduce** the issue
3. **Expected behavior** vs actual behavior
4. **Environment details**:
   - Home Assistant version
   - NRGkick firmware version
   - Integration version
5. **Logs** (if applicable)

### Suggesting Features

We welcome feature suggestions! Please create an issue with:

1. **Clear description** of the feature
2. **Use case** - why is this feature needed?
3. **Proposed implementation** (if you have ideas)

### Pull Requests

1. **Fork** the repository
2. **Create a branch** for your feature (`feature/amazing-feature`) or fix (`fix/bug-description`)
3. **Make your changes** following the code style guidelines
4. **Test thoroughly** - ensure existing functionality isn't broken
5. **Update documentation** if needed
6. **Commit** with clear, descriptive messages
7. **Open a pull request** with:
   - Clear description of changes
   - Link to related issues
   - Screenshots (if UI changes)

## Development Setup

### Prerequisites

- Python 3.13 or newer (recommended)
- Home Assistant development environment
- Access to a NRGkick Gen2 device for testing

**Note:** Python 3.13+ is required for the latest test dependencies. Python 3.11+ will work for the integration itself.

### Setting Up Development Environment

1. Clone the repository:

   ```bash
   git clone https://github.com/andijakl/nrgkick-homeassistant.git
   cd nrgkick-homeassistant
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements_dev.txt
   ```

4. Install pre-commit hooks:

   ```bash
   pip install pre-commit
   pre-commit install
   ```

   This will automatically run code quality checks before each commit.

5. Link to your Home Assistant instance:
   ```bash
   ln -s $(pwd)/custom_components/nrgkick /path/to/homeassistant/config/custom_components/
   ```

### Development Scripts

The repository includes three helper scripts to streamline development and releases.

#### Quick Reference

| Script              | Purpose           | When to Use                          |
| ------------------- | ----------------- | ------------------------------------ |
| `run-tests.sh`      | Test runner       | During development for quick testing |
| `validate.sh`       | Full validation   | Before committing/pushing changes    |
| `create-release.sh` | Release packaging | Creating releases (maintainers only) |

#### 1. `run-tests.sh` - Test Runner

**Purpose**: Quick, flexible testing during active development

**Usage**:

```bash
./run-tests.sh [option]
```

**Options**:

- `ci` - Run CI-compatible tests (recommended, no integration tests)
- `all` - Run all tests including integration tests
- `coverage` - Run tests with HTML coverage report
- `api` - Run only API tests
- `integration` - Run only integration tests
- `help` - Show help

**When to use**:

- ✅ Quick testing while coding
- ✅ Testing specific functionality
- ✅ Generating coverage reports
- ❌ NOT for final validation before push (use `validate.sh` instead)

**Examples**:

```bash
# Quick test during development
./run-tests.sh ci

# Test with coverage
./run-tests.sh coverage

# Test only API functionality
./run-tests.sh api
```

#### 2. `validate.sh` - Full Validation

**Purpose**: Complete code quality validation and testing

**Usage**:

```bash
./validate.sh
```

**What it does**:

1. Sets up virtual environment (if needed)
2. Installs all dependencies
3. Installs pre-commit hooks
4. Runs pre-commit checks (Ruff, MyPy, Pylint, Prettier)
5. Runs complete test suite with coverage
6. Runs strict type checking with mypy
7. Reports all issues

**When to use**:

- ✅ Before committing changes
- ✅ Before creating a pull request
- ✅ Before pushing to GitHub
- ✅ When setting up development environment
- ❌ NOT during active coding (too slow, use `run-tests.sh ci` instead)

**Use this before submitting a PR** to ensure your changes pass all quality checks.

#### 3. `create-release.sh` - Release Package (Maintainers Only)

**Purpose**: Create release ZIP packages for distribution

**Usage**:

```bash
# Specify new version (recommended - updates manifest.json automatically)
./create-release.sh 1.2.3

# Or use current version from manifest.json
./create-release.sh
```

**What it does**:

1. **If version provided**: Prompts to update `manifest.json` to the new version
2. **If no version**: Uses existing version from `manifest.json`
3. Optionally updates pre-commit hooks to latest versions (recommended)
4. Optionally runs `validate.sh` first (recommended)
5. Creates ZIP package in `releases/` directory
6. Shows next steps for GitHub release

**When to use**:

- ✅ When creating an official release (maintainers only)
- ✅ When testing release packages locally
- ❌ NOT during regular development

#### Windows Users

You can run these scripts using **Git Bash** (included with Git for Windows) or **WSL** (Windows Subsystem for Linux).

Alternatively, use the commands directly:

- For testing: `pytest tests/ -v`
- For pre-commit: `pre-commit run --all-files`
- Manual release creation is possible by following the steps in the scripts

#### Troubleshooting Scripts

**"Command not found"** - Make scripts executable:

```bash
chmod +x run-tests.sh validate.sh create-release.sh
```

**"Virtual environment not activated"** - Scripts handle this automatically, but you can manually activate:

```bash
source venv/bin/activate
```

**Pre-commit makes changes** - This is normal! Pre-commit auto-formats your code. Just stage and commit again:

```bash
git add .
git commit -m "Your message"
```

---

### Code Quality Checks

We use pre-commit hooks to maintain code quality. These run automatically before each commit (after running `validate.sh` once):

**What the hooks check:**

- **Ruff**: Code linting and formatting (replaces Black, isort, Flake8)
- **MyPy**: Strict type checking (PEP-561 compliant with `py.typed`)
- **Pylint**: Additional code quality checks
- **YAML/JSON**: File syntax validation
- **Prettier**: JSON/YAML/Markdown formatting

**Manual pre-commit usage:**

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run on specific files only
pre-commit run --files custom_components/nrgkick/api.py
```

**Note**: Pre-commit hooks will automatically format your code. If they make changes, you'll need to stage the changes and commit again.

### Testing During Development

For quick testing during development without full validation:

```bash
# Quick test run
./run-tests.sh ci

# Test specific functionality
pytest tests/test_api.py -v

# Run with detailed output
pytest tests/ -vv
```

## Code Style Guidelines

### Python Code

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints
- Maximum line length: 88 characters (Black default)
- Use meaningful variable names
- Add docstrings to all functions and classes

Example:

```python
async def get_charging_status(self) -> dict[str, Any]:
    """
    Get the current charging status from the device.

    Returns:
        dict: Charging status information including current, voltage, and power.

    Raises:
        ConnectionError: If device is unreachable.
    """
    return await self._request("/values")
```

### File Organization

- `__init__.py` - Integration setup and coordinator
- `api.py` - API client implementation
- `const.py` - Constants and configuration
- `config_flow.py` - Configuration flow
- `sensor.py` - Sensor entities
- `binary_sensor.py` - Binary sensor entities
- `switch.py` - Switch entities
- `number.py` - Number entities

### Entity Naming

Follow Home Assistant conventions:

- Sensor: `sensor.nrgkick_{name}`
- Binary Sensor: `binary_sensor.nrgkick_{name}`
- Switch: `switch.nrgkick_{name}`
- Number: `number.nrgkick_{name}`

### Documentation

- Update README.md for user-facing changes
- Update INSTALLATION.md for setup changes
- Add inline comments for complex logic
- Update translations if adding new config strings

## API Guidelines

When adding new API functionality:

1. **Check API documentation** - Refer to NRGkick API docs
2. **Add to api.py** - Create methods in the NRGkickAPI class
3. **Handle errors** - Use try/except and raise appropriate exceptions
4. **Use async/await** - All API calls should be asynchronous
5. **Add timeout** - Use async_timeout for all requests

Example:

```python
async def set_charging_current(self, current: float) -> dict[str, Any]:
    """Set the charging current."""
    if not 6.0 <= current <= self._max_current:
        raise ValueError(f"Current must be between 6.0A and {self._max_current}A")

    return await self._request("/control", {"current": current})
```

## Entity Guidelines

### Adding New Sensors

1. Define in `sensor.py`
2. Add appropriate device class and state class
3. Set correct unit of measurement
4. Include in entity list
5. Update README.md with new sensor

### Adding New Controls

1. Choose appropriate platform (switch/number/select)
2. Implement set methods
3. Call coordinator refresh after changes
4. Add to README.md examples

## Development Workflow

### Daily Development Workflow

**Making changes:**

```bash
# Make changes
vim custom_components/nrgkick/sensor.py

# Quick test while coding
./run-tests.sh ci

# Continue making changes...

# Validate before commit
./validate.sh

# Commit and push
git add .
git commit -m "Add new sensors"
git push
```

### Pull Request Workflow

```bash
# Ensure all validation passes
./validate.sh

# Check no uncommitted changes from pre-commit
git status

# Push and create PR on GitHub
git push
```

### Common Tasks Quick Reference

| Task                             | Command                       |
| -------------------------------- | ----------------------------- |
| Quick testing during development | `./run-tests.sh ci`           |
| Full validation before push      | `./validate.sh`               |
| Create release package           | `./create-release.sh`         |
| Run specific test                | `pytest tests/test_api.py -v` |
| Manual pre-commit check          | `pre-commit run --all-files`  |
| Test with coverage               | `./run-tests.sh coverage`     |

## Testing Checklist

Before submitting a PR, verify:

- [ ] `./validate.sh` passes without errors
- [ ] Code follows style guidelines (enforced by pre-commit)
- [ ] All functions have docstrings
- [ ] Type hints are used
- [ ] Changes are tested with real device (if applicable)
- [ ] Existing functionality still works
- [ ] No new warnings in logs
- [ ] Documentation is updated
- [ ] Translation files are updated (if needed)
- [ ] Commit messages are clear and descriptive

## Release Process (Maintainers Only)

For maintainers creating a new release:

### Method 1: Automatic Version Update (Recommended)

Complete workflow in one command:

```bash
# 1. Create release package with new version
./create-release.sh 1.2.3
# → Prompts to update manifest.json
# → Answer 'y' to update version
# → Answer 'y' to run validation

# 2. Test the ZIP file
# Install releases/nrgkick-v1.2.3.zip in Home Assistant

# 3. If all works, commit and tag
git add .
git commit -m "Release v1.2.3"
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin main --tags

# 4. Create GitHub release
# - Go to: https://github.com/andijakl/nrgkick-homeassistant/releases/new
# - Select tag: v1.2.3
# - Upload: releases/nrgkick-v1.2.3.zip
# - Add release notes
# - Publish release

# 5. HACS automatically detects the new release
```

### Method 2: Manual Version Update

If you prefer to update the version manually:

```bash
# 1. Manually update version in manifest.json
vim custom_components/nrgkick/manifest.json

# 2. Validate first
./validate.sh

# 3. Create release package (uses version from manifest)
./create-release.sh
# Answer 'n' to validation (already validated)

# 4. Continue with steps 2-5 from Method 1 above
```

### What the Release Script Does

When you run `./create-release.sh [version]`:

**If version provided:**

1. Compares with current manifest.json version
2. Prompts to update manifest.json (with confirmation)
3. Updates the file if confirmed
4. Optionally runs validation with the new version
5. Creates ZIP package in `releases/` directory

**If no version provided:**

1. Uses existing version from manifest.json
2. Optionally runs validation
3. Creates ZIP package in `releases/` directory

**Always:**

- Ensures manifest.json and ZIP version match
- Shows step-by-step instructions for publishing
- Creates properly named ZIP file

### Pre-Release Checklist

Before creating a release:

- [ ] All PRs merged and tested
- [ ] Update CHANGELOG or release notes
- [ ] Version number follows semantic versioning (X.Y.Z)
- [ ] All tests pass (`./validate.sh`)
- [ ] Integration works in test Home Assistant instance

### Important Notes

- ⚠️ **Version must be updated before validation** - The release script handles this automatically
- ✅ **Validation checks the final version** - Always let the script run validation
- 🎯 **Manifest and ZIP always match** - Script ensures consistency
- 📦 **Test the ZIP** - Always install and test the release package before publishing
- 🔖 **Tag format** - Always use `vX.Y.Z` format (e.g., `v1.2.3`)

## Questions?

If you have questions about contributing:

1. Check existing issues and discussions
2. Create a new discussion on GitHub
3. Ask in the pull request

## Recognition

Contributors will be acknowledged in:

- Release notes
- README.md contributors section
- Git commit history

Thank you for helping make this integration better!
