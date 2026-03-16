import json
import re

INPUT_FILE = "intern_ocr.txt"
OUTPUT_FILE = "intern_pairs.json"

def is_english(text):
    return len(re.findall(r"[A-Za-z]", text)) > len(re.findall(r"[가-힣]", text))

def is_korean(text):
    return len(re.findall(r"[가-힣]", text)) > len(re.findall(r"[A-Za-z]", text))

def clean(text):
    text = text.strip()
    text = re.sub(r"^[A-Z ]+:", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

with open(INPUT_FILE, encoding="utf-8-sig") as f:
    lines = [clean(l) for l in f.readlines()]

pairs = []

for i in range(len(lines) - 1):
    eng = lines[i]
    kor = lines[i + 1]

    if is_english(eng) and is_korean(kor):
        if 3 < len(eng.split()) < 20:
            pairs.append({
                "english": eng,
                "korean": kor
            })

print("Pairs found:", len(pairs))

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(pairs, f, ensure_ascii=False, indent=2)

print("Saved to", OUTPUT_FILE)