# Project Aegis GitHub Pages Site

This repository contains a static multi-page website for Project Aegis.

## Files
- `index.html` - minimal home page
- `architecture.html` - the main architecture page, organized into Azure foundation, networking layer, and AI application architecture
- `app.html` - live demo page and application flow
- `logging.html` - logging, testing, detections, and investigation examples
- `artifacts.html` - supporting documents and evidence
- `about.html` - project story, learning goals, and objectives
- `setup.html` / `networking.html` / `security.html` / `interview.html` - lightweight redirects kept for compatibility
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
- Avoid placeholder or meta commentary in the site copy except where logging screenshots intentionally use `[INSERT DESCRIPTION HERE]` placeholders.
