import os
from dotenv import load_dotenv
from openai import OpenAI
import json

SYSTEM_PROMPT = """You are extracting short-term rental (STR) regulations from Wisconsin \
government ordinance text. Wisconsin state law (Wis. Stat. 66.1014) already guarantees: \
STR cannot be banned for stays of 7+ consecutive days anywhere in the state; local governments \
may only restrict total rental days per year to a floor of 180 days minimum; a local license can \
only be required if rented more than 10 nights/year.

Read the provided text and respond with ONLY a JSON object, no markdown fences, no preamble, \
matching this exact schema:

{
  "relevant": true | false,
  "str_allowed": true | false | null,
  "permit_required": true | false | null,
  "min_stay_days": integer | null,
  "max_days_per_year": integer | null,
  "fees": string | null,
  "other_requirements": [string, ...],
  "source_quotes": [
    {"claim": string, "quote": string},
    ...
   ],
  "confidence": integer from 1 to 10,
  "notes": string | null
}

Rules:
- If the text doesn't clearly address something, use null and explain why in notes.
- source_quote must be actual text copied from what's provided, never invented.
- confidence below 7 means a human should double check this.
- Include at least 2-3 source_quotes, each pairing a specific claim (e.g. "minimum stay", "permit required") with the exact verbatim text that supports it.
- relevant: true only if this text actually discusses STR/tourist-rooming-house regulations for this specific jurisdiction. 
    false if the page is unrelated, generic, or contains no regulatory content at all — in that case, confidence should reflect how sure you are that it's irrelevant, but relevant must still be false.
- If the text is for a DIFFERENT municipality than the one specified, set relevant to false,
  regardless of topic similarity.
- If the text only references that an STR ordinance exists (a title, a table-of-contents entry,
  a "click here" link) without providing its actual substantive content, cap confidence at 5 —
  this means "I found a lead" but not "I found the answer," which should NOT stop the search
  for a better source.
"""

load_dotenv()

client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def extract_str_rules(jurisdiction: str, page_text: str) -> dict | None:
    page_text = page_text[:28000]
    user_prompt = f"Jurisdiction: {jurisdiction}\n\nOrdinance text:\n\n{page_text}"

    try:
        response = client.chat.completions.create(
            model="gemini-3.1-flash-lite",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
    except Exception as e:
        print(f"[extract_str_rules] API call failed: {e}")
        return None

    raw = response.choices[0].message.content

    try:
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        print(f"[extract_str_rules] failed to parse model response")
        print(f"[debug] raw response: {raw}") #make sure to remove this before actually deploying
        return None
    
    required_keys = ["relevant", "str_allowed", "permit_required", "min_stay_days", "max_days_per_year", "fees", "other_requirements", "source_quotes", "confidence", "notes"]

    if all(key in result for key in required_keys):
        return result
    else:
        missing = [key for key in required_keys if key not in result]
        print(f"[extract_str_rules] malformed dict, missing: {missing}")
        return None



# def ask_groq(prompt: str) -> str:
#     response = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[
#             {"role": "user", "content": prompt}
#         ]
#     )
#     return response.choices[0].message.content




if __name__ == "__main__":
    from fetch_page import fetch_page_text
    text = fetch_page_text("https://merrimacwi.gov/vertical/sites/{CBEFE108-6CEC-4014-B024-0697DD562493}/uploads/Village_of_Merrimac_Short_Term_Rental_and_Municipal_Room_Tax_Ordinances(4).pdf")
    result = extract_str_rules("Village of Merrimac, Sauk County", text)
    print(result)
