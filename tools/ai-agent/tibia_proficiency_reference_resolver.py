from __future__ import annotations

from typing import Mapping

import tibia_proficiency_reference_resolver_legacy as _legacy
from tibia_proficiency_reference_resolver_legacy import *  # noqa: F403

SUPPORTED_PROFICIENCY_INDEX_SCHEMA_VERSIONS = frozenset({1, 2})
_legacy_validate_proficiency_index = _legacy.validate_proficiency_index


def validate_proficiency_index(payload: Mapping[str, object], *, max_records: int) -> list[dict[str, object]]:
    schema_version = payload.get("schemaVersion")
    if schema_version not in SUPPORTED_PROFICIENCY_INDEX_SCHEMA_VERSIONS:
        raise ProficiencyReferenceCorrelationError(  # noqa: F405
            "proficiency index schemaVersion must be one of "
            f"{sorted(SUPPORTED_PROFICIENCY_INDEX_SCHEMA_VERSIONS)}"
        )
    legacy_compatible = dict(payload)
    legacy_compatible["schemaVersion"] = 1
    return _legacy_validate_proficiency_index(legacy_compatible, max_records=max_records)


_legacy.validate_proficiency_index = validate_proficiency_index
