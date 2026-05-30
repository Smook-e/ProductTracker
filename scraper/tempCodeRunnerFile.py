def _parse_price(raw: str) -> int:
    # strips currency symbols, commas, whitespace and converts to cents
    cleaned = "".join(c for c in raw if c.isdigit() or c == ".")
    return int(float(cleaned) * 100)