# Contributing Guide

This documentation serves as a guide for those who want to contribute to the project.

## Development Environment Setup

1. Fork the repository
2. Clone to your local machine:
```bash
git clone https://github.com/your-username/fastapi-service.git
cd fastapi-service
```

3. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Install pre-commit hooks:
```bash
pre-commit install
```

## Code Style

### Python Code Style
- Follow PEP 8 standards
- Use type hints
- Write docstrings for each function
- Maximum line length: 88 characters

### Docstring Format
```python
def function_name(param1: str, param2: int) -> dict:
    """
    Function description.

    Args:
        param1 (str): First parameter description
        param2 (int): Second parameter description

    Returns:
        dict: Return value description

    Raises:
        ValueError: Error condition description
    """
    pass
```

## Git Workflow

1. Create feature branch:
```bash
git checkout -b feature/amazing-feature
```

2. Commit your changes:
```bash
git add .
git commit -m "feat: add amazing feature"
```

3. Push your branch:
```bash
git push origin feature/amazing-feature
```

4. Create Pull Request

### Commit Messages
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes
- refactor: Code refactoring
- test: Adding or modifying tests
- chore: General maintenance

## Testing

### Writing Tests
- Write tests for each new feature
- Write tests for each bug fix
- Maintain test coverage above 80%

### Running Tests
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

## Pull Request Process

1. Fill out the PR description:
   - Changes made
   - Test results
   - Screenshots (for UI changes)

2. Wait for review
3. Make necessary corrections
4. Get approval for merge

## Documentation

### API Documentation
- Update `docs/api.md` for new endpoints
- Add request/response examples
- Specify error codes

### Architecture Documentation
- Update `docs/architecture.md` for architectural changes
- Add new patterns or services
- Specify deployment changes

## Security

### Security Vulnerability Reporting
1. Do not open security vulnerabilities as direct issues
2. Email the security team
3. Create PR for fixes

### API Key Management
- Never store API keys in code
- Use environment variables
- Use dummy keys for testing

## Performance

### Performance Optimizations
- Use pagination for large datasets
- Avoid unnecessary database queries
- Implement caching mechanisms

### Monitoring
- Add new metrics
- Update alerts
- Update dashboards

## Deployment

### Docker
- Optimize Dockerfile
- Use multi-stage builds
- Perform security scanning

### CI/CD
- Update pipeline
- Add new test stages
- Update deployment strategy

## Communication

### Slack
- Use #fastapi-service channel
- Request code reviews here
- Ask general questions here

### Email
- For critical security notifications
- For special cases
- For general communication

## License

This project is licensed under the MIT License. By contributing, you agree that your contributions will be licensed under the same license. 