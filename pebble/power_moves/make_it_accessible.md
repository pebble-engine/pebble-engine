---
id: make_it_accessible
label: Make it accessible
description: Add alt text, focus rings, labels, and contrast fixes for everyone.
triggers: accessibility, a11y, wcag, screen reader, aria, accessible, keyboard navigation
billable: true
---
Make this site accessible (toward WCAG 2.1 AA) WITHOUT redesigning it.

- Add descriptive `alt` text to meaningful images; `alt=""` for purely decorative ones.
- Give every interactive element an accessible name (`aria-label` where text isn't visible) and a visible `focus-visible:` ring.
- Ensure full keyboard operability (logical tab order, no keyboard traps; menus/dialogs closeable with Escape).
- Fix low color-contrast text against its background while staying within the existing palette/design tokens.
- Use semantic landmarks (`<header> <nav> <main> <footer>`) and correct heading order.

Do NOT change the visual design, layout, copy meaning, or invent any facts. Output only the changed files as `<pebble-file>` blocks.
