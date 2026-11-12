# Developer Intelligence

## Project Overview

Developer Intelligence is a web application developed as a final project for Harvard University's CS50x: Introduction to Computer Science.

The application allows users to analyze public GitHub repositories by retrieving repository information through the GitHub REST API, calculating development activity metrics, and storing repository data in a local SQLite database.

The project aims to provide a simple interface for exploring GitHub repositories while demonstrating practical software engineering concepts such as API integration, database persistence, backend architecture, data processing, automated testing, and web development.

Developer Intelligence is built with Python and Flask, using server-side HTML rendering and Bootstrap for its user interface.

## Features

### GitHub Repository Analysis

Users can search for a public GitHub repository by entering its owner and repository name.

The application retrieves information from the GitHub REST API, including:

- Repository name and full name.

- Description and primary programming language.

- Number of stars.

- Number of forks.

- Number of open issues.

- Repository creation date.

- Last push date.

- Last update date.

### Repository Analytics

Developer Intelligence calculates three metrics:

**Repository Age**

The number of days elapsed since the repository was created on GitHub.

**Days Since Last Push**

The number of days elapsed since the repository's most recent push. If GitHub does not provide this information, the application displays an unavailable value.

**Average Stars per Year**

An approximate historical average calculated by dividing the repository's current star count by its age in years.

For repositories younger than one year, the calculation uses a minimum denominator of one year to avoid disproportionately large results.

This metric does not measure actual star growth over the last twelve months.

### Repository History

Analyzed repositories are stored in a local SQLite database.

Users can access a history page to review previously analyzed repositories.

When an existing repository is analyzed again, its stored information is updated instead of creating a duplicate record.

### Error Handling

The application provides user-friendly error messages for common problems, including:

- Missing repository information.

- Repositories that cannot be found.

- GitHub API access errors.

- Network connection failures.

- Request timeouts.

- Database operation failures.

Errors are handled using appropriate HTTP status codes.

### Responsive User Interface

The interface uses Bootstrap 5 and Jinja2 templates to provide a responsive layout.

The application includes:

- A repository search form.

- A repository details page.

- Analytics cards.

- A repository history table.

- Dedicated error pages.

- Shared navigation and footer components.

## Technologies

Developer Intelligence uses the following technologies:

| Technology | Purpose |

|---|---|

| Python 3.12 | Main programming language |

| Flask | Web application framework |

| Requests | Communication with the GitHub REST API |

| SQLite | Local database persistence |

| Jinja2 | Server-side HTML templates |

| Bootstrap 5 | Responsive user interface |

| pytest | Automated testing |

| Ruff | Python code quality checks |

| uv | Dependency and environment management |

| Git | Version control |

## Project Structure

Developer Intelligence follows a modular architecture that separates web request handling, external API communication, data persistence, and repository analytics.

The main project structure is:

```text

developer-intelligence/

├── src/

│   └── developer_intelligence/

│       ├── __init__.py

│       ├── app.py

│       ├── persistence/

│       │   ├── database.py

│       │   ├── repository.py

│       │   └── schema.sql

│       ├── services/

│       │   ├── __init__.py

│       │   ├── github.py

│       │   └── analytics.py

│       └── templates/

│           ├── base.html

│           ├── index.html

│           ├── repository.html

│           ├── history.html

│           └── error.html

├── tests/

│   ├── conftest.py

│   ├── test_app.py

│   ├── test_github.py

│   ├── test_database.py

│   └── test_analytics.py

├── pyproject.toml

├── uv.lock

└── README.md

```

### Main Components

**`app.py` — Flask Application**

Defines the application factory, initializes the database, handles HTTP requests, coordinates services, and renders HTML templates.

The application exposes three routes:

- `GET /`: Displays the repository search form.

- `POST /repositories`: Retrieves repository information, saves it, calculates analytics, and displays the results.

- `GET /history`: Displays previously analyzed repositories.

**`services/github.py` — GitHub API Integration**

Contains `GitHubService`, which communicates with the GitHub REST API.

The service retrieves repository information and converts the API response into a consistent internal data structure.

**`services/analytics.py` — Repository Analytics**

