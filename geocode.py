import httpx

CENSUS_URL = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"

def geocode_address(address: str) -> dict:
    params = {
        "address": address,
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "layers": "Counties,Incorporated Places,County Subdivisions",
        "format": "json"
    }

    try:
        response = httpx.get(CENSUS_URL, params=params, timeout=15)
    except httpx.RequestError as e:
        return {"county": None, "municipality": None, "error": f"geocoding request failed: {e}"}
    
    data = response.json()

    matches = data["result"]["addressMatches"]

    if matches:
        match = matches[0]
        geographies = match["geographies"]

        county = geographies["Counties"][0]["NAME"]
        municipality = geographies["County Subdivisions"][0]["NAME"]

        return {"county": county, "municipality": municipality, "error": None}
    else:
        return {"county": None, "municipality": None, "error": "no match"}
    



if __name__ == "__main__":
    result = geocode_address("210 Railroad St, Eagle River, WI 54521")
    print(result)
