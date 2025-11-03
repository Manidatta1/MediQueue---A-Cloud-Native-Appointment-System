docker-compose down -v  


docker rm -f rabbitmq

docker-compose up --build

http://localhost:8000/docs



Frontend:

npm create vite@latest frontend --template react

Adding Dependencies

npm install react-router-dom

curl -X POST "http://localhost:8001/register" \
-H "Content-Type: application/json" \
-d '{
  "email": "dr.john@example.com",
  "password": "john123",
  "role": "doctor",
  "profile": {
    "name": "Dr. John Doe",
    "specialization": "Cardiology"
  }
}'



curl -X POST "http://localhost:8000/logout" \
 -H "accept: application/json" \
 -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1Iiwicm9sZSI6ImRvY3RvciIsImV4cCI6MTc2MTk3MDE2M30.2lY8anbg7iiKsPaVjRvnmJ24mY4SPl_Vc6h6nRFKxXE"


curl -X PUT "http://localhost:8000/doctor/slots/update" \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
 -d '["10:00", "10:30"]'


Patient Test:

curl -X POST "http://localhost:8001/register" \
-H "Content-Type: application/json" \
-d '{
  "email": "emma@example.com",
  "password": "emma123",
  "role": "patient",
  "profile": {
    "name": "Emma Watson",
    "phone": "555-6789"
  }
}'


curl -X POST "http://localhost:8001/login" \
-H "Content-Type: application/json" \
-d '{
  "email": "emma@example.com",
  "password": "emma123"
}'

curl -s -X POST "http://localhost:8000/book?doctor_id=1&patient_id=1&time=2025-11-01T09:00:00" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6InBhdGllbnQiLCJleHAiOjE3NjE5NzczODN9.XCUaURZoFxzplqPowD9djn_BVQZVlepHQfeO7M8T9Hk"



GKE:

In GCP Console:

Go to: https://console.cloud.google.com/projectcreate

Project name: healthcare-platform

Project ID: (copy this — you’ll use it in GitHub Secrets as GCP_PROJECT_ID)

Enable Billing (required)

Once created, click “Activate Cloud Shell” (top right) — we’ll run all next commands there.

gcloud services enable \
  container.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  iam.googleapis.com


gcloud container clusters create healthcare-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-standard-2


gcloud artifacts repositories create healthcare-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Container images for healthcare platform"


gcloud iam service-accounts create github-deployer \
  --description="Deploys from GitHub Actions to GKE" \
  --display-name="GitHub Actions Deployer"


gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member="serviceAccount:github-deployer@<PROJECT_ID>.iam.gserviceaccount.com" \
  --role="roles/container.admin" \
  --role="roles/artifactregistry.writer"


gcloud iam service-accounts keys create key.json \
  --iam-account=github-deployer@<PROJECT_ID>.iam.gserviceaccount.com


gcloud projects add-iam-policy-binding 	healthcare-platform-477020 \
  --member="serviceAccount:github-deployer@healthcare-platform-477020.iam.gserviceaccount.com" \
  --role="roles/container.admin"

gcloud projects add-iam-policy-binding 	healthcare-platform-477020 \
  --member="serviceAccount:github-deployer@healthcare-platform-477020.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding 	healthcare-platform-477020 \
  --member="serviceAccount:github-deployer@healthcare-platform-477020.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding 	healthcare-platform-477020 \
  --member="serviceAccount:github-deployer@healthcare-platform-477020.iam.gserviceaccount.com" \
  --role="roles/viewer"

gcloud projects get-iam-policy healthcare-platform-477020 \
  --flatten="bindings[].members" \
  --filter="bindings.members:github-deployer@healthcare-platform-477020.iam.gserviceaccount.com" \
  --format="table(bindings.role)"
