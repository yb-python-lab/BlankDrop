import json
import random
import re

INPUT_FILE = "intern_pairs.json"
OUTPUT_FILE = "intern_questions.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    pairs = json.load(f)

questions = []

PREPOSITIONS = {
    "in","on","at","to","for","with","about","from",
    "into","over","after","before","between","by"
}

for pair in pairs:

    eng = pair["english"]
    kor = pair["korean"]

    words = re.findall(r"\b\w+\b", eng)

    if len(words) < 4:
        continue

    candidates = []

    for w in words:
        if w.lower() in PREPOSITIONS:
            candidates.append(w)
        elif len(w) > 4:
            candidates.append(w)

    if not candidates:
        continue

    answer = random.choice(candidates)

    blank_sentence = re.sub(
        r"\b" + re.escape(answer) + r"\b",
        "____",
        eng,
        count=1
    )

    questions.append({
        "korean": kor,
        "english": blank_sentence,
        "answer": answer.lower()
    })

print("Questions created:", len(questions))

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print("Saved to", OUTPUT_FILE)