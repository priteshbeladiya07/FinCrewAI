# FinCrew AI — Six-Agent Financial Research Platform

**An AI-powered financial research and stock analysis platform built with CrewAI and Mistral AI.**

FinCrew AI is an AI-powered financial research platform designed for individual investors, retail traders, and financial researchers. It uses six specialized AI agents to analyze companies from multiple perspectives, including company news, financial fundamentals, technical indicators, market sentiment, and investment risks.

The platform coordinates these agents through a structured research workflow. The first three agents perform their research in parallel, and their findings are passed to subsequent agents for sentiment evaluation, risk assessment, and final investment analysis.

The results are consolidated into a structured investment research report and presented through an interactive web dashboard.

## Overview

Traditional financial research involves collecting information from multiple sources and evaluating several dimensions of a company. FinCrew AI aims to organize this process using specialized AI agents working together through a coordinated research workflow.

### Key Features

- **Six Specialized AI Agents:** Dedicated agents perform different financial research and analysis tasks.
- **Parallel Research Execution:** News, fundamental, and technical analysis run in parallel.
- **News Research:** Investigates company-related news and market developments.
- **Fundamental Analysis:** Evaluates company financial performance and business fundamentals.
- **Technical Analysis:** Examines stock price trends and technical indicators.
- **Sentiment Analysis:** Evaluates market sentiment using the collected research findings.
- **Risk Analysis:** Identifies potential financial and market-related risks.
- **Investment Analysis:** Consolidates specialist findings into a final research report.
- **Research History:** Stores and retrieves previous research jobs.
- **Interactive Dashboard:** Supports research submission, status tracking, and report visualization.
- **Report Export:** Allows users to export generated research reports.

## AI Agent Architecture

FinCrew AI uses six specialized AI agents, each responsible for a different part of the research process.

| Agent | Responsibility |
|---|---|
| News Research Agent | Collects relevant company news and market developments. |
| Fundamental Analysis Agent | Evaluates financial performance and business fundamentals. |
| Technical Analysis Agent | Analyzes stock price trends and technical indicators. |
| Sentiment Analysis Agent | Evaluates sentiment based on the research findings. |
| Risk Analysis Agent | Identifies investment risks and potential downside factors. |
| Investment Analysis Agent | Consolidates findings into the final investment research report. |

### Agent Workflow

The workflow is divided into two stages:

**Parallel research stage:** The News Research, Fundamental Analysis, and Technical Analysis agents execute independently and simultaneously.

**Sequential analysis stage:** After all three research outputs are ready, they are passed to the Sentiment Analysis Agent, followed by the Risk Analysis Agent and Investment Analysis Agent.

```mermaid
flowchart TD
    A([Company Research Request])

    subgraph PARALLEL["Parallel Research Stage"]
        direction LR
        B["News Research Agent"]
        C["Fundamental Analysis Agent"]
        D["Technical Analysis Agent"]
    end

    E((Research Findings Ready))
    F["Sentiment Analysis Agent"]
    G["Risk Analysis Agent"]
    H["Investment Analysis Agent"]
    I["Pydantic Report Validation"]
    J[("PostgreSQL")]
    K([Final Research Report])

    A --> B
    A --> C
    A --> D

    B --> E
    C --> E
    D --> E

    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
```

## System Architecture

The platform follows a modular client-server architecture.

```mermaid
flowchart TB
    USER([User])

    subgraph FRONTEND["Frontend Layer"]
        UI["React + Vite"]
        AXIOS["Axios API Client"]
        UI --> AXIOS
    end

    subgraph BACKEND["Backend Layer"]
        API["FastAPI"]
        SERVICE["Research Services"]
        CREW["CrewAI Workflow"]
        API --> SERVICE
        SERVICE --> CREW
    end

    subgraph STORAGE["Database Layer"]
        DB[("PostgreSQL")]
    end

    LLM["Mistral AI API"]
    SOURCES["External Research Tools and Data Sources"]

    USER --> UI
    AXIOS <-->|REST API| API
    SERVICE <--> DB
    CREW <--> LLM
    CREW <--> SOURCES
```

For detailed system design and component interactions, see [Architecture Documentation](docs/architecture.md).

## Technology Stack

| Category | Technology |
|---|---|
| Frontend | React.js, Vite |
| Styling | CSS, Tailwind CSS |
| Backend | Python, FastAPI |
| AI Agent Framework | CrewAI |
| Language Model | Mistral AI |
| Data Validation | Pydantic |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| HTTP Client | Axios |
| Package Management | uv, npm |
| Containerization | Docker, Docker Compose |

## Project Structure

