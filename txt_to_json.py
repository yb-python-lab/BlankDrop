import json

INPUT_FILE = "intern_1to10.txt"
OUTPUT_FILE = "intern_pairs.json"

pairs = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

# Every 2 lines = one pair
for i in range(0, len(lines), 2):
    korean = lines[i]
    english = lines[i + 1]

    pairs.append({
        "korean": korean,
        "english": english
    })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(pairs, f, ensure_ascii=False, indent=2)

print("Pairs created:", len(pairs))
print("Saved to:", OUTPUT_FILE)