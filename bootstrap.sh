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
RG="rg-ostebovik-prod-wus3-01"
LOC="westus3"
DEPLOYMENT_NAME="portfolio-$(date +%Y%m%d-%H%M)"

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
    owner=ostebovik \
    env=prod \
    region=wus3 \
    managed-by=bicep \
    project=portfolio

echo "    Resource group ready."

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
