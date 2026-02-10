"""Tools for managing session state."""

import numpy as np
from smolagents import tool
from mcp_utils.session import get_session


@tool
def list_datasets() -> dict:
    """
    List all datasets in session.

    Returns:
        Dictionary with count and list of dataset summaries
    """
    session = get_session()
    datasets = session.list_datasets()
    return {
        "count": len(datasets),
        "datasets": [
            {
                "name": info.name,
                "row_count": info.row_count,
                "columns": info.columns[:10],
                "source": info.path if info.path else f"derived from {info.parent}",
            }
            for info in datasets
        ],
    }


@tool
def describe_dataset(name: str) -> dict:
    """
    Get detailed info about a dataset.

    Args:
        name: Name of the dataset

    Returns:
        Dictionary with full dataset metadata
    """
    session = get_session()
    info = session.get_dataset_info(name)
    return {
        "name": info.name,
        "row_count": info.row_count,
        "columns": info.columns,
        "source_path": info.path,
        "parent": info.parent,
        "transform": info.transform,
    }


@tool
def delete_dataset(name: str) -> str:
    """
    Delete a dataset from session.

    Args:
        name: Name of the dataset to delete

    Returns:
        Confirmation message
    """
    session = get_session()
    if session.delete_dataset(name):
        return f"Deleted '{name}'"
    return f"Dataset '{name}' not found"


@tool
def clear_session() -> str:
    """
    Clear all datasets from session.

    Returns:
        Confirmation message
    """
    session = get_session()
    count = len(session.list_datasets())
    session.clear()
    return f"Cleared {count} datasets"


@tool
def preview_dataset(name: str, n: int = 5) -> dict:
    """
    Preview first N values from a dataset.

    Args:
        name: Name of the dataset
        n: Number of values to show (default: 5, max: 20)

    Returns:
        Dictionary with preview data as JSON-safe values
    """
    if n > 20:
        n = 20

    session = get_session()
    data = session.get_dataset(name)
    info = session.get_dataset_info(name)

    if isinstance(data, np.ndarray):
        preview = data[:n].tolist()
        return {
            "name": name,
            "type": "array",
            "shape": list(data.shape),
            "dtype": str(data.dtype),
            "preview": preview,
            "total_count": len(data),
        }
    elif isinstance(data, dict):
        preview = {}
        for key, val in data.items():
            if isinstance(val, np.ndarray):
                preview[key] = val[:n].tolist()
            else:
                preview[key] = val
        return {
            "name": name,
            "type": "dict",
            "keys": list(data.keys()),
            "preview": preview,
            "total_count": info.row_count,
        }
    else:
        return {
            "name": name,
            "type": str(type(data).__name__),
            "preview": str(data)[:500],
        }


@tool
def compute_statistics(name: str) -> dict:
    """
    Compute summary statistics for a dataset.

    Args:
        name: Name of the dataset

    Returns:
        Dictionary with min, max, mean, std for arrays.
        For dicts, returns stats for each array value.
    """
    session = get_session()
    data = session.get_dataset(name)

    def array_stats(arr):
        return {
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "count": int(len(arr)),
        }

    if isinstance(data, np.ndarray):
        return {
            "name": name,
            "type": "array",
            "stats": array_stats(data),
        }
    elif isinstance(data, dict):
        stats = {}
        for key, val in data.items():
            if isinstance(val, np.ndarray):
                stats[key] = array_stats(val)
            else:
                stats[key] = {"value": val, "type": str(type(val).__name__)}
        return {
            "name": name,
            "type": "dict",
            "stats": stats,
        }
    else:
        return {
            "name": name,
            "type": str(type(data).__name__),
            "error": "Statistics not available for this type",
        }


@tool
def compute_histogram(name: str, bins: int = 50, key: str = None) -> dict:
    """
    Compute histogram for a dataset.

    Args:
        name: Name of the dataset
        bins: Number of bins (default: 50, max: 200)
        key: For dict datasets, which key to use (required for dicts)

    Returns:
        Dictionary with bin_edges and counts arrays
    """
    if bins > 200:
        bins = 200

    session = get_session()
    data = session.get_dataset(name)

    if isinstance(data, dict):
        if key is None:
            return {
                "name": name,
                "error": f"Dataset is a dict. Specify key from: {list(data.keys())}",
            }
        if key not in data:
            return {
                "name": name,
                "error": f"Key '{key}' not found. Available: {list(data.keys())}",
            }
        arr = data[key]
    elif isinstance(data, np.ndarray):
        arr = data
    else:
        return {
            "name": name,
            "error": "Histogram not available for this type",
        }

    counts, bin_edges = np.histogram(arr, bins=bins)

    return {
        "name": name,
        "key": key,
        "bins": bins,
        "bin_edges": bin_edges.tolist(),
        "counts": counts.tolist(),
        "total_count": int(np.sum(counts)),
    }


@tool
def compute_percentiles(name: str, percentiles: list = None, key: str = None) -> dict:
    """
    Compute percentiles for a dataset.

    Args:
        name: Name of the dataset
        percentiles: List of percentiles to compute (default: [5, 16, 50, 84, 95])
        key: For dict datasets, which key to use (required for dicts)

    Returns:
        Dictionary mapping percentile values to data values
    """
    if percentiles is None:
        percentiles = [5, 16, 50, 84, 95]

    session = get_session()
    data = session.get_dataset(name)

    if isinstance(data, dict):
        if key is None:
            return {
                "name": name,
                "error": f"Dataset is a dict. Specify key from: {list(data.keys())}",
            }
        if key not in data:
            return {
                "name": name,
                "error": f"Key '{key}' not found. Available: {list(data.keys())}",
            }
        arr = data[key]
    elif isinstance(data, np.ndarray):
        arr = data
    else:
        return {
            "name": name,
            "error": "Percentiles not available for this type",
        }

    values = np.percentile(arr, percentiles)

    return {
        "name": name,
        "key": key,
        "percentiles": {int(p): float(v) for p, v in zip(percentiles, values)},
        "count": len(arr),
    }
