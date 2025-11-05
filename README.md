[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ebaigeslen/gestrix/blob/main/notebooks/00_colab_bootstrap.ipynb)

# Gestrix

Gestrix is a research framework for **neuro-symbolic AI planning**.
It combines classical planners (e.g., Fast Downward) with modern neural/LLM reasoning to evaluate and push the boundaries of planning benchmarks like **PlanBench**.

---

## Project Goals
- Reproduce classical baselines on benchmark domains.
- Integrate neuro-symbolic methods with reproducible pipelines.
- Enable seamless execution both locally and on **Google Colab**.
- Support reproducibility via Docker, Makefiles, and CI pipelines.

---

## Repository Structure
## Dataset Handling (Day 3)

- **Folders:** `data/raw` (original), `data/interim` (temp), `data/processed` (final/mini), `data/external` (3rd-party drops).
- **Integrity:** Run `python scripts/gen_checksums.py` after adding/changing raw files. Verify with `make verify-data`.
- **Licensing:** See **DATA_LICENSES.md**. Never publish data without license info.
- **CI Mini Sets:** Only 2–3 tiny `.pddl` per domain live in `data/processed/mini/` for fast CI.
- **Large Data:** Keep out of Git. Use Git LFS or an external mirror (link sources in docs/ADR-002 and DATA_LICENSES.md).
