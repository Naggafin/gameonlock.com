# TODO: Game On Lock Project

## 1. Core Functionality

- **Payment Integration**
  - Implement PayPal payment flow for play submission (MVP). [In Progress]
  - Secure payment handling and Celery task for marking plays as paid. [Implemented]
  - Add tests for payment edge cases. [Implemented - Forms and Tasks Tests Added]

- **Bet Slip & Betting Logic**
  - Fix AlpineJS undefined picks error and ensure localStorage sync. [Implemented]
  - Correct pick removal logic and prevent duplicate picks. [Implemented]
  - Validate bet submission (min 4 picks, no duplicates, min stake). [Implemented]
  - Persist bet slip for unauthenticated users and restore on login. [Implemented]
  - Remove duplicate markup and optimize transitions in bet-slip.html.

- **Celery Tasks**
  - Implement tasks for score syncing, outcome resolution, and admin notifications.
  - Add tests for Celery task scheduling and error handling.

- **Admin Tools**
  - Finalize spreadsheet import/export for betting lines (CSV/JSON).
  - Validate admin data before saving.
  - Add tests for admin import/export and error cases.

- **REST API**
  - Implement endpoints: `/api/betting-lines/`, `/api/plays/`, `/api/results/` using DRF.
  - Secure endpoints with authentication and permissions.
  - Add tests for API endpoints and edge cases.

- **Data Models**
  - Finalize and validate models (Sport, GoverningBody, League, Team, ScheduledGame, BettingLine, Play, PlayPick).
  - Ensure constraints and run migrations.

---

## 2. Frontend & UI/UX

- **Template Integration**
  - Integrate PerediOn template with Django templates.
  - Implement interactive betting line selection (AlpineJS/HTMX).
  - Ensure mobile-first responsiveness and accessibility.

- **Bet Slip Enhancements**
  - Persist stake amount in localStorage.
  - Add loading spinners and optimize animations.
  - Add filtering/sorting for betting lines.

- **Accessibility & Styling**
  - Add ARIA labels and keyboard navigation.
  - Refine styling for branding and mobile layouts.
  - Add visual feedback (animations) for bet selection.

- **User Dashboard**
  - Build dashboard for bet history, payouts, and settings.
  - Add filter/search functionality.

- **Onboarding & Feedback**
  - Create onboarding tour using AOS.
  - Replace alert() with Bootstrap modals for errors.

---

## 3. CMS & Content

- **Wagtail CMS**
  - Activate and configure Wagtail for blog and SEO/content pages.
  - Create initial page models and admin setup.
  - Add tests for Wagtail page creation and permissions.

- **Localization**
  - Apply `{% trans %}` to all user-facing text.
  - Test Django i18n for multiple languages.

---

## 4. Testing & Quality

- **Automated Test Coverage**
  - Ensure all features, admin tools, and edge cases are covered.
  - Add tests for new Celery tasks, payment, and Wagtail features.

- **Integration & Performance**
  - Test end-to-end flow: select picks, submit bet slip, process payment, verify backend.
  - Conduct cross-browser and performance testing.

- **Security Review**
  - Enforce LoginRequiredMixin on all betting and admin views.
  - Review for XSS, CSRF, and other vulnerabilities.

---

## 5. Documentation & Maintenance

- **Documentation**
  - Complete and maintain README.md (setup, test, deployment).
  - Document Celery, PayPal, and Wagtail setup.
  - Keep specifications.md in sync with codebase.

- **Changelog**
  - Log all major changes in CHANGELOG.md.

- **Code & Dependency Cleanup**
  - Modularize frontend logic, remove redundant files.
  - Prune unused packages from requirements.txt.
  - Comment on packages intended for future use (e.g., Django Oscar).

---

## 6. Infrastructure & Deployment

- **Dependencies**
  - Verify and update AlpineJS, Bootstrap, Font Awesome versions.
  - Minify and optimize static assets.

- **CI/CD**
  - Configure GitHub Actions for linting, testing, and deployment checks.

- **Deployment**
  - Dockerize project, configure nginx+SSL, set up Celery and logging.
  - Enable Django Silk, Debug Toolbar, and Redis in dev.

---

## 7. Stretch Goals & Future Features

- **Live Game Updates**
  - Implement real-time updates (WebSockets or polling).

- **Leaderboards & Insights**
  - Add leaderboards, betting statistics, and insights.

- **Bonus/Referral System**
  - Implement user rewards for referrals.

- **Persistent User Wallet**
  - Design and implement a user wallet/balance system.

- **E-commerce/Shop Section**
  - Integrate Django Oscar for shop features post-MVP.

- **Other Enhancements**
  - Add bet suggestions, dark mode, analytics, offline support.

---

## 8. Ongoing

- Track known issues and technical debt.
- Maintain changelog and update documentation as features evolve.
