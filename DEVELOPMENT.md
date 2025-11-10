# AI Logo Studio Development Setup

This document describes the development tools and linting setup for the project.

## Python (Backend & Worker)

### Linting and Code Quality Tools

- **Black**: Code formatter with 88 character line length
- **isort**: Import sorting compatible with Black  
- **Flake8**: Style guide enforcement
- **mypy**: Static type checking
- **Pylint**: Code analysis and quality checks
- **pytest**: Testing framework

### Configuration

Each Python service (backend/, worker/) has its own `pyproject.toml` with:
- Black formatting rules
- isort import organization
- mypy type checking configuration
- Pylint rule customization
- pytest test discovery

### Usage

```bash
# Backend
cd backend/
black app/
isort app/
flake8 app/
mypy app/
pylint app/

# Worker  
cd worker/
black src/
isort src/
flake8 src/
mypy src/
pylint src/
```

## Frontend (TypeScript/React)

### Linting Tools

- **ESLint**: JavaScript/TypeScript linting with React support
- **TypeScript**: Static type checking
- **Vite**: Build tool with hot reloading

### Configuration

- `eslint.config.js`: ESLint configuration with TypeScript and React plugins
- `tsconfig.json`: TypeScript compiler options
- `package.json`: Scripts for linting and building

### Usage

```bash
cd frontend/
npm run lint        # Run ESLint
npm run build       # TypeScript compilation check
npm run dev         # Development server
```

## Git Hooks (Recommended)

Consider adding pre-commit hooks to run linting automatically:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml (not included)
# Run on all files
pre-commit run --all-files
```

## IDE Integration

### VS Code

Recommended extensions:
- Python (ms-python.python)
- Pylint (ms-python.pylint)
- Black Formatter (ms-python.black-formatter)
- isort (ms-python.isort)
- ESLint (dbaeumer.vscode-eslint)
- TypeScript Importer (pmneo.tsimporter)

### Settings

```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "typescript.preferences.organizeImports": true,
    "eslint.format.enable": true
}
```

## Docker Integration

Linting tools are included in requirements.txt for each service, so they're available in containers for CI/CD pipelines.