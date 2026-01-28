import json

nb_path = "d:/Il mio Drive/00 MS DS/Data Science Lab On Smart Cities/Jan 2026/Milan_v3/code_note.ipynb"

try:
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    print(f"Found {len(nb['cells'])} cells.")

    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code':
            source = "".join(cell['source'])
            if "savefig" in source and "visuals/" in source:
                print(f"\n--- CELL {i} ---\n")
                print(source)
                print("\n----------------\n")
except Exception as e:
    print(f"Error: {e}")
