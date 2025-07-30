# Mobile View Components

This directory contains all mobile-specific components for the WindWatts application.

## Structure

```
mobile-view/
├── components/           # Reusable mobile components
│   ├── MobileSearchBar.tsx
│   ├── SearchResultsList.tsx
│   ├── WelcomeMessage.tsx
│   └── index.ts
├── MobileBottomSheet.tsx # Main mobile bottom sheet component
├── MapViewMobile.tsx     # Mobile-specific map view
├── LayoutMobile.tsx      # Mobile-specific layout
├── types.ts              # Centralized type definitions
├── index.ts              # Public exports
└── README.md             # This file
```

## Components

### LayoutMobile

The main mobile layout component that provides:

- Mobile-specific app bar
- Mobile bottom sheet integration
- Settings integration
- Google Maps API loading

### MapViewMobile

Mobile-specific map view with:

- Touch-optimized map interactions
- Mobile-specific zoom levels
- Bottom sheet integration on map tap
- Out-of-bounds warning support

### MobileBottomSheet

The mobile bottom sheet component that provides:

- Bottom sheet drawer functionality
- Search bar integration
- Results display
- Touch gesture handling

### MobileSearchBar

A mobile-optimized search input with:

- Google Places autocomplete
- Prediction search
- Clear functionality
- Mobile-specific styling

### SearchResultsList

Displays search predictions in a mobile-friendly list format with:

- Location icons
- Structured formatting
- Touch interactions
- Hover effects

### WelcomeMessage

A simple welcome component (currently unused due to immediate results display)

## Types

All mobile-specific types are centralized in `types.ts`:

- `MobileBottomSheetProps`
- `MobileBottomSheetRef`
- `MobileSearchBarProps`
- `MobileSearchBarRef`
- `SearchResultsListProps`

## Usage

```tsx
import { LayoutMobile, MapViewMobile, MobileBottomSheet } from "../components/mobile-view";

// Use mobile layout
<LayoutMobile />

// Use mobile map view
<MapViewMobile />

// Use mobile bottom sheet
<MobileBottomSheet isLoaded={isLoaded} onPlaceSelected={handlePlaceSelected} />;
```

## Key Features

- **Isolated Components**: Each component is self-contained and reusable
- **Centralized Types**: All types are defined in one place for consistency
- **Clean Exports**: Public API is clearly defined through index files
- **Mobile-First**: All components are designed specifically for mobile UX
- **Gesture Support**: Touch gestures for drawer interactions
- **Search Integration**: Seamless integration with Google Places API
