#!/bin/bash
# =============================================================================
# ostebovik.net Portfolio Site — Bootstrap
# Purpose: Creates the production resource group and initiates Bicep deployment
# This script runs ONCE. All subsequent changes go through Bicep.
# =============================================================================
# Run from Azure Portal Cloud Shell (Bash)
# Fix line endings if uploaded from Windows: sed -i 's/\r//' bootstrap.sh
# =============================================================================

set -e  # exit on first error

# --- Configuration -----------------------------------------------------------
RG="rg-geoste-prod-wus3-01"
LOC="westus3"
DEPLOYMENT_NAME="portfolio-$(date +%Y%m%d-%H%M)"
KV_NAME="kv-geoste-prod-wus3-01"
ST_NAME="stgeostewus301"

echo "=============================================="
echo " ostebovik.net Portfolio — Bootstrap"
echo " RG: $RG"
echo " Location: $LOC"
echo " Deployment: $DEPLOYMENT_NAME"
echo "=============================================="

# --- Step 1: Create Resource Group -------------------------------------------
# The RG is the one thing Bicep cannot create for itself when doing a
# group-scoped deployment. Bootstrap owns this single responsibility.
echo ""
echo "==> Creating resource group..."
az group create \
  --name $RG \
  --location $LOC \
  --tags \
    owner=geoste \
    env=prod \
    region=wus3 \
    managed-by=bicep \
    project=portfolio

echo "    Resource group ready."

# --- Preflight: check globally unique resource names ----------------------
echo ""
echo "==> Checking globally unique resource names..."

KV_CHECK=$(az keyvault check-name --name $KV_NAME --query nameAvailable -o tsv)
ST_CHECK=$(az storage account check-name --name $ST_NAME --query nameAvailable -o tsv)

if [[ "$KV_CHECK" != "true" ]]; then
  echo "ERROR: Key Vault name '$KV_NAME' is not available. Update prod.bicepparam."
  exit 1
fi

if [[ "$ST_CHECK" != "true" ]]; then
  echo "ERROR: Storage account name '$ST_NAME' is not available. Update prod.bicepparam."
  exit 1
fi

echo "    All names available."

# --- Step 2: What-if (dry run) -----------------------------------------------
# Always run what-if before deploying. Review the output before proceeding.
# This shows exactly what Bicep will create/modify/delete.
echo ""
echo "==> Running what-if (dry run)..."
az deployment group create \
  --resource-group $RG \
  --name "$DEPLOYMENT_NAME-whatif" \
  --template-file main.bicep \
  --parameters prod.bicepparam \
  --what-if

# --- Step 3: Confirm before deploying ----------------------------------------
echo ""
read -p "==> What-if complete. Proceed with deployment? (yes/no): " CONFIRM
if [[ "$CONFIRM" != "yes" ]]; then
  echo "    Deployment cancelled."
  exit 0
fi

# --- Step 4: Deploy -----------------------------------------------------------
echo ""
echo "==> Deploying infrastructure..."
az deployment group create \
  --resource-group $RG \
  --name "$DEPLOYMENT_NAME" \
  --template-file main.bicep \
  --parameters prod.bicepparam \
  --verbose

echo ""
echo "=============================================="
echo " Deployment complete."
echo " Next steps:"
echo " 1. Verify resources in portal"
echo " 2. Configure DNS CNAME at registrar"
echo " 3. Upload content to storage account"
echo " 4. Verify ostebovik.net resolves correctly"
echo "=============================================="
