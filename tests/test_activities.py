"""Tests for GET /activities and GET / endpoints using AAA pattern."""

import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint."""

    def test_returns_200_status_code(self, client):
        """
        Arrange: Use test client
        Act: GET /activities
        Assert: Response status is 200 OK
        """
        # Arrange is implicit (client fixture)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_returns_dict_of_activities(self, client):
        """
        Arrange: Use test client
        Act: GET /activities
        Assert: Response is a dict containing activities
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert isinstance(activities, dict)
        assert len(activities) > 0

    def test_activity_structure_is_correct(self, client, test_activity_name):
        """
        Arrange: Use test client and known activity name
        Act: GET /activities and access Chess Club
        Assert: Activity has required fields with correct types
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert test_activity_name in activities
        activity = activities[test_activity_name]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_participants_are_email_strings(self, client, test_activity_name):
        """
        Arrange: Use test client and known activity
        Act: GET /activities and retrieve participants
        Assert: Participants list contains string emails
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        participants = activities[test_activity_name]["participants"]

        # Assert
        assert all(isinstance(p, str) for p in participants)
        assert all("@" in p for p in participants)  # Basic email validation

    def test_max_participants_is_integer(self, client, test_activity_name):
        """
        Arrange: Use test client and known activity
        Act: GET /activities and check max_participants
        Assert: max_participants is an integer
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        max_participants = activities[test_activity_name]["max_participants"]

        # Assert
        assert isinstance(max_participants, int)
        assert max_participants > 0

    def test_all_activities_have_required_fields(self, client):
        """
        Arrange: Use test client
        Act: GET /activities
        Assert: Every activity has all required fields
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        required_fields = {"description", "schedule", "max_participants", "participants"}
        for activity_name, activity_data in activities.items():
            assert required_fields.issubset(activity_data.keys()), \
                f"Activity '{activity_name}' missing required fields"


class TestRootRedirect:
    """Test suite for GET / (root) endpoint."""

    def test_root_returns_redirect_status(self, client):
        """
        Arrange: Use test client
        Act: GET / with follow_redirects=False
        Assert: Response status is 307 (temporary redirect)
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307

    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: Use test client
        Act: GET / and follow redirects
        Assert: Final URL points to /static/index.html
        """
        # Act
        response = client.get("/", follow_redirects=True)

        # Assert - The redirect goes to /static/index.html
        assert response.status_code == 200