```text
FinCrewAI/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── api/
│   │   ├── crews/
│   │   ├── database/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── tasks/
│   │   ├── tools/
│   │   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── main.py
│   │
│   ├── .dockerignore
│   ├── .env.example
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── uv.lock
│
├── docs/
│   ├── api_documentation.md
│   └── architecture.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   │
│   ├── .dockerignore
│   ├── .env.example
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── reports/
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

### Backend Directory Responsibilities

| Directory | Responsibility |
|---|---|
| `agents/` | Defines the six specialized AI agents. |
| `api/` | Contains FastAPI routes and endpoints. |
| `crews/` | Coordinates the CrewAI workflow. |
| `database/` | Handles PostgreSQL connections and database operations. |
| `schemas/` | Defines Pydantic models and validation schemas. |
| `services/` | Implements application and research business logic. |
| `tasks/` | Defines the tasks assigned to agents. |
| `tools/` | Contains research tools and external integrations. |
| `utils/` | Contains shared utilities and helper functions. |

## Getting Started

### Prerequisites

Install the following:

- Python 3.12
- Node.js and npm
- uv package manager
- PostgreSQL (for local database setup)
- Docker Desktop (for containerized setup)
- Mistral AI API key
- API credentials for external research tools configured in the backend

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/FinCrewAI.git
cd FinCrewAI
```

Replace `YOUR_USERNAME` with your GitHub username and use your actual repository URL.

### 2. Backend Setup

Navigate to the backend:

```powershell
cd backend
```

Create a virtual environment:

```powershell
uv venv --python 3.12
```

Install dependencies:

```powershell
uv pip install --python .\.venv\Scripts\python.exe -r requirements.txt
```

Create a local `.env` file using `.env.example` as a reference.

Example:

```env
MISTRAL_API_KEY=your_mistral_api_key
TAVILY_API_KEY=your_tavily_api_key
DATABASE_URL=your_database_connection_url
```

Configure the database URL according to your PostgreSQL setup.

Do not commit real API keys or credentials.

Start the backend:

```powershell
uvicorn app.main:app --reload
```

Backend URL:

`http://127.0.0.1:8000`

Swagger API documentation:

`http://127.0.0.1:8000/docs`

### 3. Frontend Setup

Open another terminal:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Create a local `.env` file using `.env.example` as a reference.

Example:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start the frontend:

```powershell
npm run dev
```

Frontend URL:

`http://localhost:5173`

### 4. Database Configuration

FinCrew AI uses PostgreSQL for persistent research-job storage.

For local development:

1. Start your PostgreSQL server.
2. Create the required database.
3. Configure the database connection using the environment variable expected by your backend.
4. Ensure the required database tables are initialized.
5. Verify the connection before submitting research requests.

### 5. Docker Setup

Docker Compose can be used to build and run the application services together.

Configure the required environment variables in the root `.env` file and the backend `.env` file as appropriate for your Compose configuration.

From the project root, run:

```powershell
docker compose config
```

Build and start the application:

```powershell
docker compose up --build
```

To run containers in the background:

```powershell
docker compose up --build -d
```

To stop the application:

```powershell
docker compose down
```

Check `docker-compose.yml` for the actual service names, ports, database configuration, and environment variables.

**Note:** The Docker Compose configuration uses a PostgreSQL container, whereas local development can use a separately installed PostgreSQL server. These are separate database environments.

## API Documentation

The frontend communicates with the FastAPI backend through REST APIs.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/research` | Submit company research |
| GET | `/api/v1/research/history` | Retrieve research history |
| GET | `/api/v1/research/{research_id}` | Retrieve research status |
| GET | `/api/v1/research/{research_id}/report` | Retrieve the final report |

For detailed request formats, response examples, and error handling, see [API Documentation](docs/api_documentation.md).

## Documentation

| Document | Description |
|---|---|
| [Architecture Documentation](docs/architecture.md) | System architecture, agent workflow, database design, and deployment |
| [API Documentation](docs/api_documentation.md) | API endpoints, HTTP methods, request and response formats, and errors |

## Final Research Report

The consolidated investment research report is designed to include:

- Executive summary
- Overall investment outlook
- Confidence and risk assessment
- Positive and negative factors
- Short-, medium-, and long-term outlook
- Monitoring points
- Research limitations
- Final investment analysis

## Security Considerations

- Store API keys and credentials in environment variables.
- Never commit `.env` files containing secrets.
- Exclude virtual environments, `node_modules`, caches, and generated files using `.gitignore`.
- Validate incoming API requests and AI-generated reports.
- Verify financial claims against reliable sources before relying on them.

## Future Improvements

Potential enhancements include:

- Real-time research progress updates.
- Background execution for long-running research jobs.
- Source citations and automated fact verification.
- Agent execution monitoring and evaluation.
- User authentication and personalized research history.
- Financial data caching and performance optimization.
- Automated testing and CI/CD deployment.

## Disclaimer

FinCrew AI is an experimental AI-powered financial research platform. Its generated outputs may contain inaccuracies, incomplete information, or outdated financial data.

This application is intended for educational and research purposes only. It does not provide personalized financial advice or guarantee investment performance. Always conduct independent research before making investment decisions.

---


