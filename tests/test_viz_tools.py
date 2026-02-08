"""Test visualization tools array normalization and return values."""

import pytest
import sys
import os
import json
import tempfile
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.visualization_tools import _to_array, _parse_model_results


class TestToArray:
    """Test _to_array helper handles all MCP input formats."""

    def test_numpy_array(self):
        arr = np.array([1.0, 2.0, 3.0])
        result = _to_array(arr)
        np.testing.assert_array_equal(result, arr)
        assert result.dtype == float

    def test_python_list(self):
        result = _to_array([1.0, 2.0, 3.0])
        np.testing.assert_array_equal(result, [1.0, 2.0, 3.0])
        assert result.dtype == float

    def test_nested_list_extra_dim(self):
        """Test that nested list [[1,2,3]] gets flattened to [1,2,3]."""
        result = _to_array([[1.0, 2.0, 3.0]])
        np.testing.assert_array_equal(result, [1.0, 2.0, 3.0])
        assert result.shape == (3,)

    def test_json_string(self):
        """Test JSON string input (common from MCP protocol)."""
        result = _to_array('[1.0, 2.0, 3.0]')
        np.testing.assert_array_equal(result, [1.0, 2.0, 3.0])
        assert result.dtype == float

    def test_json_string_single_quotes(self):
        """Test JSON string with single quotes."""
        result = _to_array("['1.0', '2.0', '3.0']")
        np.testing.assert_array_equal(result, [1.0, 2.0, 3.0])

    def test_none_returns_none(self):
        result = _to_array(None)
        assert result is None

    def test_2d_array_flattened(self):
        """Test that 2D arrays get flattened to 1D."""
        arr_2d = np.array([[1.0, 2.0, 3.0]])
        result = _to_array(arr_2d)
        assert result.shape == (3,)
        np.testing.assert_array_equal(result, [1.0, 2.0, 3.0])

    def test_logspace_array(self):
        """Test with realistic k-grid values."""
        k = np.logspace(-4, 1, 300)
        result = _to_array(k)
        assert result.shape == (300,)
        np.testing.assert_array_almost_equal(result, k)

    def test_logspace_as_list(self):
        """Test k-grid passed as Python list (from JSON)."""
        k = np.logspace(-4, 1, 300)
        result = _to_array(k.tolist())
        assert result.shape == (300,)
        np.testing.assert_array_almost_equal(result, k)

    def test_logspace_as_json_string(self):
        """Test k-grid passed as JSON string."""
        k = np.logspace(-4, 1, 19)
        json_str = json.dumps(k.tolist())
        result = _to_array(json_str)
        assert result.shape == (19,)
        np.testing.assert_array_almost_equal(result, k)


class TestParseModelResults:
    """Test _parse_model_results helper."""

    def test_dict_with_numpy_arrays(self):
        model_results = {
            'ΛCDM': np.array([100.0, 200.0, 300.0]),
            'wCDM (w0=-0.9)': np.array([95.0, 195.0, 290.0]),
        }
        result = _parse_model_results(model_results)
        assert len(result) == 2
        np.testing.assert_array_equal(result['ΛCDM'], [100.0, 200.0, 300.0])
        np.testing.assert_array_equal(result['wCDM (w0=-0.9)'], [95.0, 195.0, 290.0])

    def test_dict_with_lists(self):
        """Test dict with Python list values (from MCP JSON)."""
        model_results = {
            'ΛCDM': [100.0, 200.0, 300.0],
            'wCDM (w0=-0.9)': [95.0, 195.0, 290.0],
        }
        result = _parse_model_results(model_results)
        assert isinstance(result['ΛCDM'], np.ndarray)
        assert result['ΛCDM'].dtype == float

    def test_dict_with_nested_lists(self):
        """Test dict with nested list values (extra dimension wrapping)."""
        model_results = {
            'ΛCDM': [[100.0, 200.0, 300.0]],
        }
        result = _parse_model_results(model_results)
        assert result['ΛCDM'].shape == (3,)

    def test_json_string_input(self):
        """Test JSON string input."""
        model_results = '{"LCDM": [100.0, 200.0, 300.0]}'
        result = _parse_model_results(model_results)
        assert 'LCDM' in result
        np.testing.assert_array_equal(result['LCDM'], [100.0, 200.0, 300.0])


