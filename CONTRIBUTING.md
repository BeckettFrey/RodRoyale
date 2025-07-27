# Contributing to RodRoyale Backend

Thank you for your interest in contributing! We welcome improvements, bug fixes, and new features. Please read this guide to get started.

## How to Contribute

1. **Fork the Repository**
   - Click "Fork" at the top right of the GitHub page.
   - Clone your fork locally:
     ```bash
     git clone https://github.com/beckettfrey/RodRoyale-Backend.git
     cd RodRoyale-Backend
     ```

2. **Create a Branch**
   - Use a descriptive branch name:
     ```bash
     git checkout -b feature/my-new-feature
     ```

3. **Install Dependencies**
   - Set up a virtual environment and install requirements:
     ```bash
     python -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt requirements-dev.txt
     ```

4. **Code Style**
   - Format code with Black:
     ```bash
     black .
     ```
   - Lint code with Flake8:
     ```bash
     flake8 .
     ```

5. **Testing**
   - Write unit and integration tests for new features or bug fixes.
   - Run tests locally:
     ```bash
     pytest
     ```
   - Tests should not require real external services; use mocks for MongoDB and Cloudinary.

6. **Documentation**
   - Update or add documentation for new features in `docs/`.
   - Add docstrings to new modules, classes, and functions.

7. **Commit and Push**
   - Use clear, descriptive commit messages.
   - Push your branch to your fork:
     ```bash
     git push origin feature/my-new-feature
     ```

8. **Open a Pull Request**
   - Go to the original repository and click "New Pull Request".
   - Fill out the PR template, describing your changes and linking related issues.

## Review Process
- All PRs are reviewed for code quality, style, and test coverage.
- CI/CD will run tests and coverage checks automatically.
- Address any requested changes before merging.

## Tips & Nuances
- Use async/await for all database and I/O operations.
- Never commit secrets or credentials.
- Keep tests isolated and fast by mocking external dependencies.
- Follow the project’s architecture and naming conventions.
- For major changes, open an issue first to discuss your proposal.

---
Thank you for helping make RodRoyale Backend better!
