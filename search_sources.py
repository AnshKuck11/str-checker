import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SERPAPI_API_KEY = os.environ["SERPAPI_API_KEY"]

def search_ordinance(jurisdiction: str) -> list[str]:
    query = f"{jurisdiction} Wisconsin short term rental ordinance"

    try:
        response = httpx.get(
            "https://serpapi.com/search",
            params={
                "engine": "google",
                "q": query,
                "api_key": SERPAPI_API_KEY,
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        print(f"Search failed: {e}")
        return []

    return [r["link"] for r in data.get("organic_results", [])][:7]


if __name__ == "__main__":
    jurisdiction = "Sauk County"

    print(f"Searching for: {jurisdiction}")
    urls = search_ordinance(jurisdiction)

    if not urls:
        print("No results returned.")
    else:
        print(f"\nFound {len(urls)} result(s):\n")
        for i, url in enumerate(urls, start=1):
            print(f"{i}. {url}")