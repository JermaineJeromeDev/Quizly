# Quizly Backend - AI-Powered Video Quiz API

Select Language: [🇬🇧 English](#-english) | [🇩🇪 Deutsch](#-deutsch)

---

## 🇬🇧 English

This is the RESTful Backend for the **Quizly** platform, an innovative application that automatically transforms YouTube videos into interactive quizzes. It uses **FFmpeg** and **Whisper AI** for local audio transcription, orchestrates prompts for the **Gemini Flash API** to generate exactly 10 questions with 4 options each, and features an advanced automatic fallback system for maximum stability.

The project was developed using **Test Driven Development (TDD)**, adheres strictly to **DRF best practices**, and enforces a clean code structure with functions capped at 14 lines.

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

---

### ⚙️ Installation & Setup

1. **Clone & Navigate**:
   ```bash
   git clone <your-repository-url>
   cd quizly_backend
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

---

### 🛠 Tech Stack

| Tool              | Version | Purpose                                      |
| :---------------- | :------ | :------------------------------------------- |
| **Django**        | 5.2.14  | Core Web Framework                           |
| **DRF**           | 3.15.x  | REST API Toolkit                             |
| **Pytest**        | 9.0.3   | Testing Framework (TDD)                      |
| **Pytest-Django** | 4.12.0  | Django integration for Pytest                |
| **Pytest-Cov**    | 7.1.0   | Test Coverage Reporting                      |
| **yt-dlp**        | 2025.x  | High-performance YouTube Audio Extraction    |
| **whisper**       | latest  | Local OpenAI Transcription Engine            |
| **google-genai**  | latest  | Official Google AI Studio SDK (Gemini Flash) |

---

### 🚀 API Endpoints

Authentication is strictly handled via secure **HttpOnly Cookies** (`access_token` and `refresh_token`). No manual authorization headers are required in frontend requests.

#### 🔑 Authentication

| Method   | Endpoint              | Description                                                                          |
| :------- | :-------------------- | :----------------------------------------------------------------------------------- |
| **POST** | `/api/register/`      | Register a new account. Checks for unique email and matching passwords.              |
| **POST** | `/api/login/`         | Authenticate user, receive personal details, and set secure HttpOnly cookies.        |
| **POST** | `/api/logout/`        | Log out securely, clear cookies, and push the active refresh token to the blacklist. |
| **POST** | `/api/token/refresh/` | Renew an expired access token using the HttpOnly refresh token cookie.               |

#### 🧠 AI Quiz Management

| Method     | Endpoint             | Description                                                                   |
| :--------- | :------------------- | :---------------------------------------------------------------------------- |
| **POST**   | `/api/quizzes/`      | Generate a new AI quiz from a YouTube URL (Uses yt_dlp, Whisper, and Gemini). |
| **GET**    | `/api/quizzes/`      | List all historical quizzes belonging specifically to the authenticated user. |
| **GET**    | `/api/quizzes/{id}/` | Retrieve a detailed quiz object with its 10 nested questions (Owner only).    |
| **PATCH**  | `/api/quizzes/{id}/` | Partially update a quiz's title and description (Owner only).                 |
| **DELETE** | `/api/quizzes/{id}/` | Permanently delete a quiz and all cascade-related questions (Owner only).     |

---

### 🛡 Security & Status Codes

The API strictly follows REST security and HTTP status code conventions:

- **200 OK**: Resource successfully requested or modified.
- **201 Created**: Quiz or user successfully generated.
- **204 No Content**: Quiz permanently and successfully deleted.
- **400 Bad Request**: Invalid input data, password mismatches, or invalid URLs.
- **401 Unauthorized**: Secure cookies are missing, invalid, or expired.
- **403 Forbidden**: User is authenticated but lacks permission (e.g., trying to access someone else's quiz).
- **404 Not Found**: Target quiz does not exist in the database.

---

### 🧪 Testing & Quality

- **Run all tests**: `python -m pytest`
- **Check Coverage report**: Open the generated `htmlcov/index.html` in your browser.

---

_Note: Sensitive configuration files (`.env`) and the local database (`db.sqlite3`) are excluded from version control to ensure security._

## 🇩🇪 Deutsch

Das REST-Backend für die **Quizly**-Plattform verwandelt YouTube-Videos mithilfe von künstlicher Intelligenz in interaktive Quizzes. Das System lädt Tonspuren mit **yt_dlp** herunter, extrahiert Audio über **FFmpeg**, transkribiert Texte lokal via **Whisper AI** und generiert mithilfe der kostenlosen **Gemini Flash API** strukturierte Fragenkataloge. Ein integriertes Failover-System schaltet bei Google-Überlastungen automatisch von Gemini 2.5 auf 1.5 Flash um.

Entwickelt nach strengen **TDD-Prinzipien** und den DRF Best Practices. Alle Funktionen sind maximal 14 Zeilen lang.

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

---

### 🚀 Installation & Setup

1. **Repository klonen & Verzeichnis wechseln**:
   ```bash
   git clone <deine-repo-url>
   cd quizly_backend
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

---

### 🛠 Tech-Stack

| Tool             | Version       | Zweck                                     |
| :--------------- | :------------ | :---------------------------------------- |
| **Django**       | 5.2.14        | Kern-Web-Framework                        |
| **DRF**          | 3.15.x        | REST API Toolkit                          |
| **Pytest & Cov** | 9.0.3 / 7.1.0 | TDD-Testing und Abdeckungsberichte        |
| **yt-dlp**       | 2025.x        | YouTube-Audio-Extraktion                  |
| **whisper**      | latest        | Lokale Transkription der Audiodateien     |
| **google-genai** | latest        | Google AI Studio SDK (Gemini Integration) |

---

### 🚀 API-Endpunkte

Die Authentifizierung wird vollständig über sichere **HttpOnly-Cookies** (`access_token` und `refresh_token`) abgewickelt. Es sind keine manuellen Authorization-Header im Frontend erforderlich.

#### 🔑 Authentifizierung

| Methode  | Endpunkt              | Beschreibung                                                                                       |
| :------- | :-------------------- | :------------------------------------------------------------------------------------------------- |
| **POST** | `/api/register/`      | Registriert ein neues Benutzerkonto. Prüft auf eindeutige E-Mails und übereinstimmende Passwörter. |
| **POST** | `/api/login/`         | Authentifiziert den Benutzer, liefert Profildaten und setzt sichere HttpOnly-Cookies.              |
| **POST** | `/api/logout/`        | Loggt den Benutzer sicher aus, leert die Cookies und setzt das Refresh-Token auf die Blacklist.    |
| **POST** | `/api/token/refresh/` | Erneuert ein abgelaufenes Access-Token mithilfe des HttpOnly-Refresh-Cookies.                      |

#### 🧠 KI-Quiz-Verwaltung

| Methode    | Endpunkt             | Beschreibung                                                                            |
| :--------- | :------------------- | :-------------------------------------------------------------------------------------- |
| **POST**   | `/api/quizzes/`      | Generiert ein neues KI-Quiz aus einer YouTube-URL (Nutzt yt_dlp, Whisper und Gemini).   |
| **GET**    | `/api/quizzes/`      | Listet alle bisherigen Quizze auf, die exakt dem angemeldeten Benutzer gehören.         |
| **GET**    | `/api/quizzes/{id}/` | Ruft ein spezifisches Quiz samt seinen 10 verschachtelten Fragen ab (Nur Besitzer).     |
| **PATCH**  | `/api/quizzes/{id}/` | Aktualisiert den Titel und die Beschreibung eines Quizzes partiell (Nur Besitzer).      |
| **DELETE** | `/api/quizzes/{id}/` | Löscht ein Quiz und alle verknüpften Fragen permanent aus der Datenbank (Nur Besitzer). |

---

### 🛡 Sicherheit & Status-Codes

Die Authentifizierung erfolgt vollständig über sichere **HttpOnly-Cookies** (`access_token` und `refresh_token`), um Cross-Site-Scripting (XSS) im Frontend auszuschließen.

- **200 OK**: Anfrage erfolgreich verarbeitet.
- **201 Created**: Benutzer oder Quiz erfolgreich erstellt.
- **204 No Content**: Quiz permanent und erfolgreich gelöscht.
- **400 Bad Request**: Ungültige Daten, falsche URLs oder ungleiche Passwörter.
- **401 Unauthorized**: Authentifizierungs-Cookies fehlen oder sind abgelaufen.
- **403 Forbidden**: Zugriff verweigert (z. B. Abruf eines fremden Quizzes).
- **404 Not Found**: Quiz existiert nicht in der Datenbank.

---

### 🧪 Qualitätssicherung

- **Automatische Tests ausführen**: `python -m pytest`
- **Abdeckungsbericht einsehen**: Öffne die Datei `htmlcov/index.html` im Browser.

---

_Hinweis: Sensible Konfigurationsdaten (`.env`) und die lokale Datenbank (`db.sqlite3`) sind über die `.gitignore` vom Hochladen auf GitHub ausgeschlossen._
