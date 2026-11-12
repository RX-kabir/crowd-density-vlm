"""Write the exact prompt text of every condition to prompts/*.txt.

The prompts are defined as triple-quoted constants in the GPT final-run notebooks (gpt/<condition>/*.ipynb);
their wording is character-identical to the open-source (Qwen / LLaVA / Gemma) notebooks of the same condition.
Only the message layout (API format) differs between models.

Usage:  python scripts/extract_prompts.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "prompts"
OUT.mkdir(exist_ok=True)

NOTEBOOKS = {
    "five_shot_A": "gpt/Five_Shot/GPT_ExperimentA.ipynb",
    "five_shot_B": "gpt/Five_Shot/GPT_ExperimentB.ipynb",
    "zero_shot_A": "gpt/Zero_Shot/GPT_ExperimentA_ZeroShot.ipynb",
    "zero_shot_B": "gpt/Zero_Shot/GPT_ExperimentB_ZeroShot.ipynb",
    "zero_shot_densitydef_A": "gpt/Zero_Shot_Density/GPT_ExperimentA_ZeroShot_DensityDef.ipynb",
    "zero_shot_densitydef_B": "gpt/Zero_Shot_Density/GPT_ExperimentB_ZeroShot_DensityDef.ipynb",
}
CONST = re.compile(r'^([A-Z][A-Z_0-9]*)\s*=\s*"""(.*?)"""', re.S | re.M)

for name, rel in NOTEBOOKS.items():
    nb = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    parts = []
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        for const, text in CONST.findall("".join(cell["source"])):
            parts.append(f"===== {const} =====\n{text.rstrip()}\n")
    header = (f"# Prompt text: {name}\n# Source: {rel}\n"
              "# {placeholders} such as {i}, {count}, {density}, {label}, {yolo} are filled in per image.\n\n")
    (OUT / f"{name}.txt").write_text(header + "\n".join(parts), encoding="utf-8")
    print(name, len(parts), "constants")
