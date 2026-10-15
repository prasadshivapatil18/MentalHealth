# 🌿 Aura — AI Mental Health Companion & CDC Analytics

> A contextual deep learning mental health chatbot and public health analytics platform built with **PyTorch**, **NLTK**, **FastAPI**, **Pandas**, and modern **Web Technologies**. Integrates the official **U.S. CDC Household Pulse Survey dataset** (`Indicators_of_Anxiety_or_Depression.csv`) with interactive **EDA data visualizations**, a clinically-validated **PHQ-4 self-assessment screener**, and 24/7 **emergency crisis intervention**.

---

## 📌 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [CDC Dataset Integration & Insights](#-cdc-dataset-integration--insights)
- [Architecture & Workflow](#-architecture--workflow)
- [Project Directory Structure](#-project-directory-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Model Training](#-model-training)
- [Running the Applications](#-running-the-applications)
  - [1. Web Application (FastAPI + Modern Web UI)](#1-web-application-fastapi--modern-web-ui-recommended)
  - [2. Desktop GUI (Tkinter)](#2-desktop-gui-tkinter)
  - [3. Interactive Terminal CLI](#3-interactive-terminal-cli)
- [REST API Reference](#-rest-api-reference)
- [Customizing Intents](#-customizing-intents)
- [Emergency Crisis Support & Disclaimer](#-emergency-crisis-support--disclaimer)
- [License](#-license)

---

## 📖 Overview

**Aura** unites conversational deep learning with public health epidemiology:
1. **Conversational Support**: An empathetic conversational AI that classifies user emotional states using a custom 3-layer Feedforward Neural Network (Multilayer Perceptron) implemented in PyTorch, paired with NLTK tokenization and Porter stemming.
2. **CDC Indicators EDA Dashboard**: Analyzes over **16,087 records across 72 survey time periods** from the U.S. Census Bureau & CDC Household Pulse Survey on self-reported frequency of anxiety and depression symptoms.
3. **Clinical Self-Screening (PHQ-4)**: Enables users to complete an ultra-brief, 4-item validated screening tool, calculates severity risk scores, and compares individual results against national population benchmarks.
4. **Emergency Safety Interceptor**: Critical self-harm and suicide keywords bypass standard confidence thresholds to immediately display verified 24/7 emergency hotlines.

---

## ✨ Key Features

- **🌐 Modern Web Application**:
  - Calming, high-contrast Slate/Midnight dark palette with glassmorphism and fluid animations.
  - Interactive web chat interface with real-time response generation, typing indicator, and suggestion prompt chips.
  - Interactive **Chart.js** line charts (longitudinal trends) and grouped bar charts (demographic disparities).
  - **State-by-State Explorer**: Search and view symptom prevalence, quartile ranges, and benchmark deviations for all 50 states + DC/PR.
  - **PHQ-4 Screener**: Instant score calculation, severity status, and population benchmark comparison with 1-click option to discuss results with Aura.
- **🧠 PyTorch Neural Network Classifier**:
  - 3-layer Multilayer Perceptron (Linear + ReLU) trained for high-confidence intent classification.
  - Automated resource downloads (`punkt` / `punkt_tab`), Porter stemming, and fast Bag-of-Words vectorization.
- **🖥️ Desktop GUI (Tkinter)** & **💻 Terminal CLI**:
  - Desktop Tkinter GUI with timestamps, chat bubbles, and auto-scroll.
  - Terminal CLI mode (`python chat.py`) for quick command-line interactions.
- **🛡️ Immediate Crisis Detection**:
  - Emergency hotline integration for the US/CA (988), UK (111 / SHOUT), India (KIRAN), Australia (Lifeline), and international resources.

---

## 📊 CDC Dataset Integration & Insights

The project integrates `Indicators_of_Anxiety_or_Depression.csv` from the **U.S. CDC National Center for Health Statistics (Household Pulse Survey)**:

| Metric / Dimension | Value / Finding |
| :--- | :--- |
| **Total Clean Records** | **16,087 observations** |
| **Survey Waves Tracked** | **72 longitudinal time periods** (Phase 1 – Phase 4.2) |
| **Latest National Combined Rate** | **21.4%** of respondents reporting symptoms of anxiety or depression |
| **Latest National Anxiety Rate** | **17.6%** |
| **Latest National Depression Rate** | **13.9%** |
| **Most Impacted Demographic** | **18 – 29 years** (Average prevalence: **41.3%**) |
| **Demographic Breakdowns** | By Age, Sex, Education, Race/Hispanic ethnicity, Disability, Sexual orientation |
| **Geographic Coverage** | All 50 U.S. states + District of Columbia and Puerto Rico |

---

## 🧠 Architecture & Workflow

```mermaid
flowchart TD
    User([User in Web Browser / Desktop / Terminal]) --> Choice{Interface Mode}
    
    Choice -- Web Frontend --> FastAPI[FastAPI Web Server :8000]
    Choice -- Desktop GUI --> Tkinter[Tkinter Desktop App]
    Choice -- Terminal CLI --> CLI[Terminal CLI loop]

    FastAPI --> ChatEndpoint["/api/chat"]
    FastAPI --> AnalyticsEndpoint["/api/dataset/*"]
    FastAPI --> ScreenerEndpoint["/api/screen"]

    AnalyticsEndpoint --> AnalyticsEngine[IndicatorsAnalytics (Pandas)]
    AnalyticsEngine --> CSV[(Indicators_of_Anxiety_or_Depression.csv)]

    ChatEndpoint --> SafetyCheck{Crisis Keyword?}
    Tkinter --> SafetyCheck
    CLI --> SafetyCheck

    SafetyCheck -- Yes --> Hotlines[Immediate Emergency Crisis Response]
    SafetyCheck -- No --> NLP[NLTK Tokenize + Stem + Bag-of-Words]
    
    NLP --> Model[PyTorch NeuralNet (data.pth)]
    Model --> Softmax[Softmax Probabilities & Intent Tag]
    Softmax --> Response[Contextual Response from intents.json]
```

---

## 📁 Project Directory Structure

```text
mental-health/
├── mental-health-nlp-chatbot/
│   ├── server.py                                  # FastAPI web server and REST API endpoints
│   ├── static/                                    # Modern Frontend Web Application
│   │   ├── index.html                             # Single-page application structure & tabs
│   │   ├── style.css                              # Glassmorphic dark styling & responsive grid
│   │   └── app.js                                 # Client controller (Chat, Chart.js, PHQ-4 screener)
│   ├── dataset_analytics.py                       # Analytics engine for CDC Household Pulse data
│   ├── Indicators_of_Anxiety_or_Depression.csv    # Official CDC mental health indicators dataset
│   ├── app.py                                     # Desktop Tkinter GUI application
│   ├── chat.py                                    # NLP inference engine & Terminal CLI interface
│   ├── model.py                                   # PyTorch 3-layer Feedforward Neural Network
│   ├── nltk_utils.py                              # NLP preprocessing: tokenize, stem, bag_of_words
│   ├── train.py                                   # Training script and model checkpoint generator
│   ├── intents.json                               # Dataset containing intent tags, patterns, and responses
│   ├── data.pth                                   # Trained PyTorch model weights
│   ├── requirements.txt                           # Project dependencies
│   ├── LICENSE                                    # MIT License
│   └── README.md                                  # Complete project documentation
├── requirements.txt                               # Root dependencies pointer
└── README.md                                      # Root documentation
```

---

## ⚙️ Prerequisites

- **Python**: Version `3.9` through `3.13+`
- **Operating System**: Windows, macOS, or Linux
- **Modern Web Browser**: Chrome, Edge, Firefox, Safari

---

## 🚀 Installation

1. **Clone or navigate to the project directory**:
   ```powershell
   cd "mental-health-nlp-chatbot"
   ```

2. *(Optional but recommended)* **Create and activate a virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🎓 Model Training

To train or retrain the intent classifier on [`intents.json`](file:///mental-health-nlp-chatbot/intents.json):

```bash
python train.py
```

Output:
```text
============================================================
Mental Health NLP Chatbot - Training
============================================================
Loading intents from: intents.json
Total training patterns : 106
Total intent classes    : 16
Unique vocabulary words : 141
Training device         : cpu
------------------------------------------------------------
Epoch [ 50/500] - Loss: 0.2657
...
Epoch [500/500] - Loss: 0.0000
------------------------------------------------------------
Training completed in 18.30s | Final Loss: 0.0000
Model saved successfully to: data.pth
============================================================
```

---

## 💬 Running the Applications

### 1. Web Application (FastAPI + Modern Web UI) — *Recommended*

Launch the complete web platform:
```bash
python server.py
```
Open your browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

**Features available in the web app**:
- **💬 AI Chatbot**: Real-time conversation with Aura, typing indicator, prompt chips.
- **📊 CDC Indicators Dashboard**: Longitudinal trends line chart, demographic bar charts, and interactive state explorer.
- **📋 Self-Assessment Screener**: Validated PHQ-4 screener with automated risk scoring and CDC benchmark comparison.
- **🆘 Crisis Directory**: Quick 1-click call/text buttons for emergency mental health support.

---

### 2. Desktop GUI (Tkinter)

Launch the native desktop window:
```bash
python app.py
```

---

### 3. Interactive Terminal CLI

Chat with Aura directly from your command line:
```bash
python chat.py
```

---

## 📡 REST API Reference

When `server.py` is running, the following endpoints are available:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Serves the web frontend application (`static/index.html`) |
| `/api/chat` | `POST` | Processes message: `{"message": "string"}` -> returns response, intent tag, confidence |
| `/api/dataset/summary` | `GET` | Returns CDC dataset summary, national averages, latest survey wave stats |
| `/api/dataset/trends` | `GET` | Returns longitudinal time-series data for line chart (72 survey periods) |
| `/api/dataset/demographics` | `GET` | Returns breakdown for `group` (`By Age`, `By Sex`, `By Education`, `By Race/Hispanic ethnicity`) |
| `/api/dataset/states` | `GET` | Returns all 52 states and territories with their latest rates and quartile tiers |
| `/api/screen` | `POST` | Evaluates PHQ-4 answers (0–3 per question) and benchmarks against CDC population data |
| `/docs` | `GET` | Interactive Swagger / OpenAPI documentation UI |

---

## 🛠️ Customizing Intents

To teach Aura new concepts, add entries to [`intents.json`](file:///mental-health-nlp-chatbot/intents.json):

```json
{
  "tag": "mindfulness",
  "patterns": [
    "How do I practice mindfulness?",
    "Teach me mindfulness",
    "Mindfulness exercises"
  ],
  "responses": [
    "Mindfulness is about paying attention to the present moment without judgment. Try focusing entirely on the sensation of your breath for 60 seconds."
  ]
}
```

After modifying `intents.json`, simply run:
```bash
python train.py
```

---

## ⚠️ Emergency Crisis Support & Disclaimer

> [!IMPORTANT]
> **Medical & Crisis Disclaimer**: Aura is an educational, supportive AI project. It is **NOT** a certified medical device, psychologist, or licensed crisis hotline, and does not provide medical diagnoses or psychiatric treatment.

If you or someone you know is in crisis or distress, please contact free, confidential support immediately:

- **United States & Canada**: Call or text **`988`** (Suicide & Crisis Lifeline, 24/7)
- **United Kingdom**: Call **`111`** (NHS) or text **`SHOUT`** to **`85258`**
- **India**: Call **`1800-599-0019`** (KIRAN Mental Health Helpline) or **`112`**
- **Australia**: Call **`13 11 14`** (Lifeline Australia)
- **International / Worldwide**: Visit [https://findahelpline.com](https://findahelpline.com) to find confidential local resources in your country.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
