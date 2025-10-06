# Home Assistant Bronze Tier Progress

This document tracks the progress toward achieving Bronze Tier certification for submission to the Home Assistant core repository.

## Completed Actions ✅

### Action 1: Reauthentication Flow
**Status**: ✅ COMPLETE

**Changes Made**:
1. **config_flow.py**:
   - Added `async_step_reauth()` method to handle reauthentication trigger
   - Added `async_step_reauth_confirm()` method with form to collect new credentials
   - Proper error handling for connection failures during reauth
   - Automatic entry update and reload on successful reauth

2. **__init__.py**:
   - Added `aiohttp` import for error handling
   - Added `ConfigEntryAuthFailed` import from Home Assistant
   - Modified `_async_update_data()` to catch 401 authentication errors
   - Raises `ConfigEntryAuthFailed` to trigger reauthentication flow automatically

3. **strings.json**:
   - Added `reauth_confirm` step with title, description, and data fields
   - Added `reauth_successful` abort message
   - Added `reauth_failed` abort message

4. **translations/en.json**:
   - Added complete English translations for reauthentication flow

5. **translations/de.json**:
   - Added complete German translations for reauthentication flow

**How It Works**:
- When the API returns a 401 Unauthorized error, the coordinator raises `ConfigEntryAuthFailed`
- Home Assistant automatically triggers the reauth flow
- User is prompted to enter new credentials
- On success, the integration updates and reloads automatically
- On failure, user can retry or remove and re-add the integration

---

### Action 2: CODEOWNERS File
**Status**: ✅ COMPLETE

**Changes Made**:
1. Created `.github/CODEOWNERS` file
2. Assigned `@andijakl` as the primary maintainer
3. All files in the repository are covered by the code owner

**Purpose**:
- Ensures proper review assignment for pull requests
- Required for Home Assistant core integration submission
- Demonstrates commitment to long-term maintenance

---

## Remaining Actions for Bronze Tier

### Action 3: Comprehensive Test Suite ❌
**Status**: NOT STARTED
**Priority**: HIGH

**Required Tests**:
- [ ] `tests/conftest.py` - pytest fixtures and Home Assistant test setup
- [ ] `tests/test_config_flow.py` - Test initial setup, validation, errors
- [ ] `tests/test_reauth.py` - Test reauthentication flow
- [ ] `tests/test_init.py` - Test integration setup and coordinator
- [ ] `tests/test_api.py` - Test API client methods
- [ ] `tests/test_sensor.py` - Test sensor entity creation and updates
- [ ] `tests/test_switch.py` - Test switch entity
- [ ] `tests/test_number.py` - Test number entity controls
- [ ] `tests/test_binary_sensor.py` - Test binary sensor entities

**Estimated Effort**: 8-12 hours

---

### Action 4: Pre-commit Configuration ❌
**Status**: NOT STARTED
**Priority**: HIGH

**Required Files**:
- [ ] `.pre-commit-config.yaml` - Configure hooks for black, isort, flake8, mypy
- [ ] `pyproject.toml` - Configuration for black, isort, mypy
- [ ] `.flake8` - Flake8 configuration
- [ ] Run `pre-commit install` and ensure all checks pass

**Required Tools**:
- black (code formatting)
- isort (import sorting)
- flake8 (linting)
- mypy (type checking)
- pylint (code quality)

**Estimated Effort**: 2-4 hours

---

### Action 5: CI/CD Pipeline ❌
**Status**: NOT STARTED (Optional but recommended)
**Priority**: MEDIUM

**Recommended Setup**:
- [ ] `.github/workflows/test.yml` - Run tests on PR and push
- [ ] `.github/workflows/lint.yml` - Run pre-commit checks
- [ ] `.github/workflows/hassfest.yml` - Run Home Assistant validation

**Estimated Effort**: 2-3 hours

---

### Action 6: Documentation ⏳
**Status**: PENDING (Post-Acceptance)
**Priority**: REQUIRED AFTER PR ACCEPTANCE

**Required**:
- [ ] Create documentation PR to `home-assistant/home-assistant.io`
- [ ] Page at `https://www.home-assistant.io/integrations/nrgkick/`
- [ ] Include installation, configuration, entities, services, examples

**Note**: This is typically done AFTER the integration is accepted into core.

---

## Bronze Tier Checklist Status

| Requirement | Status | Notes |
|-------------|--------|-------|
| ✅ Basic Functionality | PASS | Async, no blocking I/O, error handling |
| ⚠️ Configuration | PASS | Config flow + Options flow + Reauthentication |
| ⏳ Documentation | PENDING | Done after core acceptance |
| ✅ Translations | PASS | English and German complete |
| ❌ Testing | FAIL | No tests yet - needs comprehensive suite |
| ✅ Code Ownership | PASS | CODEOWNERS file created + manifest.json |
| ❌ Quality Standards | FAIL | Pre-commit not configured yet |

**Overall Readiness**: ~60% (4/7 requirements complete)

---

## Next Steps

1. **Immediate**: Set up pre-commit hooks and pass all checks
2. **High Priority**: Write comprehensive test suite (estimated 30+ tests)
3. **Before Submission**: Run tests in Home Assistant dev environment
4. **After Acceptance**: Create home-assistant.io documentation

---

## Testing Commands

Once tests are created:

```bash
# Install development dependencies
pip install -r requirements_dev.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=custom_components.nrgkick --cov-report=html

# Run pre-commit checks
pre-commit run --all-files
```

---

## Submission Process

Once all Bronze Tier requirements are met:

1. Create PR to `home-assistant/core` repository
2. Add integration to `homeassistant/components/nrgkick/`
3. Follow Home Assistant's PR template
4. Respond to reviewer feedback
5. After merge, create documentation PR to `home-assistant.io`

---

**Last Updated**: October 6, 2025
**Maintainer**: @andijakl
