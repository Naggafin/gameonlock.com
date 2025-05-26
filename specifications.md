[TOC]

- [Glossary](#glossary)
- [Feature Set](#2-feature-set)
- [Technical Stack](#3-technical-stack)
- [UI/UX](#4-uiux)
- [Background Jobs](#5-background-jobs)
- [Deployment](#6-deployment)
- [Non-Functional Requirements](#7-non-functional-requirements)
- [MVP Checklist](#8-mvp-checklist)
- [Stretch Goals](#9-stretch-goals)
- [Implementation Status, Testing & CI/CD](#10-implementation-status-testing--cicd)
- [API Endpoints & Data Flow](#11-api-endpoints--data-flow)
- [Dependencies](#12-dependencies)
- [Documentation](#15-documentation)
- [Security](#16-security)
- [MVP Clarifications](#17-mvp-clarifications)
- [Known Issues / Technical Debt](#13-known-issues--technical-debt)
- [Directory Structure Overview](#14-directory-structure-overview)
- [Changelog / Tracking Major Changes](#15-changelog--tracking-major-changes)

# Game On Lock - Specification Document


---

## Glossary

- **Play:** A user's bet slip, consisting of multiple picks (minimum 4).
- **BettingLine:** The odds and conditions for a specific game (spread, over/under).
- **Pick:** A user's selection on a specific betting line (e.g., Team A to cover the spread).
- **Ticket:** Uploaded or generated spreadsheet of betting lines for admin management.
- **GoverningBody:** Organization overseeing a sport or league (e.g., NCAA, NFL).
- **ScheduledGame:** A game scheduled between two teams, with associated betting lines.
- **Celery Task:** Background job for data sync, score processing, etc.
- **Admin Tool:** Any feature or view restricted to admin users (e.g., ticket upload).

---

## 1. Project Overview

**Name:** Game On Lock
**Type:** Real-money sports betting platform
**Stack:** Django (5.x), Wagtail, Bootstrap 5.3, AlpineJS, HTMX, Celery

**Purpose:**
Enable users to place real-money sports bets through an intuitive, mobile-first web interface. Plays (bet slips) consist of at least 4 bets. Users win only if all picks are correct. Admins define betting lines via upload/download of spreadsheets, fed by external betting data APIs.

**Target Audience:**
Users interested in online sports betting across various American sports leagues.

**Authentication:**
Required for play submission. Unauthenticated users can preview picks which are stored locally and resumed post-login.

**Monetization:**
Users pay immediately upon play submission (via PayPal). No user wallet/balance system initially.

**Legal:**
No legal/regulatory compliance currently required.

---

## 2. Feature Set

### User Features

* Select betting lines (spreads, over/under)
* Submit plays (min. 4 bets required)
* Pay via PayPal on submission
* View account dashboard (betting history, payouts)
* Preview bet slips (saved to `localStorage`)

### Admin Features

* Upload/download spreadsheets of betting lines
* Auto-import betting lines via API into spreadsheet
* Create/manage sports data (sports, teams, etc.)
* Admin interface for reviewing payout results

### Core Functionality

* Betting lines (spread, over/under)
* Game/score data synced from APIs
* Celery task to process final scores, determine outcomes, notify admins

### CMS/Content

* Wagtail-powered blog
* Wagtail-managed SEO/content for home and other pages

---

## 3. Technical Stack

### Backend (from `requirements.txt`)

* **Framework:** Django 5.x, Wagtail
* **Auth:** django-allauth, django-guardian
* **Data:** django-money, psycopg\[c], Redis
* **Tasks:** Celery, django-celery-beat
* **Admin/Dev Tools:** django-debug-toolbar, django-fastdev, django-extensions, django-silk, nplusone
* **Other:** django-htmx, django-user-agents, django-csp, django-template-partials, sorl-thumbnail, djangorestframework

### Frontend

* **Frameworks:** Bootstrap 5.3, AlpineJS, HTMX
* **Style:** Custom PerediOn template (mobile-first)
* **Interaction:** AlpineJS + localStorage for slip state

### APIs (Data Sources)

* Vegas odds: [the-odds-api.com](https://api.the-odds-api.com/)
* Scores + Sports info:

  * [sportsdata.io](https://sportsdata.io/)
  * [thesportsdb.com](https://www.thesportsdb.com/)
  * [NCAA API](https://github.com/henrygd/ncaa-api)
  * [sportsreference](https://github.com/sportsreference/sportsreference)
  * [nba\_api](https://github.com/swar/nba_api)
  * [nflgame](https://github.com/BurntSushi/nflgame)
  * [pybaseball](https://github.com/jbruin/pybaseball)

---

## 4. UI/UX

### Pages

* Home Page
* Betting Page (interactive betting line selection)
* Account Dashboard (history, payouts)

### Design Goals

* Fully mobile-responsive
* Modern, clean look via PerediOn template
* Custom branding (logo, palette)
* Fast, fluid interactivity

---

## 5. Background Jobs

* **Score syncing:** Periodically check APIs for completed games
* **Outcome resolution:** Calculate play results, flag winners
* **Admin alerts:** Notify when payouts are due

---

## 6. Deployment

* **Platform:** Self-hosted VPS
* **Queue:** Celery + Redis
* **Database:** PostgreSQL

---

## 7. Non-Functional Requirements

* Mobile-first design
* Secure payments (PayPal)
* Proper Django production settings (SECURE\_\*, CSRF, CSP)
* SEO editable via Wagtail
* Performance observability via django-silk/debug-toolbar

---

## 8. MVP Checklist

* [ ] Define betting data model (games, lines, picks, plays)
* [ ] Build spreadsheet import/export tooling for admins
* [ ] Implement frontend betting interaction
* [ ] Hook up PayPal payment integration
* [ ] Create Celery tasks for score syncing
* [ ] Determine winner logic & payout alerts
* [ ] Style using PerediOn template
* [ ] Build user dashboard & history views
* [ ] Integrate Wagtail for blog + SEO pages

---

## 9. Stretch Goals

* Live game updates
* Leaderboards
* Betting insights/statistics
* Bonus system or referral rewards
* Persistent user wallet/balance (Phase 2)

---

> This specification will serve as the roadmap for development using GPT-4.1 assistance. Future iterations may be tracked in a changelog or using a project board (e.g., GitHub Projects, Trello, etc.).


---

## 10. Implementation Status, Testing & CI/CD

- **Backend:** Core models (Sport, GoverningBody, League, Team, ScheduledGame, BettingLine, Play, PlayPick) implemented and tested.
- **Admin:** Import/export (via django-import-export), ticket upload/generation, and model management in place and tested.
- **Celery:** Team data sync task implemented; further tasks (score syncing, payout logic) planned.
- **Security:** All betting and admin views protected by LoginRequiredMixin.
- **CI/CD:** GitHub Actions pipeline runs linting, formatting, and all tests on every push to `openhands` branch.
- **Payment:** django-paypal present but not yet fully implemented; MVP will clarify payment integration status.
- **CMS:** Wagtail is planned but not yet implemented in codebase.
- **Requirements:** requirements.txt is comprehensive but will be pruned regularly to remove unused packages.
- **Documentation:** README.md and setup/test instructions pending.

### Testing Matrix

| Feature/Module                | Tests Present | Edge Cases Covered | Notes                       |
|-------------------------------|:-------------:|:------------------:|-----------------------------|
| Admin ticket upload           |      ✔️       |         ✔️         |                             |
| GoverningBody import/export   |      ✔️       |         ✔️         |                             |
| Betting/admin view protection |      ✔️       |         ✔️         | LoginRequiredMixin enforced |
| Celery team data sync         |      ✔️       |         ❌         | More edge cases needed      |
| Payment (PayPal)              |      ❌       |         ❌         | Not yet implemented         |
| Wagtail CMS                   |      ❌       |         ❌         | Not yet implemented         |
| User dashboard                |      ❌       |         ❌         | Not yet implemented         |
| Frontend betting interaction  |      ❌       |         ❌         | Not yet implemented         |

- Automated tests are required for all features, including admin tools and edge cases.
- CI/CD must run linting, formatting, and all tests on every push to the `openhands` branch.
- Test coverage is a release requirement.

---

## 11. API Endpoints & Data Flow

- **API Endpoints:**
  - (Planned) `/api/betting-lines/` – List available betting lines
  - (Planned) `/api/plays/` – Submit a play (bet slip)
  - (Planned) `/api/results/` – Get results for completed games
- **Data Flow:**
  - Admin uploads ticket → System parses and creates ScheduledGames/BettingLines
  - User selects lines and submits play → Payment processed (PayPal, planned)
  - Celery tasks sync scores and resolve outcomes
  - Admin reviews payouts
- Update this section as endpoints and flows are implemented.

---

## 12. Dependencies

- All dependencies are listed in requirements.txt.
- requirements.txt must be pruned regularly to remove unused packages.
- Unused packages (e.g., django-oscar, if not used) should be removed from both requirements.txt and the specification.
- djangorestframework is required for API endpoint implementation and is now present in requirements.txt.
- Django Oscar is present in requirements.txt for future e-commerce/shop features, not for MVP or current development.

---

## 13. Known Issues / Technical Debt

- requirements.txt may include unused packages (e.g., django-oscar, django-paypal not fully implemented). Django Oscar is intentionally present for future e-commerce/shop features, not for MVP or current development.
- Payment and Wagtail CMS are in the spec but not yet present in codebase.
- Celery tasks for score syncing and payout logic are planned but not yet implemented.
- Frontend (PerediOn template, AlpineJS, HTMX) is not yet implemented.
- Some admin and Celery edge cases may need more test coverage.
- Update this section as new issues or shortcuts are identified.

---


---

## 14. Directory Structure Overview

```
/gameonlock.com/
├── .env_example
├── .github/
│   └── workflows/ci.yml
├── .gitignore
├── .ruff_cache/
├── .vscode/
├── README.md
├── TODO.md
├── directory_structure.txt
├── django.log
├── gameonlock/
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py
│   ├── context.py
│   ├── forms.py
│   ├── middleware.py
│   ├── migrations/
│   ├── models.py
│   ├── pages.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── production.py
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
├── manage.py
├── pyproject.toml
├── requirements.txt
├── setup.cfg
├── specifications.md
├── sportsbetting/
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   ├── resources.py
│   │   └── views.py
│   ├── apps.py
│   ├── forms.py
│   ├── management/
│   │   └── commands/
│   │       └── generate_sportsbetting_fixtures.py
│   ├── migrations/
│   ├── models.py
│   ├── munger.py
│   ├── signals.py
│   ├── tasks.py
│   ├── templatetags/
│   │   └── sportsbetting_tags.py
│   ├── urls.py
│   ├── util.py
│   └── views.py
├── static/
├── templates/
│   ├── account/
│   ├── admin/
│   ├── emails/
│   └── peredion/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_betting_views.py
│   └── test_gb_import_export.py
└── ...
```

### Directory Notes
- Wagtail integration is scaffolded (pages.py) but not yet active.
- PerediOn template is fully present in static/ and templates/peredion/.
- Custom user model extends AbstractUser (gameonlock/models.py).
- Celery is configured (gameonlock/celery.py, sportsbetting/tasks.py).
- Admin import/export uses django-import-export (sportsbetting/admin/resources.py).
- Test coverage includes admin, import/export, and view protection (tests/).
- Django Oscar is present in requirements.txt but not used; intended for future e-commerce/shop features only after MVP maturity.
- requirements.txt includes some planned/unused packages (see Known Issues section).


---


- All dependencies are listed in requirements.txt.
- requirements.txt must be pruned regularly to remove unused packages.
- Unused packages (e.g., django-oscar, if not used) should be removed from both requirements.txt and the specification.

---

## 15. Documentation

- A README.md is required, including setup, test, and deployment instructions.
- Documentation must note any special requirements (e.g., Celery, PayPal integration, Wagtail setup).

---

## 16. Security

- All betting and admin views must be protected using LoginRequiredMixin or equivalent.
- Payment and user data must be handled securely, following Django and PayPal best practices.


---

## 15. Changelog / Tracking Major Changes

- Use this section to log major changes to the specification or project direction.
- Example:
  - 2025-05-25: Added implementation status, CI/CD, dependencies, and documentation requirements.
  - 2025-05-26: Added glossary, testing matrix, directory overview, and known issues sections.

---

---

## 17. MVP Clarifications

- Payment (PayPal) and Wagtail CMS are in the spec but not yet present in codebase; MVP status should clarify which features are implemented and which are planned.
- Frontend (PerediOn template, AlpineJS, HTMX) is not yet implemented; spec will be updated as frontend work progresses.
- APIs currently integrated: thesportsdb for team data. Additional APIs (e.g., for odds, scores) are planned and should be listed as implemented.

---

