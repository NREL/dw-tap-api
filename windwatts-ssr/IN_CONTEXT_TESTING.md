# In-Context URL Testing Guide

The WindWatts SSR POC now supports "launch in context" - you can share URLs with specific locations and settings pre-loaded.

## 🔗 URL Format

```
http://localhost:5174?lat={latitude}&lng={longitude}&hubHeight={height}&model={model}&powerCurve={curve}
```

All parameters are **optional** - missing params will use sensible defaults.

---

## 📍 Test Cases

### 1. **Default Location (Denver)**

```
http://localhost:5174/
```

Expected: lat=39.7392, lng=-104.9903, hubHeight=40, model=era5, powerCurve=nrel-reference-100kW

### 2. **Custom Location (San Francisco)**

```
http://localhost:5174?lat=37.7749&lng=-122.4194
```

Expected: Map centers on SF, other settings use defaults

### 3. **Full Configuration (Southern California)**

```
http://localhost:5174?lat=34.165&lng=-117.471&hubHeight=80&model=wtk&powerCurve=nrel-reference-2000kW
```

Expected: All settings applied, 2MW turbine, 80m height, WTK model

### 3b. **Texas Wind Farm (West Texas)**

```
http://localhost:5174?lat=31.5&lng=-100.5&hubHeight=100&model=wtk&powerCurve=nrel-reference-2000kW
```

Expected: West Texas wind resource, 100m height, 2MW turbine

### 4. **Different Hub Heights**

```
http://localhost:5174?lat=40.5&lng=-105.2&hubHeight=100
http://localhost:5174?lat=40.5&lng=-105.2&hubHeight=30
http://localhost:5174?lat=40.5&lng=-105.2&hubHeight=140
```

Expected: Same location, different hub heights

### 5. **Model Comparison**

```
http://localhost:5174?lat=39.7392&lng=-104.9903&model=era5
http://localhost:5174?lat=39.7392&lng=-104.9903&model=wtk
```

Expected: Same location, different data models

### 6. **Power Curve Variations**

```
http://localhost:5174?lat=40.5&lng=-105.2&powerCurve=nrel-reference-2.5kW
http://localhost:5174?lat=40.5&lng=-105.2&powerCurve=nrel-reference-100kW
http://localhost:5174?lat=40.5&lng=-105.2&powerCurve=nrel-reference-250kW
http://localhost:5174?lat=40.5&lng=-105.2&powerCurve=nrel-reference-2000kW
```

Expected: Different production estimates for different turbine sizes

### 7. **Offshore Location (East Coast)**

```
http://localhost:5174?lat=40.5&lng=-72.5&hubHeight=120&powerCurve=nrel-reference-2000kW
```

Expected: Offshore wind resource analysis

### 8. **Mountain Location (Colorado Rockies)**

```
http://localhost:5174?lat=39.5&lng=-105.9&hubHeight=60
```

Expected: Mountain wind resource

---

## 🧪 Validation Tests

### Valid Ranges

- **Latitude**: -90 to 90 (Falls back to default if invalid)
- **Longitude**: -180 to 180 (Falls back to default if invalid)
- **Hub Height**: 30, 40, 50, 60, 80, 100, 120, 140 meters (Falls back to 40 if invalid)
- **Model**: "era5" or "wtk" (Falls back to "era5" if invalid)
- **Power Curve**: Valid NREL reference curves (Falls back to 100kW if invalid)

### Invalid Input Tests

```
# Invalid latitude (should use default)
http://localhost:5174?lat=999&lng=-105

# Invalid longitude (should use default)
http://localhost:5174?lat=40&lng=999

# Invalid hub height (should use 40m)
http://localhost:5174?lat=40&lng=-105&hubHeight=75

# Invalid model (should use era5)
http://localhost:5174?lat=40&lng=-105&model=invalid

# Invalid power curve (should use 100kW)
http://localhost:5174?lat=40&lng=-105&powerCurve=invalid
```

---

## 📋 Share Link Feature

Click the **"📋 Share Link"** button in the header to:

1. Copy the current URL with all settings
2. Share with colleagues/stakeholders
3. Bookmark for later reference

The button shows **"✓ Copied!"** for 2 seconds after copying.

---

## 🔄 Dynamic Meta Tags

The page title and description update based on URL params:

```html
<!-- Default -->
<title>WindWatts SSR POC</title>

<!-- With location params -->
<title>WindWatts - 40.50, -105.20</title>
<meta
  name="description"
  content="Wind resource analysis for location 40.50, -105.20 at 80m hub height"
/>
```

This improves:

- **SEO** - Search engines index location-specific pages
- **Social sharing** - Link previews show relevant info
- **Browser tabs** - Easy to identify which location you're viewing

---

## 🎯 Use Cases

1. **Site Selection**: Compare multiple locations by opening tabs with different coordinates
2. **Stakeholder Sharing**: Send configured URLs to clients/partners
3. **Documentation**: Include URLs in reports or presentations
4. **Bookmarking**: Save favorite locations with optimal settings
5. **API Integration**: Generate URLs programmatically from external tools

---

## 🚀 Future Enhancements (Not in POC)

- Path-based params: `/location/40.5/-105.2/hub/80`
- Legacy URL support for backwards compatibility
- URL shortening service integration
- QR code generation for mobile sharing
- Batch URL generation for multiple sites
