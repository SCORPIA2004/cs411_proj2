## Technology Stack

- **Backend**: Python 3.x with Flask
- **Frontend**: HTML5, CSS3, Jinja2 templates
- **Storage**: CSV files
- **Testing**: pytest/unittest

## How to run

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

### 3. Install Dependencies and then run the app

```bash
pip install -r requirements.txt
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