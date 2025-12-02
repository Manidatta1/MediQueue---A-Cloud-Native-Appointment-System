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

![System Architecture](https://github.com/Manidatta1/MediQueue---A-Cloud-Native-Appointment-System/blob/main/Architecture.png)


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


## 🚀 GCP Setup 

Run these commands **once** in your GCP project before using the GitHub Actions workflow.

---

### ✅ 1. Enable Required APIs

gcloud services enable \
  container.googleapis.com \
  artifactregistry.googleapis.com \
  compute.googleapis.com

### ☸️ 2. Create a GKE Cluster

gcloud container clusters create healthcare-cluster \
  --zone=us-central1-a \
  --num-nodes=2 \
  --machine-type=e2-medium \
  --enable-autoupgrade \
  --enable-autorepair

### 🗄️ 3. Create an Artifact Registry Repository

gcloud artifacts repositories create healthcare-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Healthcare system Docker images"

## 📌 Notes

- Use the **same GCP project** for both the **GKE cluster** and the **Artifact Registry repository**.  
- `healthcare-repo` is the Docker repository referenced in the **GitHub Actions** workflow.

---

## 🔑 GitHub Secrets Required

Add these secrets in your GitHub repository:

| Secret Name       | Description |
|------------------|-------------|
| **GCP_PROJECT_ID** | Your GCP project ID |
| **ARTIFACT_REPO** | Example: `healthcare-repo` |
| **GCP_SA_KEY**     | JSON key of a GCP service account |

---

## 🛡️ Required IAM Roles for the Service Account

Assign the following roles:

- `roles/storage.admin`  
- `roles/artifactregistry.writer`  
- `roles/container.admin`

These roles provide:

- Push/pull access to Artifact Registry  
- Deployment permissions for GKE  
- Access to storage resources (if needed)

---

## 🚀 CI/CD: Build & Deploy to GKE (GitHub Actions)

The GitHub Actions workflow performs the following steps automatically:

### 🏗️ Builds Docker images for:
- Backend  
- Auth service  
- Frontend  
- Airflow  

### 📤 Pushes images to:
- **Google Artifact Registry**

### 📦 Installs core services via Helm:
- PostgreSQL  
- RabbitMQ  
- Redis  

### ☸️ Deploys the application using:
- **`healthcare-chart` Helm chart**  
- Deployment into your **GKE cluster**

---

## 🌐 Accessing the Application on GKE

After deploying the application using Helm, retrieve the external IP of the LoadBalancer service:

kubectl get svc -n healthcare

## 🔎 Look for the Service Exposed as LoadBalancer

Typically, this will be your **frontend gateway** or **nginx** service.

When you run:

kubectl get svc -n healthcare

You will see an external IP similar to:

EXTERNAL-IP 34.xx.xx.xx

---

## 🌍 Application URLs

### Main Application

http://EXTERNAL-IP:80

### Airflow Web UI 

http://EXTERNAL-IP:8080






