1. Purpose of This Document

This document defines the mandatory rules, principles, and standards that any agent modifying this repository must follow.

The objective is to ensure:

High security (aligned with OWASP Top 10 – 2025)

Maintainable and scalable architecture

Clean, testable, and well-documented code

Predictable behavior across environments

Long-term sustainability of the system

Deviation from these rules is not allowed unless explicitly authorized.

2. General Non-Negotiable Rules

No code changes without tests.

No endpoint without validation.

No business logic inside API endpoints.

No hardcoded secrets or credentials.

No undocumented methods or classes.

No breaking changes without versioning.

No logging of sensitive or personal data.

No silent failures (all errors must be handled explicitly).

3. Security Guidelines (OWASP Top 10 – 2025 + Extended)

Agents must actively prevent vulnerabilities listed in the OWASP Top 10 (2025), including but not limited to:

Broken Access Control

Cryptographic Failures

Injection (SQL, NoSQL, Command, etc.)

Insecure Design

Security Misconfiguration

Vulnerable and Outdated Components

Identification and Authentication Failures

Software and Data Integrity Failures

Security Logging and Monitoring Failures

Server-Side Request Forgery (SSRF)

Additional Mandatory Security Practices

Apply the Principle of Least Privilege (PoLP) at all levels.

Validate and sanitize all inputs and outputs.

Use Pydantic models for request and response validation.

Enforce strict CORS policies.

Implement rate limiting and throttling where applicable.

Use secure password hashing and token-based authentication.

Secrets must be loaded from environment variables or secret managers.

Dependencies must be scanned for vulnerabilities.

Fail securely and return non-revealing error messages.

4. Architectural Principles

The project follows Clean Architecture and Hexagonal Architecture concepts.

Mandatory Layering Rules

API Layer

Only handles HTTP concerns.

No business logic allowed.

Service Layer

Contains all business rules.

Orchestrates transactions.

Repository Layer

Handles data persistence.

No business logic allowed.

Domain Layer

Core entities and rules.

Infrastructure Layer

Database, logging, external services.

Design Patterns to Be Used

Repository Pattern

Service Layer Pattern

Dependency Injection

Factory Pattern (when applicable)

Strategy Pattern (for interchangeable behaviors)

5. SOLID Principles (Mandatory)

All code must comply with SOLID:

Single Responsibility Principle

Open/Closed Principle

Liskov Substitution Principle

Interface Segregation Principle

Dependency Inversion Principle

Violations must be refactored immediately.

6. Transactions & ATOMIC Principles

All database operations must respect ATOMIC principles:

Atomicity: operations succeed or fail as a unit

Transactional consistency

Operational isolation

Managed explicitly in the service layer

Idempotency where applicable

Consistency across retries

Transactions must never be handled inside repositories.

7. Coding Standards (Python)
General Rules

Python 3.11+ syntax

Use snake_case for variables, methods, and files

Use PascalCase for classes

Mandatory type hints

Async-first (async / await) when applicable

Respect Python indentation (4 spaces)

Avoid code duplication (DRY)

Formatting & Linting

Code must be compatible with:

black

ruff

isort

mypy

8. Documentation Requirements

Every class and method must include a docstring

Use Google-style or NumPy-style docstrings

Public APIs must be documented in OpenAPI

Include examples where relevant

Errors and exceptions must be documented

No undocumented code is acceptable.

9. Testing Strategy
Mandatory Testing Rules

Unit tests are required for:

Every method

Every service

Every repository

Tests must be:

Deterministic

Isolated

Repeatable

Testing Pyramid

Unit Tests (majority)

Integration Tests (DB, repositories)

API / E2E Tests

Additional Requirements

Use fixtures for setup and teardown

Mock external services

Include negative test cases

Maintain a minimum coverage of 85%

10. Logging & Observability
Logging Rules

Use structured logging (JSON)

Respect log levels:

DEBUG

INFO

WARNING

ERROR

CRITICAL

Logs must include correlation/request IDs

Sensitive data must never be logged

HTML Logs

Logs must also be exportable in HTML format

HTML logs must be readable and structured

