"""context_engineering — first-principles reference library for the curriculum.

A small, readable, standard-library-only implementation of the core
Context Engineering components introduced across the curriculum:

- tokens.py    approximate token estimation (Chapter 2)
- context.py   component model: kinds, trust, provenance (Chapter 3)
- budget.py    priority-based allocation and truncation (Chapter 12)
- assembly.py  ordering and labeled rendering (Chapters 13, 24)
- sim.py       deterministic responder for reproducible experiments

Later parts of the curriculum add retrieval, memory, tools, security,
evaluation, observability, and pipeline modules to this package.
"""

from .context import (
    ComponentKind,
    ContextBundle,
    ContextComponent,
    SourceRef,
    TrustLevel,
)
from .tokens import heuristic_token_count, make_estimator
from .budget import (
    AllocationRecord,
    AllocationResult,
    BudgetError,
    ContextBudget,
    allocate,
)
from .assembly import (
    AssembledContext,
    OrderingStrategy,
    assemble,
    render_component,
)
from .sim import Answer, DeterministicResponder

__version__ = "0.1.0"
