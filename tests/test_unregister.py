"""Tests for POST /activities/{activity_name}/unregister endpoint using AAA pattern."""

import pytest


class TestUnregisterHappyPath:
    """Test suite for successful unregister scenarios."""

    def test_unregister_returns_200_status_code(self, client, test_activity_name):
        """
        Arrange: Add a participant, get their email
        Act: POST /activities/{activity_name}/unregister
        Assert: Response status is 200 OK
        """
        # Arrange
        new_email = "temp.participant@mergington.edu"
        client.post(f"/activities/{test_activity_name}/signup", params={"email": new_email})

        # Act
        response = client.post(
            f"/activities/{test_activity_name}/unregister",
            params={"email": new_email}
        )

        # Assert
        assert response.status_code == 200

    def test_unregister_returns_success_message(self, client, test_activity_name):
        """
        Arrange: Add a participant
        Act: POST unregister
        Assert: Response contains success message
        """
        # Arrange
        new_email = "to.remove@mergington.edu"
        client.post(f"/activities/{test_activity_name}/signup", params={"email": new_email})

        # Act
        response = client.post(
            f"/activities/{test_activity_name}/unregister",
            params={"email": new_email}
        )
        data = response.json()

        # Assert
        assert "message" in data
        assert new_email in data["message"]
        assert test_activity_name in data["message"]

    def test_unregister_removes_participant_from_activity(self, client, test_activity_name):
        """
        Arrange: Add participant, get initial count
        Act: Unregister participant, get activities
        Assert: Participant count decreased by 1 and email not in list
        """
        # Arrange
        new_email = "participant.to.remove@mergington.edu"
        client.post(f"/activities/{test_activity_name}/signup", params={"email": new_email})
        
        response_before = client.get("/activities")
        count_before = len(response_before.json()[test_activity_name]["participants"])

        # Act
        client.post(
            f"/activities/{test_activity_name}/unregister",
            params={"email": new_email}
        )
        response_after = client.get("/activities")
        participants_after = response_after.json()[test_activity_name]["participants"]
        count_after = len(participants_after)

        # Assert
        assert new_email not in participants_after
        assert count_after == count_before - 1

    def test_can_resignup_after_unregister(self, client, test_activity_name):
        """
        Arrange: Add participant, then unregister
        Act: Signup again with same email
        Assert: Signup succeeds and participant is in list again
        """
        # Arrange
        test_email = "signup.again@mergington.edu"
        client.post(f"/activities/{test_activity_name}/signup", params={"email": test_email})
        client.post(f"/activities/{test_activity_name}/unregister", params={"email": test_email})

        # Act
        response = client.post(
            f"/activities/{test_activity_name}/signup",
            params={"email": test_email}
        )
        response_activities = client.get("/activities")
        participants = response_activities.json()[test_activity_name]["participants"]

        # Assert
        assert response.status_code == 200
        assert test_email in participants


class TestUnregisterErrorCases:
    """Test suite for unregister error scenarios."""

    def test_unregister_from_nonexistent_activity_returns_404(self, client, sample_email, nonexistent_activity):
        """
        Arrange: Use activity that doesn't exist
        Act: POST /activities/{nonexistent}/unregister
        Assert: Response status is 404 Not Found
        """
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/unregister",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 404

    def test_unregister_from_nonexistent_activity_returns_detail(self, client, sample_email, nonexistent_activity):
        """
        Arrange: Use activity that doesn't exist
        Act: POST /activities/{nonexistent}/unregister
        Assert: Response contains error detail
        """
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/unregister",
            params={"email": sample_email}
        )
        data = response.json()

        # Assert
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_unregister_non_participant_returns_400(self, client, test_activity_name):
        """
        Arrange: Use email that's not signed up for activity
        Act: POST unregister with non-participant email
        Assert: Response status is 400 Bad Request
        """
        # Arrange
        non_participant_email = "not.registered@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{test_activity_name}/unregister",
            params={"email": non_participant_email}
        )

        # Assert
        assert response.status_code == 400

    def test_unregister_non_participant_returns_error_message(self, client, test_activity_name):
        """
        Arrange: Use email that's not registered
        Act: POST unregister
        Assert: Response explains participant not signed up
        """
        # Arrange
        non_participant_email = "not.member@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{test_activity_name}/unregister",
            params={"email": non_participant_email}
        )
        data = response.json()

        # Assert
        assert "detail" in data
        assert "not" in data["detail"].lower() and "signed up" in data["detail"].lower()

    def test_duplicate_unregister_returns_400(self, client, test_activity_name):
        """
        Arrange: Add participant, then unregister once
        Act: Attempt unregister again
        Assert: Second unregister returns 400
        """
        # Arrange
        test_email = "double.unregister@mergington.edu"
        client.post(f"/activities/{test_activity_name}/signup", params={"email": test_email})
        client.post(f"/activities/{test_activity_name}/unregister", params={"email": test_email})

        # Act
        response = client.post(
            f"/activities/{test_activity_name}/unregister",
            params={"email": test_email}
        )

        # Assert
        assert response.status_code == 400
