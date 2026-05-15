from app.main import app


def test_search_without_resume(client):

    response = client.post("/search")

    assert response.status_code == 200
    assert "general job matches" in response.text

def test_use_saved_resume(client):

    response = client.post(
        "/search",
        data={"use_saved": "true"}
    )

    assert response.status_code == 200
    assert "resume-based ranking" in response.text

def test_upload_resume(client):

    with open("sample_resume.txt", "rb") as f:

        response = client.post(
            "/search",
            files={"file": ("resume.txt", f, "text/plain")}
        )

    assert response.status_code == 200