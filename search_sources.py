from ddgs import DDGS

def search_ordinance(jurisdition: str) -> list[str]:
    query = f"{jurisdition} Wisconsin short term rental ordinance"

    with DDGS() as ddgs:
        results = ddgs.text(query, max=7)
    
    urls = [r["href"] for r in results][:7]
    return urls

if __name__ == "__main__":
    result_urls = search_ordinance("Sauk County")
    for url in result_urls:
        print(url)