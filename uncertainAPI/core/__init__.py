"""Framework-independent core contracts for uncertainAPI.

The core package intentionally depends on protocols and data specifications,
not Django, DRF, browser vendors, observability vendors, or task systems.
"""

from uncertainAPI.core.interfaces import (
    ArtifactStore,
    ContractValidator,
    MappingEngine,
    RuntimeObserver,
    SourceAdapter,
)
from uncertainAPI.core.plan import IntegrationPlan
from uncertainAPI.core.specs import (
    ContractSpec,
    IntegrationSpec,
    MappingSpec,
    SourceSpec,
)

__all__ = [
    "ArtifactStore",
    "ContractSpec",
    "ContractValidator",
    "IntegrationPlan",
    "IntegrationSpec",
    "MappingEngine",
    "MappingSpec",
    "RuntimeObserver",
    "SourceAdapter",
    "SourceSpec",
]
