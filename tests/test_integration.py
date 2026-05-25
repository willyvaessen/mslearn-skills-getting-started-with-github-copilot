"""Integration tests for cross-endpoint workflows using AAA pattern."""

import pytest


class TestSignupToUnregisterWorkflow:
    """Test suite for complete signup → view → unregister workflows."""

    def test_full_user_journey_signup_view_unregister(self, client, test_activity_name):
        """
        Arrange: Prepare test participant
        Act: Signup, view in activities, unregister, verify removed
        Assert: Participant appears and disappears correctly
        """
        # Arrange
        test_email = "journey.test@mergington.edu"

        # Act - Step 1: Signup
        signup_response = client.post(
            f"/activities/{test_activity_name}/signup",
            params={"email": test_email}
        )
        assert signup_response.status_code == 200

        # Act - Step 2: View in activities
        view_response = client.get("/activities")
        participants_after_signup = view_response.json()[test_activity_name]["participants"]

        # Assert - Participant is visible
        assert test_email in participants_after_signup

        # Act - Step 3: Unregister
        unregister_response = client.post(
            f"/activities/{test_activity_name}/unregister",
            params={"email": test_email}
        )
        assert unregister_response.status_code == 200

        # Act - Step 4: View after unregister
        final_response = client.get("/activities")
        participants_after_unregister = final_response.json()[test_activity_name]["participants"]

        # Assert - Participant is gone
        assert test_email not in participants_after_unregister

    def test_participant_count_changes_on_signup_unregister(self, client, test_activity_name):
        """
        Arrange: Get initial participant count
        Act: Signup (count +1), unregister (count -1)
        Assert: Counts reflect changes correctly
        """
        # Arrange
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[test_activity_name]["participants"])
        test_email = "count.test@mergington.edu"

        # Act - Signup
        client.post(f"/activities/{test_activity_name}/signup", params={"email": test_email})
        after_signup = client.get("/activities")
        after_signup_count = len(after_signup.json()[test_activity_name]["participants"])

        # Assert - Count increased
        assert after_signup_count == initial_count + 1

        # Act - Unregister
        client.post(f"/activities/{test_activity_name}/unregister", params={"email": test_email})
        after_unregister = client.get("/activities")
        after_unregister_count = len(after_unregister.json()[test_activity_name]["participants"])

        # Assert - Count decreased back
        assert after_unregister_count == initial_count

    def test_availability_changes_with_signups_unregisters(self, client, test_activity_name):
        """
        Arrange: Get initial availability (max - current)
        Act: Signup (availability -1), unregister (availability +1)
        Assert: Availability reflects participant changes
        """
        # Arrange
        initial_response = client.get("/activities")
        activity = initial_response.json()[test_activity_name]
        initial_max = activity["max_participants"]
        initial_current = len(activity["participants"])
        initial_available = initial_max - initial_current
        test_email = "availability.test@mergington.edu"

        # Act - Signup
        client.post(f"/activities/{test_activity_name}/signup", params={"email": test_email})
        after_signup = client.get("/activities")
        after_signup_available = (
            after_signup.json()[test_activity_name]["max_participants"] -
            len(after_signup.json()[test_activity_name]["participants"])
        )

        # Assert - Availability decreased
        assert after_signup_available == initial_available - 1

        # Act - Unregister
        client.post(f"/activities/{test_activity_name}/unregister", params={"email": test_email})
        after_unregister = client.get("/activities")
        after_unregister_available = (
            after_unregister.json()[test_activity_name]["max_participants"] -
            len(after_unregister.json()[test_activity_name]["participants"])
        )

        # Assert - Availability increased back
        assert after_unregister_available == initial_available


