# Project Plan

## Goal

Build a reproducible workflow on top of the published Drosophila brain model so that a neuron class such as `L1`, `L2`, or `T3` can be selected by name, mapped to real FlyWire neuron IDs, stimulated in the connectome-based model, and analyzed by downstream neural activity.

The project focuses on neural activity propagation rather than inventing behavior rules.

## Core principles

- Use real FlyWire connectome data for connectivity.
- Do not invent neuron-to-neuron connections.
- Keep the original published model behavior intact unless a change is necessary and documented.
- Clearly separate measured/public data from model assumptions.
- Do not infer missing biological properties without evidence.
- Prefer small, reproducible tests before large simulations.
- Record enough metadata to reproduce every experiment.

## Current repository state

The repository already contains:

- `model.py`: Brian2 leaky integrate-and-fire brain model.
- `utils.py`: result loading and firing-rate helpers.
- `example.ipynb`: original example workflow.
- FlyWire v630 data used in the original work.
- FlyWire v783 files:
  - `Completeness_783.csv`
  - `Connectivity_783.parquet`
- `quick_test_v783.py`: minimal v783 smoke test.
- `neuron_lookup.py`: exact FlyWire v783 cell-type lookup.
- `annotations/Supplemental_file1_neuron_annotations_v2.1.0.tsv`: FlyWire v783 annotations.
- `.github/workflows/v783-smoke-test.yml`: GitHub Actions smoke-test workflow.

## Phase 1 — Verify the v783 model

### Objective

Confirm that the current repository can run the published model with FlyWire v783 data.

### Tasks

- [x] Run `quick_test_v783.py` locally.
- [x] Confirm that `Completeness_783.csv` loads successfully.
- [x] Confirm that `Connectivity_783.parquet` loads successfully.
- [x] Confirm that a valid FlyWire neuron ID maps into the model.
- [x] Run a 100 ms, single-trial simulation.
- [x] Confirm that a result parquet file is created.
- [x] Confirm that spike events can be read from the result.
- [x] Fix only issues required for v783 compatibility.
- [x] Document any compatibility changes.

### Phase 1 verification

`python3 quick_test_v783.py` passed. This environment does not provide a
`python` command, so the equivalent `python3` interpreter was used; no model
or v783 compatibility code changes were required.

### Completion condition

`python quick_test_v783.py` finishes successfully and reports recorded spikes / active neurons.

---

## Phase 2 — Neuron type lookup

### Objective

Allow neuron types to be selected by biological name instead of manually entering FlyWire IDs.

Example target interface:

```python
get_neurons("L1")
get_neurons("L2")
get_neurons("T3")
```

### Tasks

- [x] Add a FlyWire annotation / cell-type dataset compatible with v783.
- [x] Create `neuron_lookup.py`.
- [x] Implement exact cell-type lookup.
- [x] Return all matching FlyWire IDs.
- [x] Handle missing or ambiguous names explicitly.
- [x] Add tests for several known cell types.

### Phase 2 verification

The vendored annotation table is FlyWire annotations v2.1.0, based on
materialization 783. `get_neurons("L1")`, `get_neurons("L2")`, and
`get_neurons("T3")` return 1,579, 1,554, and 1,615 model-compatible IDs,
respectively. `python3 -m unittest -v test_neuron_lookup.py` passes.

### Completion condition

A cell type name such as `L1` returns the corresponding real FlyWire IDs without manual lookup.

---

## Phase 3 — Simple simulation interface

### Objective

Create a small command-line interface for experiments while leaving `model.py` as close to the published source as possible.

Target usage:

```bash
python simulate.py --activate L1
python simulate.py --activate L1 L2
python simulate.py --activate L1 --silence Mi1
```

### Tasks

- [ ] Create `simulate.py`.
- [ ] Resolve neuron names through `neuron_lookup.py`.
- [ ] Pass resolved FlyWire IDs into `run_exp`.
- [ ] Expose trial duration, trial count, and stimulation rate as explicit options.
- [ ] Store experiment parameters with each run.
- [ ] Use safe output naming and prevent accidental overwrites.

