# React Component Patterns for AgentOS

## Standard Page Component
```tsx
// src/app/{feature}/page.tsx
'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

interface Item { id: string; name: string }

export default function FeaturePage() {
  const [items, setItems] = useState<Item[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.get<Item[]>('/items')
      .then(res => setItems(res.data))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>
  if (items.length === 0) return <div>No items yet.</div>
  return <ul>{items.map(i => <li key={i.id}>{i.name}</li>)}</ul>
}
```

## API Response Type
```tsx
// All backend responses use this shape
interface APIResponse<T> {
  data: T
  meta: { request_id: string; version: string }
}
```

## Streaming Chat Pattern
```tsx
const res = await fetch(`${API_URL}/api/v1/conversations/${id}/chat/stream`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
  body: JSON.stringify({ message })
})
const reader = res.body!.getReader()
const decoder = new TextDecoder()
while (true) {
  const { done, value } = await reader.read()
  if (done) break
  setResponse(prev => prev + decoder.decode(value))
}
```

## Form Submit Pattern
```tsx
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault()
  setSubmitting(true)
  try {
    await api.post('/agents', formData)
    setSuccess(true)
  } catch (err) {
    setError('Failed to create agent')
  } finally {
    setSubmitting(false)
  }
}
```
