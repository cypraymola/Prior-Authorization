"""MCP server (stdio) exposing the fictional patient DB and the decision rule.

Tools:
  get_patient(patient_id) -> {"patient_id", "name", "plan_active"}
  get_rule()              -> {"rule_text", "evaluation_order", "thresholds"}
"""
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

DATA = Path(__file__).resolve().parent / "data"
mcp = FastMCP("prior-auth-data", log_level="WARNING")


@mcp.tool()
def get_patient(patient_id: str) -> dict:
    """Return the fictional patient's name and whether their plan is active."""
    patients = json.loads((DATA / "patients.json").read_text())
    key = patient_id.strip().upper()
    if key not in patients:
        raise ValueError(f"Unknown patient ID: {patient_id!r}")
    return {"patient_id": key, **patients[key]}


@mcp.tool()
def get_rule() -> dict:
    """Return the rule text, its evaluation order, and the two six-week thresholds."""
    return json.loads((DATA / "rule.json").read_text())


if __name__ == "__main__":
    mcp.run(transport="stdio")
