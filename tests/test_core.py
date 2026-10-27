"""Tests for riftprospect. Hand-checkable numbers; run with `pytest`."""
import numpy as np
import pandas as pd
import pytest
from affine import Affine

from riftprospect import fertility as fe, geophys as gp, combine as cb, chemmodel as cm, geology as geo
from riftprospect.grid import common_transform, local_mean, analytic_signal


def wide(**kw):
    base = dict(mcr_uid=["a"], Cu_ppm=[100.0], Ni_ppm=[200.0], Pd_ppb=[10.0], Pt_ppb=[5.0], MgO_wt=[10.0], Fe2O3T_wt=[12.0])
    base.update(kw); return pd.DataFrame(base)


def test_cu_pd_units():
    # Cu 100 ppm, Pd 10 ppb = 0.01 ppm -> Cu/Pd = 10,000
    assert fe.indicators(wide()).cu_pd.iloc[0] == pytest.approx(10000)


def test_ni_cu_and_pd_pt():
    r = fe.indicators(wide()).iloc[0]
    assert r.ni_cu == pytest.approx(2.0) and r.pd_pt == pytest.approx(2.0)


def test_mg_number_by_hand():
    # MgO 10 / 40.304 = 0.24811 mol; FeT = 2*12/159.688 = 0.15030; Fe2+ = 0.9*0.15030 = 0.13527
    assert fe.mg_number(10.0, 12.0) == pytest.approx(100 * 0.24811 / (0.24811 + 0.13527), rel=1e-3)


def test_censored_drop_and_half():
    d = wide(Pd_ppb=[-2.0])  # below detection, limit 2 ppb
    assert np.isnan(fe.indicators(d, rule="drop").cu_pd.iloc[0])
    h = fe.indicators(d, rule="half").iloc[0]
    assert h.cu_pd == pytest.approx(100 / 0.001) and bool(h.cu_pd_censored)


def test_cu_pd_classes():
    c = fe.cu_pd_class(pd.Series([1000.0, 7000.0, 50000.0, np.nan]))
    assert list(c) == ["pge_enriched", "mantle_like", "pge_depleted", "undetermined"]


def test_membership_direction():
    assert gp.membership(np.array([95.0]), +1)[0] > 0.8
    assert gp.membership(np.array([95.0]), -1)[0] < 0.2


def test_percentile_rank_keeps_nan():
    r = gp.percentile_rank(np.array([3.0, np.nan, 1.0, 2.0]))
    assert np.isnan(r[1]) and r[2] == 0 and r[0] == 100


def test_score_renormalizes_missing_layer():
    pct = pd.DataFrame({"rtp_asig": [100.0], "rtp_resid": [100.0], "k": [np.nan], "th": [np.nan]})
    s = gp.score(pct)[0]
    assert s == pytest.approx(gp.membership(np.array([100.0]), 1)[0])


def test_common_transform_snaps():
    tr, h, w = common_transform([(10, 10, 390, 190)], 200)
    assert (tr.c, tr.f, h, w) == (0, 200, 1, 2)


def test_local_mean_flat_field():
    f = np.ones((7, 7), "float32"); f[0, 0] = np.nan
    m = local_mean(f, 1)
    assert np.isnan(m[0, 0]) and m[3, 3] == pytest.approx(1)


def test_analytic_signal_constant_is_zero():
    a = analytic_signal(np.full((16, 16), 5.0), 200)
    assert np.nanmax(a) == pytest.approx(0, abs=1e-9)


def test_targets_edge_and_ranking():
    grid = pd.DataFrame({"row": [0, 0, 1, 2], "col": [0, 1, 1, 3], "cell_id": list("abcd"), "x": [0, 1, 1, 3.0], "y": [0, 0, 1, 2.0],
                         "score": [0.9, 0.8, 0.1, 0.95], "score_sd": [0.1] * 4, "edge_dist_m": [5000, 5000, 5000, 100],
                         "evidence": ["g"] * 4, "block": ["A"] * 4})
    t, lab = cb.targets(grid, (3, 4), top_pct=50, min_cells=1)
    assert len(t) == 1 and t.n_cells.iloc[0] == 2   # the edge cell (d) is excluded
    assert lab[2, 3] == 0


def test_training_table_buffer_excluded():
    df = pd.DataFrame({"rock_class": ["igneous_intrusive"] * 3, "altered_likely": [False] * 3,
                       "ni_cu": [1, 1, 1.0], "cu_pd": [1, 1, 1.0], "MgO_wt": [5, 5, 5.0], "mg_number": [50, 50, 50.0],
                       "dep_km": [1.0, 5.0, 20.0]})
    t = cm.training_table(df)
    assert list(t.label) == [1, 0]


def test_geology_multiplier():
    assert list(geo.multiplier(np.array([0, 1, 2, 3, 4], "uint8"))) == pytest.approx([1.0, 0.3, 0.6, 1.0, 1.0])
