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
    existing_calls = task_data.get("additional_data", None)

    # Retrieve any relevant documentation for the "Long Parameter List" code smell
    relevant_docs = retrieve_relevant_refactoring_docs_for_(
        "Long Parameter List",
        code_snippet,
        knowledge_base_refactoring,
        nn_model
    )
    
    SEP_OBJ   = "# === PARAM_OBJECT_SECTION ==="      # <─ surround the parameter-object/class
    SEP_CALLS = "# --- CALL_SITE_SEPARATOR ---"       # <─ between successive call-sites

    # ── Prompt template ────────────────────────────────────────────────────────────
    content = f"""
You will now refactor the following Python code snippet to eliminate the
*Long Parameter List* code smell while adhering to the system's guidelines.

1. **Provide exactly ONE code block** that contains the **COMPLETE** refactored
   definition of the function (or methods) in its final form.
2. For **each file** listed under *Existing Call-Sites* you must return
   **exactly ONE code block** – in the **same order** they appear below –
   that follows the template shown under **“Call-Site Block Format”**.
3. If **no call sites** are provided, output only the refactored function
   block.  
4. Do **NOT** introduce new functionality; behaviour must remain identical.  
5. Prefer parameter objects, small data-classes, or dictionaries to reduce
   argument count while keeping the code Pythonic and clear.

---

### Call-Site Block Format (required verbatim)

```python
{SEP_OBJ}
# ANY IMPORTS REQUIRED FOR BELOW CODE SHOULD BE ADDED HERE AS WELL (dataclass and any other import should be added after the above block)
# If you introduced a parameter object / data-class,
# place the FULL class definition here.
# should be repeated for each python block
{SEP_OBJ}
{SEP_CALLS}
# <original call-site 1>
<refactored call-site 1>
{SEP_CALLS}
# <original call-site 2>
<refactored call-site 2>
{SEP_CALLS}
# … repeat as needed …
{SEP_CALLS}
```

* Rules for the block above  
  • **Include** the object/class section only when an object-based refactor
    was required; otherwise keep the two `{SEP_OBJ}` lines empty.  
  • Preserve every original call-site as a comment (`# …`) immediately
    followed by its refactored invocation.  
  • Use `{SEP_CALLS}` **exactly** as shown to separate multiple call-sites.
  • DONT FORGET to include the `SEP_OBJ` and `SEP_CALLS` lines in your output. BOTH STARTING AND ENDING LINES ARE REQUIRED.

---

Here is the primary Python code that needs refactoring:

```python
{code_snippet}
```
""".strip()

    # ── Attach existing call-sites, one file per block ─────────────────────────────
    if existing_calls and isinstance(existing_calls, dict) and existing_calls:
        content += (
            "\n\n---\n### Existing Call-Sites (one block per file)\n"
            "Each block below represents all call-sites found in that file and "
            "must be returned refactored in the same order:"
        )
        for idx, (file_path, call_block) in enumerate(existing_calls.items(), start=1):
            content += (
                f"\n\n**File {idx}: `{file_path}`**\n"
                "```python\n"
                f"{call_block}\n"
                "```"
            )

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