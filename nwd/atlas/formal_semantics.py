"""
nwd/atlas/formal_semantics.py

Gate 1: Formal Semantics and Observational Trace Equivalence Harness.
Proves equivalence between speculatively normalized execution and canonical sequential execution:
1. Intermediate observable output equivalence: y_spec == y_seq.
2. Final state observable subspace preservation: O(sigma_spec) == O(sigma_seq).
3. Machine-checkable retraction invariants:
   - Idempotence: R(R(sigma)) == R(sigma)
   - Observable invariance: O(R(sigma)) == O(sigma)
   - Manifold stability: sigma in M ==> R(sigma) == sigma
4. Adversarial negative controls:
   - Detects unsafe reordering of non-commuting operations.
   - Detects defective/corrupt normalizers.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple
import copy
import random

from nwd.atlas.schema_v04 import TraceEquivalenceResult, SafetyTierV04

MODULUS = 4093


@dataclass
class TransactionOp:
    tx_id: int
    op_type: str  # "READ_MODIFY_WRITE", "QUERY", "TRANSFER"
    read_regs: Tuple[int, ...]
    write_regs: Tuple[int, ...]
    delta_payload: int

    def execute(self, state: List[int]) -> Tuple[List[int], Any]:
        """
        Executes operation on state, returning (new_state, observable_output).
        """
        new_state = list(state)
        # Compute observable read value
        read_val = sum(new_state[r] for r in self.read_regs) % MODULUS
        # Compute output response event (e.g. transaction return value)
        obs_output = (read_val + self.delta_payload) % MODULUS
        # Apply writes
        for w in self.write_regs:
            new_state[w] = (new_state[w] + obs_output) % MODULUS
        return new_state, obs_output


class FormalSemanticsVerifier:
    """
    Verifies formal trace equivalence, retraction properties, and catches hazards.
    """
    def __init__(
        self,
        num_registers: int = 8,
        observable_indices: Tuple[int, ...] = (0, 1, 3, 4, 5, 6, 7),
        auxiliary_indices: Tuple[int, ...] = (2,)
    ):
        self.num_registers = num_registers
        self.observable_indices = observable_indices
        self.auxiliary_indices = auxiliary_indices

    def project_observable(self, state: List[int]) -> Tuple[int, ...]:
        return tuple(state[i] for i in self.observable_indices)

    def is_on_manifold(self, state: List[int]) -> bool:
        """Manifold M: auxiliary registers R[2] == 0 (mod MODULUS)."""
        return all(state[a] == 0 for a in self.auxiliary_indices)

    def valid_retraction(self, state: List[int]) -> List[int]:
        """Valid normalizer R: resets auxiliary coordinates to 0, strictly preserving observables."""
        s = list(state)
        for a in self.auxiliary_indices:
            s[a] = 0
        return s

    def defective_retraction_corrupt(self, state: List[int]) -> List[int]:
        """Defective normalizer: mutates observable register 1!"""
        s = list(state)
        s[1] = (s[1] + 1) % MODULUS
        for a in self.auxiliary_indices:
            s[a] = 0
        return s

    def defective_retraction_non_idempotent(self, state: List[int]) -> List[int]:
        """Defective normalizer: non-idempotent shift."""
        s = list(state)
        s[2] = (s[2] // 2)  # Decrements rather than projecting to fixed point
        return s

    def verify_retraction_invariants(
        self,
        retraction_fn: Callable[[List[int]], List[int]],
        num_samples: int = 200,
        seed: int = 42
    ) -> Dict[str, Any]:
        """
        Formally tests machine-checkable retraction invariants over state space.
        """
        rng = random.Random(seed)
        idempotent = True
        observable_preserved = True
        manifold_stable = True

        for _ in range(num_samples):
            st = [rng.randint(0, MODULUS - 1) for _ in range(self.num_registers)]
            r1 = retraction_fn(st)
            r2 = retraction_fn(r1)

            # Invariant 1: Idempotence R(R(s)) == R(s)
            if r1 != r2:
                idempotent = False

            # Invariant 2: Observable preservation O(R(s)) == O(s)
            if self.project_observable(r1) != self.project_observable(st):
                observable_preserved = False

            # Invariant 3: Manifold stability s in M ==> R(s) == s
            st_m = list(st)
            for a in self.auxiliary_indices:
                st_m[a] = 0
            if retraction_fn(st_m) != st_m:
                manifold_stable = False

        return {
            "idempotent": idempotent,
            "observable_preserved": observable_preserved,
            "manifold_stable": manifold_stable,
            "all_invariants_hold": (idempotent and observable_preserved and manifold_stable)
        }

    def verify_trace_equivalence(
        self,
        initial_state: List[int],
        transactions: List[TransactionOp],
        retraction_fn: Optional[Callable[[List[int]], List[int]]] = None,
        speculative_schedule: Optional[List[int]] = None,
        inject_corrupt_reorder: bool = False
    ) -> TraceEquivalenceResult:
        """
        Executes both canonical sequential and speculative normalized schedules.
        Checks both intermediate outputs and terminal observable state.
        """
        # 1. Canonical Sequential Execution
        seq_state = list(initial_state)
        seq_outputs: List[Any] = []
        for tx in transactions:
            seq_state, out = tx.execute(seq_state)
            seq_outputs.append((tx.tx_id, out))

        # 2. Speculative Execution
        if retraction_fn is None:
            retraction_fn = self.valid_retraction

        # Determine transaction execution order
        if speculative_schedule is not None:
            order = list(speculative_schedule)
        elif inject_corrupt_reorder:
            # Force non-commutative reordering
            order = list(range(len(transactions)))
            if len(order) >= 2:
                order[0], order[1] = order[1], order[0]
        else:
            order = list(range(len(transactions)))

        spec_state = list(initial_state)
        spec_outputs: List[Any] = []

        # Execute in speculative order
        for idx in order:
            tx = transactions[idx]
            spec_state, out = tx.execute(spec_state)
            spec_outputs.append((tx.tx_id, out))

        # Apply normalizer at boundary
        spec_state_normalized = retraction_fn(spec_state)

        # Sort outputs by tx_id to test if transactions produced identical canonical results
        seq_out_dict = {tx_id: out for tx_id, out in seq_outputs}
        spec_out_dict = {tx_id: out for tx_id, out in spec_outputs}

        outputs_match = (seq_out_dict == spec_out_dict)
        final_obs_match = (self.project_observable(spec_state_normalized) == self.project_observable(seq_state))

        traces_equivalent = outputs_match and final_obs_match

        mismatch_details = None
        if not traces_equivalent:
            mismatch_details = {
                "outputs_match": outputs_match,
                "final_obs_match": final_obs_match,
                "seq_obs_state": self.project_observable(seq_state),
                "spec_obs_state": self.project_observable(spec_state_normalized),
                "seq_output_sample": seq_outputs[:5],
                "spec_output_sample": spec_outputs[:5]
            }

        return TraceEquivalenceResult(
            workload_id=f"tx_count_{len(transactions)}",
            num_transactions=len(transactions),
            intermediate_outputs_match=outputs_match,
            final_observable_state_matches=final_obs_match,
            unauthorized_side_effects=not final_obs_match,
            traces_equivalent=traces_equivalent,
            mismatch_details=mismatch_details,
            proof_obligation_notes=(
                "Observational trace equivalence holds across all intermediate outputs and terminal states."
                if traces_equivalent
                else "Trace divergence detected: intermediate outputs or final observable projections differ."
            )
        )
