# Marketing Automation CRM - CS411 Project

A Flask-based web application that implements a Marketing Automation module for a CRM system. This project demonstrates customer segmentation, campaign management, and marketing analytics using CSV-based storage.

## Project Overview

This application is part of a CS411 Software Architecture course project at Bilkent University. It focuses on the Marketing Automation component of a larger CRM system.

### Features

- **User Authentication**: Simple session-based login/logout system
- **Customer Segmentation**: Create customer segments based on age, location, and spending criteria
- **Campaign Management**: Create and send marketing campaigns to specific customer segments
- **Marketing Analytics**: Track campaign performance metrics including open rates, click-through rates, and conversions
- **CSV-Based Storage**: All data is stored in CSV files (no database required)

## Technology Stack

- **Backend**: Python 3.x with Flask
- **Frontend**: HTML5, CSS3, Jinja2 templates
- **Storage**: CSV files
- **Testing**: pytest/unittest

## Project Structure

```
cs411_proj2/
├── app.py                      # Flask application entry point
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── auth/                       # Authentication module
│   ├── __init__.py
│   ├── routes.py              # Login/logout routes
│   └── forms.py               # Login decorators
│
├── marketing/                  # Marketing automation module
│   ├── __init__.py
│   ├── routes.py              # Marketing routes
│   ├── segmentation.py        # Segmentation logic
│   ├── campaigns.py           # Campaign management
│   └── analytics.py           # Analytics calculations
│
├── data/                       # CSV data files
│   ├── customers.csv          # Customer database (50 records)
│   ├── segments.csv           # Segment definitions
│   ├── campaigns.csv          # Campaign data
│   ├── events.csv             # Marketing events
│   └── users.csv              # Login credentials
│
├── templates/                  # HTML templates
│   ├── base.html              # Base layout
│   ├── login.html             # Login page
│   ├── dashboard.html         # Main dashboard
│   ├── segments.html          # Segment list
│   ├── segment_form.html      # Create segment form
│   ├── segment_detail.html    # Segment details
│   ├── campaigns.html         # Campaign list
│   ├── campaign_form.html     # Create campaign form
│   ├── campaign_detail.html   # Campaign details
│   └── analytics.html         # Analytics dashboard
│
├── static/                     # Static files
│   └── css/
│       └── styles.css         # Application styles
│
└── tests/                      # Test files
    ├── test_segmentation.py   # Segmentation tests
    ├── test_campaigns.py      # Campaign tests
    └── test_analytics.py      # Analytics tests
```

## Setup Instructions

### 1. Clone or Download the Project

```bash
cd ~/Desktop/Shayan/Bilkent/CS\ 411/proj2/cs411_proj2
```

### 2. Create a Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

**On macOS/Linux:**
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

**On Windows (Command Prompt):**
```cmd
set FLASK_APP=app.py
set FLASK_ENV=development
flask run
```

**On Windows (PowerShell):**
```powershell
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"
flask run
```

**Alternative (works on all platforms):**
```bash
python app.py
```

The application will be available at: `http://127.0.0.1:5000`

## Default Login Credentials

- **Username**: `admin`
- **Password**: `password`

## Usage Guide

### Demo Workflow

1. **Login**
   - Navigate to `http://127.0.0.1:5000`
   - Login with credentials: username=`admin`, password=`password`

2. **Create a Customer Segment**
   - Click "Manage Segments" from the dashboard
   - Click "Create New Segment"
   - Example: "High Spenders in Ankara"
     - Min Age: 25
     - Max Age: 45
     - Location: Ankara
     - Min Total Spent: 2000
   - Submit the form

3. **View Segment Details**
   - Click "View Details" on the created segment
   - See all customers matching the criteria

4. **Create a Campaign**
   - Click "Manage Campaigns" from the dashboard
   - Click "Create New Campaign"
   - Fill in:
     - Campaign Name: "Summer Sale 2024"
     - Target Segment: Select your created segment
     - Start Date: Choose a date
     - Subject: "Exclusive Summer Offers!"
     - Body: "Dear customer, check out our amazing summer deals..."
   - Submit the form

5. **Send the Campaign**
   - Click "View Details" on the campaign
   - Review the target customers
   - Click "Send Campaign to X Customers"
   - Confirm the action

6. **View Analytics**
   - Click "View Analytics" from the dashboard
   - See campaign performance metrics:
     - Emails sent
     - Open rate
     - Click-through rate (CTR)
     - Conversion rate

## Running Tests

The project includes comprehensive unit tests for segmentation, campaigns, and analytics.

**Run all tests:**
```bash
python -m pytest tests/
```

**Run specific test file:**
```bash
python -m pytest tests/test_segmentation.py
python -m pytest tests/test_campaigns.py
python -m pytest tests/test_analytics.py
```

**Run with unittest:**
```bash
python -m unittest discover tests/
```

**Run individual test file with unittest:**
```bash
python tests/test_segmentation.py
python tests/test_campaigns.py
python tests/test_analytics.py
```

## Features Explained

### Customer Segmentation

The segmentation system allows you to filter customers based on multiple criteria:

- **Age Range**: Minimum and maximum age
- **Location**: Partial match, case-insensitive (e.g., "Ankara" matches "Ankara")
- **Spending**: Minimum total amount spent

Filters are applied using AND logic (all conditions must be met).

### Campaign Management

Campaigns target specific customer segments and can be in two states:

- **Draft**: Campaign created but not sent
- **Sent**: Campaign has been sent to target customers

When a campaign is sent, the system:
1. Generates "sent" events for all customers in the target segment
2. Simulates engagement events (opened, clicked, converted) with realistic probabilities:
   - 70% chance of being opened
   - 40% of opened emails get clicked
   - 30% of clicked emails lead to conversions

### Analytics

The analytics module calculates:

- **Event Counts**: Total sent, opened, clicked, converted
- **Open Rate**: (Opened / Sent) × 100
- **Click-Through Rate (CTR)**: (Clicked / Sent) × 100
- **Conversion Rate**: (Converted / Sent) × 100

Metrics are available per-campaign and as overall aggregates.

## CSV File Formats

### customers.csv
```csv
customer_id,name,email,age,location,total_spent,last_purchase_date
1,Ahmet Yılmaz,ahmet.yilmaz@email.com,28,Ankara,1250.50,2024-11-15
```

### segments.csv
```csv
segment_id,segment_name,rules_json
1,High Spenders,"{\"min_age\": 25, \"min_total_spent\": 2000}"
```

### campaigns.csv
```csv
campaign_id,name,segment_id,start_date,status,subject,body
1,Summer Sale,1,2024-12-01,draft,Special Offer,Check out our deals!
```

### events.csv
```csv
event_id,campaign_id,customer_id,event_type,timestamp
1,1,1,sent,2024-12-01T10:00:00
```

## Development Notes

- This is an educational project, not production-ready code
- No external email services or APIs are used
- Event simulation uses random probabilities for realistic metrics
- CSV files are used instead of a database for simplicity
- Session management is basic (no password hashing)

## Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'flask'`
- **Solution**: Make sure you activated the virtual environment and installed dependencies

**Issue**: Application won't start
- **Solution**: Check that port 5000 is not in use by another application

**Issue**: CSV files not found
- **Solution**: The data/ directory and CSV files should be created automatically on first run

**Issue**: Tests fail with import errors
- **Solution**: Run tests from the project root directory and ensure the virtual environment is activated

## Author

Muhammad Shayan Usman  
Bilkent University - CS411 Software Architecture Project  
December 2024

## License

This project is for educational purposes as part of CS411 coursework at Bilkent University.
