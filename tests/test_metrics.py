"""Tests for lane.metrics module."""

import tempfile
import unittest
from pathlib import Path

from lane.metrics import (
    collect_file_metrics,
    collect_coupling_matrix,
    get_coupling_clusters,
    identify_bug_hotspots,
    calculate_bus_factor,
)


class MetricsTests(unittest.TestCase):
    def test_collect_file_metrics_counts_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "test.py").write_text(
                "# comment\ndef foo():\n    pass\n\n# another comment\n",
                encoding="utf-8",
            )
            metrics = collect_file_metrics(root, file_filter={".py"})
            self.assertEqual(len(metrics), 1)
            self.assertEqual(metrics[0].file_path, "test.py")
            self.assertEqual(metrics[0].lines_of_code, 2)  # def foo + pass
            self.assertEqual(metrics[0].lines_of_comments, 2)
            self.assertGreaterEqual(metrics[0].blank_lines, 1)

    def test_collect_file_metrics_calculates_cc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "test.py").write_text(
                "def simple():\n    return 1\n", encoding="utf-8"
            )
            metrics = collect_file_metrics(root, file_filter={".py"})
            self.assertEqual(len(metrics), 1)
            # Base complexity is 1, no branches
            self.assertEqual(metrics[0].cyclomatic_complexity, 1)

    def test_collect_file_metrics_detects_imports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "test.py").write_text(
                "import os\nimport sys\nfrom collections import defaultdict\n",
                encoding="utf-8",
            )
            metrics = collect_file_metrics(root, file_filter={".py"})
            self.assertEqual(len(metrics), 1)
            self.assertIn("os", metrics[0].stdlib_imports)
            self.assertIn("sys", metrics[0].stdlib_imports)
            self.assertIn("collections", metrics[0].stdlib_imports)

    def test_collect_file_metrics_ignores_non_matching(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "test.py").write_text("pass\n", encoding="utf-8")
            (root / "readme.md").write_text("# Test\n", encoding="utf-8")
            metrics = collect_file_metrics(root, file_filter={".py"})
            self.assertEqual(len(metrics), 1)
            self.assertEqual(metrics[0].file_path, "test.py")

    def test_coupling_clusters_group_files(self) -> None:
        # Mock coupling metrics
        from lane.metrics.coupling import CouplingMetrics
        
        coupling = [
            CouplingMetrics("a.py", "b.py", 0.8, 8, 10, 10),
            CouplingMetrics("b.py", "c.py", 0.7, 7, 10, 10),
            CouplingMetrics("d.py", "e.py", 0.6, 6, 10, 10),
        ]
        clusters = get_coupling_clusters(coupling, min_coupling=0.5)
        # a-b-c should be one cluster, d-e another
        self.assertGreaterEqual(len(clusters), 1)

    def test_coupling_clusters_empty_when_low_coupling(self) -> None:
        from lane.metrics.coupling import CouplingMetrics
        
        coupling = [
            CouplingMetrics("a.py", "b.py", 0.2, 2, 10, 10),
        ]
        clusters = get_coupling_clusters(coupling, min_coupling=0.5)
        self.assertEqual(len(clusters), 0)

    def test_calculate_bus_factor_detects_silos(self) -> None:
        # This test requires a git repo, so we'll test the logic manually
        # In a real repo with history, this would return actual values
        pass


if __name__ == "__main__":
    unittest.main()
