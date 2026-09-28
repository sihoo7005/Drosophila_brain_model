"""Run the connectome model using FlyWire cell-type names."""

import argparse
import json
from copy import deepcopy
from pathlib import Path

from brian2 import Hz, ms

from model import default_params, run_exp
from neuron_lookup import get_neurons


ROOT = Path(__file__).resolve().parent
PATH_COMP = ROOT / "Completeness_783.csv"
PATH_CON = ROOT / "Connectivity_783.parquet"
DEFAULT_OUTPUT = ROOT / "results" / "simulate" / "simulation.parquet"


def _positive_float(value: str) -> float:
    value = float(value)
    if value <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return value


def _nonnegative_float(value: str) -> float:
    value = float(value)
    if value < 0:
        raise argparse.ArgumentTypeError("must not be negative")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the FlyWire v783 connectome model by cell type."
    )
    parser.add_argument(
        "--activate",
        nargs="+",
        default=[],
        metavar="CELL_TYPE",
        help="Cell type(s) to activate, for example L1 L2.",
    )
    parser.add_argument(
        "--silence",
        nargs="+",
        default=[],
        metavar="CELL_TYPE",
        help="Cell type(s) to silence, for example Mi1.",
    )
    parser.add_argument(
        "--duration",
        type=_positive_float,
        default=float(default_params["t_run"] / ms),
        metavar="MS",
        help="Trial duration in milliseconds (default: %(default)s).",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=default_params["n_run"],
        metavar="N",
        help="Number of trials (default: %(default)s).",
    )
    parser.add_argument(
        "--rate",
        type=_nonnegative_float,
        default=float(default_params["r_poi"] / Hz),
        metavar="HZ",
        help="Activation rate in Hz (default: %(default)s).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        metavar="PARQUET",
        help="Output parquet path (default: %(default)s).",
    )
    return parser


def _resolve_cell_types(cell_types: list[str]) -> list[int]:
    neuron_ids = set()
    for cell_type in cell_types:
        neuron_ids.update(get_neurons(cell_type))
    return sorted(neuron_ids)


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.trials < 1:
        parser.error("--trials must be at least 1")
    if args.output.suffix.lower() != ".parquet":
        parser.error("--output must end with .parquet")
    if not PATH_COMP.is_file() or not PATH_CON.is_file():
        parser.error("Completeness_783.csv and Connectivity_783.parquet are required")

    try:
        activate_ids = _resolve_cell_types(args.activate)
        silence_ids = _resolve_cell_types(args.silence)
    except (TypeError, ValueError) as exc:
        parser.error(str(exc))
    output = args.output.resolve()
    metadata_path = output.with_suffix(".json")
    if output.exists() or metadata_path.exists():
        parser.error(
            f"Refusing to overwrite existing output: {output} or {metadata_path}"
        )

    params = deepcopy(default_params)
    params["t_run"] = args.duration * ms
    params["n_run"] = args.trials
    params["r_poi"] = args.rate * Hz

    output.parent.mkdir(parents=True, exist_ok=True)
    run_exp(
        exp_name=output.stem,
        neu_exc=activate_ids,
        neu_slnc=silence_ids,
        path_res=output.parent,
        path_comp=PATH_COMP,
        path_con=PATH_CON,
        params=params,
        n_proc=1,
        force_overwrite=False,
    )

    metadata = {
        "dataset": "FlyWire v783",
        "activate": args.activate,
        "activate_ids": activate_ids,
        "silence": args.silence,
        "silence_ids": silence_ids,
        "duration_ms": args.duration,
        "trials": args.trials,
        "rate_hz": args.rate,
        "result": str(output),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Result: {output}")
    print(f"Metadata: {metadata_path}")


if __name__ == "__main__":
    main()