Log rotation must be enabled

11. Dependency Management

All required libraries must be:

Explicitly declared

Automatically added to requirements.txt

Unused dependencies must be removed

Versions should be pinned when stability is required

Security of dependencies must be considered

12. Database Versioning & Migrations

Use versioned migrations (e.g., Alembic)

Maintain strict ordering of migration files

Entity changes must always include a migration

Backward compatibility must be considered

Schema changes must be documented

13. Environment & Configuration

Follow 12-Factor App principles

Configuration must be environment-based

No environment-specific logic in code

Feature flags should be supported

14. DevOps & Lifecycle Practices

Docker-first approach

CI/CD pipelines must include:

Linting

Testing

Security scanning

Health check endpoints are mandatory:

/health

/readiness

/liveness

15. Forbidden Practices

Hardcoded secrets

Business logic in controllers

Direct DB access from API layer

Ignoring errors or exceptions

Skipping tests
16. Project Structure

Important:
The full and authoritative directory and file structure must always be placed at the end of this document and treated as the source of truth.
.
├── backend/
│   ├── bakerySpotGourmet/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── users.py
│   │   │   │   │   ├── items.py
│   │   │   │   │   ├── orders.py
│   │   │   │   │   └── admin.py
│   │   │   │   │
│   │   │   │   ├── dependencies.py          # auth, db, request_id, rate limit
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py                    # env, timeouts, rate limits
│   │   │   ├── security.py                  # auth, hashing, rate limiting
│   │   │   ├── logging.py                   # structured + HTML logs
│   │   │   ├── exceptions.py                # global exception handlers
│   │   │   ├── constants.py                 # enums, roles, limits
│   │   │   └── middleware.py                # request_id, logging, timing
│   │   │
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   ├── session.py
│   │   │   ├── migrations/
│   │   │   │   └── versions/
│   │   │   └── __init__.py
│   │   │
│   │   ├── domain/
│   │   │   ├── users/
│   │   │   │   ├── entities.py
│   │   │   │   ├── value_objects.py
│   │   │   │   └── exceptions.py
│   │   │   │
│   │   │   ├── catalog/
│   │   │   │   ├── product.py
│   │   │   │   ├── category.py
│   │   │   │   └── exceptions.py
│   │   │   │
│   │   │   ├── orders/
│   │   │   │   ├── order.py
│   │   │   │   ├── order_item.py
│   │   │   │   ├── order_type.py
│   │   │   │   ├── status.py
│   │   │   │   └── exceptions.py
│   │   │   │
│   │   │   ├── payments/
│   │   │   │   ├── payment.py
│   │   │   │   ├── status.py
│   │   │   │   └── exceptions.py
│   │   │   │
│   │   │   └── __init__.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── item.py
│   │   │   ├── order.py
│   │   │   ├── payment.py
│   │   │   └── common.py
│   │   │
│   │   ├── repositories/
│   │   │   ├── user_repository.py
│   │   │   ├── item_repository.py
│   │   │   ├── order_repository.py
│   │   │   └── payment_repository.py
│   │   │
│   │   ├── services/
│   │   │   ├── user_service.py
│   │   │   ├── item_service.py
│   │   │   ├── order_service.py
│   │   │   ├── auth_service.py
│   │   │   └── payment_service.py
│   │   │
│   │   ├── infrastructure/
│   │   │   ├── payments/
│   │   │   │   ├── payment_client.py
│   │   │   │   ├── circuit_breaker.py
│   │   │   │   ├── retry_policy.py
│   │   │   │   └── exceptions.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── utils/
│   │   │   ├── uuid.py
│   │   │   ├── datetime.py
│   │   │   ├── validators.py
│   │   │   └── idempotency.py
│   │   │
│   │   └── main.py
│   │
│   └── tests/
│       ├── api/
│       ├── services/
│       ├── repositories/
│       ├── domain/
│       │   ├── users/
│       │   ├── catalog/
│       │   ├── orders/
│       │   └── payments/
│       └── conftest.py
│
├── frontend/
├── .env
├── requirements.txt
├── Dockerfile
├── README.md
└── agent.md
