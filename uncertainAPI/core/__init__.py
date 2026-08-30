"""Framework-independent core contracts for uncertainAPI.

The core package intentionally depends on protocols and data specifications,
not Django, DRF, browser vendors, observability vendors, or task systems.
"""

from uncertainAPI.core.interfaces import (
    ArtifactStore,
    CheckpointStore,
    ContractValidator,
    DestinationAdapter,
    JobDispatcher,
    MappingEngine,
    PlanRegistry,
    RateLimiter,
    RuntimeObserver,
    SecretResolver,
    SourceAdapter,
    SourceAdapterResolver,
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
    "CheckpointStore",
    "ContractSpec",
    "ContractValidator",
    "DestinationAdapter",
    "IntegrationPlan",
    "IntegrationSpec",
    "JobDispatcher",
    "MappingEngine",
    "MappingSpec",
    "PlanRegistry",
    "RateLimiter",
    "RuntimeObserver",
    "SecretResolver",
    "SourceAdapter",
    "SourceAdapterResolver",
    "SourceSpec",
]
