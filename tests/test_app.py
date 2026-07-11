from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
INITIAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def restore_activities():
    """Reset the in-memory activity state before each test."""
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_activity_list():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()
    assert response.json()[expected_activity]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert new_email in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_deletes_participant():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 200
    assert participant_email not in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Removed {participant_email} from {activity_name}"


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "missing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_activity_not_found_returns_404_for_signup_and_delete():
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    delete_response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert signup_response.status_code == 404
    assert signup_response.json()["detail"] == "Activity not found"
    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == "Activity not found"
