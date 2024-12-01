import pytest
from endpoints_url import BASE_URL
from pydantic import ValidationError
import httpx
from app.main import app
from app.models.ast_models import ConditionDetails, ComplexConditonalResponse

# Fixture for overly complex code with many nested conditionals
@pytest.fixture
def sample_code_overly_complex():
    return """
if (a > 10) and (b < 5):
    if (c == 1):
        if (d != 0):
            if (e in range(5)):
                if (f == True):
                    print("Nested conditionals!")
"""

# Fixture for simple, non-complex code
@pytest.fixture
def sample_code_not_complex():
    return """
x = 10
y = 20
result = x + y
print(result)
"""

# Fixture for borderline complex code
@pytest.fixture
def sample_code_complex_border():
    return """
if (x > 5) and (y < 10):
    print("This is borderline complex")
"""

@pytest.fixture
def overly_complex_response():
    return {
        'conditionals': [
            {
                'line_range': (2, 7),
                'condition_code': '(a > 10 and b < 5)',
                'complexity_score': 4,
                'code_block': 'if (a > 10) and (b < 5):\n    if (c == 1):\n        if (d != 0):\n            if (e in range(5)):\n                if (f == True):\n                    print("Nested conditionals!")\n'
            },
        ],
        'success': True,
        'error': None
    }

@pytest.fixture
def not_complex_response():
    return {
        'conditionals': [],
        'success': True,
        'error': None
    }


@pytest.fixture
def complex_border_response():
    return {
        'conditionals': [
            {
                'line_range': (2, 3),
                'condition_code': '(x > 5 and y < 10)',
                'complexity_score': 4,
                'code_block': 'if (x > 5) and (y < 10):\n    print("This is borderline complex")\n'
            }
        ],
        'success': True,
        'error': None
    }



@pytest.mark.asyncio
async def test_overly_complex_conditionals(sample_code_overly_complex, overly_complex_response):
    """Test case for analyzing overly complex conditionals."""
    url = f"{BASE_URL}/overly-complex-conditionals"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_code_overly_complex})
    
    assert response.status_code == 200

    # Validate the response against the ComplexConditonalResponse model
    try:
        response_data = response.json()
        
        # Parse response data into the Pydantic model
        validated_response = ComplexConditonalResponse(**response_data)
        
        # Assert the success and error fields
        assert validated_response.success is True
        assert validated_response.error is None
        
        # Assert that 'conditionals' is a list and contains instances of ConditionDetails
        assert isinstance(validated_response.conditionals, list)
        assert len(validated_response.conditionals) > 0  # Ensure that there are conditionals detected
        overly_complex_response = ComplexConditonalResponse(**overly_complex_response)
        assert validated_response == overly_complex_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")



@pytest.mark.asyncio
async def test_not_complex_conditionals(sample_code_not_complex, not_complex_response):
    """Test case for analyzing non-complex conditionals."""
    url = f"{BASE_URL}/overly-complex-conditionals"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_code_not_complex})
    assert response.status_code == 200

    # Validate the response against the ComplexConditonalResponse model
    try:
        response_data = response.json()
        # Parse response data into the Pydantic model
        validated_response = ComplexConditonalResponse(**response_data)
        
        # Assert the success and error fields
        assert validated_response.success is True
        assert validated_response.error is None
        
        # Assert that 'conditionals' is a list and contains instances of ConditionDetails
        assert isinstance(validated_response.conditionals, list)
        for conditional in validated_response.conditionals:
            assert isinstance(conditional, ConditionDetails)
            
        not_complex_response = ComplexConditonalResponse(**not_complex_response)
        assert validated_response ==  not_complex_response
        
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")


@pytest.mark.asyncio
async def test_complex_border_conditionals(sample_code_complex_border, complex_border_response):
    """Test case for analyzing borderline complex conditionals."""
    url = f"{BASE_URL}/overly-complex-conditionals"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_code_complex_border})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        
        # Parse response data into the Pydantic model
        validated_response = ComplexConditonalResponse(**response_data)
        
        # Assert the success and error fields
        assert validated_response.success is True
        assert validated_response.error is None
        
        # Assert that 'conditionals' is a list and contains instances of ConditionDetails
        assert isinstance(validated_response.conditionals, list)
        complex_border_response = ComplexConditonalResponse(**complex_border_response)
        assert validated_response == complex_border_response
        
        
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")
