import json
import os
import sys

def convert_and_cleanup(input_path):
    if not input_path.endswith(".jsonl"):
        raise ValueError("Input file must have a .jsonl extension")

    output_path = input_path[:-6] + ".json"  # replace .jsonl with .json
    data = []

    with open(input_path, "r", encoding="utf-8") as infile:
        for line_number, line in enumerate(infile, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {e}"
                )

    # Write output JSON
    with open(output_path, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, indent=2, ensure_ascii=False)

    # Delete input file ONLY after success
    os.remove(input_path)

    print(f"✅ Created: {output_path}")
    print(f"🗑️ Deleted: {input_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python jsonl_to_json_auto.py file.jsonl")
        sys.exit(1)

    convert_and_cleanup(sys.argv[1])
