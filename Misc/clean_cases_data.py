import json

def parse_case(text):
    try:
        # Extract question (first line after "# ")
        question = text.split("\n")[0].replace("# ", "").strip()
        
        # Extract background (after "Background" heading)
        background_section = text.split("Background")[1].split("View of CIC")[0]
        background = background_section.strip().strip("\n")
        
        # Extract CIC view (after "View of CIC" heading)
        cic_section = text.split("View of CIC")[1].split("Citation:")[0]
        cic_view = cic_section.strip().strip("\n")
        
        return {
            "instruction": f"{question}\n\nBackground:\n{background}",
            "response": cic_view
        }
    except IndexError:
        print(f"Skipping malformed entry:\n{text[:200]}...")  # Show first 200 chars for debugging
        return None

with open("Extracted_data/rti_cases.jsonl", "r") as f_in, open("rti_instructions.jsonl", "w") as f_out:
    for line in f_in:
        case = json.loads(line)
        parsed = parse_case(case["text"])
        if parsed:
            f_out.write(json.dumps(parsed) + "\n")