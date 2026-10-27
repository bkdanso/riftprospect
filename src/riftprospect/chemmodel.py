"""Part A: chemistry similarity model, trained where deposits and samples coexist (Minnesota).

Plain-language note: this learns how rock chemistry near known Ni-Cu-PGE deposits differs
from rock chemistry far from them, then scores other samples by that similarity. It uses
many resampled copies of the training data (bootstrap) so each score carries a spread.
Choices marked DECISION are listed in docs/DECISIONS.md.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

# DECISION D2: samples within NEAR_KM of a deposit are positives; beyond FAR_KM negatives;
# between is a buffer left out of training (it is neither clearly near nor clearly far).
NEAR_KM, FAR_KM = 3.0, 10.0  # D2 decided by Bezali 2026-10-27: 3 km
# DECISION D9: model features. Cu/Pd is excluded from the main model because Pd was analyzed
# far more often near deposits than away from them, so its presence alone leaks the label.
FEATURES = ["log_ni_cu", "MgO_wt", "mg_number"]
# DECISION D8: rocks used.
ROCK_CLASSES = ["igneous_intrusive"]


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["log_ni_cu"] = np.log10(df["ni_cu"].where(df["ni_cu"] > 0))
    df["log_cu_pd"] = np.log10(df["cu_pd"].where(df["cu_pd"] > 0))
    return df


def nearest_deposit(xy: np.ndarray, dep_xy: np.ndarray, names) -> tuple[np.ndarray, np.ndarray]:
    d = np.hypot(xy[:, :1] - dep_xy[None, :, 0], xy[:, 1:] - dep_xy[None, :, 1])
    return d.min(1) / 1000.0, np.asarray(names)[d.argmin(1)]


def training_table(samples: pd.DataFrame) -> pd.DataFrame:
    """Rows usable for training: chosen rock classes, not altered, all features present, outside buffer."""
    s = add_features(samples)
    s = s[s.rock_class.isin(ROCK_CLASSES) & ~s.altered_likely.fillna(False).astype(bool)]
    s = s.dropna(subset=FEATURES)
    s = s[(s.dep_km <= NEAR_KM) | (s.dep_km > FAR_KM)].copy()
    s["label"] = (s.dep_km <= NEAR_KM).astype(int)
    return s


def spatial_groups(df: pd.DataFrame, block_km: float = 20.0) -> np.ndarray:
    """Group id per row for spatial cross-validation: positives by nearest deposit, negatives by block."""
    blk = (np.floor(df.x / (block_km * 1000)).astype(int).astype(str) + "_" +
           np.floor(df.y / (block_km * 1000)).astype(int).astype(str))
    return np.where(df.label == 1, "dep_" + df.dep_name.astype(str), "blk_" + blk)


def make_model():
    return make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=1000))


def spatial_cv_auc(train: pd.DataFrame, n_folds: int = 5, seed: int = 0) -> dict:
    """Grouped spatial CV: whole deposits and whole 20 km blocks are held out together."""
    from sklearn.model_selection import GroupKFold
    g = spatial_groups(train)
    X, y = train[FEATURES].values, train.label.values
    oof = np.full(len(y), np.nan)
    for tr, te in GroupKFold(n_splits=n_folds).split(X, y, g):
        if len(np.unique(y[tr])) < 2:
            continue
        m = make_model().fit(X[tr], y[tr])
        oof[te] = m.predict_proba(X[te])[:, 1]
    ok = ~np.isnan(oof)
    return {"auc": float(roc_auc_score(y[ok], oof[ok])), "n": int(ok.sum()),
            "n_pos": int(y[ok].sum()), "n_groups": int(len(np.unique(g)))}


def leave_one_deposit_out(train: pd.DataFrame) -> pd.DataFrame:
    """Hold out each deposit's positives plus negatives; report the held-out positives' median rank."""
    out = []
    neg = train[train.label == 0]
    for dep in sorted(train.loc[train.label == 1, "dep_name"].unique()):
        te_pos = train[(train.label == 1) & (train.dep_name == dep)]
        tr = train.drop(te_pos.index)
        m = make_model().fit(tr[FEATURES].values, tr.label.values)
        p_pos = m.predict_proba(te_pos[FEATURES].values)[:, 1]
        p_neg = m.predict_proba(neg[FEATURES].values)[:, 1]  # in-sample for negatives: optimistic
        pct = [(p_neg < p).mean() * 100 for p in p_pos]
        out.append({"deposit": dep, "n_heldout": len(te_pos), "median_pct_vs_neg": float(np.median(pct))})
    return pd.DataFrame(out)


def bootstrap_predict(train: pd.DataFrame, apply: pd.DataFrame, n_boot: int = 200, seed: int = 0):
    """Mean and standard deviation of predicted similarity across bootstrap refits."""
    rng = np.random.default_rng(seed)
    X, y = train[FEATURES].values, train.label.values
    Xa = apply[FEATURES].values
    preds = np.empty((n_boot, len(Xa)))
    coefs = []
    for b in range(n_boot):
        i = rng.integers(0, len(y), len(y))
        while len(np.unique(y[i])) < 2:
            i = rng.integers(0, len(y), len(y))
        m = make_model().fit(X[i], y[i])
        preds[b] = m.predict_proba(Xa)[:, 1]
        coefs.append(m[-1].coef_[0])
    return preds.mean(0), preds.std(0), np.array(coefs)
