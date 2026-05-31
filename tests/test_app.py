from fastapi.testclient import TestClient

from src import app as app_module


def test_root_redirects_to_index_html(client: TestClient):
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client: TestClient):
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"

    activities = response.json()
    assert "Chess Club" in activities
    assert "Yoga Club" in activities


def test_signup_for_activity_adds_participant(client: TestClient):
    # Arrange
    activity_name = "Yoga Club"
    email = "newstudent@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_returns_404_for_missing_activity(client: TestClient):
    # Arrange
    activity_name = "Cooking Club"
    email = "student@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_activity_returns_400_for_duplicate_registration(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_from_activity(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}

    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_returns_404_when_participant_not_found(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    email = "missingstudent@mergington.edu"
    url = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"
