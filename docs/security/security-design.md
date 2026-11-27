# FairShare security design

Status: draft v0.1, 16 November 2026.
Written from the security requirements discussed for the project. Items marked **Proposed** are not decided yet and will change as they are agreed. Items marked **In place** exist in the code today. Everything else is **Planned**.

## 1. Purpose and scope

This document says how FairShare is meant to stay secure, and why. It covers the Django backend, the MySQL database, the Next.js frontend (including the public demo), the build pipeline and the hosting.

It is written openly on purpose (principle 7). Security must not depend on anyone not knowing how the system works.

FairShare only records who owes what. It never holds or moves money.

## 2. Principles

1. **Defence in depth.** Every important risk has at least two independent controls, so one failure does not open the door.
2. **Fail safe.** When something breaks (a permission check, the rate-limit store, the database), the system denies the request and shows a generic error. It never fails open.
3. **Least privilege.** Every person, role, service and database user gets only what it needs.
4. **No privilege creep.** Access is granted for a reason, for a limited time, and is reviewed. Roles are not accumulated.
5. **Separation of duties.** For vital actions, one person cannot both do and approve the same thing. There is no single point of control.
6. **Secure by design and by default.** Security is part of each feature's design and its definition of done, and the default setting is the safe one.
7. **Open design (Kerckhoffs's principle).** Nothing relies on keeping the design secret. Only keys, passwords and tokens are secret. Renaming a cookie or moving a URL may reduce noise, but it is never counted as a control.
8. **Keep it simple (KISS).** Security should be hard for attackers and easy for legitimate users and admins. A control that people work around has failed.
9. **CIA triad.** Confidentiality, integrity and availability each have explicit controls (section 9).
10. **Data minimisation.** Collect, keep and expose only what is needed. Remove unused services, data, default accounts and sample content.

**Complexity check.** Before adding a control, answer four questions:

1. What specific attack does it stop?
2. Who does it slow down, and by how much?
3. Is there a simpler control that does the same job?
4. If it fails or someone is locked out, can a legitimate user or admin recover?

A control that fails the check is simplified or dropped. Prefer standard, widely used tools over custom code, and never write custom cryptography. Complexity is itself a vulnerability: more code means more bugs, and awkward controls get worked around.

## 3. What is protected, and from whom

Assets: user accounts (email, display name, password hash), group and expense data, comment text, the audit log, secrets, and the availability of the service itself.

Actors considered:

- anonymous visitors and bots
- registered users
- group managers trying to act outside their group
- an admin misusing their access (insider)
- a stolen admin account
- developer mistakes, including bad or compromised dependencies

## 4. Threats and layered controls

| Threat | Layers (each works even if the others fail) |
|---|---|
| SQL injection | 1) Django ORM only, no raw SQL (enforced by lint rule and review). 2) Strict input validation in serializers. 3) The app's database user cannot alter or drop tables and has no file or admin rights. 4) CodeQL scanning in CI. |
| Account enumeration | 1) Same response and wording for sign-up, login and password reset whether or not the account exists. 2) Equal work when the account does not exist, so timing does not leak it. 3) Rate limits per IP and per target account. 4) No endpoint that reports whether an email is taken. |
| Session hijacking | 1) Server-side sessions that can be revoked. 2) Cookies are HttpOnly, Secure and SameSite, with a `__Host-` name. 3) New session on login and on any privilege change. 4) Idle and absolute timeouts. 5) HTTPS only with HSTS. 6) A strict CSP so XSS cannot reach session data. |
| Cross-site scripting (XSS) | 1) React escapes output by default and `dangerouslySetInnerHTML` is banned by lint. 2) Strict Content Security Policy. 3) Comments are plain text only. 4) HttpOnly cookies cannot be read by scripts. 5) `X-Content-Type-Options: nosniff` and correct content types. |
| Cross-site request forgery (CSRF) | 1) SameSite cookies. 2) Django CSRF tokens on every state-changing request. 3) Same-origin API proxy and an exact origin allowlist (no wildcard CORS). |
| Clickjacking | 1) `frame-ancestors 'none'` in the CSP. 2) `X-Frame-Options: DENY` for older browsers. 3) Set in both Django and Next.js. |
| Denial of service | 1) Platform DDoS protection at the host. 2) An edge rate-limit rule. 3) Per-user and per-IP throttles in Django on every endpoint. 4) Request size and time limits, capped page sizes, input limits. 5) Instance caps. 6) Backups and a tested restore. A free tier cannot beat a determined flood. The goal is to degrade gracefully, never leak data and never fail open. |
| Broken access control (IDOR, BOLA, BFLA) | 1) Deny by default on every endpoint. 2) Every query is scoped to what the caller may see. 3) Random public IDs. 4) Generated tests for every endpoint against every role. |
| Mass assignment | Explicit field allow-lists in serializers. Nothing is accepted that was not listed. |
| SSRF | The server never makes outbound requests from user-supplied input. If that ever changes, it needs an allow-list and a review. |
| Supply chain | 1) Exact, hashed dependency versions. 2) Dependabot. 3) `pip-audit` and `npm audit` in CI. 4) CI actions pinned to commit hashes. 5) Few dependencies. 6) Secret scanning. |
| Weak logging | 1) Append-only audit log. 2) Alerts on bursts of failures and on role changes. 3) No secrets or full personal data in logs. |
| Mishandled errors | 1) Fail closed. 2) Generic errors with a reference number, never stack traces (DEBUG off). 3) Timeouts on every external call. |
| Cryptographic failure | 1) TLS only. 2) Argon2id for passwords. 3) Tokens from `secrets`, stored hashed where possible, single use and short lived. 4) No custom cryptography. |
| Data integrity | 1) Server-side calculation is the authority (the browser copy is for display). 2) Database constraints and transactions. 3) Append-only history for expenses and payments. 4) Optimistic locking so concurrent edits do not overwrite each other. |

