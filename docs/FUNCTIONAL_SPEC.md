# SBAAS Productivity – Functional Specification

## User Goals
1. Launch a desktop application that centralizes productivity monitoring for SBAAS teams.
2. View at-a-glance summaries (completion rate, remaining work) derived from task data.
3. Configure the application without modifying code by updating `.env` or `settings.yaml`.

## Current Scope (MVP)
- Display a welcoming dashboard window that confirms the application version and active theme.
- Provide reusable helper logic (`summarize_productivity`) for eventual dashboard widgets.
- Load configuration values from disk and initialize the backing SQLite database automatically.

## Configuration
- `.env` holds environment-specific secrets such as `DATABASE_URL`.
- `settings.yaml` stores general metadata (app name, UI theme, database path).
- The Config class exposes typed accessors ensuring downstream code remains decoupled from parsing logic.

## Future Enhancements
1. Persist productivity metrics in SQLite and visualize trends within the GUI.
2. Add task import/export integrations with the broader SBAAS ecosystem.
3. Offer user preferences (e.g., theme toggle, notifications) saved per profile.
