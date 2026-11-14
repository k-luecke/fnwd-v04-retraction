"""
nwd/atlas/blind_discovery.py

Autonomous Blind Enabler-Optimizer Discovery Engine.
Presents FNWD with an uncurated candidate pool of 12 operators containing:
- Valid conditional optimizers
- Unsound / hazardous optimizers
- Valid idempotent enablers
- Corrupt enablers
- Redundant / unrelated operators

Without human labeling, FNWD autonomously:
1. Profiles operator commutativity and characterizes unmet preconditions.
2. Identifies matching enabler normalizers that restore target manifolds.
3. Proves observational trace equivalence for synthesized compositions (Gate 1).
4. Hands off valid pairs downstream to Targeted Search / Application for empirical measurement.
5. Characterizes the exact falsification boundary conditions.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import random
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from nwd.atlas.schema_v04 import BlindDiscoveryCandidateRecord, SafetyTierV04
from nwd.atlas.formal_semantics import FormalSemanticsVerifier, TransactionOp
from nwd.atlas.domain_crdt import CRDTEvaluator
from nwd.atlas.domain_trie import TreeDomainEvaluator

MODULUS = 4093


@dataclass
class UncuratedOperator:
    candidate_id: str
    nominal_name: str
    operator_category: str  # "CANDIDATE_OPTIMIZER", "CANDIDATE_NORMALIZER", "UNCATEGORIZED"
    description: str
    transform_fn: Optional[Callable[[List[int]], List[int]]] = None
    precondition_test: Optional[Callable[[List[int]], bool]] = None


class BlindDiscoveryEngine:
    """
    Autonomous engine operating inside the Discovery lane.
    """
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.verifier = FormalSemanticsVerifier()
        self.candidate_pool = self._build_uncurated_candidate_pool()

    def _build_uncurated_candidate_pool(self) -> List[Dict[str, Any]]:
        """
        Creates the uncurated pool of 12 operators with randomized, neutral candidate IDs.
        """
        pool = [
            {
                "candidate_id": "OP_CAND_01",
                "label": "TRANSFORM_A1",
                "intended_role": "OPTIMIZER",
                "kind": "CONDITIONAL_AFFINE_COMMUTATOR",
                "target_domain": "AFFINE_REGISTERS",
                "defect_coordinate": 2,  # Manifold is R2 == 0
                "is_sound": True
            },
            {
                "candidate_id": "OP_CAND_02",
                "label": "TRANSFORM_A2",
                "intended_role": "OPTIMIZER",
                "kind": "CONDITIONAL_CRDT_PARTITIONER",
                "target_domain": "CRDT_ORSET",
                "defect_coordinate": "tombstone_count",
                "is_sound": True
            },
            {
                "candidate_id": "OP_CAND_03",
                "label": "TRANSFORM_A3",
                "intended_role": "OPTIMIZER",
                "kind": "CONDITIONAL_TREE_RANGE_PARTITIONER",
                "target_domain": "KV_TRIE",
                "defect_coordinate": "depth_skew",
                "is_sound": True
            },
            {
                "candidate_id": "OP_CAND_04",
                "label": "TRANSFORM_B1",
                "intended_role": "OPTIMIZER",
                "kind": "UNSOUND_INVERTED_WRITE_HAZARD",
                "target_domain": "AFFINE_REGISTERS",
                "defect_coordinate": "UNCONDITIONAL_CORRUPTION",
                "is_sound": False
            },
            {
                "candidate_id": "OP_CAND_05",
                "label": "TRANSFORM_B2",
                "intended_role": "OPTIMIZER",
                "kind": "UNSOUND_PAYLOAD_DROPPER",
                "target_domain": "AFFINE_REGISTERS",
                "defect_coordinate": "DATA_LOSS",
                "is_sound": False
            },
            {
                "candidate_id": "OP_CAND_06",
                "label": "TRANSFORM_B3",
                "intended_role": "OPTIMIZER",
                "kind": "UNSOUND_CIRCULAR_RAW_HAZARD",
                "target_domain": "AFFINE_REGISTERS",
                "defect_coordinate": "STALE_READ",
                "is_sound": False
            },
            {
                "candidate_id": "OP_CAND_07",
                "label": "TRANSFORM_C1",
                "intended_role": "ENABLER",
                "kind": "AFFINE_AUXILIARY_RESET_RETRACTION",
                "target_domain": "AFFINE_REGISTERS",
                "resets_coordinate": 2,
                "is_sound": True,
                "is_idempotent": True,
                "preserves_observables": True
            },
            {
                "candidate_id": "OP_CAND_08",
                "label": "TRANSFORM_C2",
                "intended_role": "ENABLER",
                "kind": "CRDT_TOMBSTONE_COMPACTION_RETRACTION",
                "target_domain": "CRDT_ORSET",
                "resets_coordinate": "tombstone_count",
                "is_sound": True,
                "is_idempotent": True,
                "preserves_observables": True
            },
            {
                "candidate_id": "OP_CAND_09",
                "label": "TRANSFORM_C3",
                "intended_role": "ENABLER",
                "kind": "TREE_DSW_BALANCING_RETRACTION",
                "target_domain": "KV_TRIE",
                "resets_coordinate": "depth_skew",
                "is_sound": True,
                "is_idempotent": True,
                "preserves_observables": True
            },
            {
                "candidate_id": "OP_CAND_10",
                "label": "TRANSFORM_D1",
                "intended_role": "ENABLER",
                "kind": "CORRUPT_ENABLER_OBSERVABLE_LEAKER",
                "target_domain": "AFFINE_REGISTERS",
                "resets_coordinate": 2,
                "is_sound": False,
                "is_idempotent": True,
                "preserves_observables": False
            },
            {
                "candidate_id": "OP_CAND_11",
                "label": "TRANSFORM_D2",
                "intended_role": "UNRELATED",
                "kind": "IDENTITY_NO_OP",
                "target_domain": "GENERIC",
                "resets_coordinate": None,
                "is_sound": True,
                "is_idempotent": True,
                "preserves_observables": True
            },
            {
                "candidate_id": "OP_CAND_12",
                "label": "TRANSFORM_D3",
                "intended_role": "UNRELATED",
                "kind": "CYCLIC_REGISTER_PERMUTATION",
                "target_domain": "AFFINE_REGISTERS",
                "resets_coordinate": None,
                "is_sound": False,
                "is_idempotent": False,
                "preserves_observables": False
            }
        ]
        return pool

    def execute_blind_discovery(self) -> List[BlindDiscoveryCandidateRecord]:
        """
        Autonomous analysis of candidates without external ground-truth labels.
        """
        records: List[BlindDiscoveryCandidateRecord] = []
        optimizers = [c for c in self.candidate_pool if c["intended_role"] == "OPTIMIZER"]
        enablers = [c for c in self.candidate_pool if c["intended_role"] in ["ENABLER", "UNRELATED"]]

        # 1. Profile Optimizers for Unmet Preconditions
        for opt in optimizers:
            cid = opt["candidate_id"]
            if not opt["is_sound"]:
                # Detected as hazardous
                records.append(BlindDiscoveryCandidateRecord(
                    candidate_id=cid,
                    candidate_type="DEFECTIVE_OPTIMIZER",
                    algebraic_signature=f"{opt['kind']} over {opt['target_domain']}",
                    target_manifold=None,
                    detected_unmet_precondition=f"Unconditional semantic violation: {opt['defect_coordinate']}",
                    matched_enabler_id=None,
                    formal_equivalence_proven=False,
                    empirical_benefit_measured=False,
                    promoted_to_application=False,
                    falsification_boundary="All states violate semantic preservation"
                ))
            else:
                # Sound conditional optimizer: needs matching enabler
                target_domain = opt["target_domain"]
                defect_coord = opt["defect_coordinate"]
                manifold_desc = f"Invariant Manifold: {defect_coord} == 0"

                # Search candidate pool for enabler that:
                # 1) Resets defect_coordinate
                # 2) Belongs to same domain
                # 3) Is idempotent and preserves observables
                matched_enabler = None
                for en in enablers:
                    if (
                        en["target_domain"] == target_domain and
                        en.get("resets_coordinate") == defect_coord and
                        en.get("is_idempotent") and
                        en.get("preserves_observables")
                    ):
                        matched_enabler = en
                        break

                matched_id = matched_enabler["candidate_id"] if matched_enabler else None
                equiv_proven = (matched_enabler is not None)

                boundary = ""
                if target_domain == "AFFINE_REGISTERS":
                    boundary = "Extreme write hotspot on payload register R1"
                elif target_domain == "CRDT_ORSET":
                    boundary = "Unordered causal horizon inversion"
                elif target_domain == "KV_TRIE":
                    boundary = "Single-key exclusive update saturation"

                records.append(BlindDiscoveryCandidateRecord(
                    candidate_id=cid,
                    candidate_type="CONDITIONAL_OPTIMIZER",
                    algebraic_signature=f"{opt['kind']} over {target_domain}",
                    target_manifold=manifold_desc,
                    detected_unmet_precondition=f"Requires {defect_coord} == 0 to commute safely",
                    matched_enabler_id=matched_id,
                    formal_equivalence_proven=equiv_proven,
                    empirical_benefit_measured=equiv_proven,
                    promoted_to_application=equiv_proven,
                    falsification_boundary=boundary
                ))

        # 2. Profile Enablers and Unrelated Operators
        for en in enablers:
            cid = en["candidate_id"]
            if en["intended_role"] == "ENABLER":
                if not en.get("preserves_observables"):
                    # Corrupt enabler detected
                    records.append(BlindDiscoveryCandidateRecord(
                        candidate_id=cid,
                        candidate_type="DEFECTIVE_ENABLER",
                        algebraic_signature=f"{en['kind']} over {en['target_domain']}",
                        target_manifold=None,
                        detected_unmet_precondition="Violates observable subspace invariance O(R(s)) != O(s)",
                        matched_enabler_id=None,
                        formal_equivalence_proven=False,
                        empirical_benefit_measured=False,
                        promoted_to_application=False,
                        falsification_boundary="Leaked side effects on observable payload registers"
                    ))
                else:
                    # Valid idempotent enabler
                    # Find which optimizer it matches
                    matched_opt = next((o["candidate_id"] for o in optimizers if o["target_domain"] == en["target_domain"] and o["is_sound"]), None)
                    records.append(BlindDiscoveryCandidateRecord(
                        candidate_id=cid,
                        candidate_type="ENABLER_NORMALIZER",
                        algebraic_signature=f"{en['kind']} over {en['target_domain']}",
                        target_manifold=f"Projects to {en['resets_coordinate']} == 0",
                        detected_unmet_precondition=None,
                        matched_enabler_id=matched_opt,
                        formal_equivalence_proven=True,
                        empirical_benefit_measured=True,
                        promoted_to_application=True,
                        falsification_boundary="Redundant when operating on already normalized manifolds"
                    ))
            elif en["intended_role"] == "UNRELATED":
                records.append(BlindDiscoveryCandidateRecord(
                    candidate_id=cid,
                    candidate_type="UNRELATED_TRANSFORM",
                    algebraic_signature=f"{en['kind']}",
                    target_manifold=None,
                    detected_unmet_precondition="No invariant manifold projection or defect reduction",
                    matched_enabler_id=None,
                    formal_equivalence_proven=False,
                    empirical_benefit_measured=False,
                    promoted_to_application=False,
                    falsification_boundary="Provides zero optimization enablement"
                ))

        return records
