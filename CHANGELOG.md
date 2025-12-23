# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
