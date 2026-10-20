# Getting Started

Ten minutes from clone to your first context-engineering experiment. Everything runs offline on a plain Python installation — no API keys, no paid services, no third-party packages.

## Requirements

- **Python 3.10 or newer** (3.12 was used for development and testing).
- Git (to clone; or download the ZIP from the repository page).
- No other software. The library and tests use only the Python standard library.

Check your Python:

```bash
python3 --version
```

## Setup

```bash
git clone https://github.com/AdilShamim8/Context-Engineering.git
cd Context-Engineering
```

Make the library importable — pick one:

```bash
pip install -e .          # recommended: installs the package and the `context-engineering` command
export PYTHONPATH=src     # zero-install alternative; prefix every CLI command below with PYTHONPATH=src
```

That is the entire installation. If you prefer an isolated environment (optional — there is nothing to install into it):

```bash
python3 -m venv .venv && source .venv/bin/activate
```

## Verify your setup: run the test suite

```bash
python -m unittest discover
```

Expected result: every test passes and the final line reports `OK` with zero failures and zero errors. If any test fails, do not continue — see *Troubleshooting* below.

## Run your first experiment (2 minutes)

The repository's first experiment demonstrates the core thesis of the whole curriculum: **changing the information available to a responder changes the answer**, deterministically and reproducibly — no model required.

```bash
python labs/lab-00-first-context-experiment/experiment.py
```

You will see the same question answered three ways as the available context changes:

1. No evidence → the responder correctly reports insufficient information.
2. Relevant policy added → the responder answers **with a citation to the source**.
3. A stale version of the policy replaces the new one → the answer silently changes to outdated information.

The third outcome is the most important one in the entire lab: nothing crashed, nothing looked wrong, and the answer was confidently outdated. That is a context-engineering failure, and the curriculum exists to teach you to prevent it. Chapter 0.3 walks through the code line by line.

## Try the CLI tools (2 minutes)

Skip ahead and see where the curriculum ends:

```bash
# Explore allocation under budget pressure (Context Budget Explorer)
python -m context_engineering.cli budget

# See the exact context that gets assembled (Context Inspector)
python -m context_engineering.cli inspect

# Ask a question of the Nimbus Dynamics knowledge base (fictional data)
python -m context_engineering.cli ask "How many remote days per week are allowed?"
```

The `inspect` command is the single most valuable habit this curriculum teaches: **never argue about what the model saw — look at it.**

## Run the evaluation suite

```bash
python -m context_engineering.cli evaluate
```

This runs the golden-case evaluation over the corpus and prints a report. You will use and extend this harness throughout the curriculum.

## Optional: editable install

If you want the CLI on your PATH or want to import the library from other projects:

```bash
pip install -e .
context-engineering --help
```

This is **not required** for any chapter; `python -m context_engineering.cli` works without installation.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `python: command not found` | Python is registered as `python3` | Use `python3` in every command |
| `No module named context_engineering` | Library not importable | Run `pip install -e .`, or prefix commands with `PYTHONPATH=src` |
| Tests fail with `ImportError` | Mixed Python versions (e.g., tests run with 3.8) | Check `python3 --version`; the library requires 3.10+ |
| `Permission denied` on scripts | Clone extracted with odd permissions | Re-clone, or run with `python <script>` instead of executing it directly |
| Unicode garbling on Windows terminals | Code page issues in cmd.exe | Use Windows Terminal / PowerShell with UTF-8 enabled |

If none of these help, open a GitHub issue with: the command you ran, the exact output, and your `python3 --version`.

## Where to go next

1. `docs/prerequisites.md` — self-assess your background.
2. `chapters/00-orientation/chapter-01-introduction.md` — start the curriculum.
3. `docs/learning-guide.md` — how to study this repository effectively.
