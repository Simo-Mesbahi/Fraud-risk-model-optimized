def test_openapi_documents_the_validated_business_record(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schemas = response.json()["components"]["schemas"]
    record = schemas["SingleClaimRequest"]["properties"]["claim"]
    assert "service_category" in record["required"]
    assert record["properties"]["service_units"]["exclusiveMinimum"] == 0
    assert record["properties"]["customer_claims_30d"]["minimum"] == 0
    batch = schemas["BatchClaimsRequest"]["properties"]["claims"]
    assert batch["maxItems"] == 10000
    assert "claim_amount" in batch["items"]["required"]
