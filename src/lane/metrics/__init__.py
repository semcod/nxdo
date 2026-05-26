"""Code metrics collection for intelligent refactoring planning."""

from .coupling import collect_coupling_matrix, get_coupling_clusters, CouplingMetrics
from .hotspots import identify_bug_hotspots, calculate_bus_factor, HotspotMetrics
from .complexity import collect_file_metrics, FileMetrics

__all__ = [
    "collect_coupling_matrix",
    "get_coupling_clusters",
    "CouplingMetrics",
    "identify_bug_hotspots",
    "calculate_bus_factor",
    "HotspotMetrics",
    "collect_file_metrics",
    "FileMetrics",
]
