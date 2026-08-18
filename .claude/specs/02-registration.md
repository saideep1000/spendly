# Spec: Registration

## Overview
This feature lets a new visitor create a Spendly account by submitting the
existing registration form. It is the first user-facing feature of the app:
until now `/register` only rendered a static template with no backend
handling. This step wires that form to the `users` table built in Step 1,
validates input, prevents duplicate emails, hashes the password, and creates
a real account a person can later sign in with (Step 3).

## Depends on
- Step 1 — Database setup (`01-database-setup.md`): requires `get_db()`,
  `init_db()`, and the `users` table (id, name, email, password_hash,
  created_at) to already exist.

## Routes
- `GET /register` — display the registration form (already exists in
  `app.py`; kept as-is for the empty-form case) — public
- `POST /register` — validate submitted name/email/password, create the
  user, and redirect on success — public

Both are served from the same `/register` view function using
`methods=["GET", "POST"]`.

## Database changes
No database changes. The `users` table from Step 1 already has every column
this feature needs (`name`, `email`, `password_hash`). Verified against
`database/db.py:21-32` — no new tables, columns, or constraints required.

## Templates
- **Create:** none
- **Modify:** `templates/register.html` — re-render submitted `name` and
  `email` values back into the inputs (`value="{{ name or '' }}"`, etc.)
  after a failed submission so the user doesn't retype everything; the
  existing `{% if error %}` block already renders validation/duplicate-email
  errors, no structural change needed there.

## Files to change
- `app.py` — change the `/register` route to accept `GET` and `POST`;
  on `POST`, validate input, call the new `database/db.py` helpers, and
  either re-render `register.html` with an `error` (and the submitted
  `name`/`email`) or redirect to `/login` on success.
- `database/db.py` — add:
  - `get_user_by_email(email)` — returns the matching row or `None`,
    using a parameterized `SELECT`.
  - `create_user(name, email, password)` — hashes `password` with
    `werkzeug.security.generate_password_hash` and inserts the row with a
    parameterized `INSERT`; returns the new user id.
- `templates/register.html` — add sticky `value` attributes to the `name`
  and `email` inputs.

## Files to create
None.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — use `sqlite3` directly via `get_db()`.
- Parameterised queries only — never format SQL strings.
- Passwords hashed with `werkzeug.security.generate_password_hash` before
  storage; never store or log plaintext passwords.
- Server-side validation is required even though the form has HTML5
  `required` attributes: reject empty/whitespace-only name, malformed
  email, and passwords under 8 characters.
- Reject registration with an email that already exists
  (`get_user_by_email`) with a clear `error` message — do not let the
  `UNIQUE` constraint raise an uncaught `IntegrityError`.
- Use CSS variables from `static/css/style.css` (e.g. `var(--danger)`) —
  never hardcode hex values — if any new styling is needed.
- `templates/register.html` must keep extending `base.html`.
- On successful registration, redirect (`302`) to `/login` — this step does
  not introduce sessions/login state; that is Step 3.

## Definition of done
- [ ] Submitting the register form with valid name, email, and an 8+
      character password creates a row in `users` with a hashed
      `password_hash` (never the plaintext password).
- [ ] After a successful registration, the browser is redirected to
      `/login`.
- [ ] Submitting with an email that already exists in `users` re-renders
      `register.html` with a visible error and does not create a duplicate
      row.
- [ ] Submitting with an empty name, empty/invalid email, or a password
      under 8 characters re-renders `register.html` with a visible error
      and does not create a row.
- [ ] On a failed submission, the previously entered name and email are
      still shown in the form fields.
- [ ] `GET /register` still renders the empty form exactly as before.
- [ ] The app starts and runs with no errors (`python app.py`).
- [ ] All new/changed queries in `database/db.py` use parameterized SQL
      (no string formatting into SQL).
