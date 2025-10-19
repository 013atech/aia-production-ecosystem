# Contributing to AIA System

Thank you for your interest in contributing to the AIA System! We welcome contributions from the community and are excited to work with you.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful and considerate
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Accept feedback gracefully

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up your development environment
4. Create a feature branch
5. Make your changes
6. Test thoroughly
7. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.11+
- Docker
- Google Cloud SDK (for deployment testing)
- Git

### Local Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/aia.git
cd aia

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r aia_system/requirements.txt
pip install -r aia_system/requirements-dev.txt

# Run tests
python aia-system-tests.py

# Start local development server
cd aia_system
python run-aia-system.py --dev
```

## How to Contribute

### Reporting Bugs

Before reporting a bug, please:
1. Check existing issues to avoid duplicates
2. Gather relevant information (error messages, logs, environment)
3. Create a minimal reproducible example

Bug reports should include:
- Clear description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)

### Suggesting Features

Feature requests should include:
- Clear use case
- Proposed solution
- Alternative solutions considered
- Impact on existing functionality

### Submitting Code

1. **Choose an Issue**: Pick an existing issue or create a new one
2. **Fork & Branch**: Create a feature branch from `main`
3. **Code**: Implement your changes
4. **Test**: Add/update tests as needed
5. **Document**: Update documentation if required
6. **Commit**: Use clear, descriptive commit messages
7. **Push**: Push to your fork
8. **PR**: Submit a pull request

## Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up-to-date with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

### Review Process

1. Automated checks run (tests, linting)
2. Code review by maintainers
3. Address feedback
4. Approval and merge

## Coding Standards

### Python Style

We follow PEP 8 with these additions:

```python
# Use type hints
def calculate_score(
    capabilities: Dict[str, float],
    requirements: Dict[str, float]
) -> float:
    """
    Calculate capability match score.
    
    Args:
        capabilities: Agent capabilities
        requirements: Task requirements
        
    Returns:
        Match score between 0.0 and 1.0
    """
    pass

# Use descriptive variable names
agent_capabilities = {}  # Good
ac = {}  # Bad

# Keep functions focused and small
# Maximum 50 lines per function
# Maximum 500 lines per file
```

### Commit Messages

Follow conventional commits:

```
feat: Add agent performance tracking
fix: Resolve task assignment race condition
docs: Update API documentation
test: Add venture lifecycle tests
refactor: Simplify token distribution logic
```

### Documentation

- Use docstrings for all public functions/classes
- Keep README files up-to-date
- Document breaking changes
- Include examples in documentation

## Testing Guidelines

### Test Coverage

Maintain minimum 80% test coverage:

```bash
# Run tests with coverage
pytest --cov=aia_system tests/

# Generate coverage report
pytest --cov=aia_system --cov-report=html tests/
```

### Test Structure

```python
import pytest

class TestAgentManager:
    """Test agent management functionality."""
    
    @pytest.fixture
    def agent_manager(self):
        """Create test agent manager."""
        return AgentManager()
    
    def test_register_agent(self, agent_manager):
        """Test agent registration."""
        # Arrange
        agent_data = {
            "id": "test_001",
            "name": "Test Agent",
            "capabilities": {"coding": 0.9}
        }
        
        # Act
        result = agent_manager.register(**agent_data)
        
        # Assert
        assert result["status"] == "registered"
        assert result["agent_id"] == "test_001"
```

## Documentation

### API Documentation

When adding/modifying endpoints:

1. Update `docs/api/API_DOCUMENTATION.md`
2. Include request/response examples
3. Document error cases
4. Update OpenAPI spec if applicable

### Code Documentation

```python
def complex_function(param1: str, param2: int) -> Dict[str, Any]:
    """
    Brief description of function purpose.
    
    Detailed explanation of what the function does,
    including any important algorithms or business logic.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is invalid
        TypeError: When param2 is not an integer
        
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result["status"])
        'success'
    """
    pass
```

## Release Process

1. **Version Bump**: Update version in relevant files
2. **Changelog**: Update CHANGELOG.md
3. **Documentation**: Ensure docs are current
4. **Testing**: Run full test suite
5. **Tag**: Create version tag
6. **Release**: Create GitHub release

## Getting Help

- **Discord**: [Join our server](https://discord.gg/aia-system)
- **Documentation**: [docs.aia.system](https://docs.aia.system)
- **Issues**: [GitHub Issues](https://github.com/013atech/aia/issues)
- **Email**: dev@aia-system.com

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Eligible for contributor badges

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AIA System! 🎉