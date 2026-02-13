<p align="center">
  <img src="assets/logo.png" alt="AccessTwin Logo" width="150">
</p>

<h1 align="center">AccessTwin</h1>

<p align="center">
  <strong>Digital Accessibility Twin Manager</strong><br>
  A desktop application that creates "Digital Accessibility Twins" for students with accommodations, allowing teachers to assess and plan supports before meeting with students.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/framework-PyQt6-green" alt="PyQt6">
  <img src="https://img.shields.io/badge/license-Apache%202.0-orange" alt="License">
  <img src="https://img.shields.io/badge/WCAG-2.1%20AA-purple" alt="WCAG 2.1 AA">
  <img src="https://img.shields.io/badge/tests-37%20passing-brightgreen" alt="Tests">
</p>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [AI Backend Configuration](#ai-backend-configuration)
- [Accessibility](#accessibility)
- [Testing](#testing)
- [Roadmap](#roadmap)
- [Changelog](#changelog)
- [License](#license)

---

## Overview

AccessTwin is built by **Tech Inclusion Pro** to bridge the gap between students who need accommodations and teachers who provide them. Students create rich profiles documenting their strengths, supports, and goals. Teachers upload learning materials and receive AI-powered analysis of how well those materials align with each student's accessibility needs — all without needing to meet first.

The application follows a **local-first, privacy-focused** architecture. All data is stored locally with AES-256 encryption, and AI processing defaults to local models (Ollama, LM Studio, GPT4All). Cloud AI providers (OpenAI, Anthropic) are available but require explicit dual consent.

---

## Features

### Role-Based Authentication
- **Two distinct roles:** Student and Teacher, each with their own login tab and color-coded UI
- **Secure accounts** with bcrypt password hashing and configurable security questions
- **Password recovery** through a multi-step security question verification flow
- **Audit logging** — every login, logout, registration, and password reset is recorded

### Three-Tab Login Screen
- **Student Login** — Magenta accent (#a23b84)
- **Teacher Login** — Deep blue accent (#3a2b95)
- **Register** — Purple accent (#6f2fa6) with role selector, password confirmation, security question, and terms consent
- Password visibility toggle, forgot password flow, and pre-login accessibility toolbar

### AI Backend Selector
AccessTwin supports multiple AI providers for analyzing learning materials against student profiles:

| Provider | Type | Default Model | Connection |
|----------|------|---------------|------------|
| **Ollama** | Local | gemma3:4b | localhost:11434 |
| **LM Studio** | Local | default | localhost:1234 |
| **GPT4All** | Local | Llama 3 8B | Direct Python |
| **OpenAI** | Cloud | gpt-4o | API |
| **Anthropic** | Cloud | Claude | API |

- **Local-first default** — no data leaves the machine unless explicitly configured
- **Connection testing** — verify provider connectivity before saving
- **Dual cloud consent** — both institutional approval and data transmission acknowledgment required

### Encrypted Database
- **SQLite** via SQLAlchemy ORM with 8 tables:
  - `users` — accounts with role, credentials, settings
  - `student_profiles` — strengths, supports, history, hopes, stakeholders
  - `support_entries` — categorized supports with UDL/POUR mappings and effectiveness ratings
  - `documents` — uploaded teacher materials
  - `twin_evaluations` — AI analysis results with confidence scores
  - `tracking_logs` — implementation and outcome tracking
  - `audit_logs` — security event trail
  - `consent_records` — data consent tracking
- **AES-256 field-level encryption** (Fernet) for sensitive data, with PBKDF2 key derivation from machine identity

### Support Categorization
Student supports are organized across seven categories aligned with educational frameworks:

| Category | Examples |
|----------|----------|
| Sensory | Large print, screen reader, captioning, FM system |
| Motor | Alternative keyboard, voice-to-text, accessible seating |
| Cognitive | Simplified instructions, visual schedules, chunked assignments |
| Communication | AAC device, visual supports, social stories |
| Social-Emotional | Calm-down space, peer buddy system, check-in system |
| Executive Function | Task checklists, visual timers, organizational systems |
| Environmental | Adapted workspace, sensory considerations |

### Comprehensive Accessibility (WCAG 2.1 AA)
- **Font scaling** — Small, Medium, Large, Extra Large presets
- **Color blind modes** — Protanopia, Deuteranopia, Tritanopia, Monochrome (based on Wong 2011 palette)
- **High contrast mode** — enhanced text visibility
- **Dyslexia-friendly font** toggle
- **Custom cursors** — Large black, Large white, Crosshair, High visibility (yellow/black), Pointer with trail
- **Reading ruler** — horizontal highlight band that follows cursor position
- **Reduced motion** — disable animations
- **Enhanced focus indicators** — thicker outlines on focused elements
- **Device-level persistence** — preferences saved to `~/.accesstwin/` and restored before login
- **Pre-login access** — accessibility toolbar visible on the login screen

### Keyboard Navigation
- All interactive widgets have `StrongFocus` policy
- Labels linked to inputs via `setBuddy()`
- Minimum 44x44px touch targets
- Logical tab order on every screen
- Focus set automatically after screen transitions
- `Ctrl+/` — Keyboard shortcuts reference dialog
- `Ctrl+Q` — Quit application

### Data-Driven Frameworks
Built-in JSON reference data for:
- **UDL Checkpoints** — Engagement, Representation, Action & Expression
- **WCAG Criteria** — Perceivable, Operable, Understandable, Robust
- **POUR Principles** — with descriptions and guidelines
- **Support Templates** — pre-built support entries by category
- **Color Palettes** — Wong 2011 color-blind safe palette

---

## Installation

### Prerequisites
- **Python 3.10** or later
- **macOS 12+** (primary platform; Linux/Windows also supported)

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Tech-Inclusion-Pro/Digital-Accessiblity-Twin.git
   cd Digital-Accessiblity-Twin
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### macOS Application Bundle

On macOS, AccessTwin can be installed as a native application in `/Applications/`:

```bash
# The app bundle can be created by placing the launcher at:
# /Applications/AccessTwin.app/Contents/MacOS/AccessTwin
# See project documentation for full .app bundle setup
```

Once installed, launch from **Finder**, **Spotlight** (search "AccessTwin"), or **Launchpad**.

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PyQt6 | >= 6.5.0 | Desktop UI framework |
| SQLAlchemy | >= 2.0 | Database ORM |
| bcrypt | latest | Password hashing |
| aiohttp | latest | Async HTTP for AI backends |
| cryptography | latest | AES-256 field encryption |

---

## Usage

### First Launch

1. **Open AccessTwin** — the three-tab login screen appears
2. **Adjust accessibility settings** using the toolbar at the top (font size, contrast, color mode) — these persist across sessions
3. **Create an account** — click the "Register" tab, select your role (Student or Teacher), fill in credentials, choose a security question, agree to terms, and click "Create Account"
4. **Log in** — use the Student Login or Teacher Login tab matching your role

### Student Workflow (Phase 2+)

1. Log in on the **Student Login** tab
2. Create your accessibility profile — document strengths, needed supports, history, and goals
3. Categorize each support (sensory, motor, cognitive, etc.)
4. Map supports to UDL checkpoints and POUR principles
5. Share your Digital Twin with your teachers

### Teacher Workflow (Phase 2+)

1. Log in on the **Teacher Login** tab
2. Upload learning materials (documents, assignments, assessments)
3. Select a student's Digital Twin profile
4. Run AI analysis to evaluate material accessibility against the student's needs
5. Review suggestions, confidence scores, and AI reasoning
6. Track implementation and outcomes over time

### AI Configuration

1. From the dashboard, open **AI Settings** (Setup Wizard)
2. Choose **Local** (recommended) or **Cloud**
3. For local: select Ollama/LM Studio/GPT4All, set server URL and model
4. For cloud: select OpenAI/Anthropic, enter API key, and check **both** consent boxes
5. Click **Test Connection** to verify
6. Click **Save Configuration**

### Password Recovery

1. Click "Forgot password?" on the login screen
2. Enter your username
3. Answer your security question(s)
4. Set a new password (minimum 8 characters)

---

## Project Structure

```
accesstwin/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── assets/
│   └── logo.png                     # Application logo
├── config/
│   ├── brand.py                     # Brand colors, role accents, spacing
│   ├── constants.py                 # Enums (UserRole, SupportCategory, etc.)
│   └── settings.py                  # Color scheme, app settings, get_colors()
├── data/
│   ├── udl_checkpoints.json         # UDL framework reference data
│   ├── wcag_criteria.json           # WCAG 2.1 criteria reference
│   ├── pour_principles.json         # POUR principles reference
│   ├── support_templates.json       # Pre-built support templates
│   └── color_palettes.json          # Color-blind safe palettes
├── models/
│   ├── database.py                  # DatabaseManager, SQLAlchemy setup
│   ├── auth.py                      # AuthManager with role enforcement
│   ├── user.py                      # User model
│   ├── student_profile.py           # StudentProfile model
│   ├── support.py                   # SupportEntry model
│   ├── document.py                  # Document model
│   ├── evaluation.py                # TwinEvaluation model
│   ├── tracking.py                  # TrackingLog model
│   └── audit.py                     # AuditLog + ConsentRecord models
├── ai/
│   ├── backend_manager.py           # Unified AI facade
│   ├── ollama_client.py             # Ollama local client
│   ├── lmstudio_client.py           # LM Studio client (OpenAI-compatible)
│   ├── gpt4all_client.py            # GPT4All direct Python client
│   ├── cloud_client.py              # OpenAI + Anthropic cloud client
│   └── prompts/
│       └── __init__.py              # System prompt stubs (Phase 2)
├── ui/
│   ├── accessibility.py             # AccessibilityManager singleton
│   ├── accessibility_prefs.py       # Device-level prefs persistence
│   ├── color_blind_engine.py        # Wong 2011 palette, contrast validation
│   ├── cursor_trail.py              # Cursor trail overlay widget
│   ├── reading_ruler.py             # Reading ruler overlay widget
│   ├── focus_manager.py             # Keyboard nav, tab trapping, announcements
│   ├── theme.py                     # Convenience re-exports
│   ├── theme_engine.py              # QSS generation with role-aware accents
│   ├── navigation.py                # MainWindow, screen routing
│   ├── screens/
│   │   ├── login_screen.py          # Three-tab login (Student/Teacher/Register)
│   │   └── setup_wizard.py          # AI backend configuration wizard
│   └── components/
│       ├── accessibility_panel.py   # Full accessibility preferences dialog
│       ├── accessibility_toolbar.py # Quick-access font/contrast/color bar
│       ├── breadcrumb.py            # Navigation breadcrumb trail
│       ├── empty_state.py           # Empty state placeholder
│       ├── help_button.py           # Contextual help button
│       └── shortcuts_dialog.py      # Keyboard shortcuts reference (Ctrl+/)
├── utils/
│   ├── encryption.py                # AES-256 Fernet encryption manager
│   └── validators.py                # Input validation (username, password, email)
├── tests/
│   ├── conftest.py                  # Shared fixtures (tmp DB, auth manager)
│   ├── test_database.py             # Table creation, CRUD, encryption roundtrip
│   ├── test_auth.py                 # Registration, login, role enforcement, recovery
│   ├── test_ai_backends.py          # Connection test mocks for all providers
│   └── test_accessibility.py        # Color blind palettes, contrast, prefs persistence
├── fonts/                           # Reserved for bundled fonts (Phase 2)
└── tutorials/                       # Reserved for tutorial content (Phase 2)
```

---

## AI Backend Configuration

### Ollama (Recommended for Local Use)

1. Install Ollama: https://ollama.com
2. Pull a model: `ollama pull gemma3:4b`
3. Ollama runs automatically on `localhost:11434`
4. In AccessTwin, select **Local > Ollama** and click **Test Connection**

### LM Studio

1. Install LM Studio: https://lmstudio.ai
2. Download a model and start the local server
3. Server runs on `localhost:1234` by default
4. In AccessTwin, select **Local > LM Studio**

### GPT4All

1. Install: `pip install gpt4all`
2. Models download automatically on first use
3. In AccessTwin, select **Local > GPT4All**

### Cloud Providers (OpenAI / Anthropic)

Cloud usage requires **dual consent**:
1. **Institutional approval** — confirm your institution permits cloud AI for student data
2. **Data transmission acknowledgment** — understand that data will be sent to a third-party service

Both checkboxes must be checked before cloud configuration can be saved.

---

## Accessibility

AccessTwin is built with accessibility as a core principle, not an afterthought. The accessibility system works **before login** so all users can configure their experience immediately.

### Pre-Login Accessibility Toolbar
Available on the login screen with quick controls for:
- Font size increase/decrease
- High contrast toggle
- Color blind mode selector
- Full settings button

### Full Accessibility Panel
Accessed via the "Settings" button, with options organized into four groups:

| Group | Settings |
|-------|----------|
| **Text & Font** | Font size (4 scales), dyslexia-friendly font |
| **Colors & Contrast** | High contrast mode, color blind mode (5 options) |
| **Cursor & Reading** | Custom cursor (6 styles), reading ruler overlay |
| **Motion & Focus** | Reduced motion, enhanced focus indicators |

### Color Blind Modes
Based on the **Wong 2011** color palette (Nature Methods), ensuring all UI elements remain distinguishable:

| Mode | Condition | Adaptation |
|------|-----------|------------|
| Protanopia | Red-blind | Blue/green substitutions |
| Deuteranopia | Green-blind | Blue/orange substitutions |
| Tritanopia | Blue-blind | Pink/green substitutions |
| Monochrome | Grayscale | Full grayscale palette |

### WCAG 2.1 AA Compliance
- All text meets minimum contrast ratios (4.5:1 normal, 3:1 large)
- Every interactive element has an accessible name and description
- Full keyboard operability with visible focus indicators
- Touch targets minimum 44x44px
- Screen reader compatible via Qt accessibility API

---

## Testing

Run the full test suite:

```bash
cd Digital-Accessiblity-Twin
python -m pytest tests/ -v
```

### Test Coverage

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_database.py` | 6 | Table creation, User CRUD, profile JSON, encryption roundtrip |
| `test_auth.py` | 11 | Registration (student/teacher/duplicate/validation), login (success/wrong password/wrong role/nonexistent), password recovery, hashing |
| `test_ai_backends.py` | 6 | Ollama connection (success/failure), LM Studio, OpenAI cloud, Anthropic key validation, BackendManager no-client |
| `test_accessibility.py` | 10 | Contrast ratios, WCAG AA/AAA pass checks, Wong palette, prefs save/load, AccessibilityManager singleton/overrides/serialization |
| **Total** | **37** | |

---

## Roadmap

### Phase 1 (Current) — Foundation
- [x] Project scaffolding and configuration
- [x] Encrypted SQLite database with 8 tables
- [x] Role-based authentication (student/teacher)
- [x] Three-tab login screen with brand theming
- [x] AI backend selector (5 providers)
- [x] Comprehensive accessibility infrastructure
- [x] WCAG 2.1 AA compliance
- [x] 37 passing tests

### Phase 2 — Student Profiles & Twin Creation
- [ ] Student profile builder (strengths, supports, history, hopes)
- [ ] Support entry wizard with UDL/POUR mapping
- [ ] Digital Twin generation and visualization
- [ ] Student dashboard with profile management
- [ ] Bundled fonts (OpenDyslexic)
- [ ] Tutorial system

### Phase 3 — Teacher Tools & AI Analysis
- [ ] Document upload and management
- [ ] AI-powered material evaluation against student profiles
- [ ] Suggestion engine with confidence scores
- [ ] Teacher dashboard with student twin browsing
- [ ] Implementation tracking and outcome logging

### Phase 4 — Collaboration & Reporting
- [ ] Student-teacher profile sharing
- [ ] Progress reporting and analytics
- [ ] Export to PDF/accessible formats
- [ ] Multi-student batch analysis
- [ ] Institutional admin features

---

## Changelog

### v1.0.0 — Phase 1 Foundation (2025-02-13)

**Added**
- **Project scaffolding** — complete directory structure with config, models, AI, UI, utils, tests, and data packages
- **Entry point** (`main.py`) — HiDPI support, palette setup, font configuration, pre-login accessibility preference loading
- **Brand identity** (`config/brand.py`) — primary purple (#6f2fa6), student magenta (#a23b84), teacher blue (#3a2b95) with role accent system and spacing constants
- **Configuration** (`config/settings.py`) — dark theme color scheme with accessibility override hook via `get_colors()`
- **Constants** (`config/constants.py`) — UserRole, SupportCategory, Severity, SupportStatus enums and security question options
- **Database layer** (`models/database.py`) — SQLAlchemy ORM with SQLite, 8 tables created automatically on first run
- **User model** (`models/user.py`) — role, username, password hash, display name, email, settings JSON, security questions, timestamps
- **Student profile model** (`models/student_profile.py`) — strengths, supports, history, hopes, stakeholders as JSON fields
- **Support model** (`models/support.py`) — category, subcategory, UDL/POUR mapping, effectiveness rating
- **Document model** (`models/document.py`) — teacher file uploads with binary blob storage
- **Evaluation model** (`models/evaluation.py`) — AI analysis, suggestions, confidence scores, reasoning
- **Tracking model** (`models/tracking.py`) — implementation and outcome notes per support
- **Audit model** (`models/audit.py`) — AuditLog for security events, ConsentRecord for data consent
- **Encryption** (`utils/encryption.py`) — AES-256 via Fernet with PBKDF2 key derivation from machine ID, salt stored in Application Support
- **Authentication** (`models/auth.py`) — register/login with role enforcement, bcrypt hashing, security question recovery, password reset, audit trail
- **Input validators** (`utils/validators.py`) — username (3-50 chars, alphanumeric), password (8+ chars), email format
- **Accessibility manager** (`ui/accessibility.py`) — singleton with font scales, color blind modes, custom cursors, reading ruler, role accent, serialization
- **Accessibility prefs** (`ui/accessibility_prefs.py`) — device-level JSON persistence at `~/.accesstwin/`
- **Color blind engine** (`ui/color_blind_engine.py`) — Wong 2011 palette, WCAG contrast ratio calculator, AA/AAA pass checks
- **Cursor trail** (`ui/cursor_trail.py`) — transparent overlay with fading cursor images at recent positions
- **Reading ruler** (`ui/reading_ruler.py`) — horizontal highlight band following cursor Y position
- **Focus manager** (`ui/focus_manager.py`) — post-transition focus, screen reader announcements, tab trapping in modals
- **Theme engine** (`ui/theme_engine.py`) — full QSS generation with role-aware accents, enhanced focus, dyslexia font support
- **Main window** (`ui/navigation.py`) — QStackedWidget screen routing, manager initialization, cursor/ruler overlays, global shortcuts
- **Three-tab login screen** (`ui/screens/login_screen.py`) — Student Login, Teacher Login, Register with role-specific accents, password toggle, forgot password dialog, consent checkbox, logo display
- **Setup wizard** (`ui/screens/setup_wizard.py`) — AI backend configuration with local/cloud selection, connection testing, dual cloud consent
- **Accessibility panel** (`ui/components/accessibility_panel.py`) — full settings dialog with font, color, cursor, motion groups
- **Accessibility toolbar** (`ui/components/accessibility_toolbar.py`) — quick-access font +/-, contrast toggle, color mode dropdown
- **Help button** (`ui/components/help_button.py`) — contextual "?" button (content stub for Phase 2)
- **Breadcrumb** (`ui/components/breadcrumb.py`) — clickable navigation trail widget
- **Empty state** (`ui/components/empty_state.py`) — placeholder with icon, message, and action button
- **Shortcuts dialog** (`ui/components/shortcuts_dialog.py`) — keyboard shortcuts reference via Ctrl+/
- **AI backend manager** (`ai/backend_manager.py`) — unified facade over local and cloud clients
- **Ollama client** (`ai/ollama_client.py`) — streaming chat, model listing, connection testing
- **LM Studio client** (`ai/lmstudio_client.py`) — OpenAI-compatible API on localhost:1234
- **GPT4All client** (`ai/gpt4all_client.py`) — direct Python library with streaming
- **Cloud client** (`ai/cloud_client.py`) — OpenAI and Anthropic APIs with streaming
- **Reference data** — UDL checkpoints, WCAG criteria, POUR principles, support templates, color palettes as JSON
- **Test suite** — 37 tests covering database, authentication, AI backends, and accessibility
- **macOS app bundle** — launchable from /Applications via Finder or Spotlight

---

## License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with care by <strong>Tech Inclusion Pro</strong><br>
  Ensuring every student's accessibility needs are understood before the first lesson begins.
</p>
