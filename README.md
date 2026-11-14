# FNWD v0.4 — Autonomous Discovery of Idempotent State-Space Retractions and Conditional Commutation Manifolds

**Author:** Kyle W. Luecke ([Driftbound Labs](https://driftboundlabs.com)) · ORCID: [`0009-0008-0202-7852`](https://orcid.org/0009-0008-0202-7852)

This repository contains the manuscript, standalone zero-dependency verification package (`nwd/atlas/`), immutable algebraic discovery catalogs (`nwd/results/`), and reproducibility manifest for **Formal Normalizer–Workload Discovery (FNWD v0.4)**.

---

## Overview

Concurrent transaction optimizers traditionally require operations to commute unconditionally across an entire state space $\Sigma$. When operations commute only on a restricted submanifold $\mathcal{M} \subsetneq \Sigma$, ordinary execution drifts off $\mathcal{M}$ as auxiliary bookkeeping state, causal tombstones, or structural tree skew accumulate.

**FNWD v0.4** discovers and verifies **enabler–optimizer compositions ($E \otimes O$)** that pair an idempotent observational retraction $E: \Sigma \to \mathcal{M}$ ($E^2 = E$, $\mathcal{O} \circ E = \mathcal{O}$) with a conditional commutator $O$ valid on $\mathcal{M} = \operatorname{Fix}(E)$:

1. **Quotient Projection Poset $(P, \le)$**: Audits 127 verified idempotent maps over $\mathbb{F}_{4093}^4 \times \mathbb{F}_{4093}^8 \times \mathcal{M}_{64}$, falsifies noncommuting right-zero bands on unconstrained state, and quotients syntactic variants into **115 distinct image equivalence classes** with **18 strict nested chains** ($[B] < [A]$) and **100.0% zero-probe deductive prediction** across 100 test pairs.
2. **Pre-Specified Six-Gate Verification Suite**:
   - **Gate 1 (`formal_semantics.py`)**: Intermediate client-event ($\vec{y}_{\text{spec}} \equiv \vec{y}_{\text{seq}}$) and terminal observable ($\mathcal{O}(\sigma_{\text{spec}}) \equiv \mathcal{O}(\sigma_{\text{seq}})$) trace equivalence across 200 randomized initial states, rejecting corrupt and non-idempotent negative controls.
   - **Gate 2 (`linearizability_oracle.py`)**: External black-box Herlihy–Wing / Lowe real-time linearizability oracle (`15/15` valid concurrent histories passed; `30/30` injected RAW and causal-inversion faults detected).
   - **Gate 3 (`causal_ablation.py`)**: $2 \times 3$ factorial ablation isolating mathematical retraction (`-94.3%` lock acquisitions, `38.5x` throughput, zero auxiliary drift) from coarse batching confounds.
   - **Gate 4 (`domain_crdt.py`, `domain_trie.py`)**: Cross-domain transfer across Modular Affine Register Automata (`43.1x` speedup), CRDT Observed-Remove Sets (`1.68x` speedup), and Transactional Key-Value DSW Trees (`-93.3%` locks, plus honest characterization of the `+69.6%` small-tree DSW rebuild latency crossover at $N = 150$).
   - **Gate 5 (`paired_statistics.py`)**: Paired non-parametric validation ($N = 30$ paired workloads/domain, 10,000 sign-flip permutations, Wilcoxon signed-rank, 99% bootstrap CIs, Holm–Bonferroni $p_{\text{adj}} = 0.0006 < 0.01$ across all 6 endpoints).
   - **Gate 6 & Blind Discovery (`blind_discovery.py`, `run_atlas_v04.py`)**: Autonomous zero-label triage over 12 unlabeled operators (`3/3` valid compositions promoted, `0/9` unsound/corrupt operators promoted) and SHA-256 provenance verification (`seed=42`).

---

## Quick Reproduction (`< 5 seconds`, Python 3.10+ Standard Library Only)

No third-party packages are required to run the full verification suite:

```bash
python -m nwd.atlas.run_atlas_v04
```

Expected terminal summary:
- `GATE 1` (Formal Trace Semantics): `PASS`
- `GATE 2` (Black-Box Linearizability): `PASS` (`15/15` valid, `30/30` faults caught)
- `GATE 3` (Causal $2 \times 3$ Factorial Ablation): `PASS` (`-94.3%` locks)
- `GATE 4` (Cross-Domain Generalization): `PASS` (3 domains verified)
- `GATE 5` (Paired Statistical Rigor): `PASS` (all 6 Holm $p_{\text{adj}} < 0.01$)
- `BLIND DISCOVERY` (12 Unlabeled Operators): `PASS` (`3/3` promoted, `0/9` false positives)
- `GATE 6` (Cryptographic Provenance): `PASS`

---

## Repository Layout

```text
.
├── FNWD_v04_Algebraic_Retraction.md     # Preprint manuscript source
├── FNWD_v04_Algebraic_Retraction.pdf    # Compiled publication PDF (8 pages)
├── references.bib                       # BibTeX bibliography (13 entries)
├── figures/
│   ├── fig1_ablation_and_domains.pdf    # Vector Figure 1 (Gate 3 + Gates 4–5)
│   └── fig1_ablation_and_domains.png    # Raster preview
├── nwd/
│   ├── atlas/                           # Standalone v0.4 verification suite (9 modules)
│   └── results/                         # Immutable JSON catalogs & provenance manifest
├── CITATION.cff                         # Citation metadata
├── .zenodo.json                         # Zenodo archival metadata
└── LICENSE                              # MIT (code) + CC BY 4.0 (manuscript & catalogs)
```

---

## License

- **Verification Software (`nwd/atlas/*.py`)**: MIT License.
- **Manuscript, Figures & Algebraic Catalogs (`*.md`, `*.pdf`, `figures/*`, `nwd/results/*.json`)**: Creative Commons Attribution 4.0 International (`CC BY 4.0`).
