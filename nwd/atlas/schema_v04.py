"""
nwd/atlas/schema_v04.py

Enhanced schema, lifecycle models, and formal specification data structures for
FNWD Atlas V0.4: General Enabler-Optimizer Discovery across the Six Acceptance Gates.

Epistemic Pillars:
1. Observational Trace Equivalence: Intermediate emitted outputs must match canonical sequential execution.
2. Independent Correctness Oracle: External history validation without internal state access.
3. Causal Mechanism Isolation: Decoupling coarse batching policies from mathematical transformations.
4. Cross-Domain Generalization: Testing across register automata, CRDT sets, and KV tries.
5. Paired Statistical Rigor: Paired difference distributions, permutation tests, Wilcoxon tests, and bootstrap CIs.
6. Blind Discovery Protocol: Autonomous precondition-enabler matching from uncurated candidate pools.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import json
import os
import time
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple


class SafetyTierV04(str, Enum):
    PROVEN_OBSERVATIONAL_EQUIVALENCE = "PROVEN_OBSERVATIONAL_EQUIVALENCE"
    LINEARIZABILITY_VERIFIED = "LINEARIZABILITY_VERIFIED"
    CONDITIONALLY_SAFE_ON_MANIFOLD = "CONDITIONALLY_SAFE_ON_MANIFOLD"
    INJECTED_FAULT_DETECTED = "INJECTED_FAULT_DETECTED"
    UNSAFE_HAZARD = "UNSAFE_HAZARD"
    UNSOUND_ABSTRACTION = "UNSOUND_ABSTRACTION"
    REJECTED_UNSOUND = "REJECTED_UNSOUND"


class GateStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    INCONCLUSIVE = "INCONCLUSIVE"
    BOUNDARY_ESTABLISHED = "BOUNDARY_ESTABLISHED"


@dataclass
class ObservableEvent:
    """An externally observable event emitted by a transaction."""
    client_id: int
    tx_id: int
    op_name: str
    args: Tuple[Any, ...]
    output_val: Any
    timestamp_ns: int


@dataclass
class TraceEquivalenceResult:
    """Gate 1: Verification of observational equivalence to sequential execution."""
    workload_id: str
    num_transactions: int
    intermediate_outputs_match: bool
    final_observable_state_matches: bool
    unauthorized_side_effects: bool
    traces_equivalent: bool
    mismatch_details: Optional[Dict[str, Any]] = None
    proof_obligation_notes: str = ""


@dataclass
class LinearizabilityAuditResult:
    """Gate 2: Independent invocation/response history checker outcome."""
    suite_name: str
    total_histories_checked: int
    valid_histories_passed: int
    injected_fault_histories_checked: int
    injected_faults_detected: int
    false_positives: int
    false_negatives: int
    detection_recall_pct: float
    witness_counterexamples: List[Dict[str, Any]] = field(default_factory=list)
    gate_status: GateStatus = GateStatus.INCONCLUSIVE


@dataclass
class CausalAblationCellResult:
    cell_name: str
    mean_locks: float
    mean_wall_clock_us: float
    throughput_tx_per_sec: float
    correctness_rate: float
    state_drift_detected: bool


@dataclass
class CausalAblationAnalysis:
    """Gate 3: Causal separation of batching policy vs mathematical normalizer."""
    unbatched_2pl: CausalAblationCellResult
    batched_identity: CausalAblationCellResult
    batched_corrupt: CausalAblationCellResult
    batched_mathematical: CausalAblationCellResult
    commutation_only: CausalAblationCellResult
    normalizer_only: CausalAblationCellResult
    synergy_vs_batched_identity_pct: float
    synergy_vs_unbatched_2pl_pct: float
    net_causal_synergy_pct: float
    batching_alone_sound: bool
    gate_status: GateStatus = GateStatus.INCONCLUSIVE


@dataclass
class DomainGeneralizationResult:
    """Gate 4: Generalization across distinct mathematical domains."""
    domain_id: str
    domain_name: str
    operator_family_description: str
    optimizer_candidate_id: str
    enabler_candidate_id: str
    baseline_locks: float
    optimized_locks: float
    lock_reduction_pct: float
    baseline_time_us: float
    optimized_time_us: float
    speedup_ratio: float
    observational_equivalence_verified: bool
    linearizability_verified: bool
    negative_control_rejected: bool
    falsification_boundary_identified: str
    gate_status: GateStatus = GateStatus.INCONCLUSIVE


@dataclass
class PairedStatisticalMetric:
    """Gate 5: Paired statistical evaluation metrics with uncertainty."""
    domain_id: str
    metric_name: str
    n_pairs: int
    baseline_mean: float
    candidate_mean: float
    mean_difference: float
    std_difference: float
    cohens_d_z: float
    paired_t_statistic: float
    paired_t_p_value: float
    wilcoxon_statistic: float
    wilcoxon_p_value: float
    paired_permutation_p_value: float
    ci_99_bootstrap_lower: float
    ci_99_bootstrap_upper: float
    holm_bonferroni_adjusted_p: float
    is_statistically_significant_alpha_01: bool


@dataclass
class BlindDiscoveryCandidateRecord:
    """Autonomous Blind Discovery candidate evaluation."""
    candidate_id: str
    candidate_type: str  # CONDITIONAL_OPTIMIZER, ENABLER_NORMALIZER, DEFECTIVE_OPTIMIZER, UNRELATED_TRANSFORM
    algebraic_signature: str
    target_manifold: Optional[str]
    detected_unmet_precondition: Optional[str]
    matched_enabler_id: Optional[str]
    formal_equivalence_proven: bool
    empirical_benefit_measured: bool
    promoted_to_application: bool
    falsification_boundary: str


@dataclass
class ProvenanceManifest:
    """Gate 6: Cryptographic provenance and audit manifest."""
    manifest_timestamp_iso: str
    git_revision: str
    python_version: str
    platform_info: str
    input_catalog_hashes: Dict[str, str]
    code_file_hashes: Dict[str, str]
    output_artifact_hashes: Dict[str, str]
    all_seeds_reproducible: bool
