"""Test MCMC tools for basic functionality."""

import pytest
import sys
import numpy as np
import tempfile
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from codes.mcmc import (
    ln_prior_uniform,
    ln_prior_gaussian,
    initialize_walkers,
    extract_mcmc_results,
    save_mcmc_samples,
    load_mcmc_samples,
    format_mcmc_summary,
)


class TestPriorFunctions:
    """Test prior probability functions."""

    def test_uniform_prior_within_bounds(self):
        """Test uniform prior returns 0 for values within bounds."""
        param_bounds = [
            {'name': 'h', 'min': 0.6, 'max': 0.8},
            {'name': 'Omega_cdm', 'min': 0.1, 'max': 0.15},
        ]
        theta = [0.7, 0.12]  # Within bounds

        lp = ln_prior_uniform(theta, param_bounds)
        assert lp == 0.0, "Uniform prior should return 0 for values within bounds"

    def test_uniform_prior_outside_bounds(self):
        """Test uniform prior returns -inf for values outside bounds."""
        param_bounds = [
            {'name': 'h', 'min': 0.6, 'max': 0.8},
            {'name': 'Omega_cdm', 'min': 0.1, 'max': 0.15},
        ]
        theta = [0.5, 0.12]  # h is below minimum

        lp = ln_prior_uniform(theta, param_bounds)
        assert lp == -np.inf, "Uniform prior should return -inf for values outside bounds"

    def test_gaussian_prior_within_bounds(self):
        """Test Gaussian prior returns finite value for values within bounds."""
        param_bounds = [
            {'name': 'h', 'min': 0.6, 'max': 0.8},
            {'name': 'Omega_cdm', 'min': 0.1, 'max': 0.15},
        ]
        theta = [0.7, 0.125]  # Center of bounds

        lp = ln_prior_gaussian(theta, param_bounds)
        assert np.isfinite(lp), "Gaussian prior should return finite value within bounds"
        assert lp <= 0, "Log of Gaussian should be non-positive (0 at center)"

        # Test away from center should be negative
        theta_off = [0.65, 0.11]
        lp_off = ln_prior_gaussian(theta_off, param_bounds)
        assert lp_off < lp, "Gaussian prior should be lower away from center"

    def test_gaussian_prior_outside_bounds(self):
        """Test Gaussian prior returns -inf for values outside bounds."""
        param_bounds = [
            {'name': 'h', 'min': 0.6, 'max': 0.8},
        ]
        theta = [0.9]  # Outside bounds

        lp = ln_prior_gaussian(theta, param_bounds)
        assert lp == -np.inf, "Gaussian prior should return -inf outside bounds"


class TestWalkerInitialization:
    """Test MCMC walker initialization."""

    def test_uniform_initialization_within_bounds(self):
        """Test walkers are initialized within parameter bounds."""
        param_bounds = [
            {'name': 'h', 'min': 0.6, 'max': 0.8},
            {'name': 'Omega_cdm', 'min': 0.1, 'max': 0.15},
        ]
        nwalkers = 20

        pos0 = initialize_walkers(param_bounds, nwalkers, init_method='uniform')

        assert pos0.shape == (nwalkers, 2), f"Expected shape ({nwalkers}, 2), got {pos0.shape}"

        # Check all values within bounds
        assert np.all(pos0[:, 0] >= 0.6) and np.all(pos0[:, 0] <= 0.8), "h values out of bounds"
        assert np.all(pos0[:, 1] >= 0.1) and np.all(pos0[:, 1] <= 0.15), "Omega_cdm values out of bounds"

    def test_center_initialization_near_center(self):
        """Test center initialization puts walkers near center of bounds."""
        param_bounds = [
            {'name': 'h', 'min': 0.6, 'max': 0.8},
        ]
        nwalkers = 100

        pos0 = initialize_walkers(param_bounds, nwalkers, init_method='center')

        # Mean should be close to center (0.7)
        mean_h = np.mean(pos0[:, 0])
        assert abs(mean_h - 0.7) < 0.05, f"Mean {mean_h} should be close to center 0.7"

    def test_initialization_different_nwalkers(self):
        """Test initialization works for different walker counts."""
        param_bounds = [{'name': 'x', 'min': 0, 'max': 1}]

        for nwalkers in [8, 16, 32, 64]:
            pos0 = initialize_walkers(param_bounds, nwalkers)
            assert pos0.shape[0] == nwalkers, f"Expected {nwalkers} walkers"


