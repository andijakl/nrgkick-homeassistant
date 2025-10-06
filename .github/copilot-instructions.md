# NRGkick Gen2 Local API Documentation

## Project Overview

This repository contains technical documentation for the **NRGkick Gen2** EV charging device's local REST JSON and ModBus TCP APIs. The entire project is a single, self-contained HTML documentation file with embedded JavaScript for interactive API testing.

**Key Facts:**

- **Product**: NRGkick Gen2 - an EV charging controller with local network APIs
- **Structure**: Single HTML file (`Documentation/NRGkick Gen2 Local API Documentation.html`)
- **Purpose**: Interactive API reference with live testing capabilities
- **Copyright**: DiniTech GmbH (2024) - Author: Florian Kloiber

## Architecture

### Single-Page Application Design

The documentation is a monolithic HTML file (~2000 lines) containing:

- Complete CSS styling (inline `<style>` blocks)
- JavaScript logic for interactive features (inline `<script>` blocks)
- API documentation tables and examples
- Dark/light theme system
- Live API testing interface

### API Coverage

1. **JSON REST API** (default view)
   - `/info` - Device information (serial, network, hardware/software versions)
   - `/control` - Charging control (current, pause, energy limits, phase count)
   - `/values` - Real-time telemetry (power, voltage, temperature, status)

2. **ModBus TCP API** (alternative view)
   - Register-based access to same data
   - Little-endian format, Unit ID 1
   - Read (0x03) and Write (0x06, 0x10) operations

### Interactive Features

- **mDNS Discovery**: Documentation for `_nrgkick._tcp` service discovery
- **URL Builder**: User inputs generate query strings dynamically
- **Live Testing**: Send requests to actual NRGkick devices on the network
- **Theme Toggle**: Animated dark/light mode switcher
- **Collapsible Sections**: Dropdown mappings for enum values

## Development Patterns

### Styling Architecture

- **CSS Custom Properties**: Colors like `#0070c0` (brand blue) used consistently
- **Responsive Design**: Media queries at 850px and 550px breakpoints
- **Theme System**: `.light` and `.dark` classes with localStorage persistence
- **Component-Based**: `.endpoint`, `.container`, `.request_fields`, `.dropdown` classes

### JavaScript Patterns

```javascript
// URL Building Pattern (lines ~1290-1340)
function update_control_url() {
  const current = document.getElementById("control_current").value;
  // ... build query string from form inputs
  last_control_url = baseUrl + params.join("&");
  document.getElementById("control_url").textContent = last_control_url;
}

// Fetch Pattern (lines ~1780+)
function fetch_data(type) {
  is_fetching = true;
  const url = req_type[type].url;
  // ... make request to device
}

// Theme Toggle (lines ~1230-1250)
function toggleTheme() {
  const currentTheme =
    localStorage.getItem("theme") === "dark" ? "light" : "dark";
  applyTheme(currentTheme);
}
```

### State Management

- **localStorage**: `theme` and `api_type` preferences
- **Global Variables**: `current_set`, `charge_pause`, `energy_limit`, `phase_count`
- **Enum Objects**: `fetch_type_t` defines request types (INFO, CONTROL, VALUES)

## Key Technical Details

### Device Communication

- **Discovery**: mDNS/Bonjour service type `_nrgkick._tcp`
- **Authentication**: Optional BasicAuth (enabled in NRGkick App)
- **Base URL**: Device IP address (discovered via mDNS or manual entry)
- **Response Format**: JSON with optional `?raw` mode for numeric enums

### Data Structures

```javascript
// Example JSON Response Structure
{
  "general": { "serial_number": "...", "model_type": "...", ... },
  "network": { "ip_address": "...", "mac_address": "...", ... },
  "powerflow": { "voltage": {...}, "current": {...}, "power": {...} },
  "temperatures": { "housing": 34.79, "connector_l1": 21.09, ... }
}
```

### Important Constants

- **Current Range**: 6.0A - rated_current (16A or 32A)
- **Phase Count**: 1-3 (when phase switching enabled)
- **Energy Limit**: 0 = no limit, >0 = Wh limit
- **ModBus Unit ID**: Always 1
- **Voltage Types**: 230V/400V grids, 50Hz/60Hz frequency

## Editing Guidelines

### When Modifying the HTML File

1. **Preserve Inline Structure**: All CSS/JS is embedded - no external files
2. **Maintain Accessibility**: Use semantic HTML and proper ARIA labels
3. **Keep Copyright**: DiniTech GmbH header comment must remain
4. **Test Both Themes**: Changes should work in light and dark modes
5. **Validate JSON Examples**: Ensure mock data matches actual API schemas

### Adding New Endpoints

1. Add table row to appropriate section (JSON API or ModBus API)
2. Update `req_type` array with new endpoint URL
3. Create corresponding `update_*_url()` function
4. Add form inputs if write operations are supported
5. Update `fetch_data()` switch statement

### Styling Conventions

- **Brand Color**: `#0070c0` (blue) for primary actions/accents
- **Dark Theme**: `#000416` background, `#f0f0f0` text
- **Light Theme**: `#ffffff` background, `#000000` text
- **Spacing**: 20px base unit for margins/padding
- **Border Radius**: 30px for endpoints, 5px for small elements

### JavaScript Best Practices

- **No Framework**: Vanilla JavaScript only - keep it dependency-free
- **Event Delegation**: Use for dynamically created elements
- **Error Handling**: Display user-friendly messages for fetch failures
- **Input Validation**: Range checks before API calls (e.g., 6-32A)

## Common Tasks

### Update API Version

Search for `"json_api_version": "v1"` and ModBus equivalent - update if API changes.

### Add New Error Code

1. Find error mapping dropdown (line ~900 and ~1170)
2. Add new `<strong>X</strong> - "ERROR_NAME"` entry
3. Maintain numeric order in mapping

### Fix Browser Compatibility

- Test in Chrome, Firefox, Safari, Edge
- No IE11 support required (modern APIs used)
- Check CSS Grid, Flexbox, fetch API support

## Testing

Since this is documentation, testing means:

1. **Visual Testing**: Open HTML in browsers, toggle themes
2. **Interactive Testing**: Try form inputs, URL generation
3. **Live Device Testing**: Connect to actual NRGkick device on network
4. **Mobile Testing**: Responsive breakpoints at 850px/550px

## Important Notes

- **No Build Process**: Direct HTML file - just open in browser
- **No Dependencies**: Self-contained, no npm/package.json needed
- **Version Requirements**: NRGkick firmware >= SmartModule 4.0.0.0 required for API access
- **Network Access**: Documentation includes live API testing - requires device on same network
- **Simulation Mode**: JavaScript includes mock data generation for offline demonstration

## Quick Reference

**File Location**: `Documentation/NRGkick Gen2 Local API Documentation.html`

**Key Sections**:

- Lines 6-560: CSS styles
- Lines 566-590: Header with theme toggle
- Lines 592-620: Overview and mDNS discovery
- Lines 621-1030: JSON API documentation
- Lines 1031-1190: ModBus API documentation
- Lines 1220+: JavaScript for interactivity

**External Resources**: None - fully self-contained HTML file.
