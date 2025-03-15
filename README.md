# Bank Case Manager
A small-scale case and file manager for basic banking affairs

## Table of Contents
- [Getting Started](#getting-started)
  - [Dependencies](#dependencies)
  - [Configuration File](#configuration-file)
  - [Running the Application](#running-the-application)
- [Code Overview](#code-overview)
- [Testing Instructions](#testing-instructions)
- [License](#license)

## Getting Started
### Dependencies
To run this project, you need:
- Python 3.x
- Virtual environment (optional but recommended)
- Required libraries from `requirements.txt`

Install dependencies using:
```bash
pip install -r requirements.txt
```

## Code Overview
code structure:
```
/bank_case_manager
│── app.py               # Main entry point
│── config.py            # Configuration settings
│── db/
│   ├── models.py        # Database models
│   ├── database.py      # Database connection
│── services/
│   ├── case_service.py  # Case management logic
│   ├── report_service.py# Report generation logic
│── routes/
│   ├── main.py          # Dashboard and main routes
│   ├── cases.py         # Case-related routes
│   ├── reports.py       # Report-related routes
│── utils/
│   ├── excel_import.py  # Excel import utilities
│── templates/           # HTML templates
│── static/              # CSS, JS, and other static files
│── logs/                # Log files
│── backups/             # Database backups
```

## Testing Instructions


## License
