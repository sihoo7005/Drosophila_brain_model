"""Minimal smoke test for FlyWire v783.

This script verifies that:
1. v783 completeness/connectivity files can be loaded,
2. a valid FlyWire neuron ID can be mapped into the Brian2 model,
3. a short simulation completes, and
4. spike output is written as a parquet file.

Run:
    python quick_test_v783.py

Optional:
    python quick_test_v783.py --neuron-id 720575940624963786
"""

from argparse import ArgumentParser
from copy import deepcopy
from pathlib import Path

import pandas as pd
from brian2 import ms

from model import default_params, run_exp


PATH_COMP = Path("./Completeness_783.csv")
PATH_CON = Path("./Connectivity_783.parquet")
PATH_RES = Path("./results/quick_test_v783")

# Neurons used by the original example notebook. The script picks the first
# one that is still present in v783, then falls back to the first v783 neuron.
EXAMPLE_NEURONS = [
    720575940624963786,
    720575940630233916,
    720575940637568838,
    720575940638202345,
    720575940617000768,
    720575940630797113,
    720575940632889389,
    720575940621754367,
    720575940621502051,
    720575940640649691,
    720575940639332736,
    720575940616885538,
    720575940639198653,
    720575940620900446,
    720575940617937543,
    720575940632425919,
    720575940633143833,
    720575940612670570,
    720575940628853239,
    720575940629176663,
    720575940611875570,
]


def choose_neuron(df_comp: pd.DataFrame, requested_id: int | None) -> int:
    available = set(int(x) for x in df_comp.index)

    if requested_id is not None:
        if requested_id not in available:
            raise ValueError(f"FlyWire ID {requested_id} is not present in v783.")
        return requested_id

    for neuron_id in EXAMPLE_NEURONS:
        if neuron_id in available:
            return neuron_id

    return int(df_comp.index[0])


def main() -> None:
    parser = ArgumentParser(description="Run a minimal FlyWire v783 smoke test.")
    parser.add_argument(
        "--neuron-id",
        type=int,
        default=None,
        help="Optional FlyWire neuron ID to activate.",
    )
    args = parser.parse_args()

    for path in (PATH_COMP, PATH_CON):
        if not path.is_file():
            raise FileNotFoundError(f"Required data file not found: {path}")

    print("Loading v783 neuron list...")
    df_comp = pd.read_csv(PATH_COMP, index_col=0)
    neuron_id = choose_neuron(df_comp, args.neuron_id)

    print(f"v783 neurons: {len(df_comp):,}")
    print(f"Test neuron: {neuron_id}")

    PATH_RES.mkdir(parents=True, exist_ok=True)

    params = deepcopy(default_params)
    params["t_run"] = 100 * ms
    params["n_run"] = 1

    exp_name = "smoke_test"

    print("Running 100 ms / 1 trial simulation...")
    run_exp(
        exp_name=exp_name,
        neu_exc=[neuron_id],
        path_res=PATH_RES,
        path_comp=PATH_COMP,
        path_con=PATH_CON,
        params=params,
        n_proc=1,
        force_overwrite=True,
    )

    result_path = PATH_RES / f"{exp_name}.parquet"
    if not result_path.is_file():
        raise RuntimeError(f"Simulation finished but result file is missing: {result_path}")

    df_spike = pd.read_parquet(result_path)

    print("\nSmoke test passed.")
    print(f"Result: {result_path}")
    print(f"Recorded spikes: {len(df_spike):,}")
    print(f"Active neurons: {df_spike['flywire_id'].nunique():,}")

    if len(df_spike):
        print("\nFirst spike rows:")
        print(df_spike.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
