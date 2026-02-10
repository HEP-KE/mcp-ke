"""Session management for MCP-KE server."""

from dataclasses import dataclass
from typing import Any, Optional
import numpy as np


@dataclass
class DatasetInfo:
    name: str
    path: Optional[str]
    parent: Optional[str]
    transform: Optional[str]
    row_count: int
    columns: list[str]


class Session:
    def __init__(self, max_datasets: int = 50):
        self._datasets: dict[str, Any] = {}
        self._dataset_info: dict[str, DatasetInfo] = {}
        self._max_datasets = max_datasets
        self._counter = 0

    def load_dataset(self, data: Any, path: str = None, name: str = None) -> tuple[str, DatasetInfo]:
        if name is None:
            if path:
                import os
                base = os.path.splitext(os.path.basename(path))[0]
                name = self._unique_name(base)
            else:
                name = self._unique_name("dataset")

        row_count, columns = self._get_metadata(data)
        self._datasets[name] = data
        info = DatasetInfo(name=name, path=path, parent=None, transform=None,
                          row_count=row_count, columns=columns)
        self._dataset_info[name] = info
        self._enforce_limit()
        return name, info

    def get_dataset(self, name: str) -> Any:
        if name not in self._datasets:
            available = list(self._datasets.keys())
            raise KeyError(f"Dataset '{name}' not found. Available: {available}")
        return self._datasets[name]

    def get_dataset_info(self, name: str) -> DatasetInfo:
        return self._dataset_info[name]

    def store_derived(self, data: Any, parent_name: str, transform: str, name: str = None) -> tuple[str, DatasetInfo]:
        if name is None:
            name = self._unique_name(f"{parent_name}_{transform.split('(')[0]}")

        row_count, columns = self._get_metadata(data)
        self._datasets[name] = data
        info = DatasetInfo(name=name, path=None, parent=parent_name, transform=transform,
                          row_count=row_count, columns=columns)
        self._dataset_info[name] = info
        self._enforce_limit()
        return name, info

    def list_datasets(self) -> list[DatasetInfo]:
        return list(self._dataset_info.values())

    def delete_dataset(self, name: str) -> bool:
        if name in self._datasets:
            del self._datasets[name]
            del self._dataset_info[name]
            return True
        return False

    def clear(self):
        self._datasets.clear()
        self._dataset_info.clear()

    def _unique_name(self, base: str) -> str:
        if base not in self._datasets:
            return base
        self._counter += 1
        while f"{base}_{self._counter}" in self._datasets:
            self._counter += 1
        return f"{base}_{self._counter}"

    def _enforce_limit(self):
        while len(self._datasets) > self._max_datasets:
            for name in list(self._datasets.keys()):
                is_parent = any(i.parent == name for i in self._dataset_info.values() if i.name != name)
                if not is_parent:
                    del self._datasets[name]
                    del self._dataset_info[name]
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
