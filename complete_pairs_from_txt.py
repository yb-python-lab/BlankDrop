import json
import re

INPUT_FILE = "intern_1to10.txt"
OUTPUT_FILE = "intern_pairs_complete.json"

def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def ends_like_complete_english(text: str) -> bool:
    text = clean(text)
    if not text:
        return False

    # clearly complete if it ends with sentence punctuation
    if re.search(r'[.!?]["\']?$', text):
        return True

    return False

def ends_like_complete_korean(text: str) -> bool:
    text = clean(text)
    if not text:
        return False

    # Korean complete endings
    complete_endings = (
        ".", "?", "!",
        "다.", "요.", "죠.", "니다.", "예요.", "이에요.",
        "군요.", "네요.", "가요.", "어요.", "아요.", "래요.",
        "까요?", "인가요?", "했어요.", "됩니다.", "싶어요."
    )

    return text.endswith(complete_endings)

def starts_like_continuation_english(text: str) -> bool:
    text = clean(text).lower()

    continuation_starts = (
        "and ", "but ", "or ", "so ", "because ", "if ", "when ",
        "then ", "as soon as ", "that ", "which ", "who ", "while ",
        "although ", "though ", "to ", "with ", "for ", "from ",
        "into ", "by ", "of ", "in ", "on ", "at "
    )

    return text.startswith(continuation_starts)

def starts_like_continuation_korean(text: str) -> bool:
    text = clean(text)

    continuation_starts = (
        "그리고", "하지만", "그러나", "그래서", "그러면", "그런데",
        "또", "또한", "곧", "특히", "결국", "즉", "그래도"
    )

    return text.startswith(continuation_starts)

with open(INPUT_FILE, "r", encoding="utf-8-sig") as f:
    lines = [clean(line) for line in f if clean(line)]

if len(lines) % 2 != 0:
    raise ValueError("The text file does not contain an even number of lines.")

raw_pairs = []
for i in range(0, len(lines), 2):
    raw_pairs.append({
        "korean": lines[i],
        "english": lines[i + 1]
    })

merged = []
i = 0

while i < len(raw_pairs):
    kor = raw_pairs[i]["korean"]
    eng = raw_pairs[i]["english"]

    # Check whether current pair is already complete
    kor_complete = ends_like_complete_korean(kor)
    eng_complete = ends_like_complete_english(eng)

    # If both are complete, keep as-is
    if kor_complete and eng_complete:
        merged.append({
            "korean": kor,
            "english": eng
        })
        i += 1
        continue

    # Otherwise merge carefully forward
    while i + 1 < len(raw_pairs):
        next_kor = raw_pairs[i + 1]["korean"]
        next_eng = raw_pairs[i + 1]["english"]

        kor = clean(kor + " " + next_kor)
        eng = clean(eng + " " + next_eng)
        i += 1

        kor_complete = ends_like_complete_korean(kor)
        eng_complete = ends_like_complete_english(eng)

        # Stop as soon as both sides look complete
        if kor_complete and eng_complete:
            break

        # Safety: if next pair clearly looks like a new sentence, stop
        if not starts_like_continuation_english(next_eng) and not starts_like_continuation_korean(next_kor):
            break

    merged.append({
        "korean": kor,
        "english": eng
    })
    i += 1

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print("Original pairs:", len(raw_pairs))
print("Merged complete pairs:", len(merged))
print("Saved to:", OUTPUT_FILE)