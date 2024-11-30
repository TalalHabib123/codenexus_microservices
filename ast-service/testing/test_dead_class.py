import pytest
from endpoints_url import BASE_URL
from pydantic import ValidationError
import httpx
from app.main import app
from app.models.ast_models import DeadClassResponse, ClassDetails

@pytest.fixture
def sample_code_dead_class():
    return """
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
"""

@pytest.fixture
def sample_code_no_dead_class():
    return """
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
"""

@pytest.fixture
def active_and_dead_class():
    return """
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
"""



@pytest.fixture
def dead_class_response():
    return {
        'conditionals': [
            {
                'line_range': (2, 7),
                'condition_code': '(a > 10) and (b < 5)',
                'complexity_score': 4,
                'code_block': 'if (a > 10) and (b < 5):\n    if (c == 1):\n        if (d != 0):\n            if (e in range(5)):\n                if (f == True):\n                    print("Nested conditionals!")\n'
            },
            {
                'line_range': (3, 7),
                'condition_code': '(c == 1)',
                'complexity_score': 1,
                'code_block': 'if (c == 1):\n        if (d != 0):\n            if (e in range(5)):\n                if (f == True):\n                    print("Nested conditionals!")\n'
            },
            {
                'line_range': (4, 7),
                'condition_code': '(d != 0)',
                'complexity_score': 1,
                'code_block': 'if (d != 0):\n            if (e in range(5)):\n                if (f == True):\n                    print("Nested conditionals!")\n'
            },
            {
                'line_range': (6, 7),
                'condition_code': '(f == True)',
                'complexity_score': 1,
                'code_block': 'if (f == True):\n                    print("Nested conditionals!")\n'
            }
        ],
        'success': True,
        'error': None
    }

@pytest.fixture
def no_dead_class_response():
    return {
        'conditionals': [],
        'success': True,
        'error': None
    }


@pytest.fixture
def active_dead_classes_response():
    return {
        'conditionals': [
            {
                'line_range': (2, 3),
                'condition_code': '(x > 5) and (y < 10)',
                'complexity_score': 2,
                'code_block': 'if (x > 5) and (y < 10):\n    print("This is borderline complex")\n'
            }
        ],
        'success': True,
        'error': None
    }



@pytest.mark.asyncio
async def test_overly_complex_conditionals(sample_code_dead_class, dead_class_response):
    url = f"{BASE_URL}/dead-class"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_code_dead_class})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = DeadClassResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        dead_class_response = DeadClassResponse(**dead_class_response)
        assert validated_response == dead_class_response
            
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")



@pytest.mark.asyncio
async def test_not_complex_conditionals(sample_code_no_dead_class, no_dead_class_response):
   
    url = f"{BASE_URL}/dead-class"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": sample_code_no_dead_class})
    assert response.status_code == 200

    try:
        response_data = response.json()
        validated_response = no_dead_class_response(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
            
        no_dead_class_response = DeadClassResponse(**no_dead_class_response)
        assert validated_response ==  no_dead_class_response
        
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")


@pytest.mark.asyncio
async def test_active_dead_classes(active_and_dead_class, active_dead_classes_response):
    url = f"{BASE_URL}/dead-class"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"code": active_and_dead_class})
    
    assert response.status_code == 200

    try:
        response_data = response.json()
        
        validated_response = DeadClassResponse(**response_data)
        
        assert validated_response.success is True
        assert validated_response.error is None
        
        active_dead_classes_response = DeadClassResponse(**active_dead_classes_response)
        assert validated_response == active_dead_classes_response
        
        
    
    except ValidationError as e:
        print(f"Response validation failed: {e}")
        pytest.fail(f"Response validation failed: {e}")
