#!/usr/bin/env python3
from pathlib import Path

path = Path("docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md")
text = path.read_text(encoding="utf-8")
old = "- no temporary write-enabled workflow was created."
new = "- temporary write-enabled workflows were used only on task-local branches to apply exact-anchor source/evidence patches; runner PRs #252 and #253 were closed unmerged and all temporary files were removed from the permanent #250 diff."
if text.count(old) != 1:
    raise RuntimeError(f"expected exactly one historical workflow statement, found {text.count(old)}")
path.write_text(text.replace(old, new), encoding="utf-8")
