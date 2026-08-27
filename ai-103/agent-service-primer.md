# Foundry Agent Service — Primer (for M7)

**Status:** introductory briefing, written 2026-08-21 ahead of M7's design/build.
Not a build log — `STATUS.md` stays the living tracker. This is the thing to
point back to mid-build: "remember we covered this? here it is."

Sources: [Azure AI Agents client library for Python](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme?view=azure-python),
[Foundry Agent Service overview](https://github.com/MicrosoftDocs/azure-ai-docs/blob/main/articles/foundry/agents/overview.md).

---

## The one thing that matters most: this is NOT the Assistants API

The Assistants API (`client.beta.assistants.create()`, from the `openai` package)
has a **hard retirement date of August 26, 2026** — five days from when this was
written. If a tutorial, course demo, or search result shows that pattern, it's
already obsolete. Foundry Agent Service is a different package (`azure-ai-agents`,
not `openai`), a different client (`AgentsClient`, not the OpenAI client M5/M6
used), and a different import path entirely. This is exactly the kind of "looks
similar, is actually a different SDK shape" trap your own working-style rule
(skip independent guessing on unfamiliar client shapes, treat as reference-lookup
territory) exists for.

## The analogy

Think of an agent the way you'd think of a new employee you're onboarding:

- **Model** = their raw reasoning ability (which of your deployed GPT models they think with)
- **Instructions** = their job description (what they're supposed to do, and what they're not)
- **Tools** = what's on their desk (what they're actually allowed to call/use to get work done)

Put those three together and Foundry calls the result an **agent**. You don't
talk to an agent directly, though — you open a **thread** with it (a conversation
session), post **messages** into that thread, and trigger a **run** (one pass
of the agent actually processing what's in the thread and responding, possibly
by calling one of its tools along the way).

Agent → Thread → Message → Run. Same shape whether it's one exchange or a long
conversation.

## Where this lives relative to what you've already built

M2–M6 used the `openai` package's client pointed at your Foundry deployment
(the "v1 GA pattern" logged in `STATUS.md`) for chat completions and embeddings.
Agent Service is a separate, project-scoped client (`AgentsClient` from
`azure-ai-agents`), pointed at your **project endpoint**
(`aif-dev-wus-01/proj-iip-dev-wus-01`), not the raw account endpoint. Different
package, different client, same underlying Foundry project and model catalog.

```bash
pip install azure-ai-agents
```

```python
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],   # the project endpoint, not the account endpoint
    credential=DefaultAzureCredential(),
)

agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="riverside-content-agent",
    instructions="You are a helpful agent",     # the actual M7 instructions get designed later
)

thread = agents_client.threads.create()

agents_client.messages.create(thread_id=thread.id, role="user", content="...")

run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

for msg in agents_client.messages.list(thread_id=thread.id):
    if msg.text_messages:
        print(f"{msg.role}: {msg.text_messages[-1].text.value}")
```

## Tools — the part that matters most for M7

This is the mechanism by which an agent becomes an *orchestrator* rather than
just a chatbot. You write ordinary Python functions, wrap them as a `FunctionTool`,
and hand them to the agent via a `ToolSet`. With auto function-calling enabled,
the agent decides *when* to call them during a run — you don't call them
yourself in a fixed sequence.

```python
from azure.ai.agents import ToolSet
from azure.ai.agents.tools import FunctionTool

toolset = ToolSet()
toolset.add(FunctionTool(user_functions))       # user_functions = your Python callables
agents_client.enable_auto_function_calls(toolset)

agent = agents_client.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="riverside-content-agent",
    instructions="...",
    toolset=toolset,
)
```

**Decided (2026-08-21):** the M6 evaluator and the CV audit are exposed to
the agent *as tools it decides to call* — genuinely agentic, the agent itself
orchestrates draft → check → decide, via `ToolSet`/`FunctionTool` with auto
function-calling enabled. Chosen deliberately over the simpler fixed-pipeline
alternative (a script calling each step in order), accepting the added
complexity, for closer alignment with AI-103's agentic exam domain and for
career relevance. Logged in `STATUS.md`'s Next action section too.

## The three agent types (context, not a decision point yet)

Foundry Agent Service actually offers three ways to build an agent:

- **Prompt agents** — no-code, configured in the portal. Not the pattern this
  project uses anywhere else.
- **Workflow agents** — multi-agent orchestration with branching logic (preview).
  This is Phase 3 territory from `agent-system-project-plan.md`, not M7.
- **Hosted/code-first agents** — built via the SDK, exactly like every other
  piece of this project (M2–M6 were all SDK-first, not portal-driven). This is
  the one M7 actually uses.

## What's still genuinely open (not covered by this primer, by design)

This primer covers the mechanism, not the M7-specific design. Still to work out
when the actual build conversation happens: the exact instructions text for the
agent, the tool-vs-fixed-pipeline fork above, how the CV audit function itself
gets built (likely a Foundry vision-capable model call, needs its own short
briefing when we get there), and whether an existing GPT-5 deployment already
handles vision input or a new deployment is needed.