Contains `RepositoryAnalyticsService`, which calculates repository age, time since the last push, and average stars per year.

Keeping these calculations separate from Flask makes them easier to test and maintain.

**`persistence/database.py` — Database Initialization**

Initializes the SQLite database using the schema defined in `schema.sql`.

The database is initialized automatically when the Flask application starts.

**`persistence/repository.py` — Data Persistence**

Contains `RepositoryRepository`, which manages database operations.

It provides methods for saving, updating, and retrieving repository information.

Existing repositories are updated using SQLite's `ON CONFLICT` functionality, preventing duplicate records based on their GitHub identifiers.

**`templates/` — User Interface**

Contains the Jinja2 templates used to render the application.

The shared `base.html` template provides common navigation, page structure, and footer elements.

**`tests/` — Automated Tests**

Contains tests covering GitHub API integration, database operations, analytics calculations, Flask routes, and error handling.

External API requests are mocked during automated testing to avoid depending on GitHub availability.

## Installation

### Prerequisites

Before installing Developer Intelligence, make sure the following tools are available:

- Python 3.12 or newer.

- Git.

- uv, the Python package and project manager.

- An internet connection to retrieve repository information from GitHub.

### Clone the Repository

Clone the project from GitHub:

```bash

git clone https://github.com/jmpardos/developer-intelligence.git

cd developer-intelligence

```

### Install Dependencies

Install the project dependencies using uv:

```bash

uv sync --locked

```

This command creates a virtual environment if necessary and installs the dependencies specified in the project's lockfile.

No separate database installation is required because SQLite is included with Python.

## Usage

### Start the Application

Run the Flask development server:

```bash

uv run flask --app developer_intelligence.app:create_app run

```

By default, the application is available at:

`http://127.0.0.1:5000`

For development, Flask's debug mode can be enabled:

```bash

uv run flask --app developer_intelligence.app:create_app run --debug

```

Debug mode should only be used in a trusted development environment.

### Analyze a Repository

1. Open the application in your web browser.

2. Enter the GitHub repository owner.

3. Enter the repository name.

4. Click the analysis button.

5. Review the repository information and calculated analytics.

For example, to analyze Flask's public GitHub repository, enter:

| Field | Value |

|---|---|

| Owner | `pallets` |

| Repository | `flask` |

The application retrieves the repository information, calculates the analytics, and stores the results in SQLite.

### View Repository History

Select ****History**** from the navigation bar.

The history page displays previously analyzed repositories, including their names, primary languages, star counts, fork counts, and last analysis dates.

Analyzing the same repository again updates its stored information rather than creating a duplicate record.

### Database Storage

Developer Intelligence uses a local SQLite database named `developer_intelligence.db`.

The database is created automatically when the Flask application starts.

The database file is excluded from version control through `.gitignore`, ensuring that local repository history is not committed to Git.

## Testing

Developer Intelligence includes an automated test suite built with pytest.

The tests verify the main components of the application, including API integration, database persistence, analytics calculations, Flask routes, and error handling.

### Running the Tests

Execute the complete test suite using:

```bash

uv run pytest -v

```

The project currently includes 54 automated tests.

### Test Organization

The tests are organized into four modules:

**`test_github.py`**

Tests the integration with the GitHub API, including:

- Successful repository retrieval.

- Repository not found errors.

- GitHub access errors.

- Request timeouts.

- Invalid repository parameters.

**`test_database.py`**

Tests SQLite persistence, including:

- Database initialization.

- Repeated database initialization.

- Repository insertion.

- Updating existing repositories.

- Retrieving stored repositories.

- Handling empty repository collections.

The tests also verify that updating an existing repository preserves its original creation timestamp, updates its modification timestamp, and does not create duplicate records.

**`test_analytics.py`**

Tests repository analytics calculations, including:

- Repository age.

- Time elapsed since the last push.

- Repositories created recently.

- Future dates.

- Different time zones.

- Repositories without stars.

- Repositories without a recorded last push.

**`test_app.py`**

Tests the Flask application, including:

- Homepage rendering.

- Repository analysis.

- Repository history.

- HTML content.

- Input validation.

- GitHub API errors.

- Database failures.

- HTTP response status codes.

