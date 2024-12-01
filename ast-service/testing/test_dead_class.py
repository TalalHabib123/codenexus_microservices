import pytest
from endpoints_url import BASE_URL
from pydantic import ValidationError
import httpx
from app.main import app
from app.models.ast_models import DeadClassResponse

@pytest.fixture
def sample_code_dead_class_request():
    return {
        'code': """
class DeadClass:
    def __init__(self):
       self.x = 10
       self.y = 20
    
    def complex_method(self, a, b, c, d, e, f):
        # Multiple nested conditions that are unlikely to be executed
        if (a > 10) and (b < 5):
            if (c == 1):
                if (d != 0):
                    if (e in range(5)):
                        if (f == True):
                            print("This nested conditional is unlikely to execute")
                            return True
        return False
""",
        'class_name': 'DeadClass'
    }

@pytest.fixture
def sample_code_no_dead_class_request():
    return {
        'code': """
class ActiveClass:
    def __init__(self):
       self.x = 10
       self.y = 20
    
    def complex_method(self, a, b, c, d, e, f):
        # Multiple nested conditions that are unlikely to be executed
        if (a > 10) and (b < 5):
            if (c == 1):
                if (d != 0):
                    if (e in range(5)):
                        if (f == True):
                            print("This nested conditional is unlikely to execute")
                            return True
        return False
        
active = ActiveClass()
active.complex_method(10, 4, 1, 1, 3, True)
""",
        'class_name': 'ActiveClass'
    }

@pytest.fixture
def dead_class_response():
    return {
        'class_details': {
            'methods': [],
            'variables': []
        },
        'success': True,
        'error': None
    }

@pytest.fixture
def no_dead_class_response():
    return {
        'class_details': {
            'methods': ['complex_method'],
            'variables': []
        },
        'success': True,
        'error': None
    }
@pytest.mark.asyncio
async def test_sample_dead_class_code(sample_code_dead_class_request, dead_class_response):
    url = f"{BASE_URL}/dead-class"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url, 
            json=sample_code_dead_class_request
        )
        
        assert response.status_code == 200
    
    try:
        response_data = response.json()
        validated_response = DeadClassResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        expected_response = DeadClassResponse(**dead_class_response)
        
        assert validated_response.class_details == expected_response.class_details
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e} {response.json()}")

@pytest.mark.asyncio
async def test_sample_active_class_codee(sample_code_no_dead_class_request, no_dead_class_response):
    url = f"{BASE_URL}/dead-class"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url, 
            json=sample_code_no_dead_class_request
        )
        
        assert response.status_code == 200
    
    try:
        response_data = response.json()
        validated_response = DeadClassResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        expected_response = DeadClassResponse(**no_dead_class_response)
        assert validated_response.class_details == expected_response.class_details
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failsed: {e}")