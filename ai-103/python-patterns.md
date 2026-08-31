# Python Patterns — IIP/AI-103

**This is a lookup, not a manual.** Check here when a problem *feels* like
one you've hit before, rather than re-deriving it from scratch. Same
living-document convention as `STATUS.md`: edited in place, no dated
copies. Azure/infra-specific gotchas (venv locations, cwd-relative paths,
`az` command quirks) stay in `STATUS.md`'s "Key Lessons" section and
`iip-cli-runbook.md` — this file is for general Python language patterns
only, so the two don't overlap.

---

## Two-pass lookahead pairing

**When it applies:** you need to associate each item in a sequence with
something that depends on the *next* item (or the *previous* one) — e.g.
"this section's content ends where the next section's heading begins."

**Why the obvious single-pass version fails:** a single `for` loop only
has access to the *current* item at each step. If what you need to
compute depends on something you haven't reached yet, no amount of
restructuring the loop body fixes it — the information genuinely doesn't
exist yet at that point in the loop.

**The fix:** split into two passes. First, materialize the full sequence
into a list (`list(re.finditer(...))`, not a live iterator — a live
iterator gets consumed as you read it, so it isn't enough either). Second,
walk that list with `enumerate()`, and reach forward with
`sequence[i + 1]` — guard the last item with a length check, since it has
no "next."

**Where this showed up:** `m5_index.py`'s `chunk_by_section()`, Aug 10 —
needed each section's content to stop exactly where the next section's
heading started.

---

## Stray auto-imports from IntelliSense

**What happens:** VS Code's auto-import quick-fix sees a name used before
it's been locally assigned (a variable about to be defined, or a `for`
loop variable) and, mistaking it for an undefined reference to some
library symbol, offers to import an unrelated module or object that
happens to share the name. Accepting it — sometimes without noticing —
adds a working-but-wrong import.

**Why it's easy to miss:** the import usually doesn't error, since the
module or attribute genuinely exists — so nothing looks broken until
either (a) the bad import happens to be unused, just dead and misleading,
or (b) it collides with something that doesn't actually exist as a
top-level module, raising `ModuleNotFoundError`.

**Real instances this project has hit, three separate times now:**
`from xmlrpc import client` instead of the real `client` variable
(July 29); `from anyio import Path` instead of `pathlib.Path` (Aug 6);
`from pydoc import text` + `import match` instead of local variables
named `text`/`match` (Aug 10).

**Habit worth building:** read every import line before running a script
right after an autocomplete-heavy editing pass — check each one actually
matches what was meant, not just that it resolves.

---

## `**kwargs` silently swallows wrong keyword names

