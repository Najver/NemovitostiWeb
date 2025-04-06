# John's Estate Assistant
A smart real estate assistant that predicts property prices using AI, calculates mortgage installments, allows user account management, and stores historical predictions. Built with Flask, MySQL, and a neural network model.

## Overview
John's Estate Assistant is an intelligent web-based tool that helps users estimate the price of properties based on their parameters, calculate mortgage payments, compare prices across regions, and manage their predictions—all in a smooth and intuitive interface.

### Key Features
AI-Based Property Price Prediction (Neural Network with Keras)

Price Comparison by Region (Kraj)

Mortgage Calculator (with fixations and rates from real data)

Custom-trained model on Czech real estate data

User registration and login

Prediction and mortgage history saving per user

Export of price comparisons to CSV


### Technologies Used
Backend: Python 3.12, Flask, Flask Blueprints

Frontend: HTML5, CSS3, Vanilla JS

AI Model: TensorFlow (Keras), trained neural network

Database: MySQL

Testing: pytest, coverage

Logging: Python’s logging module with UTF-8 output

Other Tools: pickle, json, requirements.txt, config.json

### Project Structure
johns-estate-assistant/
├── app.py                     # Flask app entry point
├── config.json                # Application configuration
├── db.py                      # MySQL connection logic
├── logs/                      # Log output directory
├── models/                    # AI model and scalers (saved)
├── routes/                    # Flask Blueprints (main, auth, hypoteka)
├── static/                    # CSS, JS, JSON data
├── templates/                 # HTML templates (Jinja2)
├── tests/                     # Unit tests
├── utils/                     # AI predictor logic
├── .coverage                  # Coverage data
├── requirements.txt           # Python dependencies
└── README.md                  # This file

### Example Functionalities
Predict property price by specifying:

Area (0–150 m²)

Layout (1+kk to 5+kk)

Energy class (A–G)

Condition (new, renovated, etc.)

Region (kraj)

Calculate a mortgage based on:

Loan amount or own capital

Fixation length (1–30 years)

Automatically applied interest rate

Validation of logic between fixations and loan duration

Account features:

Register/login/logout

Save selected predictions

View and delete past predictions

Save mortgage calculations (planned)

### Requirements
Python Environment
Python 3.12+

MySQL Server (with a user + database created)

Pip for installing dependencies

### Installation
[git clone https://github.com/your-username/johns-estate-assistant.git](https://github.com/Najver/NemovitostiWeb)
cd NemovitostiWeb
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
### Setup
Make sure your MySQL DB is running and configured.

Update config.json with correct model paths and DB config.

Run the application:

python app.py
Then visit your configured port (http://127.0.0.1:3020)

### Running Tests
coverage run -m pytest
coverage report

### AI Model Notes
The trained Keras model is stored in models/, and mappings for location, energy efficiency, and property condition are serialized via pickle. The predictor.py handles loading and predicting.

🧑‍💻 Author
Created by a student for an educational project.
This assistant was built with the goal to combine AI with real-world real estate needs in the Czech Republic.

