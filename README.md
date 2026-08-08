# GradeTrack

A simple Streamlit app to track student grades and classroom performance.

This repository provides a lightweight grading dashboard that allows teachers and administrators to view class averages, per-student details, import new grade data, and manage application settings.

> Note: Most of the UI and labels are in French — this README is in English with some French notes.

## Features

- Dashboard with class and trimester filters (📊 Dashboard)
- Per-student detail view (👤 Détail Élève)
- Add/import grade data (➕ Ajouter des Données)
- Administration panel (⚙️ Administration)
- Streamlit caching for faster interactions
- Resilient handling of empty or malformed data

## Requirements

- Python 3.9+ recommended
- streamlit
- pandas
- numpy

You can install the main dependencies with pip:

```bash
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
pip install streamlit pandas numpy
```

If the repository grows a `requirements.txt`, prefer:

```bash
pip install -r requirements.txt
```

## Quick start (development)

1. Clone the repository:

```bash
git clone https://github.com/winsonkpokpo-commits/GradeTrack.git
cd GradeTrack
```

2. Install dependencies (see Requirements above).

3. Run the app locally with Streamlit:

```bash
streamlit run app.py
```

4. The app opens in your browser (usually http://localhost:8501).

## Data format

The app expects a tabular dataset (CSV, Excel, etc.) with at least the following columns (French column names used in the code):

- Eleve — student name or identifier
- Classe — class/group name
- Matiere — subject name
- Note — numeric grade (e.g., on a 20-point scale)
- Trimestre — trimester/term (e.g., `1`, `2`, `3`)

Example CSV header:

```
Eleve,Classe,Matiere,Note,Trimestre
Dupont Alice,6A,Math,15.5,1
Martin Bob,6A,Français,12.0,1
```

If your data uses different column names, update the data loading logic in `data_manager.py` or add a preprocessing step to normalize column names to the ones above.

## Configuration

Application-level settings are read from `config.py` (app title, icons, page config, developer contact, year, etc.). Edit that file to customize the name and appearance of the app.

## Project structure (high level)

- `app.py` — main Streamlit app and UI wiring
- `data_manager.py` — data loading/saving utilities
- `views.py` — UI components and view handlers (dashboard, add data, student detail)
- `admin.py` — administration panel
- `config.py` — application configuration/constants

## Contributing

Contributions are welcome. Suggested workflow:

1. Fork the repository (or create a branch if you have push access).
2. Create a feature branch: `git checkout -b feat/your-feature`.
3. Make changes and include tests where appropriate.
4. Open a pull request describing the change and why it's needed.

Please follow any repository guidelines (linting, formatting) if present.

## License

No license file detected in the repository. If you want to make this project open-source, add a LICENSE file (e.g., MIT, Apache-2.0) and update this README accordingly.

## Contact

Maintainer: winsonkpokpo-commits — https://github.com/winsonkpokpo-commits

If you need help adapting data formats, adding features, or deploying to a hosting provider (Streamlit Cloud, Heroku, etc.), open an issue or a PR.
