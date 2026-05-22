#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def _coerce_text(value):
    if isinstance(value, list):
        return "".join(value)
    if value is None:
        return ""
    return str(value)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: summarize_notebook_outputs.py <executed-notebook.ipynb>", file=sys.stderr)
        return 2

    notebook_path = Path(sys.argv[1])
    if not notebook_path.is_file():
        print(f"Notebook not found: {notebook_path}", file=sys.stderr)
        return 1

    notebook = json.loads(notebook_path.read_text())
    found_output = False

    for cell_index, cell in enumerate(notebook.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue

        outputs = cell.get("outputs", [])
        print(f"CELL {cell_index}: outputs={len(outputs)}")

        for output in outputs:
            found_output = True
            output_type = output.get("output_type", "unknown")
            print(f"  type={output_type}")

            if output_type == "error":
                print(f"  error={output.get('ename')} {output.get('evalue')}")

            data = output.get("data", {})
            if "image/png" in data:
                print("  image/png present")

            if "text/plain" in data:
                snippet = _coerce_text(data.get("text/plain"))[:200].replace("\n", " ")
                print(f"  text/plain={snippet}")

            if output_type == "stream":
                snippet = _coerce_text(output.get("text"))[:200].replace("\n", " ")
                print(f"  stream={snippet}")

    if not found_output:
        print("No notebook outputs found")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
