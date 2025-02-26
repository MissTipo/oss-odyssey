import requests
import os

GITHUB_API_URL = "https://api.github.com/graphql"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

def fetch_github_issues(owner: str, repo: str, label: str, first: int = 10):
    query = """
    query($owner: String!, $repo: String!, $label: [String!], $first: Int!) {
      repository(owner: $owner, name: $repo) {
        primaryLanguage {
          name
        }
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
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(GITHUB_API_URL, json={"query": query, "variables": variables}, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed with status {response.status_code}: {response.text}")


def fetch_github_labels(owner: str, repo: str, first: int = 50):
    """
    Fetches labels for a given repository from GitHub.
    Returns a list of label dictionaries containing name, color, and description.
    """
    query = """
    query($owner: String!, $repo: String!, $first: Int!) {
      repository(owner: $owner, name: $repo) {
        labels(first: $first) {
          nodes {
            name
            color
            description
          }
        }
      }
    }
    """
    variables = {
        "owner": owner,
        "repo": repo,
        "first": first
    }
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(GITHUB_API_URL, json={"query": query, "variables": variables}, headers=headers)
    if response.status_code == 200:
        # Return only the list of label nodes
        return response.json().get("data", {}).get("repository", {}).get("labels", {}).get("nodes", [])
    else:
        raise Exception(f"Query failed with status {response.status_code}: {response.text}")

def fetch_github_repositories(label: str, first: int = 10):
    """
    Searches for repositories on GitHub using the provided label as a topic filter.
    Returns a list of repositories with key details.
    """
    query = """
    query($query: String!, $first: Int!) {
      search(query: $query, type: REPOSITORY, first: $first) {
        nodes {
          ... on Repository {
            id
            name
            nameWithOwner
            description
            url
            primaryLanguage {
              name
            }
          }
        }
      }
    }
    """
    # Use the label as a topic filter. For example, if label is "hacktober", then "topic:hacktober"
    variables = {
        "query": f"topic:{label}",
        "first": first
    }
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(GITHUB_API_URL, json={"query": query, "variables": variables}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        nodes = data.get("data", {}).get("search", {}).get("nodes", [])
        # Map each repository node to a dictionary matching our repository schema.
        repos = []
        for repo in nodes:
            repos.append({
                "id": repo.get("id"),
                "external_id": repo.get("id"),  # Using the repository ID as external_id
                "name": repo.get("name"),
                "full_name": repo.get("nameWithOwner"),
                "description": repo.get("description"),
                "url": repo.get("url"),
                "source": "github",
                "language": repo.get("primaryLanguage", {}).get("name") if repo.get("primaryLanguage") else None
            })
        return repos
    else:
        raise Exception(f"Query failed with status {response.status_code}: {response.text}")
        

# Example usage:
if __name__ == "__main__":
    try:
        # Example: Fetch issues
        data = fetch_github_issues("apache", "airflow", "good first issue")
        # Process the data as needed.
        issues = data.get("data", {}).get("repository", {}).get("issues", {}).get("edges", [])
        for edge in issues:
            issue = edge["node"]
            print(f"{issue['number']}: {issue['title']}")

        # Example: Fetch labels
        labels = fetch_github_labels("apache", "airflow")
        for label in labels:
            print(f"Label: {label['name']} - Color: {label['color']}")

        # Example: Fetch repositories by label/topic
        repos = fetch_github_repositories("hacktober")
        for repo in repos:
            print(f"{repo['full_name']}: {repo['description']}")
    except Exception as e:
        print("Error:", e)
    except Exception as e:
        print("Error fetching issues:", e)

