# State Management Patterns

## Local State (current standard)
Use `useState` + `useEffect` for page-level data. No global state library yet.

```tsx
const [data, setData] = useState<T | null>(null)
const [loading, setLoading] = useState(true)
const [error, setError] = useState<string | null>(null)
```

## When to Lift State
- If two sibling components need the same data → lift to parent page
- If nav-level data needed → consider `src/components/Nav.tsx` context

## Optimistic Updates
For CRUD operations that should feel instant:
```tsx
// 1. Update local state immediately
setItems(prev => [...prev, newItem])
// 2. Make API call
try { await api.post('/items', newItem) }
// 3. On failure, revert
catch { setItems(prev => prev.filter(i => i.id !== newItem.id)) }
```

## Form State
- Controlled inputs: `value` + `onChange` for all form fields
- Validation: check before submit; show inline errors
- Reset: `setFormData(initialState)` on success

## Pagination (not yet implemented)
When added: use `page` + `pageSize` state; fetch on page change.
