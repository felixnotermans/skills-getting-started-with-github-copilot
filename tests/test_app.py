from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_successfully_adds_student():
    email = "test-signup@mergington.edu"

    response = client.post(f"/activities/Chess Club/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]

    cleanup_response = client.delete(f"/activities/Chess Club/signup?email={email}")
    assert cleanup_response.status_code == 200


def test_signup_duplicate_student_returns_400():
    response = client.post(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_unknown_activity_returns_404():
    response = client.post(
        "/activities/Unknown Club/signup?email=test@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_requires_email_query_param():
    response = client.post("/activities/Chess Club/signup")

    assert response.status_code == 422


def test_unregister_successfully_removes_student():
    email = "test-unregister@mergington.edu"

    signup_response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert signup_response.status_code == 200

    unregister_response = client.delete(f"/activities/Chess Club/signup?email={email}")

    assert unregister_response.status_code == 200
    assert unregister_response.json()["message"] == (
        f"Unregistered {email} from Chess Club"
    )
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_unknown_activity_returns_404():
    response = client.delete(
        "/activities/Unknown Club/signup?email=test@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_student_not_signed_up_returns_404():
    response = client.delete(
        "/activities/Chess Club/signup?email=not-signed-up@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up"


def test_unregister_requires_email_query_param():
    response = client.delete("/activities/Chess Club/signup")

    assert response.status_code == 422
