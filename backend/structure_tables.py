TABLE_SCHEMAS = {
    "STUDENT ACHIEVEMENTS:": {
        "columns": ["Sl. No", "Name", "USN", "Sem", "Activity", "Award/Honor", "Level"],
        "split_from_right": 6,
    },
    "PLACEMENT AND HIGHER STUDIES RECORD:": {
        "columns": ["Sl. No", "Name", "USN", "Program", "University", "Place"],
        "split_from_right": 4,
    },
    "FUNDED PROJECTS:": {
        "columns": ["Project Title", "Funding Agency", "Amount", "Faculty PI"],
        "split_from_right": 3,
    },
    "PATENTS:": {
        "columns": ["Patent Title", "Status", "Application Number"],
        "split_from_right": 2,
    },
}


def safe_split(text, parts):
    tokens = text.split()
    if len(tokens) <= parts:
        return None

    cols = []
    for _ in range(parts):
        cols.insert(0, tokens.pop())
    cols.insert(0, " ".join(tokens))
    return cols


def structure_tables(sections):
    structured = {}

    for section, content in sections.items():
        structured[section] = {
            "text": content["text"],
            "images": content["images"],
            "tables": []
        }

        if section not in TABLE_SCHEMAS:
            continue

        schema = TABLE_SCHEMAS[section]

        for table in content["tables"]:
            title = table["title"]
            rows = []

            for line in table["rows"]:
                row = safe_split(line, schema["split_from_right"])
                if row:
                    rows.append(row)

            if rows:
                structured[section]["tables"].append({
                    "title": title,
                    "header": schema["columns"],
                    "rows": rows
                })

    return structured