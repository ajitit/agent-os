# Accessibility Guidelines (WCAG 2.1 AA)

## Color & Contrast
- Text on background: minimum 4.5:1 contrast ratio
- Large text (18px+): minimum 3:1
- UI components (buttons, inputs): minimum 3:1 against adjacent colors
- Never use color alone to convey meaning — add icon or text

## Keyboard Navigation
- All interactive elements reachable via Tab key
- Visible focus indicator on all focusable elements (Tailwind: `focus:ring-2`)
- Logical tab order — matches visual reading order
- Escape key closes modals and dropdowns

## ARIA & Semantics
- Use semantic HTML: `<button>`, `<nav>`, `<main>`, `<form>`, `<table>`
- Add `aria-label` to icon-only buttons
- `aria-live="polite"` for dynamic content updates (chat messages, status)
- `aria-expanded` on dropdowns and collapsible sections
- Form inputs: `<label>` must be associated via `for`/`id`

## Images & Media
- All `<img>` elements need descriptive `alt` text
- Decorative images: `alt=""`
- Charts: provide text summary or data table alternative

## Focus Management
- Modal dialogs: trap focus inside while open; return focus on close
- After navigation: focus moves to page `<h1>`
- After form submit: focus moves to success/error message
