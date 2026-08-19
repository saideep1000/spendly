# Spec: Profile Page Design

## Overview
Login (Step 3) already redirects a signed-in user to `/profile`, but that
route is still a placeholder string ("Profile page — coming in Step 4"). This
step replaces it with a real, logged-in-only account page that shows the
signed-in user's name, email, and membership date, pulled from the `users`
table rather than just the session. It also adds a way to actually reach the
page from the nav. It is a read-only account page — no editing of profile
fields and no expense listing/dashboard here; those are separate, later
steps.

## Depends on
- Step 1 — Database setup (`01-database-setup.md`): `users` table (`name`,
  `email`, `created_at`).
- Step 3 — Login and Logout (`03-login-and-logout.md`): `session["user_id"]`
  is set on login and is what gates and identifies this page; the
  conditional nav (`{% if session.get('user_id') %}`) added in
  `templates/base.html` is extended here rather than replaced.

## Routes
- `GET /profile` — show the signed-in user's name, email, and "member
  since" date; redirect to `/login` if no `user_id` is in the session —
  logged-in

## Database changes
No schema changes. `users` already has every column this page needs
(`name`, `email`, `created_at`). Verified against `database/db.py` — one new
read-only helper function is added (see below), no new tables, columns, or
constraints.

## Templates
- **Create:** `templates/profile.html` — extends `base.html`; a single card
  showing the user's name, email, and a formatted "Member since <date>"
  line. No form, no editable fields, no password shown anywhere.
- **Modify:** `templates/base.html` — inside the existing
  `{% if session.get('user_id') %}` nav branch (added in Step 3), add a
  `Profile` link (`{{ url_for('profile') }}`) alongside the existing
  `Logout` link so the page is actually reachable after login. The
  logged-out branch (`Sign in` / `Get started`) is untouched.

## Files to change
- `app.py`:
  - Import `datetime` (standard library) for formatting `created_at`.
  - Import the new `get_user_by_id` helper from `database.db`.
  - Replace the `/profile` placeholder: if `session.get("user_id")` is
    missing, `redirect(url_for("login"))`; otherwise look up the user with
    `get_user_by_id(session["user_id"])`, format `created_at` into a
    human-readable date (e.g. "August 18, 2026"), and
    `render_template("profile.html", ...)` with the user's name, email, and
    formatted join date.
- `database/db.py` — add `get_user_by_id(user_id)`: parameterized
  `SELECT * FROM users WHERE id = ?`, returns the row or `None`, following
  the same connect/fetch/close pattern as `get_user_by_email`.
- `templates/base.html` — add the `Profile` nav link described above.

## Files to create
- `templates/profile.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — use `sqlite3` directly via `get_db()`.
- Parameterised queries only — `get_user_by_id` must use a `?` placeholder,
  never string-formatted SQL.
- Never render `password_hash` or any password value in `profile.html` or
  anywhere else.
- Use CSS variables from `static/css/style.css` (e.g. `var(--paper-card)`,
  `var(--ink)`, `var(--radius-md)`) for any new styling — never hardcode
  hex values.
- `templates/profile.html` must `{% extends "base.html" %}` like every
  other page.
- `/profile` must redirect unauthenticated visitors to `/login` rather than
  showing an error or exposing any account data.

## Definition of done
- [ ] Visiting `/profile` directly while logged out redirects to `/login`.
- [ ] Logging in (e.g. with the seeded `demo@spendly.com` / `demo123`
      account) and being redirected to `/profile` shows "Demo User",
      `demo@spendly.com`, and a formatted member-since date — not raw
      session data, but a fresh lookup from the `users` table.
- [ ] The nav shows both `Profile` and `Logout` links while logged in, and
      neither while logged out (still just `Sign in` / `Get started`).
- [ ] Clicking the `Profile` nav link from any page navigates to `/profile`.
- [ ] The rendered page HTML never contains the word `password` or any
      hash-looking string.
- [ ] `templates/profile.html` renders within the shared nav/footer layout
      (i.e. extends `base.html`) exactly like other pages.
- [ ] The app starts and runs with no errors (`python app.py`).
