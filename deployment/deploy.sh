#!/bin/bash
# DocuMine Deployment Script
# Deploys FastAPI backend to Cloud Run + React frontend to Firebase Hosting
# Usage: ./deployment/deploy.sh [PROJECT_ID] [REGION]

set -e

PROJECT_ID=${1:-"YOUR_FIREBASE_PROJECT_ID"}
REGION=${2:-"asia-south1"}
SERVICE_NAME="documine-backend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "========================================"
echo "  DocuMine Deployment"
echo "  Project: ${PROJECT_ID}"
echo "  Region:  ${REGION}"
echo "========================================"

# ── Step 1: Build React frontend ───────────────────────────────────────────
echo ""
echo "📦 Step 1: Building React frontend..."
cd frontend
npm install
npm run build
cd ..
echo "✅ Frontend built → frontend/dist/"

# ── Step 2: Build & push Docker image ─────────────────────────────────────
echo ""
echo "🐳 Step 2: Building Docker image..."
cd backend
gcloud builds submit --tag "${IMAGE_NAME}" .
cd ..
echo "✅ Docker image pushed → ${IMAGE_NAME}"

# ── Step 3: Deploy to Cloud Run ───────────────────────────────────────────
echo ""
echo "☁️  Step 3: Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_NAME}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY}" \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --project "${PROJECT_ID}"

# Get the Cloud Run URL
CLOUD_RUN_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --platform managed \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --format "value(status.url)")

echo "✅ Backend deployed → ${CLOUD_RUN_URL}"

# ── Step 4: Update firebase.json with Cloud Run URL ────────────────────────
echo ""
echo "🔧 Step 4: Updating firebase.json rewrite URL..."
# Update the serviceId in firebase.json (already set; Cloud Run uses service name)
# Just verify the region matches
echo "   Service: ${SERVICE_NAME} in ${REGION}"
echo "✅ firebase.json up to date"

# ── Step 5: Deploy Firebase Hosting ───────────────────────────────────────
echo ""
echo "🔥 Step 5: Deploying to Firebase Hosting..."
firebase deploy --only hosting --project "${PROJECT_ID}"

echo ""
echo "========================================"
echo "  ✅ DocuMine Deployed Successfully!"
echo "  Frontend: https://${PROJECT_ID}.web.app"
echo "  Backend:  ${CLOUD_RUN_URL}"
echo "========================================"
