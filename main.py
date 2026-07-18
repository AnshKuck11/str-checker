from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from geocode import geocode_address
from cache import get_jurisdiction, list_pending, list_verified, approve, delete_jurisdiction, demote, init_db
from ai_research import research_jurisdiction
import asyncio

analyze_lock = asyncio.Lock()

init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    addresses: list[str]


def build_jurisdiction_key(county: str, municipality: str) -> str:
    return f"{municipality}, {county}"

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    async with analyze_lock:
        results = []

        for address in req.addresses:
            geo = geocode_address(address)

            if geo["error"] is not None:
                results.append({
                    "address": address,
                    "error": geo["error"],
                })
                continue

            key = build_jurisdiction_key(geo["county"], geo["municipality"])
            cached = get_jurisdiction(key)

            if cached is not None:
                cached["address"] = address
                cached["jurisdiction"] = key
                results.append(cached)
                continue

            researched = research_jurisdiction(key)

            if researched is None:
                results.append({
                    "address": address,
                    "jurisdiction": key,
                    "error": "could not find or extract STR rules for this jurisdiction",
                })
                continue

            researched["address"] = address
            researched["jurisdiction"] = key
            results.append(researched)

    return results

@app.get("/pending")
def pending():
    return list_pending()

@app.get("/verified")
def verified():
    return list_verified()


class ApproveRequest(BaseModel):
    jurisdiction: str


@app.post("/approve")
def approve_jurisdiction(req: ApproveRequest):
    approve(req.jurisdiction)
    return {"status": "ok"}

@app.post("/delete_jurisdiction")
def delete_jurisdiction_route(req: ApproveRequest):
    delete_jurisdiction(req.jurisdiction)
    return {"status": "ok"}


@app.post("/demote")
def demote_route(req: ApproveRequest):
    demote(req.jurisdiction)
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
        