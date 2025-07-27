# LEARNING_OUTLINE

This document outlines key concepts and nuanced details for learning and contributing to the RodRoyale Backend.

## Key Concepts

- **FastAPI Framework**: The backend is built with FastAPI, which provides async support, automatic OpenAPI docs, and dependency injection.
- **MongoDB with Motor**: Uses Motor for async MongoDB operations. Understanding async/await and non-blocking I/O is important.
- **JWT Authentication**: Implements access and refresh tokens for secure user authentication. Token handling and expiration are critical for security.
- **Password Hashing**: Passwords are hashed using Passlib (bcrypt). Never store plain-text passwords.
- **Pydantic Models**: Data validation and serialization are handled with Pydantic schemas. Learn about type enforcement and model inheritance.
- **Cloudinary Integration**: Image uploads are managed via Cloudinary. API keys are required, but are mocked in tests for safety.
- **Testing**: Pytest is used for unit and integration tests. MongoDB and Cloudinary are mocked for CI reliability.
- **Docker & CI/CD**: The project supports Docker and GitHub Actions for automated testing and deployment.
- **Async Patterns**: All database and I/O operations are async. Mixing sync and async code can cause issues—use async everywhere for consistency.
- **Environment Variables**: Sensitive config (DB URLs, API keys) is loaded from environment variables. Defaults are provided for CI/testing, but production must set real secrets.
- **Indexing in MongoDB**: Indexes are created for performance and uniqueness. Understanding compound indexes and their impact on queries is useful.
- **Token Expiry & Refresh**: Access tokens expire quickly; refresh tokens allow session extension. Handle token renewal logic carefully in clients.
- **Error Handling**: API returns detailed error codes and messages. Logging is used for debugging and monitoring.
- **Testing Isolation**: Tests use a separate test database and mock external services. This prevents accidental data loss and speeds up CI.
- **CORS & Security**: CORS origins are configurable. In production, restrict origins to trusted domains.
- **Schema Evolution**: MongoDB is schema-less, but Pydantic enforces structure at the API layer. Be mindful of migrations and backward compatibility.
- **Contribution Workflow**: Use black and flake8 for code style. PRs should include tests and docs for new features.
- **Automated Testing**: Every push and pull request triggers GitHub Actions workflows that run unit and integration tests using Pytest.