## 5. OWASP Top 10 mapping

2025 edition. Two categories are new in 2025 (A03 and A10), and SSRF is now part of A01. The 2021 names are given where they differ.

| ID | Category | Where it is handled | Status |
|---|---|---|---|
| A01 | Broken Access Control (includes SSRF) | Sections 4 and 6; deny by default; authorization test matrix | Planned |
| A02 | Security Misconfiguration (2021: A05) | Production settings, security headers, production container, no default accounts | Partly in place (DEBUG off by default, secrets from environment) |
| A03 | Software Supply Chain Failures (2021: A06) | Dependency policy in section 11 | Partly in place (audits in CI) |
| A04 | Cryptographic Failures (2021: A02) | Section 8 | Planned |
| A05 | Injection (2021: A03) | ORM only, validation, least-privilege database user | Planned |
| A06 | Insecure Design (2021: A04) | This document, threat model per feature | In progress |
| A07 | Authentication Failures (2021: A07) | Section 8 | Planned |
| A08 | Software or Data Integrity Failures | Pinned dependencies and actions, append-only history, branch protection | Partly in place (branch protection, required checks) |
| A09 | Logging and Alerting Failures | Section 10 | Planned |
| A10 | Mishandling of Exceptional Conditions | Fail-safe principle, generic errors, timeouts | Planned |

## 6. Roles and access

### 6.1 Group roles (scoped to one group)

| Role | Can | Cannot |
|---|---|---|
| Member | See the group's expenses they are part of, mark their own share paid, comment | Invite anyone, change other people's amounts |
| Manager (given by the owner) | Invite and remove members, add people to an expense | Delete the group, change the owner |
| Owner | Everything a manager can, plus delete or archive the group and appoint managers | Act on any other group |

Group roles end when the group ends or the person leaves.

### 6.2 Admin accounts

Agreed:

- **The first admin is the superuser** (the project owner). It is created from the server command line and never through the website. There are no default credentials, and MFA is set up at the first sign-in.
- **While there is only one admin, that admin needs no approval for any action.** Every action is still logged, and dangerous actions ask for a fresh MFA check (a step-up check, see section 8).
- **Admins are a separate kind of account.** A normal user can never be made an admin, and an admin can never become a normal user. A new admin is a new account with its own email, invited by an existing admin.
- **More admins can be added later.** That is a later feature.
- **There is never zero admins.** It is possible to go back down to one admin (by removing an admin, see section 7), but the last remaining admin cannot be removed, disabled or expired.
- **Admin account details can be changed**, but only by the owner of that account and only after a fresh MFA check. Changing the email also needs confirmation from the new address and a notice to the old one. No admin can edit another admin's details. They can only freeze the account or request its removal.

Proposed additions:

- **Once there are two or more admins, nobody is exempt from approvals,** including the first admin. Nobody is a single point of control.
- **Admin accounts do not join groups or expenses.** They are for running the system, not for using it.
- **Least privilege between admins.** Each admin account gets a permission set when it is created. At first there is only "full", because there is one admin. Narrower sets (for example support only) can be added when more admins exist.
- **Stricter sessions for admins:** a short idle timeout, and a step-up check before any critical action.
- **Expiry and inactivity:** admins added later get grants that expire and are renewed on purpose, and they are disabled after a period of no use. This never applies to the last remaining admin.
- **Metadata only by default.** Admins see counts, reports and timestamps. Reading someone's comments happens only through a report and is logged. There is no impersonation of users.
- **Hosting accounts count too.** The approval rules protect the application. Whoever controls GitHub, the host or the database controls everything, so those accounts need MFA, and every admin removal includes removing their access there too.

