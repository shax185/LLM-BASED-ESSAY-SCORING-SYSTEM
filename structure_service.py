import os
import json
from llm_config import llm  # Import the initialized LLM

def generate_essay_structure(topic, difficulty):
    """Generates an essay structure dynamically based on difficulty level."""

    prompt = f"""
    Generate a structured essay outline for the topic: "{topic}" at {difficulty} difficulty level.
    - Adjust complexity appropriately for the given difficulty.
    - Ensure total weightage is exactly **100%**.
    - Allow users to modify the structure (add/remove arguments).
    
    Output JSON format:
    {{
        "topic": "{topic}",
        "difficulty": "{difficulty}",
        "structure": {{
            "Grammar, Coherence & Readability": {{"weight": 20, "details": ["Grammar accuracy", "Logical flow", "Readability"]}},
            "Introduction": {{"weight": 10, "details": ["Hook", "Background", "Essay statement"]}},
            "Main Body": {{
                "weight": 60,
                "arguments": [
                    {{"name": "Key Argument 1", "weight": 20, "details": ["Discussion with examples"]}},
                    {{"name": "Key Argument 2", "weight": 20, "details": ["Supporting facts"]}},
                    {{"name": "Counterarguments", "weight": 10, "details": ["Opposing viewpoints"]}}
                ]
            }},
            "Conclusion": {{"weight": 10, "details": ["Summary", "Restating essay", "Final thoughts"]}}
        }}
    }}
    """
    
    response = llm.invoke(prompt)
    return response.content  # Ensure parsed JSON in API


def edit_essay_structure(original_structure, current_structure, user_edits, previous_edits=""):
    """
    Edits the essay structure incrementally.
    - Ensures weight remains 100%.
    - Keeps track of previous modifications.
    - Returns only the modified sections with a summary of changes.
    """
    prompt = f"""
    You are modifying an essay structure **without altering its logical flow**. 
    Apply the requested modifications **on top of the most recent version** while keeping past edits intact.

    ### **Original Structure**
    {original_structure}

    ### **Current Version (Most Recent)**
    {current_structure}

    ### **User Edits**
    {user_edits}

    ### **Editing Guidelines**
    - Apply changes incrementally without discarding previous edits.
    - Ensure **total weightage remains exactly 100%**.
    - Adjust weight distribution proportionally if a section is removed/increased.
    - Do **not** add new sections unless explicitly requested.
    - Return a **structured JSON output**:
      {{
          "updated_structure": {{
              "section_name": {{"weight": X, "details": ["Updated details"]}}
          }},
          "modifications": ["Step-by-step changes applied"]
      }}
    """
    response = llm.invoke(prompt)
    return response.content  # Ensure it's parsed JSON
