# Bronze Tier Action Items

This document outlines the specific steps needed to prepare the NRGkick integration for Home Assistant Bronze Tier certification.

## Status: 🟡 NEAR COMPLIANT
**Current Compliance**: 6/8 categories fully compliant, 2 partially compliant

---

## Critical Actions (Required for Bronze Tier)

### 1. ✅ Pre-commit Configuration (COMPLETED)

**Status**: ✅ COMPLETED  
**Files Created**:
- `.pre-commit-config.yaml` - Pre-commit hooks configuration
- `.github/workflows/quality.yml` - CI/CD quality checks

**Next Steps**:
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually to test
pre-commit run --all-files

# Fix any issues reported
```

**What It Does**:
- Automatically formats code with Black
- Sorts imports with isort
- Checks for linting issues with Flake8
- Validates types with MyPy (on custom_components only)
- Runs Pylint for additional code quality checks
- Validates Home Assistant manifest

**Expected First-Time Issues**:
- Some formatting changes from Black
- Import order changes from isort
- Possible linting warnings from Flake8

---

### 2. ⚠️ Official Documentation (Required for Official HA Integration)

**Status**: ⚠️ PENDING (only if submitting to official HA)  
**Current**: Documentation in README.md (excellent for HACS)  
**Required For**: Official Home Assistant Core integration

#### If Submitting to Official Home Assistant:

**Step 1: Create Documentation PR**
1. Fork `home-assistant/home-assistant.io` repository
2. Create new documentation file: `source/_integrations/nrgkick.markdown`
3. Follow the template structure

**Template Structure**:
```markdown
---
title: NRGkick
description: Instructions on how to integrate NRGkick EV charger with Home Assistant.
ha_category:
  - Car
ha_release: 2024.XX
ha_iot_class: Local Polling
ha_config_flow: true
ha_codeowners:
  - '@andijakl'
ha_domain: nrgkick
ha_platforms:
  - binary_sensor
  - number
  - sensor
  - switch
---

The NRGkick integration allows you to integrate your NRGkick Gen2 EV charging controller with Home Assistant.

## Prerequisites

- NRGkick Gen2 device with firmware >= SmartModule 4.0.0.0
- JSON API enabled in NRGkick app

{% include integrations/config_flow.md %}

## Sensors

This integration provides the following sensors:
[... document key sensors ...]

## Binary Sensors

[... document binary sensors ...]

## Controls

[... document number and switch entities ...]

## Automation Examples

[... include 2-3 simple examples ...]
```

**Step 2: Update manifest.json**
```json
{
  "documentation": "https://www.home-assistant.io/integrations/nrgkick",
  ...
}
```

**Step 3: Submit PR**
- PR Title: "Add documentation for NRGkick integration"
- Link to integration code repository
- Wait for review from HA docs team

#### If Staying as HACS Custom Integration:
- Current README.md is excellent and sufficient
- No action needed for documentation

---

## Recommended Improvements

### 3. 🔧 Update async_timeout Usage

**Why**: `async_timeout` is deprecated in favor of native `asyncio.timeout()` (Python 3.11+)

**File to Update**: `custom_components/nrgkick/api.py`

**Current Code**:
```python
import async_timeout

async def _request(self, endpoint: str, params: dict[str, Any] | None = None):
    async with async_timeout.timeout(10):
        async with self._session.get(url, auth=auth, params=params) as response:
            ...
```

**Updated Code**:
```python
import asyncio

async def _request(self, endpoint: str, params: dict[str, Any] | None = None):
    async with asyncio.timeout(10):
        async with self._session.get(url, auth=auth, params=params) as response:
            ...
```

**Also Update**: `requirements_dev.txt` - Remove `async-timeout>=4.0.0` if not needed elsewhere

---

### 4. 📋 Add Issue Templates

**Why**: Better user support and bug reporting

**Create**: `.github/ISSUE_TEMPLATE/bug_report.yml`
```yaml
name: Bug Report
description: File a bug report
title: "[Bug]: "
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to fill out this bug report!
  
  - type: textarea
    id: what-happened
    attributes:
      label: What happened?
      description: A clear description of what the bug is
    validations:
      required: true
  
  - type: textarea
    id: expected
    attributes:
      label: Expected behavior
      description: What you expected to happen
    validations:
      required: true
  
  - type: input
    id: version
    attributes:
      label: Integration Version
      description: What version of the integration are you running?
      placeholder: "0.1.1"
    validations:
      required: true
  
  - type: input
    id: ha-version
    attributes:
      label: Home Assistant Version
      description: What version of Home Assistant are you running?
      placeholder: "2024.10.0"
    validations:
      required: true
  
  - type: textarea
    id: logs
    attributes:
      label: Relevant log output
      description: Please copy and paste any relevant log output
      render: shell
