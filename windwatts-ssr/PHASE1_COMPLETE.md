# Phase 1: SSR POC - Complete ✅

## Overview

A fully functional Remix SSR proof-of-concept that runs alongside the original WindWatts UI, sharing the same backend API.

## Features Implemented

### 1. **Server-Side Data Fetching**

- Loader fetches both wind speed and energy production data
- URL-based parameters: `lat`, `lng`, `hubHeight`, `model`, `powerCurve`
- Fallback to dummy data if API is unavailable
- 3-second timeout with graceful error handling

### 2. **Results Pane** (Right Sidebar)

- Location display (coordinates)
- Hub height indicator
- Power curve selection
- **Wind Speed Card** (blue highlight)
  - Shows average wind speed at selected height in m/s
- **Production Estimates Card** (green highlight)
  - Average annual production
  - Lowest year
  - Highest year
  - All values formatted with proper units (kWh/yr)

### 3. **Settings Modal**

- Editable parameters:
  - Latitude/Longitude (number inputs)
  - Hub Height (dropdown: 30, 40, 50, 60, 80, 100m)
  - Model (dropdown: ERA5, WTK)
  - Power Curve (dropdown: NREL reference curves)
- **URL Parameter Sync**: Settings changes update URL and trigger new data fetch
- Cancel/Save actions

### 4. **Interactive Map**

- Google Maps integration (client-side only)
- Marker at selected location
- Respects SSR constraints (no hydration errors)
- Full-height responsive layout

### 5. **UI/UX**

- Material-UI (MUI) components
- Clean, modern card-based design
- Color-coded results for quick scanning
- Responsive grid layouts
- Professional typography and spacing

## Architecture

### File Structure

```
windwatts-ssr/
├── app/
│   ├── routes/
│   │   └── _index.tsx          # Main route with loader + UI
│   ├── components/
│   │   ├── ClientOnlyMap.tsx   # Google Maps (client-side)
│   │   ├── ResultsPane.tsx     # Right sidebar results
│   │   └── SettingsModal.tsx   # Settings dialog
│   ├── entry.client.tsx        # Client hydration
│   ├── entry.server.tsx        # SSR rendering
│   └── root.tsx                # HTML shell
├── package.json
├── vite.config.ts
└── Dockerfile.dev
```

### Data Flow

1. **User loads page** → Remix loader runs on server
2. **Loader fetches** wind + production data from backend API
3. **Server renders** HTML with data
4. **Client hydrates** React components
5. **Map loads** client-side (Google Maps script)
6. **User changes settings** → URL updates → loader re-runs → new data

### URL Parameters

```
http://localhost:5174/?lat=39.7392&lng=-104.9903&hubHeight=40&model=era5&powerCurve=nrel-reference-100kW
```

## Docker Integration

### Services

- `windwatts-ssr`: Port 5174 (this POC)
- `windwatts-ui`: Port 5173 (original UI)
- `windwatts-api`: Port 8000 (shared backend)
- `postgres`: Database
- `nginx`: Reverse proxy

### Environment Variables

- `API_BASE_URL`: Backend API endpoint (default: `http://windwatts-api:8000`)
- `VITE_MAP_API_KEY`: Google Maps API key
- `USE_DUMMY_DATA`: Optional flag for testing without backend

### Running

```bash
# Start all services
docker compose up

# View SSR POC
open http://localhost:5174

# View original UI (for comparison)
open http://localhost:5173
```

## Testing

### Manual Test Flow

1. Open http://localhost:5174
2. Verify map loads at default location (Denver)
3. Click "Settings" button
4. Change hub height to 60m
5. Change model to WTK
6. Click "Save"
7. Verify URL updates with new parameters
8. Verify results pane shows new wind speed and production data
9. Verify map marker updates to reflect current location

### Expected Results

- Wind speed: ~6-8 m/s (varies by location/height)
- Production: ~40-50k kWh/yr (for 100kW turbine)
- Page loads in <2 seconds
- No console errors
- No hydration warnings

## Phase 2 Candidates

### High Priority

1. **Search Bar Integration**

   - Google Places autocomplete
   - Update location on search
   - Recenter map + fetch new data

2. **Map Interactions**

   - Click to set location
   - Drag marker to update coordinates
   - Sync map state with URL params

3. **Time Period Selector**
   - Toggle between yearly/monthly data
   - Expandable data tables

### Medium Priority

4. **Bias Correction Toggle**

   - Settings checkbox
   - URL param sync
   - Update API calls

5. **Mobile Layout**

   - Responsive breakpoints
   - Collapsible sidebar
   - Touch-friendly controls

6. **Error Boundaries**
   - Graceful error handling
   - Retry mechanisms
   - User-friendly messages

### Lower Priority

7. **Production Data Table**

   - Expandable breakdown
   - Year-by-year or month-by-month
   - Export functionality

8. **Chart Visualizations**
   - Production over time
   - Wind speed distribution
   - Interactive tooltips

## Known Issues / Limitations

1. **Search bar not wired** - placeholder only
2. **No map click handler** - marker is read-only
3. **Limited power curve options** - only NREL reference curves
4. **No bias correction UI** - backend supports it, UI doesn't expose it
5. **Desktop-only layout** - not optimized for mobile yet

## Technical Debt

1. **Entry.server.tsx** - Using `renderToString` (sync) instead of streaming
2. **No Emotion SSR extraction** - Styles work but could be optimized
3. **Hardcoded constants** - Should pull from shared config/constants file
4. **No type safety for loader data** - Could add Zod schemas
5. **PassThrough stream class** - Simplified, could use proper Node streams

## Success Metrics

✅ SSR working correctly (view-source shows rendered HTML)
✅ Client hydration successful (no React errors)
✅ Map loads client-side only (no SSR issues)
✅ API integration working (fetches real data from backend)
✅ URL params drive data fetching (enables "launch in context")
✅ Settings modal syncs with URL (enables sharing links)
✅ MUI components render properly (SSR + client)
✅ Docker compose integration (runs alongside existing services)

## Next Steps

**User Decision Point**: What should Phase 2 focus on?

Option A: **Enhanced Interactivity**

- Wire search bar
- Add map click handlers
- Implement drag-to-update

Option B: **Data Richness**

- Production data tables
- Chart visualizations
- Time period selector

Option C: **Mobile Experience**

- Responsive layouts
- Touch controls
- Progressive Web App (PWA)

Option D: **Full Migration Planning**

- Detailed effort estimation
- Component-by-component mapping
- Migration strategy document
