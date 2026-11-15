"""Reusable, training-only preprocessing for research and reproducible refits."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

CATEGORICAL_COLUMNS = {
    "service_category",
    "service_code",
    "submission_channel",
    "coverage_level",
    "provider_type",
    "provider_region",
}
BOOLEAN_COLUMNS = {"has_invoice", "has_prescription", "recent_policy_change"}


def normalize_model_frame(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    for column in result:
        if column in CATEGORICAL_COLUMNS:
            result[column] = (
                result[column].astype(object).where(result[column].notna(), np.nan)
            )
        else:
            result[column] = pd.to_numeric(result[column], errors="raise").astype(float)
    return result


def make_preprocessor(
    features: list[str], *, imputation="median", scale=True
) -> Pipeline:
    categories = [f for f in features if f in CATEGORICAL_COLUMNS]
    boolean = [
        f
        for f in features
        if f in BOOLEAN_COLUMNS or f.endswith("_missing") or f.endswith("_is_weekend")
    ]
    numeric = [f for f in features if f not in categories and f not in boolean]
    number_steps = [
        ("impute", SimpleImputer(strategy=imputation, keep_empty_features=True))
    ]
    if scale:
        number_steps.append(("scale", StandardScaler()))
    transform = ColumnTransformer(
        [
            ("numeric", Pipeline(number_steps), numeric),
            (
                "boolean",
                SimpleImputer(strategy="most_frequent", keep_empty_features=True),
                boolean,
            ),
            (
                "categorical",
                Pipeline(
                    [
                        (
                            "impute",
                            SimpleImputer(
                                strategy="constant", fill_value="__MISSING__"
                            ),
                        ),
                        (
                            "encode",
                            OneHotEncoder(
                                handle_unknown="ignore",
                                min_frequency=10,
                                sparse_output=True,
                            ),
                        ),
                    ]
                ),
                categories,
            ),
        ],
        remainder="drop",
        verbose_feature_names_out=True,
    )
    return Pipeline(
        [
            (
                "normalize",
                FunctionTransformer(
                    normalize_model_frame, feature_names_out="one-to-one"
                ),
            ),
            ("columns", transform),
        ]
    )