class TestMultipleParticipantsWorkflow:
    """Test suite for multiple participant interactions."""

    def test_add_multiple_participants_all_appear_in_list(self, client, test_activity_name):
        """
        Arrange: Prepare multiple test emails
        Act: Signup all of them
        Assert: All appear in participants list
        """
        # Arrange
        test_emails = [
            "multi.user1@mergington.edu",
            "multi.user2@mergington.edu",
            "multi.user3@mergington.edu",
        ]

        # Act - Signup all
        for email in test_emails:
            client.post(f"/activities/{test_activity_name}/signup", params={"email": email})

        # Assert - All are in list
        response = client.get("/activities")
        participants = response.json()[test_activity_name]["participants"]
        for email in test_emails:
            assert email in participants

    def test_remove_one_participant_others_remain(self, client, test_activity_name):
        """
        Arrange: Add 3 participants
        Act: Remove one of them
        Assert: Removed participant gone, others still present
        """
        # Arrange
        test_emails = [
            "keep.user1@mergington.edu",
            "keep.user2@mergington.edu",
            "remove.me@mergington.edu",
        ]
        
        for email in test_emails:
            client.post(f"/activities/{test_activity_name}/signup", params={"email": email})

        # Act - Remove one
        client.post(
            f"/activities/{test_activity_name}/unregister",
            params={"email": "remove.me@mergington.edu"}
        )

        # Assert - Removed is gone, others remain
        response = client.get("/activities")
        participants = response.json()[test_activity_name]["participants"]
        assert "remove.me@mergington.edu" not in participants
        assert "keep.user1@mergington.edu" in participants
        assert "keep.user2@mergington.edu" in participants

    def test_sequential_signups_and_unregisters(self, client, test_activity_name):
        """
        Arrange: Track operations
        Act: Interleave signups and unregisters
        Assert: Correct sequence of adds and removals
        """
        # Arrange
        user_a = "seq.user.a@mergington.edu"
        user_b = "seq.user.b@mergington.edu"
        user_c = "seq.user.c@mergington.edu"

        # Act & Assert - Step by step
        # Add A
        client.post(f"/activities/{test_activity_name}/signup", params={"email": user_a})
        response = client.get("/activities")
        participants = response.json()[test_activity_name]["participants"]
        assert user_a in participants

        # Add B
        client.post(f"/activities/{test_activity_name}/signup", params={"email": user_b})
        response = client.get("/activities")
        participants = response.json()[test_activity_name]["participants"]
        assert user_a in participants
        assert user_b in participants

        # Add C
        client.post(f"/activities/{test_activity_name}/signup", params={"email": user_c})
        response = client.get("/activities")
        participants = response.json()[test_activity_name]["participants"]
        assert user_a in participants
        assert user_b in participants
        assert user_c in participants

        # Remove B
        client.post(f"/activities/{test_activity_name}/unregister", params={"email": user_b})
        response = client.get("/activities")
        participants = response.json()[test_activity_name]["participants"]
        assert user_a in participants
        assert user_b not in participants
        assert user_c in participants

        # Remove A
        client.post(f"/activities/{test_activity_name}/unregister", params={"email": user_a})
        response = client.get("/activities")
        participants = response.json()[test_activity_name]["participants"]
        assert user_a not in participants
        assert user_c in participants


class TestCrossActivityInteractions:
    """Test suite for interactions across multiple activities."""

    def test_same_user_signup_multiple_activities(self, client):
        """
        Arrange: Get two different activities
        Act: Sign up same user to both
        Assert: User appears in both activities
        """
        # Arrange
        response = client.get("/activities")
        activities = list(response.json().keys())[:2]  # Get first 2 activities
        test_email = "multi.activity@mergington.edu"

        # Act - Signup to both
        for activity in activities:
            client.post(
                f"/activities/{activity}/signup",
                params={"email": test_email}
            )

        # Assert - User in both
        response = client.get("/activities")
        activities_data = response.json()
        for activity in activities:
            assert test_email in activities_data[activity]["participants"]

    def test_unregister_from_one_activity_not_affecting_other(self, client):
        """
        Arrange: Sign up to two activities
        Act: Unregister from one
        Assert: Still registered in the other
        """
        # Arrange
        response = client.get("/activities")
        activities = list(response.json().keys())[:2]
        activity_a, activity_b = activities[0], activities[1]
        test_email = "cross.activity@mergington.edu"

        # Signup to both
        client.post(f"/activities/{activity_a}/signup", params={"email": test_email})
        client.post(f"/activities/{activity_b}/signup", params={"email": test_email})

        # Act - Unregister from A
        client.post(
            f"/activities/{activity_a}/unregister",
            params={"email": test_email}
        )

        # Assert - Gone from A, still in B
        response = client.get("/activities")
        activities_data = response.json()
        assert test_email not in activities_data[activity_a]["participants"]
        assert test_email in activities_data[activity_b]["participants"]
