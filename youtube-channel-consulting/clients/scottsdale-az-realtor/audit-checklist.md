# Scottsdale AZ Realtor — First Audit Pass

Working checklist, not project config. Derived from
template/intake-audit-checklist.md.

**Pull before anything else (reuse, don't re-derive):**
- Full YouTube Studio analytics export: views, watch time, CTR, average
  view duration, retention curves, traffic sources — per video and
  channel-wide, trailing 90 days minimum if available.
- All 81 videos' current titles, descriptions, thumbnails, upload dates.
- Any existing brokerage brand guidelines, logo files, headshots.
- Website URL and current tech stack (ask the client or check the site
  directly — this determines what "integration" can realistically mean).

**Verify, don't assume:**
- Go through descriptions one by one and log every factual error found
  (wrong price, address, listing status, expired link, etc.) — don't
  estimate the scope, count it.

**Ask the client directly:**
- Real goal behind the channel (see open question in living-status-doc.md).
- What "notifications" and "integration" mean in practice to her.
- Anything already tried for growth, and what happened.

**Technical notes for the two specific asks:**
- **Notifications:** no dedicated YouTube MCP connector exists in this
  environment as of 2026-07-28 (checked the connector registry directly —
  nothing YouTube-specific came back). Cheapest fix: confirm native
  YouTube Studio app push notifications are turned on for the client's
  account — that alone covers real-time views/comments/subscriber
  alerts without building anything. If she wants alerts somewhere else
  (email digest, website dashboard), that requires the YouTube Data API
  v3 + YouTube Analytics API via a Google Cloud project, polled on a
  schedule — a small custom build, not a plug-in-and-go connector. Worth
  checking the registry again before building, in case a connector gets
  added later.
- **Website integration:** simplest path is an iframe embed of the
  channel/playlist (no API needed, near-zero maintenance). A dynamic
  "latest videos" feed on the site needs the Data API and either custom
  code or a no-code embed tool wrapping it. Get the website's tech stack
  before recommending either.

**Before renaming or restructuring anything:**
- Check what's already wired to the current video titles/series
  names/playlists — external links from the website, social bios, past
  email campaigns — before changing anything, since a clean-looking
  rename can silently break an existing link.
