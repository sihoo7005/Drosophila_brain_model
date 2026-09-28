"""Look up FlyWire v783 neurons by exact cell type.

Annotations: FlyWire annotations repository v2.1.0, based on materialization
783. Source: https://github.com/flyconnectome/flywire_annotations/tree/v2.1.0
"""

from functools import lru_cache
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
ANNOTATIONS_PATH = ROOT / "annotations" / "Supplemental_file1_neuron_annotations_v2.1.0.tsv"
COMPLETENESS_PATH = ROOT / "Completeness_783.csv"


@lru_cache(maxsize=1)
def _load_annotations() -> pd.DataFrame:
    """Load v783 annotations and retain neurons present in this model."""
    annotations = pd.read_csv(
        ANNOTATIONS_PATH,
        sep="\t",
        usecols=["root_id", "cell_type"],
        dtype={"root_id": "int64", "cell_type": "string"},
    )
    model_ids = pd.read_csv(COMPLETENESS_PATH, index_col=0).index.astype("int64")
    return annotations[annotations["root_id"].isin(model_ids)]


def get_neurons(cell_type: str) -> list[int]:
    """Return model-compatible FlyWire IDs for an exact cell type name.

    Matching ignores surrounding whitespace and letter case, but does not
    perform substring, regular-expression, or synonym matching.
    """
    if not isinstance(cell_type, str):
        raise TypeError("cell_type must be a string")

    query = cell_type.strip().casefold()
    if not query:
        raise ValueError("cell_type must not be empty")

    annotations = _load_annotations()
    matches = annotations[
        annotations["cell_type"].fillna("").str.strip().str.casefold().eq(query)
    ]
    labels = sorted(matches["cell_type"].dropna().unique().tolist())
    if len(labels) > 1:
        raise ValueError(f"Cell type name {cell_type!r} is ambiguous: {labels}")
    if not labels:
        raise ValueError(f"Unknown cell type: {cell_type!r}")

    return sorted(matches["root_id"].drop_duplicates().astype("int64").tolist())


if __name__ == "__main__":
    for name in ("L1", "L2", "T3"):
        print(f"{name}: {len(get_neurons(name))} neurons")
