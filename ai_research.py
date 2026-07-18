from search_sources import search_ordinance
from fetch_page import fetch_page_text
from extract import extract_str_rules
from cache import save_draft
import time

def research_jurisdiction(jurisdiction: str) -> dict | None:
    urls = search_ordinance(jurisdiction)

    if not urls:
        print(f"[research] no search results for {jurisdiction}")
        return None

    best_result = None
    best_url = None
    best_irrelevant = None

    for url in urls:
        print(f"[research] trying {url}")
        text = fetch_page_text(url)

        if text is None or len(text) < 200:
            continue

        result = extract_str_rules(jurisdiction, text)

        if result is None:
            continue

        time.sleep(4.5)

        if result["relevant"]:
            if best_result is None or result["confidence"] > best_result["confidence"]:
                best_result = result
                best_url = url
                print(f"[research] new best so far: confidence {result['confidence']} from {url}")

            if best_result["confidence"] >= 7:
                print(f"[research] good enough, stopping early")
                break
        else:
            if best_irrelevant is None or result["confidence"] > best_irrelevant["confidence"]:
                best_irrelevant = result

    if best_result is not None:
        best_result["source_url"] = best_url
        best_result["status"] = "pending"
        save_draft(jurisdiction, best_result)
        return best_result

    if best_irrelevant is not None:
        print(f"[research] nothing relevant found for {jurisdiction} — not saving to cache")
        best_irrelevant["source_url"] = None
        return best_irrelevant

    print(f"[research] all candidates failed for {jurisdiction}")
    return None

if __name__ == "__main__":
    result = research_jurisdiction("Village of Merrimac, Sauk County")
    print(result)