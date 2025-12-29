# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-12-29

### Added
- Charts for blood glucose readings:
  - Timeline
  - 24-hour overlay
  - Daily averages
- Add blood glucose history section to dashboard

## [1.0.8] - 2025-12-27

### Added
- Quick insertion of base and correction doses when adding insulin dose

### Fixed
- Fate date/time column styling in tables

## [1.0.8] - 2025-12-26

### Fixed
- Fixed typo in 1.0.7 changelog
- Add missing `block title`

## [1.0.7] - 2025-12-26

### Added
- Date sorting functionality for glucose readings, insulin doses, and meals tables
- Sortable "Date & Time" column headers with visual indicators (↑/↓) showing current sort direction
- Date filtering for meals and insulin doses matching existing glucose readings functionality
- Export modal interface replacing previous dropdown design
- Glucose-specific export options: Include units checkbox and date format selector
- Export options isolated to glucose readings only (not displayed for other data types)

### Changed
- Export interface converted from dropdown to modal dialog for better UX
- Pagination links now preserve sort order and date filter parameters
- Page size controls maintain sort and filter state when changed
- Export functionality respects current sorting parameters
- JavaScript page size handler updated to preserve all query parameters

## [1.0.6] - 2025-12-24

### Added
- Insulin Schedule section on dashboard displaying scheduled doses and correction scale tables
- Insulin schedule and correction scale data now included in dashboard view context
- Reference tables for insulin schedule and correction scale on insulin dose add page
- Quick Add navbar link converted to dropdown menu with Blood Glucose, Insulin Dose, and Meal options
- Icons and color coding for Quick Add dropdown items matching dashboard cards
- Mobile-optimized Quick Add navigation with nested menu items

### Changed
- Dashboard layout: Insulin Schedule section moved between Quick Add and Recent Activity sections
- Insulin schedule and correction scale table width ratio changed from 1:1 to 2:1 on desktop
- Desktop navbar Quick Add now uses Bootstrap dropdown instead of direct link
- Mobile navbar Quick Add displays as section header with indented menu items

## [1.0.5] - 2025-12-24

### Added
- Export functionality for glucose readings with CSV, Excel, and plain text formats
- Export dropdown button on glucose readings and activity pages
- Plain text export uses copy-to-clipboard instead of file download
- Toast notification for successful clipboard copy
- Glucose reading text export formatted as bulleted list with date range header
- Date filter improvements: replaced "Today"/"Yesterday" with "Today"/"2 Days" quick filters
- JavaScript-powered quick filters using actual date range parameters
- Django management command for seeding database with sample data (`seed_data`)
- Root URL (`/`) now redirects to dashboard
- Dark mode styling fixes for export dropdown menu

### Changed
- Date filtering now uses URL date range parameters (`?start_date=...&end_date=...`) instead of filter query parameter
- Simplified `get_date_filters()` utility function
- Updated glucose reading export text format to `- YYYY/MM/DD HH:MM am/pm: value unit`
- Export functionality preserves applied date filters
- Removed `filter_type` from view contexts and templates

### Fixed
- Export dropdown text visibility in dark mode
- Test suite updated to match new filtering system (169 tests passing)

## [1.0.4] - 2025-12-23

### Added
- InsulinSchedule model now tracks last_modified_by user
- Add InsulinSchedule to admin panel

## [1.0.3] - 2025-12-23

### Added
- WhiteNoise for static assets serving

### Fixed
- Added `InsulinSchedule` to admin panel

## [1.0.2] - 2025-12-23

- Deployment changes

## [1.0.1] - 2025-12-23

### Fixed
- Fixed GitHub Action

## [1.0.0] - 2025-12-23

### Added
- Initial release of Diabeateeze diabetes management application
- User authentication with Django Allauth
- Blood glucose reading tracking with unit support (mg/dL and mmol/L)
- Insulin dose logging with separate base and correction units
- Meal tracking with carbohydrate counting
- Insulin type management
- Correction scale configuration
- Activity view showing chronological entries across all types
- Dashboard with Quick Add, Recent Activity, and Manage Logs sections
- Local datetime defaults for entry forms (browser timezone aware)
- Dark mode theme toggle
- Responsive Bootstrap UI with mobile support
- Docker deployment support with multi-architecture builds (ARM64/AMD64)
- GitHub Actions CI/CD pipeline with automated testing
- PostgreSQL support for production deployments
- SQLite support for development and testing
- Environment-based configuration with django-environ
- Application versioning in footer
- Comprehensive test suite with pytest
- Production-ready Docker configuration with Alpine Linux
- Docker Compose setup with PostgreSQL and optional Caddy reverse proxy
- Health checks for containers
- Database migration automation
- Static file collection and serving
- Deployment documentation

### Security
- Non-root Docker user for container security
- Environment variable validation for production
- Secret key enforcement in production
- Secure cookie settings for production
- CSRF protection enabled
- Django password validation

[1.0.0]: https://github.com/yourusername/diabeateeze/releases/tag/v1.0.0
