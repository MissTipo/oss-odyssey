import requests

KONG_PROXY_URL = "http://192.168.49.2:31579/graphql"
ISSUES_URL = "http://192.168.49.2:31579/issues"
BOOKMARK_URL = "http://192.168.49.2:31579/bookmark"

def test_user_authentication():
    """Test user registration, login, and token validation using GraphQL"""
    register_query = {
        "query": """
            mutation {
                register(input: {username: "testuser1", email: "testuser@example.com", password: "TestPassword123"}) {
                    id
                    email
                }
            }
        """
    }

    login_query = {
        "query": """
            mutation {
                login(input: {email: "testuser@example.com", password: "TestPassword123"}) {
                    accessToken
                }
            }
        """
    }

    headers = {"Content-Type": "application/json"}

    # Register user
    reg_response = requests.post(KONG_PROXY_URL, json=register_query, headers=headers)
    assert reg_response.status_code == 200, f"Failed to register: {reg_response.text}"

    # Login user
    login_response = requests.post(KONG_PROXY_URL, json=login_query, headers=headers)
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"

    token = login_response.json().get("data", {}).get("login", {}).get("accessToken")
    assert token, "Missing access token in login response"

    return token  # Use this for further tests

def test_fetch_issues():
    """Test if a user can fetch issues with a valid token"""
    token = test_user_authentication()  # Get a valid token from login
    headers = {"Authorization": f"Bearer {token}"}

    params = {"repo_url": "https://github.com/apache/airflow"}  # Ensure repo_url is provided
    response = requests.get(ISSUES_URL, headers=headers, params=params)

    assert response.status_code == 200, f"Failed to fetch issues: {response.text}"

    issues = response.json().get("issues", [])
    assert isinstance(issues, list), "Issues response is not a list"
    assert len(issues) > 0, "No issues returned from GitHub API"

    # Validate the structure of an issue
    issue = issues[0]
    assert "id" in issue and "title" in issue and "url" in issue, "Issue object is missing expected fields"


def test_issue_bookmark():
    """Test if a user can bookmark an issue"""
    token = test_user_authentication()  # Get a valid token from login
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch issues first
    params = {"repo_url": "https://github.com/apache/airflow"}
    issues_response = requests.get(ISSUES_URL, headers=headers, params=params)

    assert issues_response.status_code == 200, f"Failed to fetch issues: {issues_response.text}"

    issues = issues_response.json().get("issues", [])
    assert len(issues) > 0, "No issues returned from aggregator"

    issue_to_bookmark = issues[0]  # Pick first issue
    bookmark_payload = {"issue_id": issue_to_bookmark["id"]}

    # Bookmark issue
    bookmark_response = requests.post(BOOKMARK_URL, json=bookmark_payload, headers=headers)
    assert bookmark_response.status_code == 201, f"Failed to bookmark issue: {bookmark_response.text}"


def test_api_gateway_auth_enforcement():
    """Test that protected endpoints require authentication"""
    protected_endpoints = [ISSUES_URL, BOOKMARK_URL]

    for endpoint in protected_endpoints:
        response = requests.get(endpoint)
        assert response.status_code == 401, f"Expected 401 Unauthorized for {endpoint}, got {response.status_code}"

