# Python Template 🐍

A modern, well-engineered Python project template with batteries included. This template provides a solid foundation for Python projects with custom logging, configuration management, and modern development practices.

## ✨ Features

- **🚀 Modern Python**: Built for Python 3.9+ with type hints and modern best practices
- **📦 UV Package Manager**: Fast, reliable dependency management with UV
- **🔧 Flexible Configuration**: Environment-based configuration with YAML and environment variables
- **📝 Rich Logging**: Beautiful console logging with file rotation and structured logging
- **🧪 Testing Ready**: Pre-configured pytest with coverage reporting
- **🎨 Code Quality**: Black, isort, flake8, and mypy pre-configured
- **📁 Src Layout**: Modern Python project structure following best practices
- **🔒 Type Safety**: Full type hints with mypy configuration
- **🌍 Multi-Environment**: Support for development, staging, production, and testing environments

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- [UV](https://github.com/astral-sh/uv) package manager

### Installation

1. **Clone or copy this template**:
   ```bash
   git clone <repository-url> my-python-project
   cd my-python-project
   ```

2. **Install UV** (if you haven't already):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Activate the virtual environment**:
   ```bash
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate  # On Windows
   ```

5. **Copy environment configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Run the application**:
   ```bash
   python-template run
   ```

## 📁 Project Structure

```
python_template/
├── src/
│   └── python_template/           # Main package (src layout)
│       ├── __init__.py           # Package initialization
│       ├── main.py               # CLI application entry point
│       ├── logger.py             # Custom logging configuration
│       └── config/               # Configuration management
│           ├── __init__.py
│           └── settings.py       # Pydantic settings with environment support
├── tests/                        # Test suite
│   ├── __init__.py
│   └── test_main.py             # Main application tests
├── config/                       # Configuration files
│   ├── logging.yaml             # Logging configuration
│   ├── settings.yaml            # Base application settings
│   └── settings_dev.yaml        # Development environment settings
├── pyproject.toml               # Project configuration and dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore patterns
└── README.md                    # This file
```

## 🔧 Configuration

### Environment Variables

The application supports configuration through environment variables and YAML files. Copy `.env.example` to `.env` and customize:

```bash
# Application Settings
ENVIRONMENT=development  # development, staging, production, testing
DEBUG=true
LOG_LEVEL=INFO

# Database
DB_URL=sqlite:///./app.db

# API Settings
API_HOST=localhost
API_PORT=8000
```

### YAML Configuration

Configuration files in the `config/` directory:

- `settings.yaml`: Base configuration
- `settings_dev.yaml`: Development overrides
- `settings_staging.yaml`: Staging overrides (create as needed)
- `settings_production.yaml`: Production overrides (create as needed)

### Environment-Specific Settings

The application automatically loads environment-specific settings based on the `ENVIRONMENT` variable:

```python
from python_template import get_settings

settings = get_settings()
print(f"Running in {settings.environment} mode")
print(f"Database URL: {settings.database.url}")
```

## 🔍 Usage Examples

### Command Line Interface

```bash
# Run the main application
python-template run

# Run with debug logging
python-template run --log-level DEBUG

# Run in specific environment
python-template run --env production

# Show application information
python-template info

# Display current configuration
python-template config

# Test logging functionality
python-template test-logging

# Initialize a new project from template
python-template init-project my-new-project
```

### Using in Code

```python
from python_template import get_logger, get_settings
from python_template.logger import LoggerMixin

# Get configured logger
logger = get_logger(__name__)
logger.info("Hello from Python Template!")

# Access settings
settings = get_settings()
print(f"App: {settings.app_name} v{settings.version}")

# Use logger mixin in classes
class MyClass(LoggerMixin):
    def do_something(self):
        self.logger.info("Doing something...")
        
# Function logging decorator
from python_template.logger import log_function_call

@log_function_call
def my_function(x: int, y: int) -> int:
    return x + y
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_main.py

# Run with verbose output
uv run pytest -v
```

## 🎨 Code Quality

The project includes pre-configured tools for code quality:

```bash
# Format code with black
uv run black src/ tests/

# Sort imports with isort
uv run isort src/ tests/

# Lint with flake8
uv run flake8 src/ tests/

# Type check with mypy
uv run mypy src/

# Run all quality checks
uv run black src/ tests/ && uv run isort src/ tests/ && uv run flake8 src/ tests/ && uv run mypy src/
```

## 📊 Logging

The template includes a sophisticated logging system:

### Features

- **Rich Console Output**: Beautiful, colored console logging
- **File Logging**: Automatic log rotation with configurable size limits
- **Multiple Handlers**: Console, file, and error-specific logging
- **YAML Configuration**: Easy-to-modify logging configuration
- **Structured Logging**: Support for structured log data
- **Environment-Specific**: Different log levels per environment

### Usage

```python
from python_template import get_logger

logger = get_logger(__name__)

# Basic logging
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# Structured logging
logger.info("User login", extra={
    "user_id": "12345",
    "ip_address": "192.168.1.1",
    "action": "login"
})
```

## ⚙️ Development

### Setting up for Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd python-template
   ```

2. **Install development dependencies**:
   ```bash
   uv sync --dev
   ```

3. **Install pre-commit hooks** (optional but recommended):
   ```bash
   uv run pre-commit install
   ```

### Adding Dependencies

```bash
# Add a runtime dependency
uv add requests

# Add a development dependency
uv add --dev pytest-mock

# Update dependencies
uv sync
```

### Project Customization

To customize this template for your project:

1. **Rename the package**: Update `src/python_template/` to your package name
2. **Update pyproject.toml**: Change project name, description, authors, etc.
3. **Modify settings**: Update configuration files in `config/`
4. **Customize logging**: Modify `config/logging.yaml`
5. **Update README**: Replace this README with your project's documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and quality checks
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [UV](https://github.com/astral-sh/uv) for fast Python package management
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation and settings
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- [Typer](https://typer.tiangolo.com/) for building CLI applications
- [pytest](https://pytest.org/) for testing framework

---

**Happy coding!** 🎉 