**What happens:** a function that accepts `**kwargs` (like
`azure-ai-evaluation`'s `evaluate()`) doesn't raise `TypeError` on a
misspelled or wrong keyword argument — it absorbs it into `kwargs` and
ignores it. Python only complains about keywords that don't match *any*
parameter and are required positionally; everything else fails silently.

**Real instance:** `m6_evaluate.py` called
`evaluate(input_file=..., output_file=...)` — both wrong (should've been
`data=`, `output_path=`). No error was raised; it would have produced no
output file at all if not caught by checking the actual result rather
than trusting the call succeeded (Aug 5).

**Habit worth building:** for any `**kwargs`-based call, verify the real
keyword names against the actual signature (docs or installed source)
before trusting that "it ran without erroring" means "it did what I
asked."

---

## Structure-specific parsers fail silently, not loudly

**What happens:** a function built around one assumed structure (a
specific regex, a specific delimiter, a specific heading pattern) doesn't
raise an error when that structure isn't present in the input — it just
returns an empty result. Nothing crashes, so it's easy to mistake "got
zero results" for "this document genuinely has none of what I'm looking
for," instead of "my parser doesn't understand this document's shape."

**Why it's easy to miss:** downstream code consuming the (silently empty)
result often has nothing to complain about either — an empty list embeds
zero chunks, uploads zero documents, and the pipeline finishes
"successfully" having done nothing.

**Real instance:** `chunk_by_section()` (`m5_index.py`) is built entirely
around a regex for this document's roman-numeral headings. Run it against
a document that doesn't use that exact heading pattern and `headings`
comes back `[]`, `chunks` comes back `[]`, no error anywhere in the chain
(Aug 10 design discussion — not yet actually hit on this project, since
every document indexed so far has the expected headings).

**Habit worth building:** after any structure-specific parse, sanity-check
the count against what was expected (`assert len(chunks) == 16`, or at
minimum a printed count actually looked at) — don't infer "no structure
present" from "no output" without first checking whether the parser was
even looking for the right structure.

---

## Trusting a copied access chain over checking the real data

**What happens:** code that indexes into external data (a parsed JSON
file, an API response, any structure you didn't define yourself) gets
edited by feel — a line copied from another script "looks redundant" or
"looks wrong," so a key gets added or removed based on how the chain
reads, not on what the actual data contains.

**Why it's easy to miss:** functions like `json.load()` don't validate
structure — they faithfully turn whatever JSON text exists into nested
dicts/lists, matching your assumptions or not. There's no error to catch a
wrong guess at parse time; the parse itself always "succeeds," and only a
downstream `KeyError` (or worse, a silently wrong value that never errors
at all) reveals the mistake.

**Real instance:** `m5_index.py`'s `load_document_markdown()` was
pattern-matched off `m6_generate.py`'s working line,
`json.load(f)["result"]["contents"][0]["markdown"]`, but the `["result"]`
key was dropped as looking unnecessary — reasoning about the shape of the
copied line, not about the real file on disk (which wraps the Content
Understanding result inside a `"result"` key alongside `"status"`/`"id"`,
from the original `poll_result()` response body `m3_analyze.py` saved).
Caught on review, not before running (Aug 11).

**Habit worth building:** before trusting or editing an indexing chain
into data you didn't define, check the real data's shape first — even a
throwaway `python -c "import json; print(json.load(open(path)).keys())"`
— instead of reasoning from how a copied line looks. Applies to any
external structure (JSON files, API responses, parsed documents), not
just this one case.

---

## IntelliSense suggests API shapes from a different SDK generation

**What happens:** editor autocomplete offers a complete, syntactically
plausible code block for a real class or method — it just belongs to an
older (often pre-GA preview) version of the installed package, not the
one actually on disk. This is a different mechanism from "Stray
auto-imports from IntelliSense" above: that entry is about mistaking an
unrelated same-named symbol for a local variable. This one is about a
correctly-named symbol from a correctly-spelled library that simply
doesn't exist in the version installed — the suggestion is stale, not
mismatched.

**Why it's easy to miss:** the suggestion reads as fully coherent, often
more complete-looking than a hand-written stub, and every name in it is a
real thing the library has had at some point. Nothing looks wrong until
it's actually run and hits an `ImportError`/`AttributeError` — or, worse,
until a dropped/renamed keyword gets silently absorbed into a `**kwargs`
catch-all and does nothing (same failure mode as the `**kwargs` entry
below).

**Real instance:** `ensure_index_exists()` (`m5_index.py`, Aug 12) —
IntelliSense suggested `VectorField` and `VectorSearchConfiguration` for
the vector field, with `algorithm_config=HnswAlgorithmConfiguration(metric="cosine")`.
Neither `VectorField` nor `VectorSearchConfiguration` exist in the
installed `azure-search-documents==12.0.0` — confirmed via a direct
import check, not assumed. Traced to the SDK's own changelog: those were
the original November 2023 vector-search preview names
(`11.4.0b6`–`11.4.0b11`), before Microsoft restructured the API around
today's "profile" concept (`VectorSearchProfile` +
`vector_search_profile_name`).

**Habit worth building:** treat a fully-formed autocomplete suggestion
with the same suspicion as a copied line — check it against the actually-
installed package version (`pip show <package>`, or inspect the real
class signature) before trusting it, especially for SDKs whose API
surface is still evolving (vector search here; generally, anything
recently out of preview).

---

## List comprehensions are shorthand syntax, not a separate concept

**What it is:** a compressed way to write "build a new list by doing the
same thing to every item in an existing list." It is not a different
skill from a `for` loop that appends — it is the exact same loop,
relocated.

Long form (a shape already used in `chunk_by_section()` and elsewhere in
this project):

```python
contents = []
for chunk in chunks:
    contents.append(chunk["content"])
```

Shorthand, same three lines folded onto one:

```python
contents = [chunk["content"] for chunk in chunks]
```

Mapped piece by piece against the long form: `chunk["content"]` is the
exact same expression that was inside `.append(...)`; `for chunk in
chunks` is the same `for` line, just moved to sit after the expression
instead of above it; the surrounding `[...]` replaces both `contents = []`
and the `.append()` call — it tells Python "collect each result into a
new list" instead of doing it a line at a time.

**Where this showed up:** `embed_chunks()` (`m5_index.py`, Aug 14) —
first genuinely new Python syntax hit in this project rather than a
repeat of a known shape. Not knowing it on sight isn't a comprehension
gap — it's pure vocabulary, either seen before or not, unrelated to
whether the surrounding data-flow logic (what each function produces and
what consumes it) is understood.

**Follow-on, Aug 18 — the filtering variant:** the same idiom can also
filter, not just transform every item, by adding a condition after the
`for`:

```python
failed_chunks = []
for result in results:
    if not result.succeeded:
        failed_chunks.append(result)
```
```python
failed_chunks = [result for result in results if not result.succeeded]
```

Same mapping as above — `result` is what was inside `.append(...)`,
`for result in results` is the same loop line — plus one new piece:
`if not result.succeeded` is the same `if` condition that used to guard
the `.append()` call, now sitting after the `for` instead of wrapping it
in an indented block. Seen in `upload_chunks()` (`m5_index.py`, Aug 18),
sourced from IntelliSense and understood after the fact via this
mapping, not accepted on faith.

---

## Testing a hand-copied duplicate instead of the real function

**What happens:** a quick diagnostic snippet re-types a piece of logic
(a regex, a formula, a condition) inline in a scratch/tester file instead
of importing and calling the real function. The real source gets edited
and fixed, but the scratch copy doesn't — so re-running the "test"
re-exercises the stale duplicate, not the fix. The result reads as "the
fix didn't work" when actually the fix was never tested at all.

**Why it's easy to miss:** both versions look like the same test, the
scratch file runs without error, and there's no reason to suspect the
regex string in the tester isn't the one that matters — until something
independent (a stray warning, a printed value) exposes that the two have
drifted apart.

**Real instance:** `m5_index.py`'s `chunk_by_section()` heading regex —
the character-class fix (adding `-`/`'` to allow "ATTORNEYS'" and
"NON-WAIVER.") was correctly saved in the real function, but two rounds
of "this doesn't work" were run against a hand-typed duplicate regex left
over in a tester script from an earlier diagnostic snippet, never updated
to match (Aug 14).

**Habit worth building:** for any fix inside a function that's already
been written, test by importing and calling that real function directly
(`from module import the_function`), not by re-typing its logic inline —
even for a "quick" scratch check. If a scratch copy is unavoidable, treat
a surprising result as reason to check whether the copy and the source
have actually stayed in sync, not just reason to doubt the fix.

---

## Slice bounds: an omitted side runs to the boundary, not to the other side

**What it is:** `sequence[start:stop]` always has two positions. Leaving
one blank doesn't make Python infer it from the other — it substitutes
the boundary on that side (index `0` on the left, `len(sequence)` on the
right).

Long form:

```python
before = sig_line[0:split_point]           # start at the beginning, stop at split_point
after  = sig_line[split_point:len(sig_line)]  # start at split_point, go to the end
```

Shorthand, same meaning:

```python
before = sig_line[:split_point]
after  = sig_line[split_point:]
```

Mapped piece by piece: the blank side is the side with no boundary
written in — "wide open," running all the way to whichever edge of the
sequence sits on that side. `split_point` itself doesn't change meaning;
what changes is whether it's marking where the slice *starts* (right side
of the colon is blank) or where it *stops* (left side is blank).

