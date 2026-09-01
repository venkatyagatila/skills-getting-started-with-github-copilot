"""Tests for edge cases and validation using AAA pattern."""
import pytest


class TestValidationAndEdgeCases:
    """Test suite for validation and edge case handling."""

    def test_activity_participant_count_accuracy(self, client, sample_activity_name):
        """
        Test that participant count matches actual participants list.

        Arrange: Get an activity
        Act: Count participants and check max_participants
        Assert: Counts make sense
        """
        # Arrange
        # Act
        response = client.get("/activities")
        activities = response.json()
        activity = activities[sample_activity_name]

        # Assert
        participant_count = len(activity["participants"])
        max_participants = activity["max_participants"]
        assert participant_count >= 0
        assert max_participants > 0
        assert participant_count <= max_participants

    def test_multiple_signups_to_different_activities(self, client):
        """
        Test that a student can sign up to multiple different activities.

        Arrange: Prepare email and multiple activities
        Act: Sign up to 2+ different activities
        Assert: Student appears in all activity participant lists
        """
        # Arrange
        email = "multi.signup@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Drama Club"]

        # Act
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Assert
        activities_response = client.get("/activities")
        all_activities = activities_response.json()
        for activity in activities_to_join:
            assert email in all_activities[activity]["participants"]

    def test_unregister_does_not_affect_other_activities(self, client):
        """
        Test that unregistering from one activity doesn't affect others.

        Arrange: Sign up to 2 activities
        Act: Unregister from first activity
        Assert: Student is removed from first but still in second
        """
        # Arrange
        email = "isolation.test@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"

        client.post(f"/activities/{activity1}/signup", params={"email": email})
        client.post(f"/activities/{activity2}/signup", params={"email": email})

        # Act
        client.delete(f"/activities/{activity1}/participants/{email}")

        # Assert
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        assert email not in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]

    def test_signup_case_sensitivity_of_email(self, client, sample_activity_name):
        """
        Test email case sensitivity in signup handling.

        Arrange: Prepare emails with different cases
        Act: Sign up with different case variations
        Assert: System treats them as different emails (or same, depending on implementation)
        """
        # Arrange
        email_lower = "casesensitive@mergington.edu"
        email_upper = "CASESENSITIVE@mergington.edu"

        # Act
        response1 = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email_lower}
        )
        response2 = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email_upper}
        )

        # Assert - Both should succeed (case-sensitive storage)
        assert response1.status_code == 200
        assert response2.status_code == 200

        # Verify both are stored
        activities_response = client.get("/activities")
        activities = activities_response.json()
        participants = activities[sample_activity_name]["participants"]
        assert email_lower in participants
        assert email_upper in participants

    def test_special_characters_in_activity_name(self, client):
        """
        Test activity names with special characters are handled correctly.

        Arrange: Use standard activity name from data
        Act: Try signup with activity name
        Assert: URL encoding/decoding works correctly
        """
        # Arrange
        activity_name = "Science Olympiad"  # Has space
        email = "special.char.test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        
        # Verify with space in name
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_empty_string_email_handling(self, client, sample_activity_name):
        """
        Test that empty string email is handled (may be invalid).

        Arrange: Prepare empty email
        Act: Attempt signup with empty email
        Assert: Either rejected or handled gracefully
        """
        # Arrange
        email = ""

        # Act
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email}
        )

        # Assert - Should either be 400 or succeed with empty string in list
        # This documents current behavior
        assert response.status_code in [200, 400, 422]

    def test_root_redirect_to_static(self, client):
        """
        Test that root path redirects to static files.

        Arrange: No setup needed
        Act: GET request to root
        Assert: Redirect response to /static/index.html
        """
        # Arrange
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code in [301, 302, 307, 308]
        assert "/static/index.html" in response.headers.get("location", "")
