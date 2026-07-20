from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_TEST = Path(__file__).resolve().parents[2] / "tests" / "e2e" / "test_otbm_candidate_physical_validation.py"
_SPEC = importlib.util.spec_from_file_location("candidate_physical_validation_focus_suite", _TEST)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)

CandidatePhysicalValidationTest = _MODULE.CandidatePhysicalValidationTest
