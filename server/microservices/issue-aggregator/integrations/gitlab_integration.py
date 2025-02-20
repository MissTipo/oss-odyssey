import requests
import os

GITLAB_API_URL = "https://api.gitlab.com/graphql"
GITLAB_TOKEN = os.environ.get("gitlab_TOKEN")  # Ensure your token is set in the environment

def fetch_gitlab_issues(owner: str, repo: str, label: str, first: int = 10):
    query = """
    query($owner: String!, $repo: String!, $label: [String!], $first: Int!) {
      repository(owner: $owner, name: $repo) {
        issues(first: $first, labels: $label, states: OPEN) {
          edges {
            node {
              id
              number
              title
              body
              createdAt
              updatedAt
              url
              labels(first: 10) {
                nodes {
                  name
                }
              }
            }
          }
        }
      }
    }
    """
    variables = {
        "owner": owner,
        "repo": repo,
        "label": [label],
        "first": first
    }
    headers = {
        "Authorization": f"Bearer {GITLAB_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(GITLAB_API_URL, json={"query": query, "variables": variables}, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed with status {response.status_code}: {response.text}")

# Example usage:
if __name__ == "__main__":
    try:
        data = fetch_gitlab_issues("octocat", "Hello-World", "good first issue")
        # Process the data as needed. For instance:
        issues = data.get("data", {}).get("repository", {}).get("issues", {}).get("edges", [])
        for edge in issues:
            issue = edge["node"]
            print(f"{issue['number']}: {issue['title']}")
    except Exception as e:
        print("Error fetching issues:", e)

