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


6. The Execution Worker (app/worker/tasks.py)
Contains the background functions executed by Celery. The worker pulls a job assignment from Redis, calls the data logic in etl_service.py, transfers the output to ai_service.py, updates the database tables with the final metrics, and marks the job status as SUCCESS.