**Where this showed up:** `chunk_by_section()` (`m5_index.py`, Aug 17) —
splitting the trailing signature block out of section XV's content
required both directions of the same slice on the same string.

---

## Assignment aliases a mutable object — it doesn't copy it

**What happens:** `new_name = existing_dict` does not create a second,
independent dict. It creates a second name pointing at the *same* dict in
memory. Mutating through either name — `new_name["key"] = ...` or
`existing_dict["key"] = ...` — changes the one object both names refer
to. This is true for dicts, lists, and other mutable objects; it is not
true for immutable values like strings or ints, which is why reassigning
a string variable (`sig_line = sig_line[split_point:]`) never touches
whatever the string used to be bound to elsewhere.

**Why it's easy to miss:** the line `new_name = existing_dict` reads like
"make a copy," especially coming from languages where assignment does
copy. Nothing about the syntax signals "this is now a second label for
the same box," and code written on that mistaken assumption can still
run without error — it just makes a later "restore the original" or
"keep them independent" step silently pointless, since there was never a
second object to begin with.

**Real instance:** an early draft of the signature-block split used
`new_XV_content = chunks[-1]` and later `chunks[-1] = new_XV_content`,
intending the second line to "save" the edit back. Both lines were
no-ops with respect to that goal — `new_XV_content` was `chunks[-1]` the
whole time, so mutating one already mutated the other, and reassigning
`chunks[-1]` to itself did nothing. The code happened to produce the
right result anyway, but for a different reason than the draft assumed.
Collapsed to a single direct line once the aliasing was understood:
`chunks[-1]["content"] = chunks[-1]["content"][:split_point]`.

