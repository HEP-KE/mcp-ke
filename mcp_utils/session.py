"""Session management for MCP-KE server.

Uses file-backed storage so session state survives across MCP subprocess
restarts.  langchain-mcp-adapters with stdio transport spawns a **new
process for every tool call**, so purely in-memory state is lost between
calls.  This module transparently persists numpy arrays as .npy files and
keeps a JSON index for metadata.
"""

from dataclasses import dataclass, asdict
from typing import Any, Optional
import json
import os

import numpy as np


@dataclass
class DatasetInfo:
    name: str
    path: Optional[str]
    parent: Optional[str]
    transform: Optional[str]
    row_count: int
    columns: list[str]


def _session_dir() -> str:
    """Return (and create) the directory used for persisted session data."""
    from mcp_utils.path_utils import get_output_dir
    d = os.path.join(get_output_dir(), "_datasets")
    os.makedirs(d, exist_ok=True)
    return d


_INDEX_FILE = "_index.json"


class Session:
    def __init__(self, max_datasets: int = 50):
        self._cache: dict[str, Any] = {}          # in-memory cache
        self._dataset_info: dict[str, DatasetInfo] = {}
        self._max_datasets = max_datasets
        self._counter = 0
        self._dir = _session_dir()
        self._index_path = os.path.join(self._dir, _INDEX_FILE)
        self._load_index()

    # -- public API -----------------------------------------------------------

    def load_dataset(self, data: Any, path: str = None, name: str = None) -> tuple[str, DatasetInfo]:
        if name is None:
            if path:
                base = os.path.splitext(os.path.basename(path))[0]
                name = self._unique_name(base)
            else:
                name = self._unique_name("dataset")

        row_count, columns = self._get_metadata(data)
        info = DatasetInfo(name=name, path=path, parent=None, transform=None,
                          row_count=row_count, columns=columns)

        self._cache[name] = data
        self._dataset_info[name] = info
        self._persist(name, data)
        self._save_index()
        self._enforce_limit()
        return name, info

    def get_dataset(self, name: str) -> Any:
        # Try in-memory cache first
        if name in self._cache:
            return self._cache[name]

        # Try loading from disk
        data = self._load_from_disk(name)
        if data is not None:
            self._cache[name] = data
            return data

        available = list(self._dataset_info.keys())
        raise KeyError(f"Dataset '{name}' not found. Available: {available}")

    def get_dataset_info(self, name: str) -> DatasetInfo:
        if name not in self._dataset_info:
            raise KeyError(f"Dataset info '{name}' not found.")
        return self._dataset_info[name]

    def store_derived(self, data: Any, parent_name: str, transform: str, name: str = None) -> tuple[str, DatasetInfo]:
        if name is None:
            name = self._unique_name(f"{parent_name}_{transform.split('(')[0]}")

        row_count, columns = self._get_metadata(data)
        info = DatasetInfo(name=name, path=None, parent=parent_name, transform=transform,
                          row_count=row_count, columns=columns)

        self._cache[name] = data
        self._dataset_info[name] = info
        self._persist(name, data)
        self._save_index()
        self._enforce_limit()
        return name, info

    def list_datasets(self) -> list[DatasetInfo]:
        return list(self._dataset_info.values())

    def delete_dataset(self, name: str) -> bool:
        if name in self._dataset_info:
            self._cache.pop(name, None)
            del self._dataset_info[name]
            npy_path = os.path.join(self._dir, f"{name}.npy")
            if os.path.exists(npy_path):
                os.remove(npy_path)
            self._save_index()
            return True
        return False

    def clear(self):
        for name in list(self._dataset_info.keys()):
            npy_path = os.path.join(self._dir, f"{name}.npy")
            if os.path.exists(npy_path):
                os.remove(npy_path)
        self._cache.clear()
        self._dataset_info.clear()
        self._save_index()

    # -- persistence helpers --------------------------------------------------

    def _persist(self, name: str, data: Any):
        """Save a dataset to disk."""
        npy_path = os.path.join(self._dir, f"{name}.npy")
        if isinstance(data, np.ndarray):
            np.save(npy_path, data)
        elif isinstance(data, dict):
            # For dicts, save as a pickle-able .npy with allow_pickle
            np.save(npy_path, data, allow_pickle=True)
        elif isinstance(data, (list, tuple)):
            np.save(npy_path, np.asarray(data))
        # else: skip persistence for unknown types

    def _load_from_disk(self, name: str) -> Any:
        """Try to load a dataset from disk."""
        npy_path = os.path.join(self._dir, f"{name}.npy")
        if not os.path.exists(npy_path):
            return None
        try:
            data = np.load(npy_path, allow_pickle=True)
            # np.load wraps dicts in a 0-d array; unwrap
            if data.ndim == 0:
                data = data.item()
            return data
        except Exception:
            return None

    def _save_index(self):
        """Write dataset metadata index to disk."""
        index = {name: asdict(info) for name, info in self._dataset_info.items()}
        with open(self._index_path, "w") as f:
            json.dump(index, f, indent=2)

    def _load_index(self):
        """Restore dataset metadata from disk index."""
        if not os.path.exists(self._index_path):
            return
        try:
            with open(self._index_path) as f:
                index = json.load(f)
            for name, d in index.items():
                self._dataset_info[name] = DatasetInfo(**d)
        except Exception:
            pass  # start fresh if index is corrupted

    # -- internal helpers -----------------------------------------------------

    def _unique_name(self, base: str) -> str:
        if base not in self._dataset_info:
            return base
        self._counter += 1
        while f"{base}_{self._counter}" in self._dataset_info:
            self._counter += 1
        return f"{base}_{self._counter}"

    def _enforce_limit(self):
        while len(self._dataset_info) > self._max_datasets:
            for name in list(self._dataset_info.keys()):
                is_parent = any(i.parent == name for i in self._dataset_info.values() if i.name != name)
                if not is_parent:
                    self.delete_dataset(name)
                    break

    def _get_metadata(self, data: Any) -> tuple[int, list[str]]:
        if isinstance(data, np.ndarray):
            return len(data), [f"col_{i}" for i in range(data.shape[1] if data.ndim > 1 else 1)]
        elif isinstance(data, dict):
            return len(data), list(data.keys())
        elif isinstance(data, (list, tuple)):
            return len(data), [f"col_{i}" for i in range(len(data))]
        return 0, []


_session: Optional[Session] = None


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
    return _session


def reset_session():
    global _session
    _session = None
