import pytest

# Wherner we need to run some code before test, we use pytest fixture;
# Modular fixtures for managing small or parametrized long-lived test resources;
# Pytest is a feature-rich, plugin-based ecosystem for testing your Python code;


@pytest.fixture
def temp_data():
    temp = [
        'str',
        'string',
        'int',
        'integer',
        'biginteger',
        'float',
        'datetime',
        'date',
        'timestamp',
        'varchar']
    return temp
