# Open-Source Contributor Hub - Server

## Overview

The Open-Source Contributor Hub server is a FastAPI-based microservice that aggregates beginner-friendly issues from GitHub (and optionally GitLab). It fetches issue data via external APIs, processes and stores the data in a PostgreSQL database (using SQLAlchemy), and exposes a GraphQL API (using Strawberry) for querying and mutating data. The server supports background tasks (via Celery) and caching (using Redis) to ensure up-to-date information with high performance.

## Features

- **Issue Aggregation**
  - Fetches issues from GitHub (and GitLab) using GraphQL/REST.
  - Filters issues by labels (e.g., "good first issue"), source, and programming language.
  - Caches frequently accessed data with Redis to reduce external API calls.

- **GraphQL API**
  - Query resolvers to retrieve and filter issues.
  - Mutation resolvers (e.g., `refreshIssues`) to refresh external data and update the database.

- **Data Persistence**
  - Uses PostgreSQL with SQLAlchemy ORM for storing issue data.

- **Background Processing & Caching**
  - Scheduled background tasks using Celery.
  - Redis caching to improve performance and reduce load on external services.

- **Configuration**
  - Environment-based configuration via a `.env` file (loaded using `python-dotenv`).

## Technologies

- **Backend Framework:** FastAPI
- **GraphQL Library:** Strawberry
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Caching:** Redis
- **Task Scheduler:** Celery
- **External Integrations:** GitHub GraphQL API (and GitLab API, if needed)
- **Containerization:** Docker (optional)
- **Deployment:** Kubernetes / Cloud Providers (AWS, GCP, etc.)

## Setup and Installation

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd server/microservices/issue-aggregator

2. **Create and Activate a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt

4. **Configure Environment Variables:**

   Create a `.env` file in the project root with the following variables:

   ```bash
    GITHUB_TOKEN="your_github_token_here"
    GITLAB_TOKEN="your_gitlab_token_here"
    POSTGRES_DB_URL="postgresql://username:password@localhost:5432/yourdbname"
    REDIS_URL="redis://localhost:6379"

5. **Run Database Migrations (if applicable):**

   ```bash
   alembic upgrade head

6. **Start the Server:**
   ```bash

    uvicorn main:app --reload

  The GraphQL endpoint will be available at http://127.0.0.1:8000/graphql.

## Usage

  **GraphQL Playground:**
        Visit http://127.0.0.1:8000/graphql to explore your GraphQL API.

  **Example Query:**
  ```bash
  {
    issues {
      id
      title
      description
      state
      source
      labels
    }
  }
```
 **Example Mutation (Refresh Issues):**

  ```bash
  mutation {
    refreshIssues
  }
```

## Testing

  **Run Tests:**
  ```bash
  pytest
  ```
  This will run all tests located in the tests/ directory.

## Deployment

  **Containerization & Orchestration:**
        Build Docker images and deploy using Kubernetes or your preferred orchestration tool.
    CI/CD Pipeline:
        Use GitHub Actions, Jenkins, or CircleCI for automated testing and deployment.

## License

This project is licensed under the MIT License.


