# Open Source Contributor Hub GraphQL Server

This repository contains the GraphQL server for the Open Source Contributor Hub—a platform designed to help developers discover, manage, and contribute to open-source projects. The server aggregates issues from GitHub and GitLab via their APIs and offers resolvers to query and manage user-specific project issues.

## Features

- **Aggregated Issues:** Fetches issues from GitHub and GitLab based on filters like labels (e.g., `good first issue`, `help wanted`).
- **GraphQL API:** Built with FastAPI and Strawberry, providing a robust and flexible API.
- **Project & Issue Management:** Enables users to create projects, add issues to projects, mark issues as in progress, completed, or dropped, and update or delete issues as needed.
- **Background Refresh:** Supports periodic updates of issue data (e.g., via Celery) to keep information current.
- **Caching:** Uses Redis to cache frequently accessed data, reducing external API calls.
- **Database Integration:** Stores persistent data in PostgreSQL.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Development](#development)
- [Project Structure](#project-structure)
- [GraphQL API](#graphql-api)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL (for persistent storage)
- Redis (for caching and background task queues)
- (Optional) Docker for containerized deployment

### Setup Steps

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/MissTipo/open-source-contributor-hub.git
   cd open-source-contributor-hub/graphql_server


2. **Create a virtual Environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the Dependencies:**

   ```bash
   pip install -r requirements.txt


4. **Set Up the Environment Variables:**

   Create a `.env` file in the project root and add the following environment variables:

   ```bash
   DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database>
   REDIS_URL=redis://<host>:<port>
   GITHUB_TOKEN=<your_github_token>
   GITLAB_TOKEN=<your_gitlab_token>
   ```

5. **Run the Migrations:**

   ```bash
   alembic upgrade head
   ```

6. **Start the Server:**

   ```bash
   uvicorn graphql_server.main:app --reload
   ```

7. **Access the GraphQL Playground:**

   Open `http://localhost:8000/graphql` in your browser to access the GraphQL Playground.

## Usage

 **Run the Background Worker (Optional):**

   If you want to enable background tasks (e.g., periodic issue updates), start the Celery worker:

   ```bash
   celery -A graphql_server.worker worker --loglevel=info
   ```

## Development

**Running Tests:**
  ```bash
  pytest
  ```
## Project Structure

graphql_server/
├── __init__.py
├── schemas/
│   └── issue_schema.py       # GraphQL schema definitions for issues
├── resolvers/
│   └── issue_resolver.py     # Query and mutation resolvers for issue operations
├── services/
│   └── issue_service.py      # Service layer for fetching and managing issues
├── celery_worker.py          # Celery configuration for background tasks
└── main.py                   # Entry point for the FastAPI application

## GraphQL API

The GraphQL endpoint is available at /graphql. Here are some example operations:

### Query Example

```graphql
query {
  issues {
    id
    title
    url
    project {
      id
      name
    }
  }
}
```

### Mutation Example

```graphql
mutation {
  createIssue(
    title: "Update README"
    url: "

## Testing
**Unit Tests:** Located in the `tests/` directory.

**Run the Tests:**
```bash
pytest
```

## Contributing

Contributions are welcome! Please refer to the [contributing guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```


