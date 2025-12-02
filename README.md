# MediQueue – A Cloud-Native Healthcare Appointment System

A microservices-based healthcare platform where:

- Patients can register, log in, view doctors, and book appointments  
- Doctors can log in and manage their available slots  
- Background workers handle asynchronous appointment events  
- Everything is containerized with Docker and orchestrated on **Google Kubernetes Engine (GKE)**  
- CI/CD uses **GitHub Actions + Artifact Registry + Helm**

---

## 👥 Team

- **Manidatta Anumandla**  
- **Pramod Kumar Ajmera**

---

## 🧩 Architecture Overview

**Microservices**

- **Frontend:** React + Vite + Tailwind (patient/doctor UI)
- **Backend (app_service):** FastAPI – appointments, doctors, patients, slot management
- **Auth Service (authentication_service):** FastAPI – JWT auth, login, registration
- **Worker:** Python service consuming RabbitMQ events (appointment created/cancelled)
- **Airflow:** Runs scheduled DAGs (e.g., daily doctor slot reset)

**Infrastructure**

- **PostgreSQL (Bitnami chart):** Main relational DB
- **Redis (Bitnami chart):** Cache + distributed locking for slot booking
- **RabbitMQ (Bitnami chart):** Message broker for async workflows
- **Kubernetes / GKE:** Orchestration + scaling
- **Google Artifact Registry:** Docker image registry
- **GitHub Actions:** CI/CD to build, push, and deploy

---

## 📂 Repository Structure

```text
.
├── .github/workflows/        # GitHub Actions pipeline (deploy.yaml)
├── airflow/                  # Airflow Dockerfile + DAGs (e.g., reset_doctor_slots.py)
├── app_service/              # Main FastAPI backend
├── authentication_service/   # FastAPI auth microservice
├── frontend/                 # React + Vite + Tailwind SPA
├── healthcare-chart/         # Helm chart for app deployment
├── docker-compose.yml        # Local development stack
└── README.md


## 🧩 Tech Stack Overview

### 🎨 Frontend  
- **React**  
- **Vite**  
- **Tailwind CSS**

### 🧠 Backend / Authentication  
- **FastAPI (Python)**

### 📬 Async Processing / Messaging  
- **RabbitMQ**

### ⚡ Cache / Distributed Locking  
- **Redis**

### 🗄️ Database  
- **PostgreSQL**

### ⏱️ Workflow Orchestration / Scheduler  
- **Apache Airflow**

### ☸️ Container Orchestration  
- **Kubernetes (GKE)**

### 📦 Containerization  
- **Docker**

### 🚀 CI/CD Pipeline  
- **GitHub Actions**  
- **Google Artifact Registry**

### ☁️ Cloud Platform  
- **Google Cloud Platform (GCP)**
