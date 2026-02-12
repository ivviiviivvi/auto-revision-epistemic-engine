"""
Auto-Revision Epistemic Engine (v4.2)

A self-governing orchestration framework with eight phases and four human oversight gates.
Balances automation and governance via HRGs, RBAC, and SLAs, ensuring reproducibility,
ethical audits, and full auditability through append-only logs and BLAKE3 hashing.

Usage:
    python -m auto_revision_epistemic_engine demo
    python -m auto_revision_epistemic_engine run --seed 42 --inputs '{"data": {"records": 50}}'
    python -m auto_revision_epistemic_engine audit --after-run
    python -m auto_revision_epistemic_engine status
"""

__version__ = "4.2.0"

from .core.engine import AutoRevisionEngine
from .core.orchestrator import Orchestrator
from .phases.phase_manager import PhaseManager
from .hrg.human_review_gate import HumanReviewGate
from .rol_t.resource_optimizer import ResourceOptimizationLayer
from .reproducibility.state_manager import StateManager
from .ethics.axiom_framework import AxiomFramework
from .audit.audit_logger import AuditLogger
from .__main__ import main as cli_main

__all__ = [
    "AutoRevisionEngine",
    "Orchestrator",
    "PhaseManager",
    "HumanReviewGate",
    "ResourceOptimizationLayer",
    "StateManager",
    "AxiomFramework",
    "AuditLogger",
    "cli_main",
]
