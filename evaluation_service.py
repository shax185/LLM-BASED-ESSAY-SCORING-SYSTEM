from llm_config import llm  # Import the initialized LLM
import json
import re

def evaluate_essay(essay_text, rubric):
    """
    Evaluates the essay based on finalized rubrics.
    - Uses rubric-defined weight distribution for content & grammar.
    - Ensures total weight remains exactly 100%.
    """

    # Extract rubric-defined weightages
    grammar_weight = rubric.get("Grammar, Coherence & Readability", {}).get("weight", 20)
    content_weight = 100 - grammar_weight  # Ensure total = 100%

    prompt = f"""
    Evaluate the following essay based on the finalized rubric.

    ### **Essay Text:**
    {essay_text}

    ### **Finalized Rubric Weightage**
    - **Content Score ({content_weight}%)**: Based on structure alignment, argument depth, and coherence.
    - **Grammar, Coherence & Readability Score ({grammar_weight}%)**: Based on overall fluency, grammar correctness, and readability.
    - Total score must sum to **100%**.

    Output JSON format:
    {{
        "total_score": X,
        "section_scores": {{
            "Grammar, Coherence & Readability": {{ "score": Y }},
            "Introduction": {{ "score": Z }},
            "Main Body": {{ "score": A }},
            "Conclusion": {{ "score": B }}
        }},
        "feedback": {{
            "grammar_feedback": "Grammar feedback here...",
            "content_feedback": "Content feedback here..."
        }}
    }}
    """

    response = llm.invoke(prompt)
    if not response or not response.content.strip():
        raise ValueError("❌ Empty response from LLM in evaluation_service.")

    try:
        # Try to parse from markdown-style block
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response.content, re.DOTALL)
        json_text = match.group(1) if match else response.content.strip()

        print("🧪 Raw Evaluation Response:\n", response.content)
        return json.loads(json_text)

    except Exception as e:
        print("❌ Failed to parse LLM evaluation response:")
        print(response.content)
        raise e
