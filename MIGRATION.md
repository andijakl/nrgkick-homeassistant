# Migration Guide: v1.x to v2.0.0

## Overview

Version 2.0.0 introduces breaking changes to entity IDs as part of achieving Home Assistant Bronze quality tier compliance. This is a **one-time migration** that affects all existing users.

## What Changed

### Entity ID Format

Entity IDs now follow the modern Home Assistant naming convention with `has_entity_name = True`, which means:

- The device name is automatically prefixed to entity names
- Entity IDs are regenerated based on the new naming scheme
- Friendly names remain similar but may have different formatting

**Before v1.x:**

```yaml
Entity ID: sensor.nrgkick_total_active_power
Name: "NRGkick Total Active Power"
```

**After v2.0.0:**

```yaml
Entity ID: sensor.nrgkick_total_active_power_2 # Note: suffix may vary
Name: "NRGkick Total Active Power"
```

### Why This Change

This change implements the Home Assistant Bronze quality tier requirements:

- ✅ `runtime_data` - Modern coordinator storage pattern
- ✅ `has_entity_name` - Automatic device-based entity naming

These improvements provide:

- Cleaner entity management
- Better device context handling
- Future-proof alignment with Home Assistant core standards
- Automatic memory cleanup

## Migration Steps

### 1. Before Upgrading

**Document your current entity IDs:**

1. Go to **Settings** → **Devices & Services** → **NRGkick**
2. Click on your device
3. Take a screenshot or note down all entity IDs you're currently using
4. Check your configuration files for entity references:
   - `automations.yaml`
   - `scripts.yaml`
   - `dashboards/lovelace files`
   - Any custom templates

### 2. Upgrade the Integration

**Method A: Clean Installation (Recommended)**

This method ensures you get clean entity IDs (e.g., `sensor.nrgkick_total_active_power`) without `_2` suffixes.

1. **Remove the existing integration**:
   - Go to **Settings** → **Devices & Services**.
   - Click the three dots (⋮) on the **NRGkick** integration entry.
   - Select **Delete**.
   - _Note: This removes the old entities but preserves your configuration in YAML files._
2. **Upgrade the files**:
   - **HACS**: Go to HACS, update NRGkick to v2.0.0.
   - **Manual**: Replace the `custom_components/nrgkick` folder with the new version.
3. **Restart Home Assistant**.
4. **Add the integration**:
   - Go to **Settings** → **Devices & Services** → **Add Integration**.
   - Search for **NRGkick** and follow the setup steps.

**Method B: In-Place Upgrade**

If you upgrade without removing the integration first, you may end up with duplicate entities or `_2` suffixes (e.g., `sensor.nrgkick_total_active_power_2`) because the old entities still occupy the IDs.

1. Upgrade via HACS or Manual replacement.
2. Restart Home Assistant.
3. If you see `_2` entities:
   - Go to **Settings** → **Devices & Services** → **Entities**.
   - Filter by `nrgkick`.
   - Delete the old "Unavailable" entities.
   - Rename the new `_2` entities to remove the suffix (click Entity → Settings → Entity ID).

### 3. Verify Entity IDs

After re-adding the integration (Method A) or fixing suffixes (Method B):

1. Go to **Settings** → **Devices & Services** → **NRGkick**.
2. Click on your device.
3. Verify the entity IDs match your expectations.

**Expected Pattern:**

- `sensor.nrgkick_total_active_power`
- `switch.nrgkick_charge_pause`
- `number.nrgkick_charging_current`

### 4. Update Your Configuration

#### Dashboards/Lovelace Cards

Edit your dashboard cards to use the new entity IDs:

**Before:**

```yaml
type: entities
entities:
  - sensor.nrgkick_total_active_power
  - switch.nrgkick_charge_pause
```

**After:**

```yaml
type: entities
entities:
  - sensor.nrgkick_total_active_power_2
  - switch.nrgkick_charge_pause_2
```

#### Automations

Update entity references in your automations:

**Before:**

```yaml
trigger:
  - platform: state
    entity_id: binary_sensor.nrgkick_charging
    to: "on"
action:
  - service: switch.turn_on
    target:
      entity_id: switch.nrgkick_charge_pause
```

**After:**

```yaml
trigger:
  - platform: state
    entity_id: binary_sensor.nrgkick_charging_2
    to: "on"
action:
  - service: switch.turn_on
    target:
      entity_id: switch.nrgkick_charge_pause_2
```

#### Scripts

Update entity references in scripts similarly to automations.

#### Templates

Update any templates that reference entity IDs:

**Before:**

```yaml
{ { states('sensor.nrgkick_total_active_power') } }
```

**After:**

```yaml
{ { states('sensor.nrgkick_total_active_power_2') } }
```

### 5. Test Your Configuration

After updating:

1. Check that all dashboards display correctly
2. Test automations to ensure they trigger properly
3. Verify scripts execute as expected
4. Check templates render correctly

### 6. Clean Up Old Entities (Optional)

Once everything is working with the new entity IDs:

1. Go to **Settings** → **Devices & Services** → **Entities**
2. Filter by "nrgkick" or "Unavailable"
3. Find orphaned entities (showing as unavailable with old IDs)
4. For each old entity:
   - Click the entity
   - Click the **Settings icon** (gear)
   - Click **Delete**

**Note:** Historical data from old entities will not automatically transfer. Consider keeping old entities if you need access to historical data, or export statistics before deletion if needed.

## Tips for Easier Migration

### Use Global Find & Replace

If you maintain YAML configuration files:

1. Open your configuration directory in a text editor (VS Code, Sublime, etc.)
2. Use "Find & Replace" across all files
3. Search for old entity IDs and replace with new ones
4. Be careful with pattern matching to avoid unintended replacements

### Check Developer Tools

Use **Developer Tools** → **States** to:

- View all entity IDs and their current states
- Verify old entities are unavailable
- Confirm new entities are working

### Update Entity Labels (Optional)

If you use entity labels for organization, remember to add them to the new entities.

## Rollback (If Needed)

If you encounter issues and need to rollback:

1. Downgrade to v1.x via HACS or manual installation
2. Restart Home Assistant
3. Your original entity IDs will be restored
4. No data loss occurs during rollback

## Need Help?

- **Issues**: [GitHub Issues](https://github.com/andijakl/nrgkick-homeassistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/andijakl/nrgkick-homeassistant/discussions)

## Technical Details

For developers interested in the technical changes:

### Internal Changes

1. **runtime_data Pattern**: Coordinator now stored in `ConfigEntry.runtime_data` instead of `hass.data[DOMAIN]`
2. **has_entity_name**: Base `NRGkickEntity` class now sets `_attr_has_entity_name = True`
3. **Entity Naming**: Entity names no longer include "NRGkick" prefix (handled by device context)
4. **Translation Keys**: Simplified to use entity key without prefix

### Unique IDs

Entity unique IDs remain unchanged: `{serial_number}_{entity_key}`

This ensures Home Assistant recognizes entities as the same logical entities, but the entity ID generation algorithm differs when `has_entity_name = True`, causing new IDs to be created.

### Benefits

- **Cleaner Code**: Modern Home Assistant patterns
- **Better Memory Management**: Automatic cleanup on integration unload
- **Improved Type Safety**: Better type hints with runtime_data
- **Future-Proof**: Alignment with Home Assistant core integration standards
- **Quality Compliance**: Meets Bronze quality tier requirements

## Version History

- **v2.0.0**: Breaking changes for Bronze quality tier compliance
- **v1.x**: Original entity ID format
