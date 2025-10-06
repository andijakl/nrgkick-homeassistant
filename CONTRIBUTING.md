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

- Python 3.11 or newer
- Home Assistant development environment
- Access to a NRGkick Gen2 device for testing

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

### Code Quality Checks

We use pre-commit hooks to maintain code quality. The hooks will run automatically before each commit, but you can also run them manually:

```bash
# Run all pre-commit hooks on all files
pre-commit run --all-files

# Run on specific files only
pre-commit run --files custom_components/nrgkick/api.py
```

**What the hooks check:**
- **Black**: Code formatting (88 character line length)
- **isort**: Import statement organization
- **Flake8**: Code linting and style issues
- **MyPy**: Type checking
- **Pylint**: Additional code quality checks
- **YAML/JSON**: File syntax validation

### Testing

Run tests before submitting:

```bash
# Run all tests with coverage
pytest tests/ -v --cov=custom_components.nrgkick --cov-report=term

# Run specific test file
pytest tests/test_api.py -v

# Run with detailed output
pytest tests/ -vv

# Run pre-commit checks manually
pre-commit run --all-files
```

**Note**: Pre-commit hooks will automatically format your code. If they make changes, you'll need to stage the changes and commit again.

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

## Testing Checklist

Before submitting a PR, verify:

- [ ] Code follows style guidelines
- [ ] All functions have docstrings
- [ ] Type hints are used
- [ ] Changes are tested with real device
- [ ] Existing functionality still works
- [ ] No new warnings in logs
- [ ] Documentation is updated
- [ ] Translation files are updated (if needed)
- [ ] Commit messages are clear

## Release Process

Maintainers will:

1. Review and merge PR
2. Update version in `manifest.json`
3. Create GitHub release with changelog
4. Update HACS repository

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