### Mocking External Services

Automated tests use mocks to simulate GitHub API responses.

This approach allows the test suite to run without making real HTTP requests to GitHub.

It also makes it possible to test error conditions, such as timeouts and API failures, in a predictable and repeatable way.

### Code Quality

The project uses Ruff for Python code quality checks.

Run:

```bash

uv run ruff check .

```

Ruff helps identify potential errors, unused imports, and other code quality issues.

## Design Decisions

Several architectural decisions were made to keep Developer Intelligence maintainable, testable, and appropriate for the scope of a CS50 final project.

### Flask Application Factory

The application uses Flask's application factory pattern through the `create_app()` function.

This approach separates application initialization from execution and makes it possible to create isolated application instances during testing.

It also allows test-specific configuration, such as using temporary SQLite databases.

### Separation of Responsibilities

The application separates its main responsibilities into independent components:

- `GitHubService` handles communication with the GitHub REST API.

- `RepositoryRepository` handles database persistence.

- `RepositoryAnalyticsService` performs repository calculations.

- Flask routes coordinate these components and render the results.

This separation makes the application easier to understand, test, and extend.

For example, analytics calculations can be tested independently without starting Flask or connecting to GitHub.

### SQLite Instead of a Database Server

SQLite was selected because the application requires relatively simple local data persistence.

Using SQLite avoids the need to install and configure a separate database server.

It also makes the application easier to install and run on different development environments.

For a larger application with multiple concurrent users, a database server such as PostgreSQL could be considered.

### Server-Side Rendering

Developer Intelligence uses Jinja2 templates to render HTML on the server.

This approach was selected because the application does not require complex client-side interactions.

Bootstrap provides responsive layouts and reusable interface components without introducing a separate frontend framework or JavaScript build process.

### Repository Updates

GitHub repositories are identified using their unique GitHub IDs.

When a repository is analyzed again, the application updates its existing database record using SQLite's `ON CONFLICT` functionality.

This avoids duplicate records while preserving the original local creation timestamp.

### Timezone-Aware Date Calculations

GitHub provides timestamps that include timezone information.

Repository analytics use timezone-aware Python datetime objects to calculate elapsed time consistently.

Future dates are handled by returning zero elapsed days instead of negative values.

### Dependency Management

The project uses uv to manage Python dependencies and virtual environments.

The `uv.lock` file allows dependencies to be installed consistently across development environments.

## Limitations

Developer Intelligence is designed as a small educational application rather than a production-ready GitHub analytics platform.

Its current limitations include:

**Public Repositories Only**

The application retrieves publicly accessible repository information without GitHub authentication.

Private repositories are not supported.

**GitHub API Rate Limits**

Unauthenticated requests are subject to GitHub API rate limits.

The application handles API access failures but does not implement authentication or automatic rate-limit recovery.

**No Historical Star Data**

The average stars per year metric is calculated using the repository's current star count and age.

The application does not retrieve historical star counts, so it cannot calculate actual annual star growth.

**Limited Activity Metrics**

The application focuses on repository metadata and basic activity indicators.

It does not currently analyze commit frequency, pull requests, contributors, or code quality.

**Local Data Storage**

Repository information is stored in a local SQLite database.

The application does not provide synchronization between installations or support multiple user accounts.

**No Background Updates**

Repository information is refreshed only when a user analyzes the repository again.

The application does not automatically update stored repositories.

## Future Improvements

Possible future enhancements include:

- GitHub authentication to support higher API rate limits.

- Historical repository metrics and trend visualization.

- Commit activity and contributor analysis.

- Repository comparison features.

- Background synchronization of repository information.

- Interactive charts and dashboards.

- Additional filtering and sorting options for repository history.

- Deployment to a cloud hosting platform.

These features were intentionally left outside the initial project scope to prioritize a reliable application with a clear architecture, automated tests, and a manageable set of features.

## AI Assistance

AI-assisted development tools were used during the project for technical explanations, code review, debugging support, test design discussions, documentation assistance, and language consistency checks.

The application was developed incrementally, with implementation decisions, code changes, and validation performed and reviewed by the project author.

AI-generated suggestions were evaluated and tested before being incorporated into the project.
