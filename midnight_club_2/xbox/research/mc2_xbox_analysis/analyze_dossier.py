import re
from pathlib import Path

dossier_path = Path("research/mc2_xbox/rea_dossiers/career_and_hookmen.md")
text = dossier_path.read_text(encoding="utf-8")

sections = text.split("### `")
print(f"Total sections: {len(sections) - 1}")

out_lines = []
for sec in sections[1:]:
    name = sec.split("`")[0]
    # find VA
    va_match = re.search(r"\*\*MC2 Xbox VA:\*\* `([^`]+)`", sec)
    va = va_match.group(1) if va_match else "unknown"
    # find code block
    code_match = re.search(r"```cpp\n(.*?)\n```", sec, re.DOTALL)
    code_len = len(code_match.group(1).splitlines()) if code_match else 0
    out_lines.append(f"{name:65} | VA: {va:22} | {code_len:4d} lines")

print("\n".join(out_lines))
