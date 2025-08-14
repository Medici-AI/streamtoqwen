#!/usr/bin/env bash
set -euo pipefail

: "${ACR_NAME:?Set ACR_NAME}"
: "${RG_NAME:?Set RG_NAME}"
: "${KV_NAME:?Set KV_NAME}"

IMG="${ACR_NAME}.azurecr.io/streamllm:$(git rev-parse --short HEAD)"

# Build remotely in ACR to avoid local Docker
az acr build -r "$ACR_NAME" -t "$IMG" .

# Get secrets from Key Vault and create/update k8s secret
OPENAI=$(az keyvault secret show --vault-name "$KV_NAME" -n OPENAI--API--KEY --query value -o tsv)
PINECONE=$(az keyvault secret show --vault-name "$KV_NAME" -n PINECONE--API--KEY --query value -o tsv)
SB=$(az keyvault secret show --vault-name "$KV_NAME" -n AZURE--SERVICE--BUS--CONNECTION --query value -o tsv)
COSMOS=$(az keyvault secret show --vault-name "$KV_NAME" -n AZURE--COSMOS--CONNECTION --query value -o tsv)

kubectl create namespace app-dev --dry-run=client -o yaml | kubectl apply -f -
kubectl -n app-dev delete secret streamllm-secrets --ignore-not-found
kubectl -n app-dev create secret generic streamllm-secrets \
  --from-literal=OPENAI--API--KEY="$OPENAI" \
  --from-literal=PINECONE--API--KEY="$PINECONE" \
  --from-literal=AZURE--SERVICE--BUS--CONNECTION="$SB" \
  --from-literal=AZURE--COSMOS--CONNECTION="$COSMOS"

# Deploy with helm
helm upgrade --install streamllm deploy/helm \
  --namespace app-dev \
  --set image.repository=${ACR_NAME}.azurecr.io/streamllm \
  --set image.tag=$(git rev-parse --short HEAD) \
  -f deploy/helm/values-dev.yaml

echo "Deployed: $IMG to namespace app-dev"

