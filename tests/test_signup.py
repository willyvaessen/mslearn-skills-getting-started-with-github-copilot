"""Tests for POST /activities/{activity_name}/signup endpoint using AAA pattern."""

import pytest


class TestSignupHappyPath:
    """Test suite for successful signup scenarios."""

    def test_signup_returns_200_status_code(self, client, test_activity_name, sample_email):
        """
        Arrange: Prepare email that's not yet registered for activity
        Act: POST /activities/{activity_name}/signup
        Assert: Response status is 200 OK
        """
        # Arrange
        new_email = "unique.signup@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{test_activity_name}/signup",
            params={"email": new_email}
        )

        # Assert
        assert response.status_code == 200

    def test_signup_returns_success_message(self, client, test_activity_name):
        """
        Arrange: Prepare new email for signup
        Act: POST /activities/{activity_name}/signup
        Assert: Response contains success message
        """
        # Arrange
        new_email = "new.member@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{test_activity_name}/signup",
            params={"email": new_email}
        )
        data = response.json()

        # Assert
        assert "message" in data
        assert new_email in data["message"]
        assert test_activity_name in data["message"]

    def test_signup_adds_participant_to_activity(self, client, test_activity_name):
        """
        Arrange: Get current participants, prepare new email
        Act: POST signup, then GET activities
        Assert: New email appears in participants list
        """
        # Arrange
        new_email = "added.participant@mergington.edu"
        response_before = client.get("/activities")
        participants_before = response_before.json()[test_activity_name]["participants"]
        initial_count = len(participants_before)

        # Act
        client.post(
            f"/activities/{test_activity_name}/signup",
            params={"email": new_email}
        )
        response_after = client.get("/activities")
        participants_after = response_after.json()[test_activity_name]["participants"]

        # Assert
        assert new_email in participants_after
        assert len(participants_after) == initial_count + 1


class TestSignupErrorCases:
    """Test suite for signup error scenarios."""

    def test_signup_to_nonexistent_activity_returns_404(self, client, sample_email, nonexistent_activity):
        """
        Arrange: Use activity that doesn't exist
        Act: POST /activities/{nonexistent}/signup
        Assert: Response status is 404 Not Found
        """
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 404

    def test_signup_to_nonexistent_activity_returns_detail(self, client, sample_email, nonexistent_activity):
        """
        Arrange: Use activity that doesn't exist
        Act: POST /activities/{nonexistent}/signup
        Assert: Response contains error detail message
        """
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": sample_email}
        )
        data = response.json()

        # Assert
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_duplicate_signup_returns_400(self, client, test_activity_name):
        """
        Arrange: Get existing participant email from activity
        Act: POST signup with existing participant email
        Assert: Response status is 400 Bad Request
        """
        # Arrange
        response = client.get("/activities")
        existing_participant = response.json()[test_activity_name]["participants"][0]

        # Act
        response = client.post(
            f"/activities/{test_activity_name}/signup",
            params={"email": existing_participant}
        )

        # Assert
        assert response.status_code == 400

    def test_duplicate_signup_returns_error_message(self, client, test_activity_name):
        """
        Arrange: Get existing participant
        Act: POST signup with existing participant
        Assert: Response explains participant already signed up
        """
        # Arrange
        response = client.get("/activities")
        existing_participant = response.json()[test_activity_name]["participants"][0]

        # Act
        response = client.post(
            f"/activities/{test_activity_name}/signup",
            params={"email": existing_participant}
        )
        data = response.json()

        # Assert
        assert "detail" in data
        assert "already" in data["detail"].lower() or "signed up" in data["detail"].lower()


class TestSignupCapacityLimits:
    """Test suite for signup capacity validation."""

    def test_signup_to_full_activity_returns_400(self, client):
        """
        Arrange: Find or create full activity, prepare new email
        Act: POST signup to full activity
        Assert: Response status is 400
        """
        # Arrange - find activities with available capacity first
        response = client.get("/activities")
        activities = response.json()

        # Find or create a small capacity activity to fill
        # Using a fixture approach - we'll find Chess Club with max_participants: 12
        small_activity = "Chess Club"
        if small_activity in activities:
            activity_data = activities[small_activity]
            max_participants = activity_data["max_participants"]
            current_participants = len(activity_data["participants"])

            # Only test if we can actually fill it
            if current_participants < max_participants:
                # Fill remaining spots
                for i in range(current_participants, max_participants):
                    client.post(
                        f"/activities/{small_activity}/signup",
                        params={"email": f"filler.{i}@mergington.edu"}
                    )

                # Act - Try to signup to full activity
                response = client.post(
                    f"/activities/{small_activity}/signup",
                    params={"email": "overflow@mergington.edu"}
                )

                # Assert
                assert response.status_code == 400
