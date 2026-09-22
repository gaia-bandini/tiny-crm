# Tiny CRM — notes for Codex

This is a starter project for a university course (Introduction to Programming, Nova SBE). The person asking is a **beginner**. Teach, don't just do.

## Running things

- Run the app: `uv run streamlit run app.py` — uv installs Python and the libraries by itself. Never use `pip` or `python -m venv`.
- Reset the data: `uv run python seed.py` (copies `seed/*.csv` over `data/*.csv`).
- Tests: `uv run pytest`. **Many tests fail on purpose** — they describe features not built yet (`specs/`) and bugs not fixed yet (`issues/`). Never edit, delete or skip a test to make it pass.
- If `uv` is missing, install it: macOS `curl -LsSf https://astral.sh/uv/install.sh | sh`, Windows `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`. Then open a new terminal.

## The project

`app.py` = the screens (entry point), `logic.py` = the rules (stages, search, overdue follow-ups), `db.py` = reading and writing the CSV files in `data/`. `seed/` is the pristine copy of the data. Everything that comes out of a CSV is text: ids are `"3"`, dates are strings.

## How to answer

- Every claim about the code comes with **file and line**. Show the lines; don't paraphrase a function the student can read.
- When asked "where does X happen", walk the chain: the button in `app.py` → the function in `logic.py` → the call in `db.py`.
- **Change code only when asked** to fix one specific issue or build one specific spec. Fix that one thing, show the diff, explain it in two sentences. Do not fix other bugs or build other features you notice — they are the course.
- `ONBOARDING.md` is the student's answer sheet. Write in it only what the student tells you to write, under the question they name.
- Build each task on a branch named after it, e.g. feature-2-categories. Never commit to main directly.
- After every change, run the tests for the task and paste the final output. The output is the proof, not a sentence.
- Never edit, delete or skip anything in tests/. If a test looks wrong, say so and stop.
