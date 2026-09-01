"""Tests for GET /activities endpoint using AAA pattern."""
import pytest


class TestGetActivities:
    """Test suite for retrieving activities."""

    def test_get_all_activities_returns_list(self, client):
        """
        Test that GET /activities returns a list of all activities.

        Arrange: No setup needed
        Act: Make GET request to /activities
        Assert: Response has 200 status and contains expected activities
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Basketball Club",
            "Drama Club",
            "Art Studio",
            "Science Olympiad",
            "Debate Team",
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) >= len(expected_activities)
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self, client):
        """
        Test that each activity has all required fields.

        Arrange: No setup needed
        Act: Get activities and inspect structure
        Assert: Each activity has description, schedule, max_participants, participants
        """
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)

    def test_participants_list_contains_strings(self, client):
        """
        Test that participants list contains email strings.

        Arrange: No setup needed
        Act: Get activities
        Assert: All participants are valid string emails
        """
        # Arrange
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant, f"Invalid email format: {participant}"

    def test_max_participants_is_positive_integer(self, client):
        """
        Test that max_participants is a positive integer.

        Arrange: No setup needed
        Act: Get activities
        Assert: All max_participants values are positive integers
        """
        # Arrange
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert activity_data["max_participants"] > 0
