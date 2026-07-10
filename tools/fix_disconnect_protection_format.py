from pathlib import Path

path = Path("src/config/configmanager.cpp")
text = path.read_text(encoding="utf-8")
old = '\t\tloadIntConfig(L, DISCONNECT_PROTECTION_COOLDOWN, "disconnectProtectionCooldown", 30 * 60 * 1000);\n\tloadIntConfig(L, DISCONNECT_PROTECTION_DETECTION_TIME, "disconnectProtectionDetectionTime", 10 * 1000);\n\tloadIntConfig(L, DISCONNECT_PROTECTION_DURATION, "disconnectProtectionDuration", 30 * 1000);\n\tloadIntConfig(L, DEPOT_BOXES, "depotBoxes", 20);'
new = '\t\tloadIntConfig(L, DISCONNECT_PROTECTION_COOLDOWN, "disconnectProtectionCooldown", 30 * 60 * 1000);\n\t\tloadIntConfig(L, DISCONNECT_PROTECTION_DETECTION_TIME, "disconnectProtectionDetectionTime", 10 * 1000);\n\t\tloadIntConfig(L, DISCONNECT_PROTECTION_DURATION, "disconnectProtectionDuration", 30 * 1000);\n\t\tloadIntConfig(L, DEPOT_BOXES, "depotBoxes", 20);'
if old not in text:
    raise RuntimeError("Formatting anchor not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
