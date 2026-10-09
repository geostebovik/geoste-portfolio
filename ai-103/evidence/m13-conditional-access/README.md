# M13 evidence: Conditional Access policies (exported 2026-10-09)

Written by Claude, 2026-10-09. Gerard ran the export and the ID checks.

**What this is:** the five Conditional Access policies in the `letter7`
tenant, exported read-only from Microsoft Graph after all six tests (T1-T6)
passed with CA001 On. This is decision C8 in
`../../phase2-conditional-access-spec-draft.md`; the test results are in that
file's "Progress, 2026-10-09".

## Files

| File | What it is |
|---|---|
| `all-policies-raw.json` | The Graph response exactly as returned (`az rest`, see below) |
| `CA001-IIPResults-Viewers-RequireAuthStrength.json` | The app policy: the results page needs phishing-resistant MFA |
| `CA900-Baseline-AllUsers-BlockLegacyAuth.json` | Baseline: block legacy authentication |
| `CA901-Baseline-AllUsers-MFA-AzureMgmt.json` | Baseline: MFA for Azure management |
| `CA902-Baseline-Admins-MFA.json` | Baseline: MFA for 14 admin roles |
| `CA903-Baseline-AllUsers-MFA.json` | Baseline: MFA for all users |

The five per-policy files are the raw response split one policy per file
(Claude, unchanged content, pretty-printed).

## How it was exported

```powershell
az rest --method GET `
  --url "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies" `
  --output-file "<this folder>\all-policies-raw.json"
```

Read-only. Run as `djeemunee` on 2026-10-09, about 11:00 Phoenix.

## The IDs in the policies

The export names users, groups and apps only by ID. Confirmed by name on
2026-10-09 with `az ad user show`, `az ad group show` and `az ad sp show`:

| ID | Is | Where |
|---|---|---|
| `6fc71916-d22a-477b-b3df-c8e6e4956a48` | `bg-admin-01@letter7.onmicrosoft.com` (break-glass) | excluded from all five |
| `8a926b21-65c2-4377-a690-3701dd22da15` | group **IIP Results Viewers (dev)** | CA001's users |
| `16565c24-5afd-4581-8430-c615ded0291a` | app **IIP Results (dev)** | CA001's target |
| `797f4846-ba00-4fd7-ba43-dac1f8f63013` | **Azure Resource Manager** (Microsoft's app ID) | CA901's target |
| `d29b2b05-8046-44ba-8758-1e26182fcf32` | directory role **Directory Synchronization Accounts** | excluded from CA903 (from the template; no directory sync here) |

## What the export shows

- All five are **On** (`"state": "enabled"`).
- CA001: grant = authentication strength **Phishing-resistant MFA**; session =
  sign-in frequency **8 hours**; no persistent-browser control (C5, amended
  2026-10-08).
- CA001 was last modified 2026-10-08 20:41Z (13:41 Phoenix), when it was
  switched On.

These policies are deleted in C9, before the Entra ID P2 trial ends
(2026-11-06). After that, this folder is the only record of them.
