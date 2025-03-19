from utils.content_prompt.detection.utils.retrieve_relevant_docs import retrieve_relevant_refactoring_docs_for_

def create_long_parameter_list_content(task_data, knowledge_base_refactoring, nn_model):
    """
    Creates the user-facing prompt content for refactoring Python code
    to remove the 'Long Parameter List' code smell. Incorporates the
    updated system guidance on how the LLM should structure output,
    and ensures no additional code blocks are generated if no call sites
    are provided.
    """
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
You will now refactor the following Python code snippet to eliminate the 'Long Parameter List' code smell while adhering to the system's guidelines. Specifically:

1. **Provide exactly one code block** containing the **complete** refactored snippet.
2. For **each** existing call site below, produce **one separate** code block reflecting the updated invocation in the **same order** it is provided.
3. If **no call sites** are provided, output **only** the refactored code snippet in one code block.
4. Do **not** introduce new functionality; the logic and behavior must remain the same.
5. Use parameter objects, dictionaries, or classes to reduce parameter counts while keeping the code Pythonic and clear.

Here is the primary Python code that needs refactoring:

```python
{code_snippet}
```
""".strip()
    if existing_calls:
        content += (
            "\n\nBelow are the existing call sites (invocations) for this snippet. "
            "After refactoring, you must update each to match the new parameter structure. "
            "Each updated set of calls must be placed in its own separate code block, in the same order:\n"
        )
        for i, call_data in enumerate(existing_calls, start=1):
            content += f"\n**Call Site {i}:**\n```python\n{call_data}\n```"

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