from llm_config import llm  # Import the initialized LLM
import json
import re

def generate_feedback(essay_text, structure):
    """
    Generates feedback based on the finalized essay structure.
    - Uses structure as the rubric.
    - Provides section-wise feedback.
    - Evaluates content relevance, coherence, and readability.
    """

    prompt = f"""
    ALWAYS RETURN JSON
    Return ONLY the following JSON inside a ```json fenced code block.
    Do NOT include any explanation or introduction.

    Evaluate the following essay based on its finalized structure.

    ### **Essay Text:**
    {essay_text}

    ### **Finalized Structure (Used as Rubric)**
    {json.dumps(structure, indent=4)}

    ### **Feedback Guidelines**
    - Provide **section-wise feedback** (Introduction, Main Body, Conclusion).
    - Highlight **strengths** (e.g., good coherence, strong arguments).
    - Point out **areas for improvement** (e.g., missing key arguments, weak transitions).
    - Provide **grammar and readability suggestions** separately.
    - Keep feedback **concise yet informative**.

    ### **Expected Output**
    {{
        "feedback": {{
            "Grammar, Coherence & Readability": "Grammar is mostly correct, but some sentences lack clarity.",
            "Introduction": "Strong hook, but lacks a clear essay statement.",
            "Main Body": {{
                "Key Argument 1": "Well-explained with good examples.",
                "Key Argument 2": "Needs more supporting evidence.",
                "Counterarguments": "Missing a rebuttal to the opposing view."
            }},
            "Conclusion": "Good summary but could reinforce key points more strongly."
        }}
    }}
    """

    response = llm.invoke(prompt)
    if not response or not response.content.strip():
        raise ValueError("❌ Empty response from LLM in feedback_service.")


    try:
        # Extract JSON block if it's wrapped in ```json ... ```
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response.content, re.DOTALL)
        json_text = match.group(1) if match else response.content.strip()
        print("🔍 Raw LLM output:\n", response.content)

        return json.loads(json_text)

    except Exception as e:
        print("❌ Failed to parse LLM response in feedback_service.py:")
        print(response.content)
        raise e
