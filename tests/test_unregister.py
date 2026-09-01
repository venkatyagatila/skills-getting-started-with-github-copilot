"""Tests for DELETE /activities/{activity}/participants/{email} endpoint using AAA pattern."""
import pytest


class TestUnregisterParticipant:
    """Test suite for activity unregistration functionality."""

    def test_successful_unregister_removes_participant(self, client, sample_activity_name):
        """
        Test that a valid unregister request removes the student from participants.

        Arrange: Add a student to an activity
        Act: DELETE request to unregister
        Assert: Student is removed from participants list
        """
        # Arrange
        email = "unregister.test@mergington.edu"
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email}
        )

        # Act
        response = client.delete(
            f"/activities/{sample_activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

        # Verify student was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[sample_activity_name]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """
        Test that unregistering from a non-existent activity returns 404.

        Arrange: Use a fake activity name
        Act: DELETE request to non-existent activity
        Assert: Response is 404
        """
        # Arrange
        fake_activity = "Fake Activity Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{fake_activity}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_nonexistent_participant_returns_404(self, client, sample_activity_name):
        """
        Test that unregistering a non-existent participant returns 404.

        Arrange: Use an email not in any activity
        Act: DELETE request for non-existent participant
        Assert: Response is 404
        """
        # Arrange
        email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{sample_activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_unregister_response_message_format(self, client, sample_activity_name):
        """
        Test that unregister response has correct message format.

        Arrange: Add a student then prepare to remove
        Act: DELETE request
        Assert: Response message contains email and activity name
        """
        # Arrange
        email = "message.test@mergington.edu"
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email}
        )

        # Act
        response = client.delete(
            f"/activities/{sample_activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 200
        message = response.json()["message"]
        assert email in message
        assert sample_activity_name in message

    def test_can_reregister_after_unregister(self, client, sample_activity_name):
        """
        Test that a student can re-register after being unregistered.

        Arrange: Register, then unregister a student
        Act: Register the same student again
        Assert: Re-registration is successful
        """
        # Arrange
        email = "reregister.test@mergington.edu"
        
        # First signup
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email}
        )
        
        # Unregister
        client.delete(
            f"/activities/{sample_activity_name}/participants/{email}"
        )

        # Act
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        
        # Verify student is back in list
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[sample_activity_name]["participants"]

    def test_unregister_email_url_encoding(self, client, sample_activity_name):
        """
        Test that unregister handles URL-encoded email addresses.

        Arrange: Register a student with special characters in email
        Act: DELETE request with URL-encoded email
        Assert: Student is successfully unregistered
        """
        # Arrange
        email = "test+tagged@mergington.edu"
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email}
        )

        # Act
        response = client.delete(
            f"/activities/{sample_activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 200
        
        # Verify removal
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[sample_activity_name]["participants"]
