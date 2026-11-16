# Accessibility Statement for CycloneSense

**CycloneSense** is committed to ensuring digital accessibility for all users, including researchers, emergency analysts, and developers with disabilities. We continually improve the user experience and apply relevant accessibility standards to our Earth observation dashboards, matrix viewers, and explainability diagnostic tools.

---

## Conformance Status

We aim to conform to the **Web Content Accessibility Guidelines (WCAG) 2.1 Level AA** standards. These guidelines outline how to make web content more accessible to people with disabilities, and user-friendly for all individuals.

---

## Accessibility Features Implemented

### 1. High-Contrast Scientific UI & Theming
- **Color Contrast:** Text, numerical indicators, and interactive controls maintain a contrast ratio of at least **4.5:1** against the deep space backdrop (`#0c121e`), satisfying WCAG AA contrast minimums.
- **Colorblind-Safe Visualizations:**
  - Satellite infrared brightness temperature gradients and biophysical differencing maps ($\Delta\text{NDVI}$, $\Delta\text{NDWI}$) use perceptually uniform, colorblind-friendly color scales (Viridis and high-contrast diverging palettes).
  - Status indicators (e.g., QC passing, rapid intensification, pairing status) never rely solely on color; they include explicit text badges, icons, and numerical values.

### 2. Semantic HTML & Structural Markup
- Pages use semantic HTML5 elements (`<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`, `<aside>`).
- Data tables (such as Model Benchmarks, Ingestion Catalogs, and Lineage Records) implement full tabular semantics (`<thead>`, `<tbody>`, `<th scope="col">`) for predictable screen reader traversal.
- Form inputs, sliders, and buttons feature programmatic labels and descriptive placeholders.

### 3. Keyboard Navigation & Focus Management
- All interactive controls (buttons, links, search filters, tabs) are reachable and operable via standard keyboard navigation (`Tab`, `Shift+Tab`, `Enter`, `Space`, `Escape`).
- Visible focus rings (`focus-visible:ring-2`, `ring-cyan-500`) provide immediate visual confirmation of the currently active element.
- Modal dialogues and side drawers trap focus while active and restore focus to the triggering element upon dismissal.

### 4. Screen Reader Compatibility & Assistive Tech
- SVGs and custom icons use `aria-hidden="true"` when decorative, or provide accompanying screen-reader-only labels (`sr-only`) when interactive.
- Dynamic data updates (such as live ingestion telemetry and analysis job status) announce changes politely via ARIA live regions (`aria-live="polite"`).

---

## Supported Environments & Assistive Technologies

CycloneSense is designed to be compatible with:
- **Browsers:** Modern versions of Google Chrome, Mozilla Firefox, Microsoft Edge, and Apple Safari.
- **Screen Readers:** NVDA, JAWS on Windows; VoiceOver on macOS and iOS; TalkBack on Android.
- **Display Configurations:** Responsive zoom up to 200% without loss of content or functionality.

---

## Known Limitations & Planned Enhancements

While we strive for comprehensive accessibility, certain complex scientific visualizations have known constraints:
- **High-Density Raster Canvases:** Raw 2D NetCDF4 matrix visualizations (e.g., full-swath geostationary ABI arrays) render via HTML5 Canvas for performance. Full numerical cell data is accessible in raw JSON/table export formats, but canvas pixels themselves cannot be directly traversed by screen readers.
- **Mermaid Interactive Architecture Diagrams:** Diagrams render as scalable SVGs with text labels, but complex node relationships are best navigated alongside the written architecture documentation.

---

## Feedback & Barrier Reporting

We welcome feedback on the accessibility of CycloneSense. If you encounter accessibility barriers, experience difficulty using any component, or have recommendations for improvement:

- **Email:** [koushikkatkam@gmail.com](mailto:koushikkatkam@gmail.com)
- **Subject:** `[ACCESSIBILITY] CycloneSense Accessibility Feedback`
- **Response Commitment:** We review accessibility feedback within **3 business days** and prioritize remediation in upcoming releases.

---

*This statement was created on 16 November 2026 and last reviewed in accordance with WCAG 2.1 standards.*
