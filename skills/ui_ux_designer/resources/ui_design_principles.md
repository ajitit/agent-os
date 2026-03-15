# Vishwakarma UI Design Principles

## Visual Language
- **Framework:** Tailwind v4 — use utility classes only; no inline styles
- **Dark mode:** All components must support `dark:` prefix variants
- **Typography:** Geist Sans (body), Geist Mono (code/IDs)
- **Color:** Use Tailwind semantic colors; avoid hardcoded hex values

## Layout Patterns
- **Persistent Nav:** `Nav.tsx` — always visible; do not alter without architect sign-off
- **Page structure:** `<main>` wrapper with consistent padding (`p-6` or `p-8`)
- **Tables:** Use for registry/list views; include empty state and loading skeleton
- **Forms:** Stacked labels above inputs; inline validation messages

## Interaction Standards
- **Loading:** Skeleton loaders for data fetches; spinner for actions
- **Empty states:** Message + CTA button (not just blank space)
- **Error states:** Inline error below field; toast for global errors
- **Success feedback:** Toast notification with auto-dismiss (3s)
- **Destructive actions:** Confirmation dialog before delete/cancel

## Page Patterns
| Page Type | Pattern |
|-----------|---------|
| Registry list | Table with search + create button |
| Detail/edit | Split: info panel left, edit form right |
| Chat | Messages feed + sticky input at bottom |
| Dashboard | Cards with key metrics + quick actions |
| Settings | Sidebar sub-nav + form content area |
