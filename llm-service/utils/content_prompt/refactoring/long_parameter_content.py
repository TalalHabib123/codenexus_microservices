from utils.content_prompt.detection.utils.retrieve_relevant_docs import retrieve_relevant_refactoring_docs_for_

def create_long_parameter_list_content(task_data, knowledge_base_refactoring, nn_model):
    # Extract the code snippet and existing calls from the task data
    code_snippet = task_data.get("code_snippet", "")
    existing_calls = task_data.get("additonal_data", [])

    # Retrieve any relevant documentation for the "Long Parameter List" code smell
    relevant_docs = retrieve_relevant_refactoring_docs_for_(
        "Long Parameter List",
        code_snippet,
        knowledge_base_refactoring,
        nn_model
    )

    # Build the main content of the user prompt
    content = f"""
You will now refactor the following Python code snippet to eliminate the 'Long Parameter List' code smell while adhering to the system's guidelines. Preserve the logic and functionality, but use parameter objects or other strategies to reduce and group parameters. Clearly document the changes you make as specified in the system prompt.

Here is the primary Python code that needs refactoring:

```python
{code_snippet}
```
Below are the existing call sites (invocations) for this snippet. They are provided in a specific order. After refactoring, you must update these invocations to match the new parameter structure or objects you introduce. Each updated set of calls must be placed in its own separate code block, in the same order:

""".strip()

    for i, call_data in enumerate(existing_calls, start=1):
        content += f"\n\n**Call Site {i}:**\n```python\n{call_data}\n```"

    # If we have additional references, append them
    if relevant_docs:
        content += "\n\n### Additional References:\n"
        content += "If applicable, use the following documents for guidance on refactoring 'Long Parameter List':\n\n"
        for index, doc in enumerate(relevant_docs, start=1):
            for key, value in doc.items():
                content += (
                    f"Reference {index} - {key}:\n\n"
                    "```\n"
                    f"{value}\n"
                    "```\n\n"
                )

    return {
        "role": "user",
        "content": content
    }
