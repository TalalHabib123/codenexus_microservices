import pytest
from endpoints_url import REFACTOR_SERVICE_URL
from pydantic import ValidationError
import httpx
from app.refactoring_models.refactor_models import RefactorResponse, MagicNumbersDetails

# Fixture for simple magic number code
@pytest.fixture
def simple_magic_number_code():
    return """
def calculate_area(radius):
    # Calculate area of circle
    return 3.14159 * radius * radius

def calculate_tax(amount):
    # Calculate tax at 8.5%
    return amount * 0.085
"""

# Fixture for multiple magic numbers code
@pytest.fixture
def multiple_magic_numbers_code():
    return """
def calculate_metrics(value):
    # Area calculation with pi
    area = 3.14159 * value * value
    
    # Tax calculation at 8.5%
    tax = value * 0.085
    
    # Add 42 because it's the answer
    result = area + tax + 42
    
    # Multiply by 365 days
    return result * 365
"""

# Fixture for complex code with magic numbers
@pytest.fixture
def complex_code_with_magic_numbers():
    return """
class Calculator:
    def __init__(self):
        # Initialize with default tax rate
        self.tax_rate = 0.085
    
    def calculate_area(self, radius):
        # Using pi
        return 3.14159 * radius * radius
    
    def calculate_tax(self, amount):
        return amount * self.tax_rate
    
    def calculate_yearly_total(self, amount, radius):
        area = self.calculate_area(radius)
        tax = self.calculate_tax(amount)
        # Add constants
        return (area + tax) * 365 + 42
"""

# Expected response fixtures
@pytest.fixture
def single_magic_number_response():
    return {
        'refactored_code': """
PI = 3.14159

def calculate_area(radius):
    # Calculate area of circle
    return PI * radius * radius

def calculate_tax(amount):
    # Calculate tax at 8.5%
    return amount * 0.085
""",
        'dependencies': None,
        'success': True,
        'error': None
    }

@pytest.fixture
def multiple_magic_numbers_response():
    return {
        'refactored_code': """
PI = 3.14159
TAX_RATE = 0.085
ANSWER = 42
DAYS_IN_YEAR = 365

def calculate_metrics(value):
    # Area calculation with pi
    area = PI * value * value
    
    # Tax calculation at 8.5%
    tax = value * TAX_RATE
    
    # Add 42 because it's the answer
    result = area + tax + ANSWER
    
    # Multiply by 365 days
    return result * DAYS_IN_YEAR
""",
        'dependencies': None,
        'success': True,
        'error': None
    }

@pytest.mark.asyncio
async def test_refactor_single_magic_number(simple_magic_number_code, single_magic_number_response):
    """Test refactoring a single magic number via the API."""
    url = f"{REFACTOR_SERVICE_URL}/refactor/magic-numbers"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": simple_magic_number_code,
            "magic_numbers": [
                {"magic_number": 3.14159, "line_number": 3}
            ]
        })
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = RefactorResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert "PI = 3.14159" in validated_response.refactored_code
        assert "return PI * radius * radius" in validated_response.refactored_code
        assert "3.14159" not in validated_response.refactored_code.split("\n")[3:]  # Skip the constant definition
        # The other magic number should remain unchanged
        assert "0.085" in validated_response.refactored_code
        
        expected_response = RefactorResponse(**single_magic_number_response)
        assert validated_response.refactored_code.strip() == expected_response.refactored_code.strip()
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_refactor_multiple_magic_numbers(multiple_magic_numbers_code, multiple_magic_numbers_response):
    """Test refactoring multiple magic numbers via the API."""
    url = f"{REFACTOR_SERVICE_URL}/refactor/magic-numbers"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": multiple_magic_numbers_code,
            "magic_numbers": [
                {"magic_number": 3.14159, "line_number": 3},
                {"magic_number": 0.085, "line_number": 6},
                {"magic_number": 42, "line_number": 9},
                {"magic_number": 365, "line_number": 12}
            ]
        })
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = RefactorResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert "PI = 3.14159" in validated_response.refactored_code
        assert "TAX_RATE = 0.085" in validated_response.refactored_code
        assert "ANSWER = 42" in validated_response.refactored_code
        assert "DAYS_IN_YEAR = 365" in validated_response.refactored_code
        
        assert "area = PI * value * value" in validated_response.refactored_code
        assert "tax = value * TAX_RATE" in validated_response.refactored_code
        assert "result = area + tax + ANSWER" in validated_response.refactored_code
        assert "return result * DAYS_IN_YEAR" in validated_response.refactored_code
        
        expected_response = RefactorResponse(**multiple_magic_numbers_response)
        assert validated_response.refactored_code.strip() == expected_response.refactored_code.strip()
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_refactor_duplicate_magic_numbers():
    """Test refactoring when the same magic number appears multiple times."""
    code = """
def duplicate_magic():
    x = 42
    y = x + 42
    z = y - 42
    return z + 42
"""
    url = f"{REFACTOR_SERVICE_URL}/refactor/magic-numbers"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": code,
            "magic_numbers": [
                {"magic_number": 42, "line_number": 3},
                {"magic_number": 42, "line_number": 4},
                {"magic_number": 42, "line_number": 5},
                {"magic_number": 42, "line_number": 6}
            ]
        })
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = RefactorResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        assert "MAGIC_NUMBER = 42" in validated_response.refactored_code  # Only one constant should be defined
        assert "x = MAGIC_NUMBER" in validated_response.refactored_code
        assert "y = x + MAGIC_NUMBER" in validated_response.refactored_code
        assert "z = y - MAGIC_NUMBER" in validated_response.refactored_code
        assert "return z + MAGIC_NUMBER" in validated_response.refactored_code
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")

@pytest.mark.asyncio
async def test_empty_magic_numbers_list(simple_magic_number_code):
    """Test with an empty list of magic numbers."""
    url = f"{REFACTOR_SERVICE_URL}/refactor/magic-numbers"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "code": simple_magic_number_code,
            "magic_numbers": []
        })
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = RefactorResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        # The code should remain unchanged
        assert validated_response.refactored_code.strip() == simple_magic_number_code.strip()
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")