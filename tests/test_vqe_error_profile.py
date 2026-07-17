"""Tests for src/vqe_error_profile.py."""
import numpy as np
import pytest

from src.loader import load_ising
from src.vqe_error_profile import gradient_variance_vs_field, hea_error_sweep


@pytest.fixture(scope="module")
def data_1x4():
    return load_ising("1x4")


def test_hea_error_sweep_shape(data_1x4):
    indices = list(range(0, 100, 20))
    fields, errors = hea_error_sweep(data_1x4, indices=indices, n_layers=2, steps=50)
    assert fields.shape == errors.shape == (len(indices),)
    assert np.all(errors >= 0)


def test_hea_errors_finite(data_1x4):
    fields, errors = hea_error_sweep(data_1x4, indices=[10, 50, 90], n_layers=2, steps=50)
    assert np.all(np.isfinite(errors))


def test_gradient_variance_vs_field_shape(data_1x4):
    var_idx = [10, 50, 90]
    f_hea, v_hea = gradient_variance_vs_field(
        "hea", data_1x4, field_indices=var_idx, n_layers=2, n_samples=10
    )
    f_hva, v_hva = gradient_variance_vs_field(
        "hva", data_1x4, field_indices=var_idx, n_layers=2, n_samples=10
    )
    assert f_hea.shape == v_hea.shape == (3,)
    assert f_hva.shape == v_hva.shape == (3,)
    assert np.all(v_hea >= 0)
    assert np.all(v_hva >= 0)