## 7. Separation of duties and approvals

### 7.1 Two kinds of action

| Kind | Examples | Who acts |
|---|---|---|
| Routine | Suspend a user temporarily, resolve a report, read a reported comment | One admin. Logged. |
| Critical | Delete a user account, change platform limits or security settings, restore from a backup, create an admin, remove an admin, change an admin's permissions | Requested by one admin and approved by one other admin |

Rules that always hold when approval is needed:

- The approver is never the requester.
- For an action about another admin, the approver is never the person it is about, unless they are the only other admin (see 7.2).

### 7.2 What changes with the number of admins

| Admins | Critical actions | Removing an admin |
|---|---|---|
| 1 | No approval needed. Fresh MFA check. Logged. | Not possible: the last admin cannot be removed |
| 2 | The other admin approves | An admin who leaves: the other admin approves. One admin removing the other: the other is the only possible approver, so they must agree. If they cannot or will not (lost access, or compromised), use the recovery path in 7.5. |
| 3 or more | Any one other admin approves | Leaving or being removed is the same action: one admin requests it and one other admin (not the person being removed) approves |

Removing an admin is how the system goes back from many admins to one. The final step down to one admin is allowed, and going below one is not.

### 7.3 Rules for every approval

1. Nobody can approve their own request.
2. An approval is tied to one exact request (it includes a hash of what will happen), is single use, and expires.
3. The approver sees exactly what they are approving and confirms with MFA (a signed confirmation).
4. Every request, approval, cancellation and execution is written to the audit log, and all admins are notified.
5. **Safe direction is easy, dangerous direction is guarded.** Any admin can immediately freeze another admin's sessions or cancel a pending request. Unfreezing, approving and removing need the normal approvals.
6. **Audit or refuse.** If the audit log cannot be written, the critical action does not happen.
7. The audit log is append-only. The application's database user can add entries but cannot change or delete them, and no admin screen can turn logging or alerts off. Only a reviewed code change can.

### 7.4 Failsafes for changes that could break the system

- Every setting has a minimum and a maximum that is checked on save (for example, a rate limit cannot be set to unlimited).
- Settings are versioned, with one step to return to the last known good version.
- Risky features sit behind a switch that can turn them off without a new deployment.
- A backup is taken before any destructive operation.
- Failure paths are tested, not just the working paths.

### 7.5 Recovery (Proposed)

Used when an admin is locked out (lost MFA devices), or when two admins cannot agree on a removal because the other is unreachable or compromised.

- The owner (the first admin) holds offline recovery codes, printed and kept somewhere safe, never stored on a computer.
- Using one starts a 72-hour delay, alerts every admin, and is logged. After the delay, the requested recovery (an MFA reset or the removal) takes effect.
- A stolen recovery code is full control, so they are guarded like a house key.

Open question: in a stuck two-admin removal, the owner's recovery codes decide. That makes the owner the root of trust, which is a deliberate trade-off. Someone has to be able to break a deadlock.

Honest limit: real separation of duties needs more than one person. The mechanism is built and tested, and until there is a second human, a second account stands in for them.

## 8. Authentication and sessions

Proposed unless stated otherwise.

- **Server-side sessions in HttpOnly cookies** through the same-origin proxy, not tokens stored in the browser. Sessions can be revoked, and users can see and end their own sessions.
- **Login is email plus password.** Display names are not unique and are shown only inside groups, so there are no usernames to enumerate.
- **Passwords:** minimum 12 characters, no complexity rules, a local blocklist of common passwords, Argon2id hashing. No external breach-check service (an extra dependency we do not strictly need).
- **MFA:** required for admin accounts, optional for users, with recovery codes.
- **Throttling:** progressive delays per account and per IP, not hard lockouts, because lockouts let an attacker lock real users out.
- **Email verification and password reset:** single-use, short-lived tokens stored hashed. The response never says whether an account exists.
- **Step-up checks.** Being signed in is not enough for dangerous actions (changing email or password, deleting an account, any critical admin action). The app asks you to prove it is you again, with the password or an MFA code, and that proof only counts for a few minutes. It protects against a session that was left open or stolen.

