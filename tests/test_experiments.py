def test_create_experiment_validation(client, admin_headers):
    response = client.post("/api/experiments", json={}, headers=admin_headers)
    assert response.status_code == 422


def test_create_experiment_success(client, admin_headers):
    payload = {
        "experiment_name": "prompt_test",
        "model_version": "gpt-4",
        "prompt_template": "Explain {topic}",
    }

    response = client.post("/api/experiments", json=payload, headers=admin_headers)
    assert response.status_code == 200
