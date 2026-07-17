"""Tests for src/finite_size_scaling.py."""
import numpy as np
import pytest

from src.physics.finite_size_scaling import (
    collect_central_charges,
    collect_hc_estimates,
    fit_hc_power_law,
)


def test_collect_hc_estimates_shape():
    ns, hc_infl, hc_bind = collect_hc_estimates(("1x4", "1x8", "1x16"))
    assert ns.shape == (3,)
    assert hc_infl.shape == (3,)
    assert hc_bind.shape == (3,)


def test_hc_estimates_monotone():
    """h_c(N) should increase toward 1 as N grows (finite-size correction shrinks)."""
    ns, hc_infl, _ = collect_hc_estimates(("1x4", "1x8", "1x16"))
    assert hc_infl[0] < hc_infl[1] < hc_infl[2]
    assert all(hc_infl < 1.05)


def test_fit_hc_power_law_exact_nu():
    """With ν fixed to 1 the fit should extrapolate close to h_c=1."""
    ns = np.array([4, 8, 16], dtype=float)
    hcs = 1.0 - 0.5 / ns  # synthetic data with exact ν=1
    result = fit_hc_power_law(ns, hcs, nu_fixed=1.0)
    assert abs(result["h_inf"] - 1.0) < 1e-6
    assert abs(result["a"] - 0.5) < 1e-6
    assert result["nu"] == 1.0


def test_fit_hc_power_law_free():
    """Free fit with 3 points / 3 params is exactly determined — just check sanity.
    The fixed-ν variant is the reliable estimator; this just guards against crashes."""
    ns, hc_infl, _ = collect_hc_estimates(("1x4", "1x8", "1x16"))
    result = fit_hc_power_law(ns, hc_infl)
    assert result["nu"] > 0
    assert 0.5 < result["h_inf"] < 2.0


def test_collect_central_charges():
    ns, cs = collect_central_charges(("1x8", "1x16"))
    assert len(ns) == len(cs) == 2
    # CFT c = 0.5; allow some finite-size overshoot
    assert all(0.3 < c < 1.0 for c in cs)