**Where this showed up:** `chunk_by_section()` (`m5_index.py`, Aug 17).

---

## A running Python process doesn't notice a file changed on disk

**What happens:** editing and saving a `.py` file has no effect on code
that's already been imported into a *currently running* interpreter.
`import module_name` only reads the file the first time; every later
`import` in that same process — including one inside a script you re-run
— hands back the already-loaded module object from `sys.modules`, edits
or not. This bites hardest in a persistent session (VS Code's Python
Interactive Window, a Jupyter-style cell, a long-lived REPL), where
"re-run the cell" does not mean "re-read the file." A plain `python
some_script.py` from a fresh terminal doesn't have this problem, because
each run starts a brand-new process with nothing yet imported.

**Why it's easy to misdiagnose as a code bug:** the symptom — "I fixed
this, saved it, re-ran the test, and got the old broken behavior" — looks
identical to "the fix is wrong." Reading the file confirms the fix is
correct; the disk and the running process have just quietly drifted
apart. Nothing errors, so there's no signal pointing at the environment
instead of the logic.

**Diagnostic that settles it fast:** run the *saved* source
independently of whatever session produced the confusing result — a
fresh `python` invocation, or (as done here) extracting the function's
literal text from the file on disk and `exec`-ing it in a clean
namespace. If that independent run gives the correct result against the
real input, the code is fine and the running session is stale — restart
it.

**Real instance:** the signature-block split in `chunk_by_section()`
looked broken (XV's content still contained the marker text) after being
correctly fixed and saved, because `tester2.py` was being re-run in a
session that had `m5_index` imported from before the fix (`m5_index.py`,
Aug 17). Restarting the interpreter and re-running resolved it with no
code changes.

---

## "Loop and a half": checking before deciding whether to keep going

**When it applies:** a loop needs to run its check *before* it can know
whether to stop — e.g. "keep polling until a value matches, or until
time runs out." A normal `while <condition>:` can't express this
cleanly, because the condition would need to reference something (the
freshly-checked value) that doesn't exist until the loop body has
already run.

**The shape:**

```python
while True:
    count = search_client.get_document_count()
    if count == len(chunks) or elapsed >= timeout:
        break
    time.sleep(interval)
    elapsed += interval
```

`while True:` means the loop always enters its body with no upfront
gate. The exit decision moves inside, right after the value that matters
(`count`) gets refreshed — `break` fires for either of two independent
reasons (success, or time exhausted), checked at the same instant. Only
code below the `break` (here, the `sleep` and the increment) is skipped
once either condition is true.

**Why the more obvious version is subtly wrong:** a version gating entry
with `while elapsed < timeout:` and only checking the value *inside* the
loop has a real gap — if the value still doesn't match on the very last
iteration, the loop sleeps once more, increments past the timeout, and
exits via the `while` condition failing, without ever rechecking the
value after that final wait. Whatever the value was on the second-to-
last check is what gets reported, even though the true up-to-date value
was never fetched. `while True:` with the exit condition checked
immediately after the fetch closes that gap — every exit, for either
reason, happens right after a fresh check.

**Where this showed up:** `main()`'s closing verification (`m5_index.py`,
Aug 18) — retrying `get_document_count()` a few times to tolerate Azure
Search's eventual-consistency lag (see `STATUS.md`'s "Key Lessons" entry
on the same date) without looping forever if something's actually wrong.

