# Uni-Carpooling

**Uni-Carpooling** is a web-based platform aimed at optimizing commutes for the university community. It allows users with their own vehicles to share rides with others, reducing travel costs and their environmental footprint.

It was developed as part of the "Internet Information Systems" course (December 2025).

**Author:** Antonios Bardanis (Registration Number: P21110)

## 🛠️ Technology Stack
* **Backend:** Python 3.10, Flask Framework
* **Database:** SQLite (via SQLAlchemy ORM)
* **Frontend:** HTML5, CSS3, Bootstrap 5 (Responsive Design)
* **Security:** Bcrypt (password hashing), CSRF Tokens, Role-Based Access Control (RBAC)

## ✨ Key Features & Core Logic
* **Data Retrieval (APIs):** Utilizes the Nominatim API (OpenStreetMap) for geocoding addresses and the OSRM API (Open Source Routing Machine) to calculate actual driving distances.
* **Environmental Impact:** Automatically calculates the kilograms of CO2 saved based on the route distance (using a coefficient of 0.12kg/km).
* **Economic Suggestion:** Recommends a fair gas contribution cost based on the distance.
* **User Roles:**
  * **User (Student/Staff):** Can register, create routes, and book seats on routes created by others.
  * **Administrator:** Accesses the Admin Panel to view and delete users, triggering a Cascade Delete to clear their associated routes and maintain database integrity.

## 🚀 Installation & Setup
To run the application locally, follow these steps:

1. Open your terminal in the project directory and install the dependencies:
   ```bash
   pip install flask flask-sqlalchemy flask-login flask-bcrypt flask-wtf geopy requests
