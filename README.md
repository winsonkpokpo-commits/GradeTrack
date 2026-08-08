# 📊 GradeTrack

> **A student academic performance tracking and visualization application built with Python and Streamlit.**

GradeTrack is a web application designed to simplify the **management, exploration, and visualization of students' academic results**.

The project currently focuses on building a reliable foundation for academic data management: loading and validating grade data, filtering results, monitoring class performance, and exploring individu[...]

Machine Learning and AI capabilities are **future development goals** and are not part of the current version.

---

## 🎯 Project Overview

Managing academic results can quickly become repetitive when information is spread across spreadsheets or manually processed.

GradeTrack aims to provide a centralized interface where academic data can be explored more easily.

The current application allows users to:

* explore academic results;
* filter results by class and trimester;
* inspect individual students;
* view basic performance statistics;
* add or import academic data;
* access administrative functionality;
* work with imperfect or incomplete datasets more safely.

The project is currently focused on **software engineering, data management, and academic visualization**.

---

## ✨ Current Features

### 📊 Interactive Dashboard

The dashboard provides an overview of the available academic data.

Current statistics include:

* Number of students
* Number of recorded grades
* Overall average grade

The displayed data can be filtered interactively.

### 🏫 Class Filtering

Users can select a specific class or view all classes.

```text
Toutes
Terminale D
Terminale C
...
```

### 📅 Trimester Filtering

Academic results can be filtered by trimester:

* All trimesters
* Trimester 1
* Trimester 2
* Trimester 3

### 👤 Student Details

GradeTrack provides a dedicated student view.

Users can select an individual student and inspect the academic data associated with that student.

### ➕ Data Management

The application includes an interface for adding or importing academic data.

The data-management layer is designed to deal with incomplete or malformed records without unnecessarily breaking the application.

### ⚙️ Administration

An administration section is available for application-level management operations.

### 🔄 Data Refresh

The application provides a refresh mechanism that clears Streamlit's cached data and reloads the dataset.

### 🛡️ Defensive Data Handling

GradeTrack performs several validation and cleaning operations before displaying academic data.

For example:

* missing grades are excluded from performance calculations;
* empty subjects are ignored;
* missing class/student values are handled;
* empty datasets are detected;
* unexpected application errors are logged and handled gracefully.

---

# 🧮 Data Model

GradeTrack currently works with structured academic data organized around several core concepts:

| Field       | Description   |
| ----------- | ------------- |
| `Eleve`     | Student       |
| `Classe`    | Class         |
| `Matiere`   | Subject       |
| `Note`      | Grade         |
| `Trimestre` | Academic term |

A simplified example:

```csv
Eleve,Classe,Matiere,Note,Trimestre
Alice,Terminale D,Mathématiques,15.5,1
Bob,Terminale D,Physique,12.0,1
Alice,Terminale D,SVT,17.0,1
```

The application processes this data with **Pandas** before presenting it through the Streamlit interface.

---

# 🏗️ Project Architecture

The current version follows a modular architecture rather than putting the entire application in a single file.

```text
GradeTrack/
│
├── app.py
├── config.py
├── data_manager.py
├── views.py
├── admin.py
│
├── README.md
├── LICENSE
├── PULL_REQUEST_TEMPLATE.md
│
└── .devcontainer/
```

### `app.py`

The main application entry point.

It is responsible for:

* initializing Streamlit;
* loading the data;
* managing application navigation;
* applying filters;
* connecting the different modules;
* handling application-level errors.

### `data_manager.py`

Responsible for academic data loading, processing, and data-management operations.

### `views.py`

Contains the user-facing application views, including the dashboard, student details, and data-related interfaces.

### `admin.py`

Contains administration-related functionality.

### `config.py`

Centralizes application configuration such as:

* application name;
* application icon;
* description;
* developer information;
* Streamlit page configuration.

---

# 🛠️ Technology Stack

## Current

* **Python**
* **Streamlit**
* **Pandas**
* **NumPy**

## Development principles

The project currently emphasizes:

* modular Python code;
* separation of responsibilities;
* structured data processing;
* defensive programming;
* reusable functions;
* Streamlit caching;
* basic logging and error handling.

---

# 📈 Project Roadmap

GradeTrack is being developed progressively.