class TestResultExtraction:
    """Test MCMC result extraction functions."""

    def test_extract_results_structure(self):
        """Test extract_mcmc_results returns correct structure."""
        # Create fake samples
        np.random.seed(42)
        samples = np.random.randn(1000, 2)
        samples[:, 0] = samples[:, 0] * 0.01 + 0.7  # h ~ N(0.7, 0.01)
        samples[:, 1] = samples[:, 1] * 0.005 + 0.12  # Omega_cdm ~ N(0.12, 0.005)
        param_names = ['h', 'Omega_cdm']

        results = extract_mcmc_results(samples, param_names)

        assert isinstance(results, dict), "Should return dictionary"
        assert 'h' in results, "Should have 'h' key"
        assert 'Omega_cdm' in results, "Should have 'Omega_cdm' key"

        for name in param_names:
            assert 'median' in results[name], f"{name} missing 'median'"
            assert 'mean' in results[name], f"{name} missing 'mean'"
            assert 'std' in results[name], f"{name} missing 'std'"
            assert 'upper_err' in results[name], f"{name} missing 'upper_err'"
            assert 'lower_err' in results[name], f"{name} missing 'lower_err'"

    def test_extract_results_values(self):
        """Test extracted values are reasonable."""
        np.random.seed(42)
        # Create samples with known mean
        samples = np.random.randn(10000, 1) * 0.1 + 5.0
        param_names = ['test_param']

        results = extract_mcmc_results(samples, param_names)

        # Mean should be close to 5.0
        assert abs(results['test_param']['mean'] - 5.0) < 0.05
        # Std should be close to 0.1
        assert abs(results['test_param']['std'] - 0.1) < 0.02


class TestSampleIO:
    """Test sample save/load functions."""

    def test_save_and_load_samples(self):
        """Test samples can be saved and loaded correctly."""
        # Create fake samples
        np.random.seed(42)
        samples = np.random.randn(100, 3)
        param_names = ['a', 'b', 'c']

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            filepath = f.name

        try:
            # Save
            save_mcmc_samples(samples, param_names, filepath)
            assert os.path.exists(filepath), "File should be created"

            # Load
            loaded_samples, loaded_names = load_mcmc_samples(filepath)

            assert loaded_names == param_names, "Parameter names should match"
            assert loaded_samples.shape == samples.shape, "Sample shape should match"
            np.testing.assert_array_almost_equal(loaded_samples, samples, decimal=6)
        finally:
            os.unlink(filepath)

    def test_save_creates_file(self):
        """Test save function creates file."""
        samples = np.array([[1.0, 2.0], [3.0, 4.0]])
        param_names = ['x', 'y']

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            filepath = f.name

        try:
            result_path = save_mcmc_samples(samples, param_names, filepath)
            assert result_path == filepath
            assert os.path.exists(filepath)
        finally:
            os.unlink(filepath)


class TestSummaryFormatting:
    """Test summary formatting functions."""

    def test_format_summary_structure(self):
        """Test format_mcmc_summary returns proper string."""
        results = {
            'h': {'median': 0.7, 'mean': 0.7, 'std': 0.01,
                  'upper_err': 0.01, 'lower_err': 0.01, 'upper': 0.71, 'lower': 0.69},
        }
        param_names = ['h']

        summary = format_mcmc_summary(results, param_names,
                                      acceptance_fraction=0.3,
                                      nwalkers=32, nburn=100, nrun=500)

        assert isinstance(summary, str), "Should return string"
        assert 'h' in summary, "Should contain parameter name"
        assert '0.7' in summary, "Should contain median value"
        assert '32' in summary, "Should contain nwalkers"
        assert '0.3' in summary or '0.30' in summary, "Should contain acceptance fraction"


class TestToolImports:
    """Test that MCP tools can be imported and have correct attributes."""

    def test_mcmc_tools_import(self):
        """Test MCMC tools can be imported."""
        from tools.mcmc_tools import (
            run_mcmc_cosmology,
            create_mcmc_corner_plot,
            create_mcmc_trace_plot,
            analyze_mcmc_samples,
            compute_best_fit_power_spectrum,
        )

        tools = [
            run_mcmc_cosmology,
            create_mcmc_corner_plot,
            create_mcmc_trace_plot,
            analyze_mcmc_samples,
            compute_best_fit_power_spectrum,
        ]

        for tool in tools:
            assert callable(tool), f"{tool} should be callable"
            assert hasattr(tool, 'name'), f"{tool} should have 'name' attribute"

    def test_mcmc_tools_have_descriptions(self):
        """Test MCMC tools have descriptions."""
        from tools.mcmc_tools import (
            run_mcmc_cosmology,
            create_mcmc_corner_plot,
            create_mcmc_trace_plot,
            analyze_mcmc_samples,
            compute_best_fit_power_spectrum,
        )

        tools = [
            run_mcmc_cosmology,
            create_mcmc_corner_plot,
            create_mcmc_trace_plot,
            analyze_mcmc_samples,
            compute_best_fit_power_spectrum,
        ]

        for tool in tools:
            desc = getattr(tool, 'description', None) or tool.__doc__
            assert desc is not None, f"{tool.name} should have description"
            assert len(desc) > 10, f"{tool.name} description too short"


class TestMCPDiscovery:
    """Test tools are discoverable by MCP server."""

    def test_mcmc_tools_discovered(self):
        """Test MCMC tools are discovered by MCP server."""
        from mcp_server import discover_tools

        tools = discover_tools()

        expected_mcmc_tools = [
            'run_mcmc_cosmology',
            'create_mcmc_corner_plot',
            'create_mcmc_trace_plot',
            'analyze_mcmc_samples',
            'compute_best_fit_power_spectrum',
        ]

        for tool_name in expected_mcmc_tools:
            assert tool_name in tools, f"MCMC tool '{tool_name}' not discovered"

    def test_all_tools_callable(self):
        """Test all discovered tools are callable."""
        from mcp_server import discover_tools

        tools = discover_tools()

        for name, func in tools.items():
            assert callable(func), f"Tool '{name}' is not callable"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
