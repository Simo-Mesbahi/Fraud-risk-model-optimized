"""Typed source-claim contract. Derived ratios are rebuilt at the boundary."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from health_fraud.config import MAX_STRING_LENGTH, MAX_UPLOAD_COLUMNS

Name = Annotated[str, Field(min_length=1, max_length=MAX_STRING_LENGTH)]
Count = Annotated[int, Field(ge=0, le=10_000_000)]
Amount = Annotated[float, Field(ge=0, le=1_000_000_000)]


class SourceClaim(BaseModel):
    """Version 1.1 enriched source record, compatible with the frozen model.

    Extra synthetic labels/analysis metadata are deliberately discarded. They
    cannot become features. Unknown categorical strings remain supported by the
    frozen encoder; unknown feature names cannot alter the feature contract.
    """

    model_config = ConfigDict(
        extra="ignore", allow_inf_nan=False, str_strip_whitespace=True
    )
    claim_id: Name | None = None
    customer_id: Name | None = None
    policy_id: Name | None = None
    provider_id: Name | None = None
    service_category: Name
    service_code: Name
    service_units: Annotated[int, Field(gt=0, le=10000)]
    service_date: datetime
    claim_submission_timestamp: datetime
    claim_amount: Annotated[float, Field(gt=0, le=1_000_000_000)]
    requested_reimbursement: Amount
    coverage_limit: Annotated[float, Field(gt=0, le=1_000_000_000)]
    submission_channel: Name
    document_count: Count | None
    has_invoice: bool
    has_prescription: bool | None
    customer_age: Annotated[int, Field(ge=0, le=125)] | None
    customer_tenure_months: Count | None
    coverage_level: Name
    policy_tenure_months: Count | None
    recent_policy_change: bool | None
    days_since_policy_change: Amount | None
    provider_type: Name | None
    provider_region: Name | None
    provider_tenure_months: Count | None
    customer_claims_7d: Count
    customer_claims_30d: Count
    customer_claims_90d: Count
    customer_claims_365d: Count
    customer_amount_30d: Amount
    customer_amount_365d: Amount
    customer_avg_claim_amount_365d: Amount | None
    days_since_customer_previous_claim: Amount | None
    days_since_same_provider_claim: Amount | None
    customer_provider_claims_30d: Count
    same_service_claims_30d: Count
    provider_claims_30d: Count
    provider_claims_90d: Count
    provider_avg_claim_amount_90d: Amount | None
    service_typical_amount: Amount | None

    @model_validator(mode="after")
    def business_rules(self) -> SourceClaim:
        for field in ("service_date", "claim_submission_timestamp"):
            value = getattr(self, field)
            if value.tzinfo is not None:
                setattr(
                    self, field, value.astimezone(timezone.utc).replace(tzinfo=None)
                )
        if self.service_date.date() > self.claim_submission_timestamp.date():
            raise ValueError("Service date cannot be after submission.")
        if (
            self.requested_reimbursement
            > min(self.claim_amount, self.coverage_limit) + 0.01
        ):
            raise ValueError("Reimbursement exceeds claim amount or coverage limit.")
        if not (
            self.customer_claims_7d
            <= self.customer_claims_30d
            <= self.customer_claims_90d
            <= self.customer_claims_365d
        ):
            raise ValueError(
                "Customer historical counts must be monotonic across windows."
            )
        if self.provider_claims_30d > self.provider_claims_90d:
            raise ValueError("Provider 30-day count exceeds the 90-day count.")
        if (
            max(self.same_service_claims_30d, self.customer_provider_claims_30d)
            > self.customer_claims_30d
        ):
            raise ValueError("Relationship counts exceed the customer 30-day count.")
        return self

    def inference_record(self) -> dict[str, Any]:
        record = self.model_dump(mode="json")
        record["claim_submission_date"] = (
            self.claim_submission_timestamp.date().isoformat()
        )
        record["days_service_to_submission"] = (
            self.claim_submission_timestamp.date() - self.service_date.date()
        ).days
        record["reimbursement_ratio"] = min(
            1.0, self.requested_reimbursement / self.claim_amount
        )
        for reference, ratio in (
            (self.service_typical_amount, "claim_to_service_median_ratio"),
            (self.customer_avg_claim_amount_365d, "claim_to_customer_avg_ratio"),
            (self.provider_avg_claim_amount_90d, "claim_to_provider_avg_ratio"),
        ):
            record[ratio] = (
                self.claim_amount / reference
                if reference is not None and reference > 0
                else None
            )
        return record


def validate_claim_record(record: dict[str, Any]) -> dict[str, Any]:
    if len(record) > MAX_UPLOAD_COLUMNS:
        raise ValueError(f"A claim cannot exceed {MAX_UPLOAD_COLUMNS} fields.")
    for key, value in record.items():
        if not isinstance(key, str) or len(key) > MAX_STRING_LENGTH:
            raise ValueError("Invalid claim field name.")
        if isinstance(value, (dict, list, tuple, set)):
            raise ValueError("Claim fields must be scalar values.")
        if isinstance(value, str) and len(value) > MAX_STRING_LENGTH:
            raise ValueError(
                f"Field {key} exceeds the {MAX_STRING_LENGTH}-character limit."
            )
    try:
        return SourceClaim.model_validate(record).inference_record()
    except ValidationError as exc:
        details = "; ".join(
            ".".join(map(str, e["loc"])) + ": " + e["msg"] for e in exc.errors()
        )
        raise ValueError(details) from exc


def validate_claim_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    identifiers: set[str] = set()
    for index, record in enumerate(records):
        try:
            claim = validate_claim_record(record)
        except ValueError as exc:
            raise ValueError(f"Claim {index + 1}: {exc}") from exc
        claim_id = claim.get("claim_id")
        if claim_id is not None:
            if claim_id in identifiers:
                raise ValueError(f"Duplicate claim identifier at row {index + 1}.")
            identifiers.add(claim_id)
        normalized.append(claim)
    return normalized
