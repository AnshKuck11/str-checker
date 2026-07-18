import httpx
import trafilatura
from pypdf import PdfReader
import io

def extract_pdf_text(pdf_bytes: bytes) -> str | None:
    reader = PdfReader(io.BytesIO(pdf_bytes))

    pages_text = []

    for page in reader.pages:
        pages_text.append(page.extract_text())
    
    full_text = "\n".join(pages_text)

    return full_text if full_text.strip() else None

def fetch_page_text(url: str) -> str | None:
    try:
        response = httpx.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    except httpx.RequestError:
        return None

    if response.status_code != 200:
        return None

    content_type = response.headers.get("content-type", "")

    if "application/pdf" in content_type:
        return extract_pdf_text(response.content)

    text = trafilatura.extract(response.text)
    return text

if __name__ == "__main__":
    text = fetch_page_text("https://merrimacwi.gov/vertical/sites/{CBEFE108-6CEC-4014-B024-0697DD562493}/uploads/Village_of_Merrimac_Short_Term_Rental_and_Municipal_Room_Tax_Ordinances(4).pdf")
    print(text[:1000] if text else "no text extracted")

    


