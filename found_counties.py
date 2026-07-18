from parse_listings import parse_addresses
from geocode import geocode_address

with open("listings.txt") as f:
    text = f.read()

addresses = parse_addresses(text)

counties = set()

for address in addresses:
    print(f"Checking: {address}")
    result = geocode_address(address)
    if result["error"]:
        print(f"FAILED: {address} — {result['error']}")
        continue
    counties.add(result["county"])

print(counties)
