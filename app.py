"""CLI: python app.py <patient_id> <note_file>"""
import sys
from pathlib import Path

from workflow import QUESTION, build_graph, resume, start


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python app.py <patient_id> <note_file>   e.g. python app.py P001 data/P001.txt")
        return 2
    patient_id, note_path = sys.argv[1], Path(sys.argv[2])
    if not note_path.is_file():
        print(f"ERROR: note file not found: {note_path}")
        return 1

    graph = build_graph()
    res = start(graph, patient_id, note_path.read_text())
    if res["status"] == "review":
        p = res["proposal"]
        print(f"\nProposed recommendation: {p['recommendation']}\nReason: {p['reason']}\n")
        answer = ""
        while answer not in {"yes", "no", "y", "n"}:
            answer = input(f"{QUESTION} ").strip().lower()
        res = resume(graph, res["thread_id"], answer)
    if res["status"] == "error":
        print(f"ERROR: {res['error']}")
        return 1
    print(res["output"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