## 9. The CIA triad

- **Confidentiality:** access control by default, TLS everywhere, minimal data, no personal data in logs, admins see metadata not content.
- **Integrity:** the server recalculates every amount, database constraints, append-only history, reversals add records instead of deleting them, signed and verified dependencies.
- **Availability:** rate limits and caps, graceful failure, backups with a tested restore, a static demo that needs no backend.

## 10. Logging, monitoring and incident response

- **Logged (Planned):** sign-ins and failures, password and email changes, session revocations, role grants and removals, admin actions, rate-limit hits, permission denials.
- **Never logged:** passwords, tokens, session IDs, full request bodies.
- **Alerts:** many failed logins for one account or from one IP, any role change, any use of the break-glass role.
- **If something goes wrong:** contain (revoke sessions and tokens, suspend the affected accounts), preserve the audit log, tell affected users, and report to the ICO within 72 hours where the law requires it.
- **Disclosure:** a `SECURITY.md` and `security.txt` with a contact and what to expect.

## 11. Secure development process

Every feature's "definition of done" includes a security check:

- [ ] A short threat note: what could go wrong and who might do it
- [ ] Deny by default, and explicit permissions in code
- [ ] Input validated with an allow-list of fields
- [ ] Throttling on every new endpoint
- [ ] Audit log entries for sensitive actions
- [ ] Tests for the allowed and the denied cases, for each role
- [ ] No new dependency unless it is needed

Pipeline and supply chain:

- **In place:** pull requests only, required status checks, minimal CI permissions, `pip-audit` and `npm audit` (production dependencies) in CI, secrets kept in a git-ignored `.env`.
- **Planned:** exact hashed dependency versions, Dependabot, CodeQL, secret scanning, actions pinned to commit hashes, a separate production container (multi-stage, non-root, no dev tools), separate database users for the running app and for migrations, separate development and production secrets with a rotation procedure.

### 11.1 Repository and hosting accounts (the root of trust)

Whoever owns the GitHub repository and the hosting accounts can change the code, the secrets and the data. That power sits outside the application's admin rules, and today it belongs to one person, who is also the first admin. So these accounts need their own protection. The controls are designed now and switched on at production (see 11.2).

| Control | Why | When |
|---|---|---|
| Two hardware security keys (one in daily use, one stored offline) for GitHub, hosting, database and email accounts | Stops account takeover even if a password leaks | Production |
| Two credentials, one account: daily Git work uses an SSH key (or a narrow token) that can push code but cannot change settings. Settings and production approvals need a web sign-in with the hardware key | A credential stolen from the everyday computer cannot change repository settings or approve deployments. GitHub's terms allow one free personal account per person, so this is done with credentials, not a second account | Production |
| Offline recovery material: recovery codes for GitHub and the hosts, plus the app's own recovery codes, printed and kept somewhere safe, never on a computer | Recovery without creating a way in for attackers | Production |
| Repository rules: pull request required, required checks, force pushes blocked, no bypass list | Already in place | In place |
| Repository rules: signed commits and at least one approval (needs a second person) | Commits can be traced to a person, and nothing merges unreviewed | Production |
| Protected production environment: a deployment waits for a manual approval, signed in with the hardware key | A deliberate pause before anything reaches users. With one person this guards against mistakes and stolen tokens, not against the owner | Production |
| Environment-scoped secrets, short-lived and narrowly scoped tokens, separate development and production secrets, a rotation routine | A leaked key opens as little as possible | Production |
| Secret scanning with push protection, CodeQL, Dependabot | Cheap, free for a public repository, and in nobody's way | Now |
| Separate database users for the running app and for migrations, the database not open to the internet, backups kept in a separate place with a tested restore | Limits damage from a bug or a stolen app credential | Production |
| Alerts for repository setting changes, new tokens or deploy keys, and production deployments | Changes to the root of trust do not go unnoticed | Production |

Honest limit: these controls protect against stolen accounts, mistakes and malware on a daily-use machine, and they leave an audit trail. They cannot stop the person who holds the owner account from acting badly. That needs a second human.

### 11.2 The production gate

- Every control above has three states: designed, built, enabled. A checklist of GitHub issues labelled `production-gate` tracks them.
- Controls inside the application are **on by default**. They are switched off only in the development settings file, and the production settings refuse to start (fail closed) if a required control is off. That way a control can be absent while developing, but it cannot be off by accident in production.
- Going live is blocked until every item is enabled and a restore test has passed.

### 11.3 Build order

Everything in this document is designed now, but it is built and switched on in stages, so the system stays simple while it is being developed.

