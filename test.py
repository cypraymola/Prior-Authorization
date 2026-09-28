"""Run: python test.py  -- runs the 3 required cases (real LLM call each) plus a few extra checks.
The human-review step is answered automatically with a simulated "yes"."""
import sys
from pathlib import Path

from mcp_client import call_tool
from workflow import REJECTED, build_graph, decide, resume, start

DATA = Path(__file__).resolve().parent / "data"
CASES = [("P001", "Approve"), ("P002", "Deny"), ("P003", "Need more information")]


def run_case(pid: str, answer: str = "yes", note_id: str | None = None) -> dict:
    graph = build_graph()
    res = start(graph, pid, (DATA / f"{note_id or pid}.txt").read_text())
    if res["status"] == "review":
        res["proposal_rec"] = res["proposal"]["recommendation"]
        res = {**resume(graph, res["thread_id"], answer), "proposal_rec": res["proposal_rec"]}
    return res


def report(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))
    return ok


def main() -> int:
    results = []
    print("Required cases")
    for pid, expected in CASES:
        try:
            r = run_case(pid)
            ok = r["status"] == "done" and r["proposal_rec"] == expected and expected in r["output"]
            results.append(report(f"{pid} -> {expected}", ok, "" if ok else f"got {r.get('proposal_rec') or r.get('error')}"))
        except Exception as e:
            results.append(report(f"{pid} -> {expected}", False, f"{type(e).__name__}: {e}"))

    print("\nExtra checks")
    try:
        rule = call_tool("get_rule")
        extra = [
            ("exactly 6 weeks meets requirement", decide(True, 6, 6, rule)[0] == "Approve"),
            ("0 weeks physio (none tried) -> Deny", decide(True, 10, 0, rule)[0] == "Deny"),
            ("pain under 6 weeks -> Deny", decide(True, 5, 8, rule)[0] == "Deny"),
            ("null physio -> Need more information", decide(True, 9, None, rule)[0] == "Need more information"),
            ("inactive plan wins over missing info", decide(False, None, None, rule)[0] == "Deny"),
        ]
        results += [report(n, ok) for n, ok in extra]
        r = run_case("P999", note_id="P001")
        results.append(report("unknown patient -> error, no recommendation", r["status"] == "error"))
        r = run_case("P001", answer="no")
        results.append(report("reviewer 'no' -> exact rejection text", r.get("output") == REJECTED))
    except Exception as e:
        results.append(report("extra checks", False, f"{type(e).__name__}: {e}"))

    print(f"\n{sum(results)}/{len(results)} passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
