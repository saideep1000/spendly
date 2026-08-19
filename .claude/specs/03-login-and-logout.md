# Spec: Login and Logout

## Overview
This feature lets a registered user actually sign in and out of Spendly. Step 2
(Registration) already lets someone create an account with a hashed password,
but `/login` is still GET-only and `/logout` is a placeholder string
("Logout — coming in Step 3"). This step wires `/login` to verify credentials
against the `users` table and start a Flask session, wires `/logout` to end
that session, and updates the site nav so it reflects whether a visitor is
signed in. It does not build a dashboard or gate any pages behind login —
that begins in Step 4 (Profile).

## Depends on
- Step 1 — Database setup (`01-database-setup.md`): `get_db()`, `users` table.
- Step 2 — Registration (`02-registration.md`): accounts must already exist
  to log into; reuses `get_user_by_email(email)` from `database/db.py`.

## Routes
- `GET /login` — display the login form (already exists, unchanged) — public
- `POST /login` — verify email/password, start a session, redirect on
  success — public
- `GET /logout` — clear the session and redirect to the landing page —
  public (safe to hit whether or not a session exists)

`/login` is served from the same view function using
`methods=["GET", "POST"]`, matching the `/register` pattern from Step 2.

## Database changes
No database changes. `get_user_by_email(email)` (added in Step 2) already
returns the full row including `password_hash`, which is everything login
needs. Verified against `database/db.py` — no new tables, columns, or
constraints required.

## Templates
- **Create:** none
- **Modify:**
  - `templates/login.html` — add a sticky `value="{{ email or '' }}"` on the
    email input, same pattern as `templates/register.html` from Step 2 (the
    password field is never echoed back).
  - `templates/base.html` — make the nav conditional on login state: when
    `session.get('user_id')` is set, show a single `Logout` link
    (`{{ url_for('logout') }}`) in place of the current "Sign in" /
    "Get started" links; when not logged in, keep the nav exactly as it is
    today.

## Files to change
- `app.py`:
  - Set `app.secret_key` (required for Flask sessions to sign the cookie).
  - Import `check_password_hash` from `werkzeug.security` and `session`
    from `flask`.
  - Change the `/login` route to `methods=["GET", "POST"]`. On `POST`:
    read and normalize `email` (trim + lowercase, same as Step 2) and read
    `password` (unmodified); look up the user with `get_user_by_email`;
    verify the password with `check_password_hash`; on success store
    `session["user_id"]` (and optionally `session["user_name"]`) and
    redirect to `/profile`; on failure re-render `login.html` with a single
    generic error and the sticky email (never reveal whether the email or
    the password was wrong).
  - Change the `/logout` route: clear the session (`session.clear()`) and
    redirect to `/` instead of returning the placeholder string.
- `templates/base.html` — conditional nav block described above.
- `templates/login.html` — sticky email value.

## Files to create
None.

## New dependencies
No new dependencies — Flask's built-in `session` (signed cookies) and
`werkzeug.security.check_password_hash` (already installed alongside
`generate_password_hash`) cover everything needed.

## Rules for implementation
- No SQLAlchemy or ORMs — use `sqlite3` directly via `get_db()`.
- Parameterised queries only — reuse `get_user_by_email`, do not write a new
  raw query for this.
- Passwords verified with `werkzeug.security.check_password_hash` — never
  compare plaintext passwords, and never store or log a submitted password.
- Show one generic error message ("Invalid email or password.") for both a
  nonexistent email and a wrong password — do not let a user probe which
  emails are registered.
- Use CSS variables from `static/css/style.css` — never hardcode hex values
  — if any new styling is needed for the nav's logged-in state.
- `templates/login.html` and `templates/base.html` continue to extend/serve
  as the base template correctly; no template stops extending `base.html`.
- `/logout` must not error when hit with no active session — clearing an
  empty session is a no-op.

## Definition of done
- [ ] Logging in with the seeded demo account (`demo@spendly.com` /
      `demo123`) succeeds and redirects to `/profile`.
- [ ] After a successful login, the nav on any page shows `Logout` instead
      of `Sign in` / `Get started`.
- [ ] Logging in with a correct email but wrong password re-renders
      `login.html` with the generic "Invalid email or password." error and
      does not start a session.
- [ ] Logging in with an email that has no account shows the same generic
      error message (not a different one) and does not start a session.
- [ ] On a failed login attempt, the previously entered email is still
      shown in the form field.
- [ ] Visiting `/logout` while logged in clears the session and redirects
      to `/`; the nav on the next page load shows `Sign in` / `Get started`
      again.
- [ ] Visiting `/logout` while not logged in does not error — it redirects
      to `/` the same way.
- [ ] `GET /login` still renders the empty form exactly as before when
      there is no error.
- [ ] The app starts and runs with no errors (`python app.py`).