---

## A variable assigned inside a loop only exists if the loop ran

**What happens:** Python doesn't scope variables to the block they're
assigned in — a name assigned inside a `while` or `for` body is still
readable after the loop ends, unlike block-scoped languages where it
would fall out of scope. That makes code like this look risky but
actually be fine:

```python
while True:
    count = search_client.get_document_count()
    if count == len(chunks) or elapsed >= timeout:
        break
    ...
print(count)   # still valid here
```

**The real condition to check, though:** this only works because the
loop is *guaranteed* to execute its body at least once — `while True:`
always does, and so does a `while <condition>:` whose condition is true
on the first check (e.g. `elapsed = 0` against `timeout = 30`). If a
loop's very first condition check could ever be false — a `for` over a
sequence that might be empty, or a `while` whose starting values could
already fail the test — the variable assigned inside might never get
created, and referencing it afterward raises `NameError`. The safety
isn't "Python remembers variables from loops"; it's "this specific loop
happens to always run at least once," which is a property of the
numbers/data involved, not a language guarantee.

**Habit worth building:** before relying on a loop-assigned variable
after the loop, check whether the loop is actually guaranteed to run —
don't assume it just because it happened to in the case tested.

**Where this showed up:** `main()`'s closing verification (`m5_index.py`,
Aug 18) — `count` is referenced after the retry loop; safe only because
`timeout = 30` and `elapsed` starts at `0`, guaranteeing at least one
pass.

---

## Triple-quoted strings are not comment syntax

**What it is:** `"""..."""`/`'''...'''` are just string literals with a
different quoting style — nothing about triple-quoting makes a string
into a comment. Python special-cases exactly one situation: a string
literal that is the *first statement* inside a `def`, `class`, or module
body becomes that object's docstring (`__doc__`), stored and later
readable via `help()`/`.__doc__`. That's a compiler behavior tied to
position, not something triple quotes confer generically.

**Why it's easy to miss:** a triple-quoted block dropped anywhere else —
mid-function, between two real statements — is still syntactically legal
Python. It doesn't error. It gets evaluated (building a string object)
and then silently discarded, exactly like writing a bare `42` alone on
its own line would be. The text reads like a comment, runs like a no-op,
and gives no signal that it was never attached to anything.

**Real instance:** `m5_index.py`'s `embed_chunks()` had a correct `#`
comment (explaining why `.index` is used instead of `zip()`) rewritten as
a `"""..."""` block under this exact misunderstanding — it wasn't the
function's first statement, so it was never a docstring, just a
discarded expression sitting between real lines. Caught via an
ast-based scan of the whole `scripts/` folder for stray string-literal
statements not in first-statement position; one other hit,
`tester.py`, turned out to be intentional (a saved REPL demo, not a
mistake) (Aug 19).

**Habit worth building:** reserve triple-quoted strings for the one
literal position that gives them meaning — first line of a `def`/
`class`/module body. Anywhere else, use `#` for an explanatory comment,
even a long one spanning several `#`-prefixed lines.

**Meta-note, worth carrying forward:** this was caught after naming
directly, at the end of the same session, that rising confidence had
been correlating with skipping verification rather than with actually
needing less of it. Worth treating "I'm pretty sure now" as a prompt to
double-check once, not a signal to stop asking.

**Where this showed up:** `m5_index.py`'s `embed_chunks()` (Aug 19,
self-corrected before the session ended).

---

## Escaping meant for display inside a docstring isn't escaping for real code

**What happens:** a code example written inside a docstring, meant to be
*read* by a human as instructional text, sometimes needs extra escaping
just so it *displays* the right characters — writing `\\n` inside a
docstring so the rendered text shows the two visible characters `\n`,
rather than the docstring itself containing an actual newline at that
spot. When that example gets copied into real, executable code, the
escaping that existed for *display* purposes carries over as if it were
meant for *execution* — and in real code, `\\n` isn't a newline. It's a
literal backslash followed by the letter n.

