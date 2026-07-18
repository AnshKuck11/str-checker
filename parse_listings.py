import re

CITY_STATE_ZIP = re.compile(r"^[A-Za-z\s.'-]+,\s*WI\s+\d{5}(-\d{4})?$")

def parse_addresses(text: str) -> list[str]:
    lines = text.splitlines()
    addresses = []

    for i, line in enumerate(lines):
        line = line.strip()
        if CITY_STATE_ZIP.match(line):
            address = lines[i-1].strip()
            full_address = address + ", " + line
            addresses.append(full_address)
    
    return addresses


if __name__ == "__main__":
    with open("listings.txt") as f:
        text = f.read()
    result = parse_addresses(text)
    print(len(result), "address found")
    for a in result:
        print(a)