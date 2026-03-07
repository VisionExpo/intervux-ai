def test_decision_endpoint(client, recruiter_headers, sample_interview_id):
    response = client.post(
        f"/api/interview/{sample_interview_id}/decision",
        headers=recruiter_headers,
    )

    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert "candidate_summary" in data
        assert "recommendation" in data
