# M10 prep — the keyless migration, surveyed before starting

> ## SURVEYED 2026-09-21 · TESTED 2026-09-22 — read this box before the page
>
> The survey below was written before anything was run. Four probes then tested
> its assumptions. **It was right about the shape of the work and wrong about
> three specific things**, and it is kept unedited beneath this box so the
> difference between a survey and a measurement stays visible.
>
> | Survey said | Measured |
> |---|---|
> | Group C is a **PROBABLE BLOCKER**; free tier may force a paid recreate | **Wrong.** Keyless works on free. Inbound Entra auth is fine; the "billable tier" line is about *outbound* managed identity. No recreate, no bill. |
> | The tracked scope is **ten** scripts, not eleven | **Still short by one.** `m6_probe.py` is gitignored on the same `.gitignore` line as `tester*.py`. **Nine.** |
> | Group A is nine uniform `azure_ad_token_provider=` edits | **Seven.** `m6_evaluate.py` and `m7_evaluator_tool.py` build an `AzureOpenAIModelConfiguration` — a TypedDict, not a client. It has no such parameter. The fix is to **omit `api_key`**. Passing `credential=` is accepted by the TypedDict and then rejected by the SDK's validator. |
> | Group B (Vision Read) is the real unknown | **Right to test it first, wrong about the stakes.** Foundry User covers it — because its dataAction is the wildcard `Microsoft.CognitiveServices/*`. And the "expected fix" this page implies, Cognitive Services User, is a **legacy** role superseded by Foundry User. |
>
> **The decisive-test design also had a flaw.** The Group C test as written
> ("if it 401s or 403s, the free tier does not support keyless") could not
> distinguish a tier limit from a missing role — and no Search role was
> assigned at the time, so it would have returned 403 and pointed M10 at a
> one-way door. Search Index Data Reader was assigned first, which is what made
> the result mean anything.
>
> Probes: `probe_keyless_vision.py`, `probe_keyless_search.py`,
> `probe_keyless_eval.py`, `probe_keyless_v1_scope.py`,
> `probe_keyless_smoke.py`. Migration committed at `aa96bea`.

**Written 2026-09-21** at the end of the M8/M9 session, so M10 opens with the
migration rather than the survey. Claude surveyed the scripts and the docs;
nothing here has been changed or run.

## The headline: this is not ten script migrations

Every one of the ten tracked key-based scripts gets its Foundry key from **one
function**: `get_subscription_key()` in `m3_analyze.py`. Nine of them then pass
it the same way, as `AzureOpenAI(api_key=...)`. The Search key has its own single
source: `get_search_admin_key()` in `m5_index.py`, reused by `m5_retrieve.py`.

So M10 is **two helper functions and three client-construction patterns**, not
ten independent rewrites. That is a much smaller change than the plan's "eleven
scripts move to Entra ID" implies, and it should be sized accordingly.

| Group | Pattern | Scripts | Count |
|---|---|---|---|
| **A** | `AzureOpenAI(api_key=get_subscription_key(...))` | `m5_index`, `m5_retrieve`, `m6_evaluate`, `m6_generate`, `m6_probe`, `m7_cv_audit_tool`, `m7_evaluator_tool`, `m7_vision_test`, `probe_reasoning_params` | 9 call sites |
| **B** | `ImageAnalysisClient(credential=AzureKeyCredential(...))` | `m7_legibility_check` | 1 |
| **C** | `SearchClient` / `SearchIndexClient` with `AzureKeyCredential(admin_key)` | `m5_index`, `m5_retrieve` | 2 |

`tester3.py` also reads keys and is excluded: `.gitignore` covers
`ai-103/scripts/tester*.py` as scratch. **The tracked scope is ten, not eleven** —
worth fixing in the plan, because a done-when of "no script reads a key" cannot
be satisfied while it counts a file that is not in the repo.

## Group A — the bulk of it, and the easy part

Replace the key with a bearer-token provider. One new helper in `m3_analyze.py`
beside `get_subscription_key()`, then nine constructor edits from `api_key=key`
to `azure_ad_token_provider=<provider>`:

