# IIP CLI Runbook

Quick-reference for commands used repeatedly on the IIP/AI-103 project. Goal:
look here instead of re-deriving these each time, until they're memorized.
Full debugging history and *why* behind each stays in MASTER-REFERENCE
Section 4.12 — this file is just the commands.

Resource names assumed throughout: RG `rg-iip-dev-wus-01`, Foundry account
`aif-dev-wus-01`, storage account `stiipdevwus01`. Update if these change.

---

## Get the Foundry endpoint

```bash
az cognitiveservices account show \
  --name aif-dev-wus-01 \
  --resource-group rg-iip-dev-wus-01 \
  --query properties.endpoint -o tsv
```

Store it in a variable before using it in other commands: `ENDPOINT=$(...)`.
Check the trailing slash before concatenating a path onto it.

## Get a Foundry key

```bash
az cognitiveservices account keys list \
  --name aif-dev-wus-01 \
  --resource-group rg-iip-dev-wus-01 \
  --query key1 -o tsv
```

Swap `key1` for `key2` as needed. Store in a variable (`KEY=$(...)`) —
never paste the actual value into chat.

## Rotate a Foundry key

```bash
az cognitiveservices account keys regenerate \
  --key-name Key1 \
  --resource-group rg-iip-dev-wus-01 \
  -n aif-dev-wus-01
```

Swap `Key1`/`Key2`. **If it's unclear which key actually leaked, rotate
both** — guessing wrong leaves the real exposure live.

## List blob containers / blobs

```bash
az storage container list --account-name stiipdevwus01 --auth-mode login -o table
az storage blob list --account-name stiipdevwus01 --container-name <container> --auth-mode login -o table
```

## Generate a read-only SAS URL for a blob

```bash
STORAGE_KEY=$(az storage account keys list --account-name stiipdevwus01 --resource-group rg-iip-dev-wus-01 --query "[0].value" -o tsv)

az storage blob generate-sas \
  --account-name stiipdevwus01 \
  --account-key "$STORAGE_KEY" \
  --container-name <container> \
  --name <blob> \
  --permissions r \
  --expiry $(date -u -d "1 hour" +%Y-%m-%dT%H:%MZ) \
  --https-only \
  --full-uri \
  -o tsv
```

`--full-uri` returns the complete blob URL with the SAS token appended —
no manual concatenation needed. Blob names are case-sensitive; a SAS
signs whatever name it's given whether the blob exists or not.

Current sample doc: `--container-name docs --name loan-agreement-promissory-note.pdf`
(confirmed via `az storage blob list`, July 27, 2026).

## Submit an analyze call

```bash
curl -i -X POST "${ENDPOINT}contentunderstanding/analyzers/iip_loan_agreement_analyzer:analyze?api-version=2025-11-01" \
  -H "Ocp-Apim-Subscription-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"inputs\":[{\"url\": \"$SAS_URL\"}]}"
```

Alternative for a local file not yet in blob storage — base64 `data`
instead of `url` (only one of the two, not both):

```bash
DATA=$(base64 -w 0 /path/to/file.pdf)
curl -i -X POST "${ENDPOINT}contentunderstanding/analyzers/iip_loan_agreement_analyzer:analyze?api-version=2025-11-01" \
  -H "Ocp-Apim-Subscription-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d "{\"inputs\":[{\"data\": \"$DATA\", \"mimeType\": \"application/pdf\"}]}"
```

Returns `202 Accepted` with an `Operation-Location` header — the result is
not in this response.

## Poll for the analyze result

Copy the full `Operation-Location` value from the POST response headers,
then:

```bash
OPLOC="<paste the full Operation-Location header value here>"
curl -i -X GET "$OPLOC" -H "Ocp-Apim-Subscription-Key: $KEY"
```

Poll every 1–2 seconds until `"status": "Succeeded"`. Don't reconstruct
the URL by hand from `{request-id}` — copy the real header value.

## Check TPM/RPM quota

```bash
az cognitiveservices usage list \
  --name aif-dev-wus-01 \
  --resource-group rg-iip-dev-wus-01 \
  --query "[].{Model:name.value, Current:currentValue, Limit:limit, Unit:unit}" \
  -o table
```

Plain `-o table` without the explicit `--query` silently drops the model
name column (nested object field) — always use the query above.

## Check for soft-deleted Cognitive Services accounts

```bash
az cognitiveservices account list-deleted
```

Found the source of an unexpected quota hold once already (a purged RG's
account surviving as soft-deleted, still counted against quota). Worth
running after any `az group delete` that included a Cognitive
Services/Foundry account.

---

*Log new entries here as they come up. First real entries above date to
July 24, 2026, drawn from that session's key-rotation and analyze
verification work.*

## July 27, 2026 (midday)

First real end-to-end run of `m3_analyze.py` (the Python wrapper around
the submit/poll commands above) succeeded against the sample doc, using
the SAS/blob values now recorded above. Python-specific debugging notes
for that script live in MASTER-REFERENCE Section 4.12, not here — this
file stays commands-only.
