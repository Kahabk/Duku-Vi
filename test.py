def extract_name(text):
    if not text:
        return None

    text = text.strip()

    patterns = [
        r"\bmy name is\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bmy name\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bi am\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bi'm\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bit is\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bit's\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bcall me\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bpeople call me\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bthey call me\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bthe name is\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\bactually my name\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        r"\b([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+here\b",
        r"\b([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+speaking\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()

            # Filter obvious non-name phrases
            if len(name.split()) > 5:
                continue

            return name.title()

    return text.strip().capitalize()
import re

tests = [
    "My name is Mohammed ameen ashraf",
    "I'm kahab",
    "Call me kahab",
    "Kahab here",
    "People call me kahab",
    "The name is kahab",
    "actually my name kahab",]


for t in tests:
    print(t, "->", extract_name(t))