The objective is to first build a solid academic data platform before introducing more advanced analytical and machine-learning capabilities.

## Phase 1 — Academic Data Management

**Current phase**

* [x] Load academic data
* [x] Filter academic records
* [x] Filter by class
* [x] Filter by trimester
* [x] Filter by student
* [x] Display basic statistics
* [x] Student detail view
* [x] Data management interface
* [x] Administration interface
* [x] Basic data validation
* [x] Error handling
* [x] Modular application structure

---

## Phase 2 — Academic Analytics

**Planned**

The next stage will focus on extracting more meaningful information from academic results.

Potential features include:

* [ ] Weighted averages
* [ ] Subject-level performance analysis
* [ ] Performance evolution across trimesters
* [ ] Identification of academic strengths and weaknesses
* [ ] Class performance analysis
* [ ] More advanced visualizations
* [ ] Academic reports
* [ ] Improved data validation

---

## Phase 3 — Machine Learning

**Future**

Once the analytical foundation is sufficiently mature, GradeTrack may incorporate Machine Learning.

Possible applications include:

* [ ] Feature engineering from academic history
* [ ] Performance prediction
* [ ] Performance trend prediction
* [ ] Identification of declining performance
* [ ] Academic risk classification
* [ ] Model evaluation and comparison

These features are **not implemented in the current version**.

---

## Phase 4 — Intelligent Educational Features

**Long-term direction**

A future version could explore AI-assisted academic analysis.

Possible directions include:

* [ ] Natural-language explanations of academic trends
* [ ] Personalized learning recommendations
* [ ] Automated academic reports
* [ ] Conversational academic assistant

These are research and development objectives rather than current GradeTrack features.

---

# 🧠 Development Philosophy

GradeTrack is intentionally being developed incrementally.

The project follows a progression from fundamental software engineering toward more advanced AI systems:

```text
Software Engineering
        ↓
Data Management
        ↓
Data Analysis
        ↓
Machine Learning
        ↓
Artificial Intelligence
```

The principle is simple:

> **Build the data foundation first, understand the problem second, and introduce AI only when it provides a meaningful solution.**

This approach is intended to prevent the project from becoming an AI layer placed on top of poorly structured data.

---

# 🔐 Data & Privacy

Academic records can contain sensitive personal information.

Any future deployment using real student data should take into consideration:

* data anonymization;
* access control;
* secure storage;
* appropriate data retention;
* responsible use of student information.

The examples used for development should preferably contain fictional or anonymized data.

---

# 💻 Installation

## 1. Clone the repository

```bash
git clone https://github.com/winsonkpokpo-commits/GradeTrack.git
cd GradeTrack
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Run GradeTrack

```bash
streamlit run app.py
```

The application will open in your browser through the local Streamlit server.

---

# 📌 Project Status

**Status: Active Development**

GradeTrack is currently a functional academic data management and visualization application.

The current priority is to strengthen the application's:

* architecture;
* data processing;
* academic analytics;
* testing;
* documentation.

Machine Learning and AI features will be developed in later stages once the underlying academic analytics are sufficiently mature.

---

# 🗺️ Roadmap at a Glance

```text
┌─────────────────────────────┐
│  Phase 1                    │
│  Academic Data Management   │
│  ✅ CURRENT                 │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Phase 2                    │
│  Academic Analytics         │
│  🔜 NEXT                    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Phase 3                    │
│  Machine Learning           │
│  🔬 FUTURE                  │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Phase 4                    │
│  Intelligent Features       │
│  🚀 LONG TERM               │
└─────────────────────────────┘
```

---

# 🤝 Contributing

Contributions, suggestions, and feedback are welcome.

For significant changes, consider opening an issue before submitting a pull request.

A typical development workflow is:

```bash
git checkout -b feat/my-feature
git add .
git commit -m "feat: describe the change"
git push origin feat/my-feature
```

Then open a Pull Request.

---

# 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

# 👨‍💻 Author

**Winson Kpokpo**

GitHub: [@winsonkpokpo-commits](https://github.com/winsonkpokpo-commits/GradeTrack)

---

> **GradeTrack starts with a simple question: how can academic data be managed and understood more effectively?**
>
> The long-term goal is to explore how data analysis and machine learning can eventually transform that data into meaningful educational insights.