**Why it's easy to miss:** nothing errors. `f"{context}\\n\\nQuestion:
{question}"` is completely valid Python — it just doesn't do what the
single-backslash version does. The string builds without complaint, the
API call succeeds, and a chat model is often robust enough to still
answer something reasonable even with literal `\n\n` sitting in the
prompt instead of a blank line — so nothing in the chain fails in a way
that points back at the real problem. `print()` on the built string can
even look right at a glance, since terminal output doesn't always make a
literal backslash-n obviously different from a real line break unless
looked at closely.

**Real instance:** `answer_question()`'s TODO (inside `m5_retrieve.py`'s
own docstring, written before the function existed) wrote
`f"{context}\\n\\nQuestion: {question}"` — correct *as documentation
text*, since the docstring needed to display the literal characters
`\n\n` to describe what to type. When that line got typed into the
function's real, executable body, the extra backslash carried over
unchanged, sending literal `\n\n` as visible text in every prompt instead
of an actual blank line separating retrieved context from the question.
Caught by testing the real built string with `repr()`, which shows
backslash characters literally instead of interpreting them — not by
reading the code, which looked correct on inspection (Aug 20, caught and
fixed same day, before any live test question was asked against it).

**Habit worth building:** when copying an example straight out of a
docstring or comment into real code, check whether any escape sequences
in it were serving the docstring's own *display* purposes rather than
describing the literal characters actually needed at runtime —
especially anything with a backslash. `repr()` on the resulting string
(not just `print()`) is the fast way to check, since `repr()` shows
escape sequences literally instead of rendering them.

**Where this showed up:** `answer_question()` (`m5_retrieve.py`), Aug 20.

---

## Hardcoded `/tmp` + naive `file://` string concatenation is not a valid Windows file URL

**The bug:** building a local file URL by hand — `"file://" + str(path)` —
instead of using `pathlib.Path.as_uri()`, combined with hardcoding a Unix
temp directory (`/tmp/...`) instead of `tempfile.gettempdir()`. On Linux/Mac
this often happens to work by accident; on Windows it doesn't, because a
Windows path has a drive letter (`C:\\...`) and backslashes, which naive
string concatenation doesn't turn into a well-formed `file://` URI at all.

**Why it's easy to miss:** the bug only surfaces where the code actually
runs, not where it's written or reviewed. `build.py`'s own pattern (`/tmp/
m7-riverside-hardware` + `"file://" + str(html_path)`) presumably worked
fine in whatever environment it was first tested in, and copying that
pattern into a new script feels like reusing an already-proven approach,
not introducing a new bug — nothing about the code *looks*
platform-specific.

**Real instance:** `build_legibility_diagnostics.py`, written new this
session, inherited this exact pattern from `build.py` uncritically (my
mistake, not caught in review before the first run). Playwright's
`page.goto()` failed with `net::ERR_FILE_NOT_FOUND` on the Windows device
this session actually runs against, since `"file://" + "/tmp/
m7-legibility-diagnostics/diag-a.html"` isn't a real path on this machine
at all — there is no `/tmp` directory, and even if there were, the string
is missing the drive letter a real Windows file URI needs
(`file:///C:/...`). Fixed with `tempfile.gettempdir()` (resolves to the
correct temp directory on whatever OS is actually running) and
`pathlib.Path(...).as_uri()` (builds a correct, OS-appropriate `file://`
URI, drive letter included on Windows).

**Habit worth building:** any time a path is about to become a URL string,
reach for `Path.as_uri()` instead of string concatenation — same instinct
as not hand-building a URL query string when `urllib.parse` exists. And
treat `/tmp` as a Unix-only assumption on sight, even inside code that's
"just a temp file, doesn't matter" — `tempfile.gettempdir()` costs nothing
and is correct everywhere.

**Where this showed up:** `build_legibility_diagnostics.py`
(`iip-docs/m7-riverside-hardware/`), Aug 31. **Known, not fixed:**
`build.py` in the same folder has the identical pattern and has not been
touched — flagged in `m7-orientation.md`'s backlog.

---

*(Add more entries here as new patterns come up — living document, edited
in place, same rule as `STATUS.md`.)*
