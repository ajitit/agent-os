# Sprint Planning Guide

## Sprint Structure
- **Duration:** 2 weeks
- **Ceremonies:** Planning (2h), Daily (15min), Review (1h), Retro (30min)
- **Capacity:** Assume 70% of total hours for feature work (30% for bugs, reviews, meetings)

## Story Sizing (Complexity Points)
| Size | Description | Example |
|------|-------------|---------|
| XS | < 1h | Fix a typo, update a label, add a field to existing form |
| S | 1–4h | Add a new registry endpoint (CRUD already exists as pattern) |
| M | 4–8h | New feature page + backend endpoint + tests |
| L | 1–2 days | New module (e.g., notifications system) |
| XL | 2+ days | Architectural change (e.g., DB migration, new adapter) |

## Backlog Prioritization (MoSCoW)
- **Must:** Blocking critical features; sprint cannot close without
- **Should:** High value; planned for sprint but can slip to next
- **Could:** Nice to have; include only if capacity allows
- **Won't:** Explicitly out of scope this sprint

## Sprint Checklist
Before sprint starts:
- [ ] All Must stories have acceptance criteria written
- [ ] XL stories broken into smaller pieces
- [ ] Dependencies between stories identified
- [ ] Stories tagged with skill types needed (backend_developer, etc.)

During sprint:
- [ ] Daily: flag any blocker immediately
- [ ] Stories marked in_progress when started (only one at a time per person)
- [ ] PR opened and linked to story before review

End of sprint:
- [ ] All Must stories meet Definition of Done
- [ ] Incomplete stories re-estimated and added to next sprint backlog
- [ ] Retro: 1 process improvement identified for next sprint
