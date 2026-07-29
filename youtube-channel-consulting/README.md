# YouTube Channel Consulting

Working repo for YouTube channel consulting engagements — strategy docs,
per-client status tracking, and the reusable process this is built on.

## Structure

```
template/           Generic, client-agnostic skeleton. Copy from here when
                     starting a new client engagement. Don't edit in place
                     per-client — copy it into clients/<name>/ first.
clients/
  scottsdale-az-realtor/
                     First engagement. Each client folder holds:
                     - custom-instructions.md → pastes into that client's
                       Claude Project settings
                     - living-status-doc.md   → pastes into that Claude
                       Project's Project Knowledge; edited in place every
                       session, never copied/dated
                     - audit-checklist.md     → working checklist for the
                       initial channel audit, not project config
source-notes/        Provenance — the original process-lessons doc this
                     whole template was derived from.
```

## Working rules for this repo

- **One living doc per client, edited in place.** `living-status-doc.md`
  gets updated every session. It does not get copied, dated, or forked —
  if something needs to change, edit the file and commit. This mirrors
  the exact mistake this template was built to avoid (seven README-mode-
  edit failures becoming five dated `MASTER-REFERENCE` copies in a past
  project).
- **Record the reasoning, not just the decision**, in each living doc's
  "Decisions made" section.
- **The `template/` folder is the source of truth for process
  improvements.** If something learned on one client should apply to all
  future ones, update `template/`, not just the one client folder.
