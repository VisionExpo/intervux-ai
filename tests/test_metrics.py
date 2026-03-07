def test_metrics_endpoint(client, recruiter_headers):
    response = client.get("/api/evaluation-dashboard", headers=recruiter_headers)
    assert response.status_code == 200
