from utils.system_prompts.import_system_prompt import ( 
    system_detection_prompts,
    system_refactoring_prompts
)

from utils.content_prompt.import_content_prompt import (
    content_detection_prompts,
    content_refactoring_prompts
)                


def create_detection_prompt(task_job, task_data, knowledge_base_detection, nn_model):
    content_prompt = {}
    system_prompt = {}
    processed_data = task_data
    
    content_prompt, content_prompt_addtional ,processed_data = content_detection_prompts[task_job](task_data, 
                                                                                                   knowledge_base_detection, 
                                                                                                   nn_model)
    system_prompt = system_detection_prompts[task_job]
        
    prompt = [
        system_prompt,
        content_prompt
    ]
    
    secondary_prompt = [
        system_prompt,
        content_prompt_addtional
    ]
    return prompt, secondary_prompt, processed_data

def create_refactoring_prompt(task_job, task_data, knowledge_base_refactoring, nn_model):
    content_prompt = {}
    system_prompt = {}
    
    content_prompt= content_refactoring_prompts[task_job](task_data, 
                                                            knowledge_base_refactoring, 
                                                            nn_model)
    system_prompt = system_refactoring_prompts[task_job]
        
    prompt = [
        system_prompt,
        content_prompt
    ]
    return prompt


def create_prompt(task_type, 
                  task_data, 
                  task_job, 
                  knowledge_base, 
                  nn_model):
    
    if task_type == "detection":
        return create_detection_prompt(task_job, task_data, knowledge_base, nn_model)
    
    elif task_type == "refactoring":
        return create_refactoring_prompt(task_job, task_data, knowledge_base, nn_model)
    

def final_prompt(prompt, task_type, task_data):
    if task_type == "detection":
        return detection_cleaning_prompt(prompt, task_data)

    elif task_type == "refactoring":
        return refactoring_verification_prompt(prompt, task_data)
    
    
def update_prompt(previous_prompt, previous_prompt_answer, additional_prompt, additional_prompt_answer):
    # Define the system prompt with clear instructions
    system_prmpt = previous_prompt[0]

    # Construct the new prompt with optimized and clear language
    new_prompt = """
You are tasked with analyzing and validating two sets of prompts and answers provided below. Your job is to determine whether the answers are correct based on the detection task outlined in the prompts.

### Task Description:
1. Analyze both prompts and their corresponding answers.
2. Verify if the answers correctly identify the presence of the specified code smell in the provided code snippets.
3. Only return detections that are positive and confirm the presence of the code smell.

### Important Guidelines:
- **Correct Answer**: Means the detection is positive, and the code smell is definitively present in the code snippet.
- If an answer includes any statements like "maybe" or "may not be" followed by a conclusion that the smell is absent, omit it from the new response.
- Ensure that all valid detections are returned in the exact format as originally provided.
- The Answer you will return should be in accordance to the prompts provided, by that the exact format specified within the prompts!

### Inputs:
Here is the first prompt:
{previous_prompt[1]}

Here is the first answer:
{previous_prompt_answer}

Here is the second prompt:
{additional_prompt[1]}

Here is the second answer:
{additional_prompt_answer}
""".format(
        previous_prompt=previous_prompt,
        previous_prompt_answer=previous_prompt_answer,
        additional_prompt=additional_prompt,
        additional_prompt_answer=additional_prompt_answer
    )

    return [
        system_prmpt,
        {
            "role": "user",
            "content": new_prompt.strip()
        }
    ]

    
def detection_cleaning_prompt(prompt_ans, task_data):
    # Define the system prompt with clear instructions
    system_prompt = """
You are an expert at making logical deductions. You will be tasked with analyzing the provided answer to determine whether it is junk or valid.
You will also clean and reformat the answer to make it more readable and understandable while ensuring it adheres strictly to the specified format.

### Format for the Answer:
File:{ file_name.py }
Detected:{CLASSNAME.FUNCTIONNAME or FUNCTIONNAME}
Issue:{A brief description of why it's considered long (e.g., multiple responsibilities, too many lines, excessive nesting)}

### Key Guidelines:
1. The cleaned answer must strictly follow the above format.
2. Use only the data from the provided answer; do not add any new information.
3. Any data outside the specified format should be removed.
4. The Answer should also be consistent with the provided Code Smell as well:
    The Code Smell whose analysis is being provided is: 
"""
    system_prompt += task_data
    
    system_prompt += """
    Ensure that the Analysis being done and the answer being provided is consistent with the Code Smell provided above.
    If the answer is correct, return it as is. If it is incorrect, clean and reformat it to adhere to the specified format.
5. Ensure that the cleaned answer is clear, concise, and free of any irrelevant information.
"""


    # Construct the user prompt with optimized clarity
    user_prompt = """
You are tasked with analyzing the provided answer to determine if it is correct. You will clean and reformat the answer to make it more readable and ensure it follows the specified format.

### Format for the Answer:
File:{ file_name }.py
Detected:{CLASSNAME.FUNCTIONNAME or FUNCTIONNAME}
Issue:{A brief description of why it's considered long (e.g., multiple responsibilities, too many lines, excessive nesting)}

This is the generic format. All data should be derived from the existing answer provided below.

Here is the answer you will be analyzing and cleaning:\n
"""

    user_prompt += prompt_ans

    return [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt.strip()
        }
    ]

   
def refactoring_verification_prompt(prompt, task_data):
    # Define the system prompt with clear instructions
    system_prompt = """
You are a coding specialist with extensive knowledge of Python programming. You will receive refactored code and the original code it was derived from. Your task is to verify if the refactoring is correct by comparing it to the original code. If the refactoring is absolutely correct, return `None` (just `None`, nothing else). If there is an issue with the refactoring, fix the errors using the original code and return the corrected refactoring in the format:

```python
{ refactored_code }
```
"""

    user_prompt = """
I will provide you with refactored code along with the original code it was derived from. 
Your task is to determine whether the refactoring is correct. 
If there are issues, correct them using the original code and return the fixed version.
However, if the refactoring is correct, simply return `None` (just `None`, nothing else).

Here is the original code: ```python
{original_code}
```
Here is the refactored code: ```python
{refactored_code}
```
""".format(
        original_code=task_data.get('original_code', 'No original code provided'),
        refactored_code=prompt
    )

    return [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    

        