| Stage | What | Why then |
|---|---|---|
| Now | Secret scanning with push protection, CodeQL, Dependabot, exact dependency versions, production Django settings, REST deny-by-default and default throttles, security headers | Cheap, free, and in nobody's way |
| With accounts (v1) | Server-side sessions, CSRF, Argon2id, sign-up and login that do not reveal whether an account exists, throttling on every endpoint, authorization tests, a simple append-only audit log, email verification, password reset, MFA for the admin, the first admin created from the command line | These are the basics every account system needs |
| At go-live (production gate) | Hardware keys, SSH key for daily Git, protected production environment, signed commits, separate database users, backups with a tested restore, alerts, recovery codes, the production container | These matter when real people use it, and get in the way of development |
| Later, only when there are two or more admins | Approval workflow, expiring grants, inactivity rules, freeze and cancel, per-admin permission sets, access review page | They do nothing while there is one admin |
| Not planned unless a real need appears | A hash-chained audit log, signed approvals with hardware-key signatures, IP allow-lists for admins | The simpler control above does most of the job |

## 12. Data and privacy

- Collected: email, display name, password hash, and what users enter (groups, expenses, comments).
- Exposed identifiers are random UUIDs, not sequential numbers. This is a backup to proper access checks, not a replacement.
- Users can delete their account. Shared records keep their amounts but show "Deleted user".
- Remove unused: starter assets, unused framework apps, default accounts, sample data.

## 13. Known limits

- A free hosting tier cannot withstand a large, determined DDoS attack.
- A single operator cannot provide true separation of duties. The repository owner, the hosting owner and the first admin are currently the same person.
- No independent penetration test has been done.
- The public demo is client-side only, so it has no server attack surface, but it is still served by the hosting platform.

## 14. Status snapshot (16 November 2026)

In place today:

- CSRF and clickjacking middleware are enabled in Django.
- `DEBUG` defaults to off and the secret key must come from the environment (the app will not start without it).
- `.env` is ignored by Git.
- Branch protection with required checks on `main`; CI runs with read-only permissions.
- Dependency audits for production packages in CI.
- The demo page makes no network calls and uses no cookies, storage or raw HTML (checked 16 November).

Not yet in place (found during review):

- Production settings: HTTPS redirect, HSTS, secure cookie flags, hosts from the environment
- REST framework is not configured, so its defaults are permissive
- Argon2id and the 12-character password minimum
- Security headers and a CSP on the frontend; the default `X-Powered-By` header is on
- Backend container runs as root with development tools and the dev server
- Dependencies are version ranges, not exact pins (two machines already installed different Django patch versions)
- Django admin is on at the default path with no MFA
- No rate limiting, audit log or alerting yet

## 15. Decisions to confirm

| # | Decision | Status |
|---|---|---|
| 1 | Server-side sessions in HttpOnly cookies (not browser-stored tokens) | Proposed |
| 2 | Login by email; display names are not unique | Proposed |
| 3 | MFA required for admin accounts, optional for users | Proposed |
| 4 | Small custom admin area; Django admin off in production | Proposed |
| 5 | First admin is the superuser; admins are separate accounts; a normal user can never become an admin; approvals as in section 7 | Agreed in principle, details Proposed |
| 6 | 12-character passwords, local blocklist, no external breach service | Proposed |
| 7 | Progressive delays instead of hard lockouts | Proposed |
| 8 | Admins see metadata only; content only via reports; no impersonation | Proposed |
| 9 | Random UUIDs for exposed identifiers | Proposed |
| 10 | No approval for the sole admin; with two or more admins, critical actions are requested by one and approved by one other | Agreed |
| 11 | Any admin can freeze another admin's sessions or cancel a pending request at once | Proposed |
| 12 | Offline recovery codes held by the owner (lost MFA, or a stuck two-admin removal), with a 72-hour delay and alerts | Proposed |
| 13 | Expiry and inactivity rules apply only to admins added later, never to the last admin | Proposed |
| 14 | Admin account details change only by the account's own admin, after a fresh MFA check | Agreed |
| 15 | Repository and hosting controls are designed now and switched on at go-live through a production gate | Proposed |
| 16 | Application security controls are on by default, off only in development settings, and production refuses to start if one is off | Proposed |
| 17 | While there is one admin, use Django's built-in admin, hardened (admin accounts only, MFA), and build the custom admin area when the multi-admin features are needed. This revises decision 4 to avoid extra custom code early | Proposed |

## 16. Review

Review this document when a feature changes who can do what, when a new dependency or service is added, and after any security incident.