### Completion condition

A user can run an experiment using only neuron type names.

---

## Phase 4 — Annotated output

### Objective

Convert raw FlyWire-ID spike output into biologically readable results.

Target output:

```text
time      flywire_id           cell_type
0.023     720575940...         Mi1
0.031     720575940...         Tm3
0.034     720575940...         T4a
```

### Tasks

- [ ] Join spike results with FlyWire annotations.
- [ ] Preserve the original FlyWire ID.
- [ ] Add cell type / annotation fields where available.
- [ ] Mark unknown annotations as unknown rather than guessing.
- [ ] Export annotated parquet and/or CSV files.

### Completion condition

Simulation results can be interpreted without manually searching long FlyWire IDs.

---

## Phase 5 — Neural activity analysis

### Objective

Summarize how activity propagates after stimulation.

### Metrics

- Number of active neurons.
- Spike count.
- Mean firing rate.
- Response latency.
- Cell types activated.
- Activity shared between conditions.
- Activity specific to each condition.

### Tasks

- [ ] Create `analysis.py`.
- [ ] Rank downstream neurons and cell types by response.
- [ ] Calculate firing rates across repeated trials.
- [ ] Calculate first-spike / response latency where meaningful.
- [ ] Compare multiple stimulation conditions.
- [ ] Export machine-readable summary tables.
- [ ] Add simple plots only after the numerical pipeline is validated.

---

## Phase 6 — Sensory pathway experiments

### Objective

Compare activity propagation from different sensory pathways.

Initial candidate groups:

### Visual

- L1
- L2
- L3
- T3
- additional well-annotated visual neurons where appropriate

### Olfactory

- identified olfactory receptor neurons or other well-supported sensory input classes

### Mechanosensory

- identified mechanosensory neurons with reliable FlyWire annotations

### Experimental structure

For each input class:

1. Resolve real FlyWire IDs.
2. Use the same stimulation protocol where biologically reasonable.
3. Run repeated trials.
4. Record raw spikes.
5. Annotate responding neurons.
6. Compare firing rate, latency, and downstream cell types.

---

## Controls

At minimum, compare conditions such as:

- No stimulation.
- Single sensory class stimulation.
- Another sensory class under the same protocol.
- Combined stimulation where relevant.
- Stimulation plus silencing of a specific downstream class where justified.

Controls should be added only when they answer a defined experimental question.

---

## Model limitations to track

The repository is not a literal biological simulation of every property of a fly neuron.

The model uses a leaky integrate-and-fire approximation and parameters defined in the published implementation. Therefore:

- Real connectivity does not mean all dynamics are directly measured.
- Poisson stimulation approximates experimental activation.
- Model parameters and empirical connectome data must be reported separately.
- Results should be described as predictions of a connectome-based computational model, not direct observations of a living fly.

## Reproducibility requirements

Every experiment should record:

- FlyWire dataset version.
- Input neuron IDs.
- Input cell-type names.
- Silenced neuron IDs / cell types, if any.
- Simulation duration.
- Number of trials.
- Stimulation frequency.
- Model parameter changes.
- Code commit hash when practical.
- Output filename.

## File structure target

```text
model.py              # published model; minimize edits
utils.py              # original helper functions
neuron_lookup.py      # cell type -> FlyWire IDs
simulate.py           # experiment CLI
analysis.py           # downstream analysis
quick_test_v783.py    # minimal compatibility test
PLAN.md               # project direction and task status
results/               # generated simulation outputs
```

## Rules for Codex / contributors

Before making changes:

1. Read this file.
2. Identify the current unfinished phase.
3. Inspect existing code before adding new abstractions.
4. Prefer the smallest change that advances the current phase.
5. Run relevant tests after changes.
6. Do not silently change scientific assumptions.
7. Document assumptions and data sources.
8. Update checklist items in this file when a phase is completed.

## Immediate next task

Run:

```bash
python quick_test_v783.py
```

Then:

1. Fix any runtime or v783 compatibility error.
2. Confirm that spike output is produced.
3. Record the result in this file.
4. Only after the smoke test passes, begin Phase 2.
