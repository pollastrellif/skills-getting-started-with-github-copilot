"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

# Create test client
client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    # Store initial state
    initial_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team with games and tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in matches",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["alex@mergington.edu", "sarah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Play instruments and perform in school concerts",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu"]
        },
        "Science Research Lab": {
            "description": "Conduct experiments and work on scientific research projects",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        }
    }
    
    # Clear current activities and restore initial state
    activities.clear()
    activities.update(initial_state)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(initial_state)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, reset_activities):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_has_required_fields(self, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_success(self, reset_activities):
        """Test successfully signing up a new participant"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_duplicate_participant_fails(self, reset_activities):
        """Test that signing up the same participant twice fails"""
        # First signup
        response1 = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second signup with same email
        response2 = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_already_registered_participant_fails(self, reset_activities):
        """Test that signing up someone already registered fails"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, reset_activities):
        """Test that signing up for a non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_adds_participant_to_list(self, reset_activities):
        """Test that signup actually adds the participant to the activity"""
        new_email = "newstudent@mergington.edu"
        
        # Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Chess Club"]["participants"])
        
        # Sign up new participant
        client.post(f"/activities/Chess%20Club/signup?email={new_email}")
        
        # Check participant was added
        final_response = client.get("/activities")
        final_count = len(final_response.json()["Chess Club"]["participants"])
        assert final_count == initial_count + 1
        assert new_email in final_response.json()["Chess Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant_success(self, reset_activities):
        """Test successfully unregistering an existing participant"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
    
    def test_unregister_nonexistent_participant_fails(self, reset_activities):
        """Test that unregistering a non-existent participant fails"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_nonexistent_activity_fails(self, reset_activities):
        """Test that unregistering from a non-existent activity fails"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_removes_participant_from_list(self, reset_activities):
        """Test that unregister actually removes the participant"""
        email_to_remove = "michael@mergington.edu"
        
        # Verify participant is initially registered
        initial_response = client.get("/activities")
        assert email_to_remove in initial_response.json()["Chess Club"]["participants"]
        
        # Unregister
        client.delete(f"/activities/Chess%20Club/unregister?email={email_to_remove}")
        
        # Check participant was removed
        final_response = client.get("/activities")
        assert email_to_remove not in final_response.json()["Chess Club"]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static(self, reset_activities):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
