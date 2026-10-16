# Quizly Backend - AI-Powered Video Quiz API

Select Language: [🇬🇧 English](#-english) | [🇩🇪 Deutsch](#-deutsch)

---

## 🇬🇧 English

This is the RESTful Backend for the **Quizly** platform, an innovative application that automatically transforms YouTube videos into interactive quizzes. It uses **FFmpeg** and **Whisper AI** for local audio transcription, prompts the **Gemini Flash API** for 10 questions with 4 options each, and falls back from Gemini 2.5 Flash to 1.5 Flash on server errors. The generated response is not validated against those counts.

The project was developed using **Test Driven Development (TDD)** and follows **Django REST Framework (DRF)** conventions.

### Table of Contents

1. [Prerequisites](#-prerequisites)
2. [Installation & Setup](#-installation--setup)
3. [Tech Stack](#-tech-stack)
4. [API Endpoints](#-api-endpoints)
5. [Security & Status Codes](#-security--status-codes)
6. [Testing & Quality](#-testing--quality)

---

### 📋 Prerequisites

Unlike standard Django applications, this project relies on **FFmpeg** to extract audio tracks from video files.

- **FFmpeg Installation**: You must have FFmpeg installed globally on your operating system and added to your system's PATH.
  - _Windows_: Install via Chocolatey (`choco install ffmpeg`) or download manually.
  - _Mac_: Install via Homebrew (`brew install ffmpeg`).
  - _Linux_: Install via APT (`sudo apt install ffmpeg`).
- **Redis**: Required as the Celery broker for background quiz generation.

---

### ⚙️ Installation & Setup

1. **Clone & Navigate**:
   ```bash
   git clone <your-repository-url>
   cd Quizly
   ```
2. **Environment Setup**:
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate | Mac/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Environment Variables**:
   ```bash
   cp .env.template .env
   # Update the values inside your private .env file in the root folder!
   ```
4. **Database & Server**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```
5. **Start Redis and the background worker** (in separate terminal sessions):
   ```bash
   redis-server
   celery -A core worker --loglevel=INFO
   ```
   Set `CELERY_BROKER_URL` in `.env` if Redis is not available at
   `redis://127.0.0.1:6379/0`. The worker must share access to this project's
   database and `media/audio` directory.
   For production, keep Redis and the worker running under a process manager
   (such as systemd or Supervisor) and enable persistence for the Redis broker.

---

### 🛠 Tech Stack

| Tool              | Version | Purpose                                      |
| :---------------- | :------ | :------------------------------------------- |
| **Django**        | 5.2.14  | Core Web Framework                           |
| **DRF**           | 3.17.1  | REST API Toolkit                             |
| **Pytest**        | 9.0.3   | Testing Framework (TDD)                      |
| **Pytest-Django** | 4.12.0  | Django integration for Pytest                |
| **Pytest-Cov**    | 7.1.0   | Test Coverage Reporting                      |
| **Celery**         | >=5.4, <6  | Background task processing                  |
| **yt-dlp**         | 2026.3.17  | High-performance YouTube Audio Extraction   |
| **openai-whisper** | 20250625   | Local audio transcription                   |
| **google-genai**   | 2.7.0      | Official Google AI Studio SDK (Gemini Flash) |

---

### 🚀 API Endpoints

Authentication uses **HttpOnly cookies** (`access_token` and `refresh_token`); frontend requests do not need manual authorization headers. The current implementation sets the cookie `Secure` flag to `False`, so enable it before deploying behind HTTPS.

#### 🔑 Authentication

| Method   | Endpoint              | Description                                                                          |
| :------- | :-------------------- | :----------------------------------------------------------------------------------- |
| **POST** | `/api/register/`      | Register a new account. Checks for unique email and matching passwords.              |
| **POST** | `/api/login/`         | Authenticate user, receive personal details, and set HttpOnly cookies.               |
| **POST** | `/api/logout/`        | Log out securely, clear cookies, and push the active refresh token to the blacklist. |
| **POST** | `/api/refresh/`       | Renew an expired access token using the HttpOnly refresh token cookie.               |

#### 🧠 AI Quiz Management

| Method     | Endpoint             | Description                                                                   |
| :--------- | :------------------- | :---------------------------------------------------------------------------- |
| **POST**   | `/api/quizzes/`      | Queue quiz generation and return a generation ID (`202 Accepted`). |
| **GET**    | `/api/quiz-generations/{id}/` | Poll generation status and receive the quiz when ready. |
| **GET**    | `/api/quizzes/`      | List all historical quizzes belonging specifically to the authenticated user. |
| **GET**    | `/api/quizzes/{id}/` | Retrieve a detailed quiz object with its generated questions (Owner only).   |
| **PATCH**  | `/api/quizzes/{id}/` | Partially update a quiz's title and description (Owner only).                 |
| **DELETE** | `/api/quizzes/{id}/` | Permanently delete a quiz and all cascade-related questions (Owner only).     |

Quiz generation is asynchronous: `POST /api/quizzes/` returns a `generation_id`
and `pending` status with HTTP 202. Poll
`GET /api/quiz-generations/{generation_id}/` while the status is `pending` or
`processing`, until it is `succeeded` (the response includes the quiz) or
`failed` (the response includes an error). The Gemini prompt requests exactly
10 questions with 4 options each, but the generated response is not validated
against those counts.

---

### 🛡 Security & Status Codes

The API strictly follows REST security and HTTP status code conventions:

- **200 OK**: Resource successfully requested or modified.
- **201 Created**: User successfully registered.
- **202 Accepted**: Quiz generation successfully queued.
- **204 No Content**: Quiz permanently and successfully deleted.
- **400 Bad Request**: Invalid input data, password mismatches, or invalid URLs.
- **401 Unauthorized**: Authentication cookies are missing, invalid, or expired.
- **403 Forbidden**: User is authenticated but lacks permission (e.g., trying to access someone else's quiz).
- **404 Not Found**: Target quiz does not exist in the database.
- **503 Service Unavailable**: The Celery broker is unavailable when a generation request is submitted.

---

### 🧪 Testing & Quality

- **Run all tests**: `python -m pytest`
- **Check Coverage report**: Open the generated `htmlcov/index.html` in your browser.

---

_Note: Sensitive configuration files (`.env`) and the local database (`db.sqlite3`) are excluded from version control to ensure security._

## 🇩🇪 Deutsch

Das REST-Backend für die **Quizly**-Plattform verwandelt YouTube-Videos mithilfe von künstlicher Intelligenz in interaktive Quizzes. Das System lädt Tonspuren mit **yt-dlp** herunter, extrahiert Audio über **FFmpeg**, transkribiert Texte lokal via **Whisper AI** und generiert mithilfe der **Gemini API** strukturierte Fragenkataloge. Ein integriertes Failover-System wechselt bei einem Gemini-Serverfehler automatisch von Gemini 2.5 Flash auf 1.5 Flash.

Entwickelt nach **TDD-Prinzipien** und den Konventionen von Django REST Framework (DRF).

### Inhaltsverzeichnis

1. [Systemvoraussetzungen](#-systemvoraussetzungen)
2. [Installation & Setup](#-installation--setup)
3. [Tech-Stack](#-tech-stack)
4. [API-Endpunkte](#-api-endpunkte)
5. [Sicherheit & Status-Codes](#-sicherheit--status-codes)
6. [Qualitätssicherung](#-qualitätssicherung)

### 📋 Systemvoraussetzungen

Dieses Projekt benötigt zwingend **FFmpeg** auf Systemebene, um die Audiokonvertierung für Whisper AI durchzuführen.

- **FFmpeg-Installation**: FFmpeg muss global installiert und in der PATH-Umgebungsvariable deines Systems hinterlegt sein.
  - _Windows_: Über Chocolatey (`choco install ffmpeg`) oder als manueller Download.
  - _Mac_: Über Homebrew (`brew install ffmpeg`).
  - _Linux_: Über den Paketmanager (`sudo apt install ffmpeg`).
- **Redis**: Wird als Broker für die asynchrone Quiz-Generierung mit Celery benötigt.

---

### 🚀 Installation & Setup

1. **Repository klonen & Verzeichnis wechseln**:
   ```bash
   git clone <deine-repo-url>
   cd Quizly
   ```
2. **Virtuelle Umgebung einrichten**:
   ```bash
   python -m venv .venv
   # Aktivieren (Windows)
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Umgebungsvariablen anlegen**:
   ```bash
   cp .env.template .env
   # Befülle die .env-Datei im Stammverzeichnis mit deinen echten API-Keys!
   ```
4. **Migrationen & Server starten**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```
5. **Redis und Celery-Worker starten** (in separaten Terminals):
   ```bash
   redis-server
   celery -A core worker --loglevel=INFO
   ```
   Falls Redis nicht unter `redis://127.0.0.1:6379/0` erreichbar ist, setze
   `CELERY_BROKER_URL` in `.env`. Webserver und Worker benötigen Zugriff auf
   dieselbe Datenbank und dasselbe Verzeichnis `media/audio`. In der
   Produktionsumgebung sollten Redis und Worker dauerhaft über einen
   Prozessmanager (z. B. systemd oder Supervisor) laufen; aktiviere außerdem
   die Redis-Persistenz.

---

### 🛠 Tech-Stack

| Tool             | Version       | Zweck                                     |
| :--------------- | :------------ | :---------------------------------------- |
| **Django**       | 5.2.14        | Kern-Web-Framework                        |
| **DRF**           | 3.17.1         | REST API Toolkit                          |
| **Pytest & Cov** | 9.0.3 / 7.1.0 | TDD-Testing und Abdeckungsberichte        |
| **Pytest-Django** | 4.12.0       | Django-Integration für Pytest             |
| **Celery**       | >=5.4, <6      | Verarbeitung asynchroner Hintergrundaufgaben |
| **yt-dlp**       | 2026.3.17      | YouTube-Audio-Extraktion                  |
| **openai-whisper** | 20250625     | Lokale Transkription der Audiodateien     |
| **google-genai** | 2.7.0          | Google AI Studio SDK (Gemini Integration) |

---

### 🚀 API-Endpunkte

Die Authentifizierung verwendet **HttpOnly-Cookies** (`access_token` und `refresh_token`); manuelle Authorization-Header sind im Frontend nicht erforderlich. Die aktuelle Implementierung setzt das Cookie-Flag `Secure` auf `False`. Aktiviere es vor einem Deployment hinter HTTPS.

#### 🔑 Authentifizierung

| Methode  | Endpunkt              | Beschreibung                                                                                       |
| :------- | :-------------------- | :------------------------------------------------------------------------------------------------- |
| **POST** | `/api/register/`      | Registriert ein neues Benutzerkonto. Prüft auf eindeutige E-Mails und übereinstimmende Passwörter. |
| **POST** | `/api/login/`         | Authentifiziert den Benutzer, liefert Profildaten und setzt HttpOnly-Cookies.                       |
| **POST** | `/api/logout/`        | Loggt den Benutzer sicher aus, leert die Cookies und setzt das Refresh-Token auf die Blacklist.    |
| **POST** | `/api/refresh/`       | Erneuert ein abgelaufenes Access-Token mithilfe des HttpOnly-Refresh-Cookies.                      |

#### 🧠 KI-Quiz-Verwaltung

| Methode    | Endpunkt             | Beschreibung                                                                            |
| :--------- | :------------------- | :-------------------------------------------------------------------------------------- |
| **POST**   | `/api/quizzes/`      | Startet die Generierung und liefert eine ID (`202 Accepted`).                           |
| **GET**    | `/api/quiz-generations/{id}/` | Liefert Status und nach Abschluss das fertige Quiz.                             |
| **GET**    | `/api/quizzes/`      | Listet alle bisherigen Quizze auf, die exakt dem angemeldeten Benutzer gehören.         |
| **GET**    | `/api/quizzes/{id}/` | Ruft ein spezifisches Quiz samt den generierten Fragen ab (Nur Besitzer).               |
| **PATCH**  | `/api/quizzes/{id}/` | Aktualisiert den Titel und die Beschreibung eines Quizzes partiell (Nur Besitzer).      |
| **DELETE** | `/api/quizzes/{id}/` | Löscht ein Quiz und alle verknüpften Fragen permanent aus der Datenbank (Nur Besitzer). |

---

### 🛡 Sicherheit & Status-Codes

Der Gemini-Prompt fordert genau 10 Fragen mit jeweils 4 Antwortmöglichkeiten an. Die generierte Antwort wird jedoch nicht auf diese Anzahl geprüft.

- **200 OK**: Anfrage erfolgreich verarbeitet.
- **201 Created**: Benutzerkonto erfolgreich registriert.
- **202 Accepted**: Quiz-Generierung erfolgreich in die Warteschlange gestellt.
- **204 No Content**: Quiz permanent und erfolgreich gelöscht.
- **400 Bad Request**: Ungültige Daten, falsche URLs oder ungleiche Passwörter.
- **401 Unauthorized**: Authentifizierungs-Cookies fehlen oder sind abgelaufen.
- **403 Forbidden**: Zugriff verweigert (z. B. Abruf eines fremden Quizzes).
- **404 Not Found**: Quiz existiert nicht in der Datenbank.
- **503 Service Unavailable**: Der Celery-Broker ist beim Einreichen einer Quiz-Generierung nicht erreichbar.

---

### 🧪 Qualitätssicherung

- **Automatische Tests ausführen**: `python -m pytest`
- **Abdeckungsbericht einsehen**: Öffne die Datei `htmlcov/index.html` im Browser.

---

_Hinweis: Sensible Konfigurationsdaten (`.env`) und die lokale Datenbank (`db.sqlite3`) sind über die `.gitignore` vom Hochladen auf GitHub ausgeschlossen._
