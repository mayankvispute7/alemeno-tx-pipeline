# AIONYX Engine: Financial ETL & Anomaly Detection Pipeline

The **AIONYX Engine** is a production-grade, containerized Financial ETL (Extract, Transform, Load) and Anomaly Detection pipeline. It automates the ingestion of raw financial transaction datasets, performs programmatic cleaning, executes statistical anomaly identification, and leverages Large Language Models via the native Google GenAI SDK to categorize transactions and generate strategic risk narratives.

---

## 🚀 Key Features
* **Asynchronous Task Architecture:** Offloads heavy processing workloads to Celery workers backed by a Redis message broker, maintaining a highly responsive user experience.
* **Dual-Currency Streamlining:** Dynamically handles mixed multi-currency transaction logs (INR/USD), calculating total exposure and tracking exchange rates natively.
* **Statistical Anomaly Core:** Detects operational and security anomalies based on historical deviation thresholds and transactional flags.
* **GenAI Intelligence Suite:** Integrated with `gemini-2.5-flash` via the native Google GenAI SDK for zero-shot transaction categorization and context-aware financial risk summaries.
* **Production Deployment Ready:** Fully containerized utilizing Docker and Docker Compose for seamless environment reproducibility across staging and production.
* **Lit Cyber-Noir UI Dashboard:** Implements a modern glassmorphic presentation layer featuring real-time state hydration, tabular spend drill-downs, and explicit visual highlighting for detected anomalies.

---

## 🛠️ Tech Stack & System Components
* **Backend Framework:** FastAPI (Asynchronous Python Web Server)
* **Task Queuing & Processing:** Celery + Redis
* **Data Persistence Engine:** PostgreSQL 15
* **AI Engine:** Google GenAI SDK (`gemini-2.5-flash`)
* **Environment Virtualization:** Docker & Docker Compose
* **Frontend Matrix:** Semantic HTML5, CSS3 Custom Properties (Cyber-Noir Matrix Theme), Asynchronous Vanilla JavaScript (Fetch API Engine)

---

## 📂 Project Architecture & File Meanings

```text
alemeno-tx-pipeline/
├── app/
│   ├── core/
│   │   ├── config.py          # Centralized configuration management and env validation
│   │   ├── database.py        # SQLAlchemy engine orchestration and session pooling
│   │   └── celery_app.py      # Celery instance declaration and broker provisioning
│   ├── models/
│   │   └── transaction.py     # Relational database schemas for Job metadata & Transactions
│   ├── services/
│   │   ├── etl_service.py     # Heavy lifting: CSV parsing, math cleaning, anomaly logic
│   │   └── ai_service.py      # Upgraded Google GenAI SDK client mapping for classification & analysis
│   ├── worker/
│   │   └── tasks.py           # Atomic worker tasks consumed by the background Celery cluster
│   ├── static/
│   │   └── index.html         # Cyber-Noir UI application matrix layout
│   └── main.py                # FastAPI server kernel declaration and route mounting
├── Dockerfile                 # Multi-stage blueprint for uniform container environment setup
├── docker-compose.yml         # Multi-container multi-network orchestration suite
├── requirements.txt           # Explicit locked dependencies manifest
└── .env                       # Local cryptographic and API credential secrets storage

⚡ Quick Start & Deployment Guide
Prerequisites
Docker Desktop installed and running on your local machine.

A valid Google Gemini API Key.

Execution Steps
Clone and Navigate to the Repository:

Bash
cd alemeno-tx-pipeline
Configure Environment Secrets:
Create a .env file in the root directory and append your valid credentials:

Code snippet
GEMINI_API_KEY=your_actual_gemini_api_key_here
DATABASE_URL=postgresql://user:password@db:5432/tx_pipeline
REDIS_URL=redis://redis:6379/0
Spin Up the Infrastructure Stack:
Force a clean compilation to clear any Docker daemon cache and bring up the container network:

Bash
docker compose down
docker compose build --no-cache
docker compose up -d
Access the Interface:
Open your browser and navigate to http://127.0.0.1:8000/. Upload your transaction CSV and monitor the runtime logs directly in your terminal using:

Bash
docker logs tx_worker -f

---

## 🧠 Simple Project Summary (For Pitching & Explaining)

Imagine a financial analyst at a company who receives a messy Excel spreadsheet every week containing thousands of card expenses. Some numbers use dollar signs, some are in rupees, some rows have broken text, and some purchases might be fraudulent or way too expensive. Reading and sorting this manually takes hours.

**AIONYX Engine** solves this. The analyst uploads the raw file to our web interface. The system immediately starts fixing the broken text, standardizes all currencies, and mathematical checks look out for anomalies or weird spending patterns. Then, the clean data goes directly to an integrated Google AI model, which reads the vendor names, accurately categorizes what the purchase was for (like tagging an "Uber" charge as "Transport"), and drafts a professional executive risk summary automatically.

---

## 🛠️ Complete Technical Architecture Deep Dive

Here is how the components talk to each other under the hood:

```text
[ Browser UI ] ---> ( FastAPI ) ---> [ Redis Queue ] ---> [ Celery Worker ]
                        |                                       |
                        v                                       v
                [ PostgreSQL DB ]                       [ Google Gemini API ]
1. The Entry Point (app/main.py)
This file is the nervous system of the web API. It initializes FastAPI and handles the HTTP requests. When the user hits "Upload", it triggers an async function that writes an initial tracking row into PostgreSQL with a status of PENDING and pushes the workload off to the background queues.

2. The Configuration Center (app/core/)
config.py: Uses Pydantic to read your .env variables safely. If an API key or database string is missing, it raises an early error instead of letting the application crash later.

database.py: Sets up SQLAlchemy to open connections to your PostgreSQL container using a production connection pool.

celery_app.py: Configures Celery to use Redis as its messaging mailbox, allowing the application to distribute heavy computation away from the main web server.

3. The Data Layout (app/models/transaction.py)
Defines the structure of our SQL tables. It sets up two primary tables:

Job: Tracks metadata (e.g., job ID, processing status, final AI summary text).

Transaction: Stores individual lines from the CSV post-cleaning (amount, currency, merchant name, category, and whether it was classified as an anomaly).

4. The Processing Engine (app/services/etl_service.py)
This handles the heavy numerical lifting. It opens files using Python, converts string values into exact floating-point numbers, tracks multi-currency metrics across INR and USD pools, and applies business rules to isolate abnormal spikes or merchant warnings, flagging them before they hit the database.

5. The Intelligent Mind (app/services/ai_service.py)
This acts as our pipeline's direct bridge to the Google GenAI SDK targeting gemini-2.5-flash. It formats the cleaned data into dynamic prompts with strict formatting instructions. It requests raw, structured JSON arrays back from the AI to map transaction categories cleanly and generate a high-quality narrative summary without broken markdown tags.

6. The Execution Worker (app/worker/tasks.py)
Contains the background functions executed by Celery. The worker pulls a job assignment from Redis, calls the data logic in etl_service.py, transfers the output to ai_service.py, updates the database tables with the final metrics, and marks the job status as SUCCESS.