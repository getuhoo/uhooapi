# uhooapi
This is a API library for uHoo premium accounts.


# Install dev dependencies
pip install -e .[dev]

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_client.py -v

# Run tests with coverage
pytest --cov

# Run async tests with specific markers
pytest -m "not integration" --asyncio-mode=auto
