import json
import re
from typing import Dict, Any

def extract_json(text: str) -> Dict[str, Any]:
    """
    Robust JSON parser with fallback logic for LLM outputs.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: try to find a JSON block in the text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Final fallback: return an error dictionary
        return {"error": "Failed to parse JSON", "raw_output": text}

def calculate_cohens_kappa(po: float, pe: float) -> float:
    """
    Calculate Cohen's Kappa score given observed and expected agreement.
    """
    if pe == 1.0:
        return 1.0
    return (po - pe) / (1 - pe)

def interpret_kappa(kappa: float) -> str:
    if kappa < 0:
        return "Poor agreement"
    elif kappa <= 0.20:
        return "Slight agreement"
    elif kappa <= 0.40:
        return "Fair agreement"
    elif kappa <= 0.60:
        return "Moderate agreement"
    elif kappa <= 0.80:
        return "Substantial agreement"
    else:
        return "Almost perfect agreement"
