# emojournal
Your dynamic journal

## Prerequisites

1. **Python 3.9+** – the app was built and tested with Python 3.11, but any recent Python 3.9 or newer should work.
2. **Pip** – the Python package manager for installing dependencies.
3. (Optional) A **virtual environment** to isolate the project dependencies.

## Setup

1. Clone or download this repository, then open a terminal in the project directory (`emojournal/`).
2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   If you prefer to install manually, you can run `pip install streamlit pandas` instead; these are the only packages the app uses.

## Running the app

1. Launch Streamlit from the project root:
   ```bash
   streamlit run app.py
   ```
2. Streamlit will print a local URL (usually `http://localhost:8501`). Open it in your browser to access the **Dynamic Emotion-Aware Journal**.
3. As you interact with the journal, entries are saved to `journal_data.json` in the project folder. You can revisit the same day, and the app will pre-fill your previous entries.

## Common tasks

- **Stop the server:** Press `Ctrl+C` in the terminal running Streamlit.
- **View logs:** The same terminal will display any log messages or errors from Streamlit.
- **Reset data:** Delete `journal_data.json` (while the server is stopped) to clear all saved entries.