```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

def build_token_provider():
    return get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default",
    )
```

Mechanical, and the role is already in place — M9 assigned Foundry User on the
account to both Gerard and `id-iip-dev-wus-01`.

**Keep `get_subscription_key()` until the acceptance test passes**, then remove
it in its own commit. Deleting it in the same change as the migration removes the
fallback at the moment it is most likely to be needed.

## Group B — this is row 4's VERIFY, and it is the real unknown

`m7_legibility_check.py` calls Vision Read through `ImageAnalysisClient`. Swap
`AzureKeyCredential(key)` for `DefaultAzureCredential()`.

The RBAC model marked this **VERIFY**: does Foundry User actually cover Vision
Read? Nothing has tested it. Microsoft's Foundry RBAC page describes Foundry User
as granting "data actions for a Foundry project", which is not the same statement
as "covers every AI Services modality on the account".

**Test this one first, in isolation, before touching anything else.** It is one
call on one image and it is the single piece of M10 that could require a role
change rather than a code change. Finding that out after migrating nine other
call sites would be the wrong order.

## Group C — PROBABLE BLOCKER, and it needs settling before M10 starts

`srch-iip-dev-wus-01` is on the **free** tier, and the Microsoft Learn pages
disagree about whether keyless auth works there:

- *Enable or disable role-based access control in Azure AI Search* — prerequisites:
  "A search service in any region, on any tier, **including free**."
- *Connect your app to Azure AI Search using identities* — prerequisites:
  "Azure AI Search, any region but it must be a **billable tier (basic or
  higher)**."

One says free is fine for enabling RBAC; the other says keyless client
connections need basic or higher. Both are current. **Neither is a safe
assumption.**

Good news: RBAC is already enabled on the service. The M8 baseline recorded
`authOptions.aadOrApiKey` and `disableLocalAuth: false`, which is the
both-methods-allowed state, so nothing needs switching on to try this.

**The decisive test, and it is cheap** — run before writing any Group C code:

```powershell
az account get-access-token --scope https://search.azure.com/.default --query accessToken -o tsv
```

then one `SearchClient` query against the existing index using
`DefaultAzureCredential()`. If it returns results, the free tier supports keyless
and Group C is a code change. If it 401s or 403s, the free tier does not, and
Group C is blocked behind a **service recreate on a paid tier** — a one-way door
with a recurring bill, which is a decision for Gerard and not a migration step.

**Two roles are also missing either way.** The RBAC model deliberately assigns
nothing on Search ("AI Search is not used by the Phase 2 app"). But M10's scope
includes the M5 scripts, and keyless Search needs, per Microsoft Learn:
- **Search Service Contributor** and **Search Index Data Contributor** for
  `m5_index.py`, which creates the index and uploads documents;
- **Search Index Data Reader** for `m5_retrieve.py`, which queries.

So M10 either extends the RBAC model with a Search section, or M10's done-when
explicitly excludes the M5 Search path and those two scripts keep their key. That
is a scope decision, not an implementation detail.

## Suggested order

1. **Group B alone.** One image, one call. Settles row 4's VERIFY and tells us
   whether Foundry User is sufficient before anything else changes.
2. **The Group C tier test.** One token request and one query. Settles whether
   Group C is in scope at all.
3. **Decide Group C's scope** with both answers in hand.
4. **Group A**, all nine call sites, in one change.
5. **Re-run the M7 acceptance test** (~95 min). The orchestrator's own auth path
   is already keyless, so this tests the migrated tools rather than the agent.
6. **Only then** remove `get_subscription_key()`, and only then consider
   `disableLocalAuth` on Foundry and shared-key access on storage — the model's
   build-time rule, and the order that keeps the key-based scripts working
   throughout.

## One thing not to assume

The Foundry **project** managed identity only received its Foundry User role on
2026-09-21, in M9. Before that the account had no direct role assignments at all.
So no prior successful run proves the keyless path works — the account keys were
concealing a missing role. Treat every keyless call in M10 as untested, including
ones that look like they have been working for months.
