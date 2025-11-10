# SBAAS Productivity – Functional Specification

## User Goals
1. Launch a desktop application that centralizes productivity monitoring for SBAAS teams.
2. View at-a-glance summaries (completion rate, remaining work) derived from task data.
3. Configure the application without modifying code by updating `.env` or `settings.yaml`.

## Current Scope (MVP)
- Display a welcoming dashboard window that confirms the application version and active theme.
- Provide a site blocking capability that persists domains, keeps the Windows hosts file synchronized, and offers in-app controls to add/remove blocked domains.
- Offer a focus timer tab where users set a minute-based goal, run a countdown, and automatically log successfully completed (non-aborted) sessions.
- When administrative privileges are missing, the GUI informs the user that site blocking is temporarily disabled.
- Load configuration values from disk and initialize the backing SQLite database automatically.

## Configuration
- `.env` holds environment-specific secrets such as `DATABASE_URL`.
- `settings.yaml` stores general metadata (app name, UI theme, database path).
- The Config class exposes typed accessors ensuring downstream code remains decoupled from parsing logic.

## Future Enhancements
1. Enhance the site blocking UI with scheduling and bulk import/export controls.
2. Persist productivity metrics in SQLite and visualize trends within the GUI.
3. Add task import/export integrations with the broader SBAAS ecosystem.
4. Offer user preferences (e.g., theme toggle, notifications) saved per profile.
5. Extend the focus timer with session history charts, streak tracking, and configurable alerts.
