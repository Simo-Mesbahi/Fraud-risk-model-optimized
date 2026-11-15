"""Platt calibration on a separate chronological calibration period."""

import numpy as np
from sklearn.linear_model import LogisticRegression


def _logits(probabilities):
    values = np.asarray(probabilities, dtype=float)
    if (
        values.ndim != 1
        or not np.isfinite(values).all()
        or ((values < 0) | (values > 1)).any()
    ):
        raise ValueError("Calibration expects finite probabilities in [0,1].")
    values = np.clip(values, 1e-7, 1 - 1e-7)
    return np.log(values / (1 - values)).reshape(-1, 1)


def fit_platt(probabilities, labels):
    if len(np.unique(labels)) != 2:
        raise ValueError("Calibration requires both classes in the calibration period.")
    return LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000).fit(
        _logits(probabilities), labels
    )


def apply_platt(calibrator, probabilities):
    return calibrator.predict_proba(_logits(probabilities))[:, 1]
