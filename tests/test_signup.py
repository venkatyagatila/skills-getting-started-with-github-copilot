"""Tests for POST /activities/{activity}/signup endpoint using AAA pattern."""
import pytest


class TestSignupForActivity:
    """Test suite for activity signup functionality."""

    def test_successful_signup_adds_participant(self, client, sample_activity_name, sample_student_email):
        """
        Test that a valid signup adds the student to participants.

        Arrange: Prepare new student email
        Act: POST signup request
        Assert: Response is 200 and student is in participants list
        """
        # Arrange
        new_email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": new_email}
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

        # Verify student was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert new_email in activities[sample_activity_name]["participants"]

    def test_duplicate_signup_rejected(self, client, sample_activity_name):
        """
        Test that a student cannot sign up for the same activity twice.

        Arrange: Sign up a student once
        Act: Attempt to sign up the same student again
        Assert: Second signup returns 400 error
        """
        # Arrange
        email = "duplicate.test@mergington.edu"
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email}
        )

        # Act
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Test that signup to a non-existent activity returns 404.

        Arrange: Use a made-up activity name
        Act: POST signup request to non-existent activity
        Assert: Response is 404
        """
        # Arrange
        fake_activity = "Underwater Basket Weaving Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_response_message_format(self, client, sample_activity_name):
        """
        Test that signup response has correct message format.

        Arrange: Prepare valid signup data
        Act: POST signup request
        Assert: Response message contains email and activity name
        """
        # Arrange
        email = "formattest@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        message = response.json()["message"]
        assert email in message
        assert sample_activity_name in message

    def test_signup_email_url_encoding(self, client, sample_activity_name):
        """
        Test that signup handles URL-encoded email addresses.

        Arrange: Use email with special characters that need URL encoding
        Act: POST signup request with URL-encoded email
        Assert: Student is registered with correct email
        """
        # Arrange
        # Note: httpx.TestClient handles URL encoding automatically
        email = "test+tag@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        
        # Verify exact email was stored
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[sample_activity_name]["participants"]
