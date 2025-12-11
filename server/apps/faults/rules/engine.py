
import yaml
import os
from typing import Optional, Dict, Any
from apps.faults.utils import build_fault_context

RULES_FILE = os.path.join(os.path.dirname(__file__), "rules.yaml")


def load_rules():
    with open(RULES_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)["rules"]


def match_condition(data: Dict[str, Any], cond: Dict[str, Any]) -> bool:
    for key, expected in cond.items():
        if "__" in key:
            field, op = key.split("__", 1)
            value = data.get(field)
            if value is None:
                return False
            if op == "gt" and not (isinstance(value, (int, float)) and value > expected):
                return False
            elif op == "lt" and not (isinstance(value, (int, float)) and value < expected):
                return False
            elif op == "contains" and not (isinstance(value, str) and expected in value):
                return False
            elif op == "in" and not (value in expected):
                return False
        else:
            if data.get(key) != expected:
                return False
    return True


def apply_rules_to_event(event) -> Optional[Dict[str, Any]]:

    fault_data = build_fault_context(event)
    rules = load_rules()
    for rule in rules:
        if match_condition(fault_data, rule["condition"]):
            action = rule["action"]
            return {
                "source": "rule",
                "rule_id": rule["id"],
                "root_cause": action["root_cause"],
                "suggestion": action["suggestion"],
                "confidence": action["confidence"]
            }
    return None