class TestPlotPowerSpectra:
    """Test plot_power_spectra tool with various input formats."""

    def test_with_numpy_arrays(self):
        """Test with proper numpy array inputs."""
        os.environ['MCP_OUTPUT_DIR'] = tempfile.mkdtemp()

        from tools.visualization_tools import plot_power_spectra

        k = np.logspace(-4, 1, 50)
        pk_lcdm = 1e4 * (k / 0.01) ** (-2.5)
        pk_wcdm = 0.95 * pk_lcdm

        model_results = {
            'ΛCDM': pk_lcdm,
            'wCDM (w0=-0.9)': pk_wcdm,
        }
        k_obs = np.logspace(-0.5, 0.5, 10)
        Pk_obs = 1e4 * (k_obs / 0.01) ** (-2.5) * (1 + 0.1 * np.random.randn(10))
        Pk_obs_err = 0.1 * Pk_obs

        result = plot_power_spectra(k, model_results, k_obs, Pk_obs, Pk_obs_err)
        assert isinstance(result, str)
        assert 'Plot saved to:' in result
        save_path = result.replace('Plot saved to: ', '')
        assert os.path.exists(save_path)
        os.unlink(save_path)

    def test_with_list_inputs(self):
        """Test with Python list inputs (simulating MCP JSON deserialization)."""
        os.environ['MCP_OUTPUT_DIR'] = tempfile.mkdtemp()

        from tools.visualization_tools import plot_power_spectra

        k = np.logspace(-4, 1, 50)
        pk_lcdm = 1e4 * (k / 0.01) ** (-2.5)
        pk_wcdm = 0.95 * pk_lcdm

        # Pass as lists (MCP JSON format)
        model_results = {
            'ΛCDM': pk_lcdm.tolist(),
            'wCDM (w0=-0.9)': pk_wcdm.tolist(),
        }
        k_obs = np.logspace(-0.5, 0.5, 10)
        Pk_obs = 1e4 * (k_obs / 0.01) ** (-2.5)
        Pk_obs_err = 0.1 * Pk_obs

        result = plot_power_spectra(
            k.tolist(), model_results, k_obs.tolist(),
            Pk_obs.tolist(), Pk_obs_err.tolist()
        )
        assert isinstance(result, str)
        assert 'Plot saved to:' in result
        save_path = result.replace('Plot saved to: ', '')
        assert os.path.exists(save_path)
        os.unlink(save_path)

    def test_with_json_string_arrays(self):
        """Test with JSON string arrays (critical MCP failure case)."""
        os.environ['MCP_OUTPUT_DIR'] = tempfile.mkdtemp()

        from tools.visualization_tools import plot_power_spectra

        k = np.logspace(-4, 1, 19)
        pk_lcdm = 1e4 * (k / 0.01) ** (-2.5)

        # Pass k_theory as JSON string (what the LLM sends)
        k_json = json.dumps(k.tolist())
        model_results = {'ΛCDM': pk_lcdm.tolist()}
        k_obs_json = json.dumps(k.tolist())
        Pk_obs = pk_lcdm * 1.05
        Pk_obs_err = 0.1 * Pk_obs

        result = plot_power_spectra(
            k_json, model_results, k_obs_json,
            Pk_obs.tolist(), Pk_obs_err.tolist()
        )
        assert isinstance(result, str)
        assert 'Plot saved to:' in result
        save_path = result.replace('Plot saved to: ', '')
        assert os.path.exists(save_path)
        os.unlink(save_path)

    def test_with_nested_list_arrays(self):
        """Test with nested list arrays (extra dimension wrapping)."""
        os.environ['MCP_OUTPUT_DIR'] = tempfile.mkdtemp()

        from tools.visualization_tools import plot_power_spectra

        k = np.logspace(-4, 1, 19)
        pk_lcdm = 1e4 * (k / 0.01) ** (-2.5)

        # Wrap in extra list dimension
        result = plot_power_spectra(
            [k.tolist()],  # nested
            {'ΛCDM': [pk_lcdm.tolist()]},  # nested
            [k.tolist()],
            [pk_lcdm.tolist()],
            [(0.1 * pk_lcdm).tolist()]
        )
        assert isinstance(result, str)
        assert 'Plot saved to:' in result
        save_path = result.replace('Plot saved to: ', '')
        assert os.path.exists(save_path)
        os.unlink(save_path)


class TestPlotSuppressionRatios:
    """Test plot_suppression_ratios tool."""

    def test_basic_call(self):
        os.environ['MCP_OUTPUT_DIR'] = tempfile.mkdtemp()

        from tools.visualization_tools import plot_suppression_ratios

        k = np.logspace(-3, 1, 100)
        ratios = {
            'wCDM (w0=-0.9)': (0.95 * np.ones_like(k)).tolist(),
        }

        result = plot_suppression_ratios(k.tolist(), ratios)
        assert isinstance(result, str)
        assert 'Plot saved to:' in result
        save_path = result.replace('Plot saved to: ', '')
        assert os.path.exists(save_path)
        os.unlink(save_path)


class TestMCMCArrayNormalization:
    """Test MCMC tools handle various array input formats."""

    def test_run_mcmc_json_string_arrays(self):
        """Test run_mcmc_cosmology parses JSON string arrays."""
        from tools.mcmc_tools import run_mcmc_cosmology
        import numpy as np

        k_obs = np.logspace(-0.5, 0.5, 5)
        Pk_obs = 1e3 * np.ones(5)
        Pk_obs_err = 1e2 * np.ones(5)

        # Pass as JSON strings
        result = run_mcmc_cosmology(
            param_bounds=[{'name': 'h', 'min': 0.6, 'max': 0.8}],
            k_obs=json.dumps(k_obs.tolist()),
            Pk_obs=json.dumps(Pk_obs.tolist()),
            Pk_obs_err=json.dumps(Pk_obs_err.tolist()),
            nwalkers=4,
            nburn=2,
            nrun=3,
            save_samples=False,
        )
        assert isinstance(result, str)
        # Should not start with "Error" (it might still have CLASS issues)
        # Just check that array parsing didn't fail
        assert 'unhashable' not in result.lower()
        assert 'dimension' not in result.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
