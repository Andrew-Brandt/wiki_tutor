import anthropic
import os
import json
import re

# Load API Key
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Define Prompt Map
prompt_map = {
    "basic": "Your task is to rewrite the provided text so that young learners in grades 3-5 can easily read and understand it. Use simple words, short sentences, and clear explanations. Replace difficult words with familiar ones, and break down complex ideas in a fun and engaging way. If necessary, use relatable examples or comparisons to help children grasp the key concepts. Keep the summary short, clear, and enjoyable to read...",
    "intermediate": "Rewrite the given text for an audience of high school students (grades 9-12). Maintain the key ideas and important details, but simplify highly technical terms and complex sentence structures. Assume the reader has some background knowledge of the subject but still needs clear explanations for advanced concepts. Use a conversational yet informative tone, ensuring the text remains engaging and easy to follow...",
    "advanced": "Summarize the given text for an audience at the master’s degree level. Maintain academic rigor while ensuring clarity and conciseness. Preserve complex terminology but provide precise explanations where needed. Assume the reader has foundational knowledge in the subject, so focus on deeper insights, nuanced interpretations, and contextual significance. Keep the language formal, structured, and aligned with academic standards..."
}


def extract_json_from_text(response_text):
    """
    Extracts the JSON object from the response text by locating the first `{` and last `}`.
    Cleans the extracted JSON to remove any invalid control characters before parsing.
    """
    json_start = response_text.find("{")
    json_end = response_text.rfind("}")

    if json_start == -1 or json_end == -1:
        return None  # JSON not found in the response

    json_text = response_text[json_start:json_end + 1]  # Extract JSON substring

    # Remove control characters (e.g., newlines within JSON keys/values)
    json_text = re.sub(r"[\x00-\x1F]+", " ", json_text)

    return json_text


def summarize_text(text):
    """
    Summarizes a Wikipedia article at all three levels (Basic, Intermediate, Advanced),
    while handling unexpected LLM response structures.
    """
    prompt = f"""
    Summarize this Wikipedia article at three levels:


    Basic: {prompt_map['basic']}

    Intermediate: {prompt_map['intermediate']}

    Advanced: {prompt_map['advanced']}

    Article:
    {text}

    Return the summaries as a JSON object with "basic", "intermediate", and "advanced" keys.
    
    Do not preamble.
    """

    # Step 1: Measure Input Token Usage
    token_count = client.messages.count_tokens(
        model="claude-3-haiku-20240307",
        messages=[{"role": "user", "content": prompt}]
    )

    input_tokens = token_count.input_tokens  # Exact input tokens

    print(f"\nToken Usage Report (BEFORE API CALL):")
    print(f"Input Tokens: {input_tokens}")

    # Step 2: Call Claude
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    output_tokens = response.usage.output_tokens  # Exact output tokens

    print(f"Output Tokens: {output_tokens}")
    print(f"Total Tokens: {input_tokens + output_tokens}")
    print(f"DEBUG LLM RESPONSE: {response}")  # Print full response for debugging

    # Step 3: Extract JSON from Response
    try:
        if isinstance(response.content, list) and isinstance(response.content[0].text, str):
            json_text = extract_json_from_text(response.content[0].text)  # Extract JSON part
        elif isinstance(response.content, str):
            json_text = extract_json_from_text(response.content)  # Handle string response

        if not json_text:
            raise ValueError("No valid JSON found in response.")

        summaries_dict = json.loads(json_text)  # Convert JSON string to dictionary

        # Handle expected JSON structure correctly
        if not all(level in summaries_dict for level in ["basic", "intermediate", "advanced"]):
            raise ValueError("JSON is missing expected summary keys.")

        print(f"Successfully parsed summaries: {summaries_dict.keys()}")
        return summaries_dict
    except (json.JSONDecodeError, ValueError, AttributeError) as e:
        print(f"Error parsing response JSON: {e}")
        print(f"Unexpected LLM response structure: {response.content}")
        return None
