# Components Directory Structure

This directory contains all React components for the WindWatts application, organized by functionality and platform.

## Structure

```
components/
├── core/                    # Core reusable components
│   ├── SearchBar.tsx       # Main search component
│   └── index.ts
├── desktop-view/           # Desktop-specific components
│   ├── LayoutDesktop.tsx   # Desktop layout
│   ├── MapViewDesktop.tsx  # Desktop map view
│   └── index.ts
├── mobile-view/            # Mobile-specific components
│   ├── components/         # Reusable mobile components
│   ├── LayoutMobile.tsx    # Mobile layout
│   ├── MapViewMobile.tsx   # Mobile map view
│   ├── MobileBottomSheet.tsx
│   ├── types.ts
│   ├── index.ts
│   └── README.md

├── resultPane/             # Results display components
│   ├── AnalysisResults.tsx
│   ├── ProductionCard.tsx
│   ├── ProductionDataTable.tsx
│   ├── RightPane.tsx
│   ├── WindResourceCard.tsx
│   ├── WindSpeedCard.tsx
│   └── index.ts
├── settings/               # Settings components
│   ├── HubHeightSettings.tsx
│   ├── ModelSettings.tsx
│   ├── PowerCurveSettings.tsx
│   ├── SettingToggleButtonGroup.tsx
│   ├── Settings.tsx
│   ├── UnitsSettings.tsx
│   └── index.ts
├── shared/                 # Shared components
│   └── OutOfBoundsWarning.tsx
├── Layout.tsx              # Main layout router
├── MapView.tsx             # Main map view router
├── index.ts                # Public exports
└── README.md               # This file
```

## Component Categories

### Core Components (`core/`)

Fundamental components used across the application:

- **SearchBar**: Main search functionality with Google Places integration

### Desktop Components (`desktop-view/`)

Components specifically designed for desktop experience:

- **LayoutDesktop**: Desktop layout with sidebar and footer
- **MapViewDesktop**: Desktop map view with search bar overlay

### Mobile Components (`mobile-view/`)

Components specifically designed for mobile experience:

- **LayoutMobile**: Mobile layout with bottom sheet
- **MapViewMobile**: Mobile map view with touch interactions
- **MobileBottomSheet**: Bottom drawer for search and results
- **MobileSearchBar**: Mobile-optimized search input
- **SearchResultsList**: Mobile search results display

### Results Components (`resultPane/`)

Components for displaying analysis results:

- **RightPane**: Main results container
- **ProductionCard**: Power production display
- **WindResourceCard**: Wind resource information
- **WindSpeedCard**: Wind speed data display
- **ProductionDataTable**: Tabular data display
- **AnalysisResults**: Analysis summary

### Settings Components (`settings/`)

Components for user preferences and configuration:

- **Settings**: Main settings container
- **ModelSettings**: Model selection
- **PowerCurveSettings**: Power curve configuration
- **HubHeightSettings**: Hub height configuration
- **UnitsSettings**: Unit system selection

### Shared Components (`shared/`)

Components used across multiple platforms:

- **OutOfBoundsWarning**: Warning for out-of-bounds coordinates

## Usage

```tsx
// Import main components
import { Layout, MapView } from "../components";

// Import platform-specific components
import { LayoutDesktop, MapViewDesktop } from "../components/desktop-view";
import { LayoutMobile, MapViewMobile } from "../components/mobile-view";

// Import core components
import { SearchBar } from "../components/core";

// Import feature-specific components
import { RightPane } from "../components/resultPane";
import { Settings } from "../components/settings";
```

## Key Features

- **Platform Separation**: Clear separation between desktop and mobile components
- **Modular Organization**: Components grouped by functionality
- **Type Safety**: TypeScript throughout with centralized type definitions
- **Consistent Exports**: Clean public API through index files

- **Shared Components**: Reusable components across platforms
