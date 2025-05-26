# TODO: Game On Lock Project

## 1. Core Functionality

- **Payment Integration**
  - Implement PayPal payment flow for play submission (MVP).
  - Secure payment handling and Celery task for marking plays as paid.
  - Add tests for payment edge cases.

- **Bet Slip & Betting Logic**
  - Fix AlpineJS undefined picks error and ensure localStorage sync.
  - Correct pick removal logic and prevent duplicate picks.
  - Validate bet submission (min 4 picks, no duplicates, min stake).
  - Persist bet slip for unauthenticated users and restore on login.
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








## Improve Accessibility

Action: Add aria-label to .single-t-match radios and ensure bet-slip-header toggle is keyboard-navigable in bet-slip.html. Follow WCAG 2.1 guidelines.
Test: Navigate with screen reader and keyboard, verify usability.
Outcome: Accessible interface.


## Refine Styling

Action: In styles.css, fix button hover states, ensure Asap font, and optimize mobile layouts (Bootstrap col-md-*).
Test: Check styling on desktop/mobile, verify hover effects.
Outcome: Consistent, branded visuals.


## Add Visual Feedback

Action: In styles.css, add CSS animations (e.g., scale) for .single-bet-place.placed/.active classes in .single-t-match.
Test: Select a bet, confirm animation triggers.
Outcome: Engaging UI feedback.


## Create Onboarding Tour

Action: Use AOS (if included) to create a modal tour in index.html, guiding users through bet placement and bet slip usage.
Test: Complete tour, verify clarity.
Outcome: Improved user adoption.



# Project-Level Features

## Build User Dashboard

Action: Create a Django template for user dashboard, showing bet history, payout status, balance, and settings. Add filter/search functionality.
Test: View past bets, filter by status, verify data accuracy.
Outcome: Comprehensive user hub.


## Enable Live Updates

Action: Use WebSockets (via Django Channels) or polling to update game data in real-time.
Test: Simulate game start, confirm UI updates.
Outcome: Dynamic match status.


## Configure Wagtail CMS

Action: Set up Wagtail for blog (list/single views, tagged posts), SEO metadata, and homepage content blocks. Create admin interfaces.
Test: Create/edit blog post, verify frontend display.
Outcome: Flexible content management.


## Localize Content

Action: Apply {% trans %} to all user-facing text in HTML templates. Test Django i18n for multiple languages.
Test: Switch languages, verify translations.
Outcome: Multi-language support.


## Improve Error Handling

Action: Replace window.alert in bet-slip.html with Bootstrap modals for failed submissions or network errors.
Test: Trigger failed submission, confirm modal display.
Outcome: User-friendly error messages.



# Testing & Quality

## Write Unit Tests

Action: Use Jest to test frontend, betting line validation, spreadsheet import/export, and outcome logic.
Test: Run tests, ensure 90%+ coverage.
Outcome: Reliable codebase.


## Perform Integration Tests

Action: Test end-to-end flow: select picks, submit bet slip, process payment, verify backend Play creation.
Test: Complete flow, confirm database updates.
Outcome: Validated user journey.


## Conduct Cross-Browser Testing

Action: Test in Chrome, Firefox, Safari, Edge, focusing on AlpineJS and Bootstrap 5.3 compatibility.
Test: Verify consistent behavior across browsers.
Outcome: Broad compatibility.


## Run Performance Audit

Action: Profile page load and bet slip updates using browser dev tools. Optimize localStorage access and AlpineJS reactivity.
Test: Measure load time <2s, smooth interactions.
Outcome: Fast, responsive UI.


## Security Review

Action: Review security implementation.
Test: Attempt XSS, verify protections.
Outcome: Secure application.



# Documentation & Maintenance


## Update README

Action: Add setup, test, and deployment steps for AlpineJS (3.x), Bootstrap (5.3), Font Awesome (6.0.0) in README.md.
Test: Follow setup steps, verify functionality.
Outcome: Easy onboarding.


## Refactor Code

Action: Modularize bet-slip.html into functions (e.g., pick validation), remove redundant files, prune unused requirements.txt packages.
Test: Run app, confirm no regressions.
Outcome: Clean codebase.


## Maintain Changelog

Action: Log major changes (e.g., payment integration, live updates) in CHANGELOG.md.
Test: Review for completeness.
Outcome: Transparent change tracking.


## Enable Logging

Action: Add console logging to frontend. Integrate with Django logging if available.
Test: Trigger actions, verify logs.
Outcome: Debuggable system.



# Infrastructure

## Verify Dependencies

Action: Check AlpineJS (3.x), Bootstrap (5.3), Font Awesome (6.0.0) versions in index.html. Update if outdated.
Test: Load page, confirm assets work.
Outcome: Up-to-date dependencies.


## Optimize Assets

Action: Minify assets. Run collectstatic for Django production.
Test: Deploy, verify asset loading.
Outcome: Faster load times.


## Set Up CI/CD

Action: Configure GitHub Actions for linting (ESLint), testing (Jest), and deployment checks.
Test: Push code, verify pipeline passes.
Outcome: Automated quality checks.


## Deploy Application

Action: Dockerize project, configure nginx+SSL, set up systemd/Docker Compose for Celery, and enable logging (stdout/syslog).
Test: Deploy to VPS, access site securely.
Outcome: Production-ready app.


## Enable Developer Tools

Action: Activate Django Silk, Debug Toolbar in dev environment. Configure Redis for Celery and caching.
Test: Debug a request, verify tools.
Outcome: Enhanced debugging.



# Stretch Goals

## Add Bet Suggestions

Action: In playing-bet.html#tab-content, add a "recommended bets" section using backend API data (e.g., popular picks).
Test: Display suggestions, verify relevance.
Outcome: Increased engagement.


## Support Dark Mode

Action: In styles.css, add CSS variables for dark mode, toggle via AlpineJS. Preserve #D03355 branding.
Test: Switch modes, verify styling.
Outcome: Modern UI option.


## Integrate Analytics

Action: Add Google Analytics to track bet placements, slip toggles in index.html.
Test: Trigger events, verify tracking.
Outcome: Actionable user insights.


## Enable Offline Support

Action: Use Service Workers to cache .single-t-match data for limited offline access.
Test: Go offline, verify cached display.
Outcome: Resilient UX.


## Add Leaderboards/Insights

Action: Create a dashboard view for user rankings and betting stats.
Test: Display leaderboard, verify accuracy.
Outcome: Competitive features.


## Implement Bonus/Referral System

Action: Add backend logic and frontend UI for user rewards on referrals.
Test: Refer user, verify bonus.
Outcome: User retention boost.


## Design User Wallet

Action: Create a model and UI for persistent user balance.
Test: Deposit/withdraw, verify balance.
Outcome: Streamlined payments.


## Add E-commerce

Action: Integrate Django Oscar for shop features post-MVP.
Test: Add product, complete purchase.
Outcome: Expanded revenue stream.