```

**Create**: `.github/ISSUE_TEMPLATE/feature_request.yml`
```yaml
name: Feature Request
description: Suggest an idea for this integration
title: "[Feature]: "
labels: ["enhancement"]
body:
  - type: textarea
    id: feature-description
    attributes:
      label: Feature Description
      description: A clear description of what you want to happen
    validations:
      required: true
  
  - type: textarea
    id: use-case
    attributes:
      label: Use Case
      description: Why would this feature be useful?
    validations:
      required: true
```

---

### 5. 📊 Enhance CI/CD Coverage Reporting

**Add to** `.github/workflows/test.yml`:

```yaml
      - name: Generate coverage badge
        if: github.ref == 'refs/heads/main'
        run: |
          coverage-badge -o coverage.svg -f
          
      - name: Commit coverage badge
        if: github.ref == 'refs/heads/main'
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add coverage.svg
          git diff --staged --quiet || git commit -m "Update coverage badge"
          git push
```

**Add to README.md**:
```markdown
[![Coverage](coverage.svg)](https://github.com/andijakl/nrgkick-homeassistant)
```

---

### 6. 🧪 Add Integration Quality Scale Badge

**Add to README.md** (after achieving Bronze):
```markdown
[![Integration Quality Scale](https://img.shields.io/badge/Integration%20Quality%20Scale-Bronze-CD7F32)](https://www.home-assistant.io/docs/quality_scale/)
```

---

## Testing Your Changes

### Test Pre-commit Locally

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Make a commit to test automatic hooks
git add .
git commit -m "Test pre-commit hooks"
```

### Test Integration After Code Quality Fixes

```bash
# Activate virtual environment
source venv/bin/activate

# Install development dependencies
pip install -r requirements_dev.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=custom_components.nrgkick --cov-report=term

# Test in Home Assistant
# 1. Copy custom_components/nrgkick to your HA config
# 2. Restart Home Assistant
# 3. Add integration via UI
# 4. Verify all entities work correctly
```

---

## Validation Checklist

Before submitting for Bronze Tier, verify:

- [ ] Pre-commit hooks installed and passing
- [ ] All tests passing (`pytest tests/`)
- [ ] GitHub Actions workflows all green
- [ ] Code formatted with Black
- [ ] Imports sorted with isort
- [ ] No Flake8 errors
- [ ] MyPy type checking clean (or documented exceptions)
- [ ] Integration loads successfully in Home Assistant
- [ ] All entities created correctly
- [ ] Config flow works (initial setup)
- [ ] Reauth flow works (test with wrong credentials)
- [ ] Options flow works (reconfiguration)
- [ ] Documentation complete (README or home-assistant.io)
- [ ] CODEOWNERS file present
- [ ] Manifest.json has codeowners field
- [ ] Translations complete (at least English)

---

## Timeline Estimate

| Task | Estimated Time | Priority |
|------|----------------|----------|
| Install and run pre-commit | 15 minutes | High |
| Fix formatting/linting issues | 30-60 minutes | High |
| Update async_timeout usage | 15 minutes | Medium |
| Add issue templates | 20 minutes | Low |
| Create official docs (if needed) | 2-3 hours | High* |
| Test everything | 30 minutes | High |

*Only required for official Home Assistant integration submission

**Total Time for Critical Items**: ~1-2 hours  
**Total Time for All Improvements**: ~4-5 hours

---

## Next Steps

1. **Run pre-commit**: `pre-commit run --all-files`
2. **Fix any issues**: Address formatting and linting errors
3. **Run tests**: Ensure all tests still pass
4. **Decide on documentation**: HACS (current README) or official HA (create PR)
5. **Optional improvements**: Issue templates, async_timeout update
6. **Final validation**: Use checklist above

---

## Support

If you encounter issues during Bronze Tier preparation:

1. **Pre-commit issues**: Check `.pre-commit-config.yaml` syntax
2. **Test failures**: Review test output for specific failures
3. **CI/CD issues**: Check GitHub Actions logs
4. **Integration issues**: Check Home Assistant logs

**Home Assistant Quality Scale Documentation**:
https://developers.home-assistant.io/docs/integration_quality_scale_index/

---

**Document Created**: October 6, 2025  
**Integration Version**: 0.1.1  
**Status**: Ready for Bronze Tier preparation
