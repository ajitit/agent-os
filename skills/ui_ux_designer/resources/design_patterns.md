# AgentOS UI Design Patterns

## Pattern: Registry Management Page
```
[Header: "Tool Registry"]  [+ Create button]
[Search bar]
[Table: Name | Description | Status | Actions]
  Row: name | desc | badge | [Edit] [Delete]
[Empty state: "No tools yet. Create your first tool."]
```

## Pattern: Detail + Edit Split
```
[Back link]  [Page Title]
[Left panel 60%]        [Right panel 40%]
  Info display            Edit form
  Key: Value              [Save] [Cancel]
```

## Pattern: Streaming Chat
```
[Messages feed - scrollable]
  [User bubble right]
  [Assistant bubble left - streams token by token]
[Input bar - sticky bottom]
  [Textarea] [Model selector] [Send button]
```

## Pattern: Confirmation Dialog
```
[Modal overlay]
  Title: "Delete Agent?"
  Body: "This action cannot be undone."
  [Cancel]  [Delete - destructive color]
```

## Pattern: Status Badge
```
active   → green badge
inactive → gray badge
error    → red badge
pending  → yellow badge
```

## Pattern: Progressive Disclosure Form
```
[Basic fields - always visible]
[▼ Advanced settings - collapsed by default]
  [Additional fields]
```
