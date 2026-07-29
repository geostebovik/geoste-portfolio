# Client Intake / Channel Audit Checklist (Template)

Use this before writing any strategy for a new client. The point is to
build on what already exists and verify claims against real data, not
vanity metrics or generic "best practice."

**Assets to gather (reuse, don't re-derive):**
- Full analytics export (not just the dashboard summary) — views, watch
  time, CTR, average view duration, traffic source, audience retention
  curves, per-video breakdown
- Every existing video's title, description, thumbnail, upload date
- Any brand guidelines, logo files, color palette, past thumbnail
  templates
- Prior scripts, outlines, or content calendars if they exist
- Comment history — sentiment, recurring questions, engagement patterns

**Questions for the client:**
- What's the actual business goal behind the channel? (Leads, brand
  authority, referrals, direct sales — views alone are rarely the real
  goal.)
- What's already been tried, and what happened?
- Any constraints: time to film/edit per week, budget for
  equipment/editing, comfort on camera?
- What does "success" look like to them in 6 months — in their own words,
  not in view-count terms?

**Metrics to actually track (not just the easy/flattering ones):**
- Click-through rate on thumbnails/titles
- Audience retention (where viewers drop off, not just average duration)
- Traffic source mix (browse, search, suggested, external)
- Conversion signal specific to the goal above (site clicks, inquiry form
  fills, DMs/comments asking about a property) — views and subscriber
  count are vanity metrics unless tied back to this
- Independent benchmark: comparable channels in the same niche/market, not
  just the channel's own history — a channel shouldn't grade itself

**Before changing anything already "wired":**
- Check what depends on it first — series names, established posting
  schedule, playlist structure, external links (website, social bios,
  email signatures) pointing at specific videos/playlists. A clean-looking
  rename or reschedule can silently break something a viewer or the site
  depends on.

**Testing discipline:**
- One variable at a time. If testing a new thumbnail style, hold title,
  upload time, and topic constant — otherwise a result can't be
  attributed to the actual change.

**Technical notes — platform access:**
- No dedicated YouTube MCP connector is registered as of this writing.
  Practical options for pulling data or building automation:
  - **YouTube Data API v3** — video/channel metadata, comments, search.
    Requires a Google Cloud project + OAuth or API key.
  - **YouTube Analytics API** — the real metrics (retention, traffic
    source, CTR); separate from Data API, same Google Cloud project.
  - **Native notifications** — YouTube Studio's mobile app and browser
    push already alert the channel owner to new comments/views in
    real time; check these are actually turned on before building
    anything custom.
  - **Website integration** — simplest is an iframe embed of the channel
    or a playlist; a dynamic "latest videos" feed needs the Data API and
    a small amount of custom code (or a no-code embed tool that wraps the
    same API).
  - Revisit this section if an official YouTube connector becomes
    available later — check the connector registry again before building
    anything custom.
