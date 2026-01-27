"""Test domain tools for basic functionality."""

import pytest
import sys
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools import (
    get_lcdm_params,
    create_theory_k_grid,
    compute_power_spectrum,
    load_observational_data
)


def test_lcdm_model():
    """Test get_lcdm_params returns expected parameter structure."""
    params = get_lcdm_params()

    # Check it's a dictionary
    assert isinstance(params, dict), "get_lcdm_params should return a dictionary"

    # Check for required cosmological parameters
    required_keys = ['output', 'h', 'Omega_b', 'Omega_cdm', 'A_s', 'n_s']
    for key in required_keys:
        assert key in params, f"get_lcdm_params missing required parameter '{key}'"


def test_create_theory_k_grid():
    """Test theory k-grid creation."""
    k_values = create_theory_k_grid()

    # Check it's a numpy array
    assert isinstance(k_values, np.ndarray), "Should return numpy array"

    # Check it has reasonable values
    assert len(k_values) > 0, "k-grid should not be empty"
    assert k_values.min() > 0, "k-values should be positive"
    assert k_values.max() > k_values.min(), "k-values should span a range"


def test_compute_power_spectrum():
    """Test power spectrum computation with LCDM model."""
    # Get LCDM parameters
    params = get_lcdm_params()

    # Create k-grid
    k_values = create_theory_k_grid()

    # Compute power spectrum
    try:
        pk_values = compute_power_spectrum(params, k_values)

        # Basic checks
        if pk_values is not None:
            assert isinstance(pk_values, np.ndarray), "Should return numpy array"
            assert len(pk_values) == len(k_values), "P(k) should match k-grid length"
            assert np.all(pk_values > 0), "P(k) values should be positive"
    except Exception as e:
        # If CLASS not installed, skip this test
        if "classy" in str(e).lower() or "class" in str(e).lower():
            pytest.skip("CLASS not installed")
        else:
            raise


def test_load_observational_data():
    """Test observational data loading."""
    # Test with a dummy filepath - should handle gracefully
    result = load_observational_data(filepath="nonexistent_file.txt")

    # Function returns a tuple (k, Pk, errors) or (None, None, None) on error
    assert isinstance(result, tuple)
    assert len(result) == 3

    # On error, should return (None, None, None)
    if result == (None, None, None):
        # This is expected when file doesn't exist
        pass
    else:
        # If data loaded, check it's valid
        k, pk, errors = result
        assert k is not None
        assert pk is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
