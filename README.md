# Cloud-Based Vehicle Data Storage

A cloud-ready vehicle telemetry platform built using FastAPI, SQLAlchemy, SQLite, JWT authentication, and Streamlit.

The system simulates vehicle telemetry, securely uploads the data to a REST API, stores it in a relational database, performs analytics, automatically detects vehicle alerts, and visualizes the results through an interactive dashboard.

---

## Project Overview

Modern connected vehicles continuously generate telemetry such as:

- Vehicle speed
- Engine RPM
- Engine temperature
- Fuel level
- Battery voltage
- GPS latitude
- GPS longitude

This project provides a backend system for receiving, validating, storing, querying, and analyzing this telemetry.

The platform also automatically generates alerts when abnormal vehicle conditions are detected.

---

## System Architecture

Vehicle Simulator
        |
        | REST API + JWT
        v
FastAPI Backend
        |
        | SQLAlchemy ORM
        v
SQLite Database
        |
        +----------------+
        |                |
        v                v
Telemetry Data       Alert Data
        |
        v
Analytics API
        |
        v
Streamlit Dashboard

---

## Features

### 1. Vehicle Management

The system supports registration and management of multiple vehicles.

Each vehicle contains:

- Vehicle ID
- VIN
- Manufacturer
- Model
- Manufacturing year

---

### 2. Vehicle Telemetry

The simulator continuously generates realistic telemetry data including:

- Speed
- Engine RPM
- Engine temperature
- Fuel level
- Battery voltage
- GPS coordinates

Telemetry is uploaded to the FastAPI backend every few seconds.

---

### 3. JWT Authentication

The API is protected using JWT-based authentication.

Users must authenticate before accessing protected endpoints.

Authentication credentials and the JWT secret are stored in environment variables using `.env`.

---

### 4. Data Validation

Incoming telemetry is validated using Pydantic.

Examples:

- Speed cannot be negative.
- Speed cannot exceed the configured maximum.
- RPM must remain within a valid range.
- Fuel level must be between 0 and 100.
- GPS coordinates must be valid.

Invalid data is rejected with an appropriate HTTP response.

---

### 5. Automatic Alert Detection

The system automatically generates alerts when abnormal conditions are detected.

Current alert conditions include:

| Condition | Alert | Severity |
|---|---|---|
| Speed > 100 km/h | Overspeed | WARNING |
| Engine temperature > 95°C | Engine Overheating | CRITICAL |
| Fuel < 20% | Low Fuel | WARNING |
| Battery voltage < 11.5V | Low Battery | CRITICAL |

---

### 6. Telemetry Analytics

The backend provides vehicle-level analytics including:

- Total telemetry records
- Average speed
- Maximum speed
- Average engine RPM
- Maximum engine temperature
- Minimum fuel level
- Average battery voltage

---

### 7. Multi-Vehicle Support

The system supports multiple vehicles simultaneously.

Each vehicle has independent:

- Telemetry records
- Analytics
- Alerts
- Dashboard information

---

### 8. Interactive Dashboard

A Streamlit dashboard provides:

- Vehicle selection
- Vehicle information
- Vehicle status
- Alert summary
- Telemetry statistics
- Speed analysis
- Engine analysis
- Fuel analysis
- Battery analysis
- Alert history
- Latest telemetry

---

## Technology Stack

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic

### Database

- SQLite

### Authentication

- JWT
- python-jose

### Simulator

- Python
- Requests
- Random telemetry generation

### Dashboard

- Streamlit
- Pandas
- Plotly

### Development

- Visual Studio Code
- Python Virtual Environment
- REST API
- Swagger/OpenAPI

---

## Project Structure

```text
wipro_project/
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── auth.py
│       ├── database.py
│       │
│       ├── models/
│       │   ├── vehicle.py
│       │   ├── telemetry.py
│       │   └── alert.py
│       │
│       └── schemas/
│           ├── vehicle.py
│           └── telemetry.py
│
├── simulator/
│   └── vehicle_simulator.py
│
├── dashboard/
│   └── app.py
│
├── .env
├── .gitignore
├── requirements.txt
├── README.md
└── vehicle_telemetry.db