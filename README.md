# Project Aegis GitHub Pages Site

This repository contains a static multi-page website for Project Aegis.

## Files
- `index.html` - friendly home page and project overview
- `setup.html` - Azure tenant, identity, governance, secrets, and diagnostics baseline
- `networking.html` - hub-and-spoke layout, private endpoints, DNS, and Linux NVA egress path
- `app.html` - Flask app flow, hybrid search, citations, and live demo link
- `logging.html` - logging, testing, detections, and investigation examples
- `artifacts.html` - supporting documents and evidence
- `about.html` - personal context, learning goals, and project motivation
- `architecture.html` / `security.html` / `interview.html` - lightweight redirects kept for compatibility
- `styles.css` - shared site styling
- `script.js` - header and reveal behavior

## How to publish with GitHub Pages
1. Create a GitHub repository.
2. Upload these files to the repository root.
3. In GitHub, go to **Settings → Pages**.
4. Under **Build and deployment**, choose:
   - **Source:** Deploy from a branch
   - **Branch:** `main` and `/root`
5. Save.
6. GitHub will publish the site at your Pages URL.

## Notes
- Supporting documents live in `SupportingDocs/`.
- Keep project content aligned with the actual Azure build, threat model, and implementation evidence.
- Avoid placeholder or meta commentary in the site copy.
