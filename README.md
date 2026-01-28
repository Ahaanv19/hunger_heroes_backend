
# 🚗 Poway Auto Backend

The **Poway Auto Backend** is the server-side system behind Poway Auto — a full-stack platform built to improve routing and traffic efficiency in the City of Poway.

This backend handles routing logic, traffic data processing, and communication with the frontend and external APIs.

---

## 💡 How It Works

1. **Receives Requests from Frontend**  
   The frontend sends route requests, hazard reports, or user actions to the backend using HTTP endpoints.

2. **Processes Real-Time Traffic Data**  
   The backend connects with Google Maps and Poway’s open datasets to calculate accurate and optimized routes.

3. **Returns Optimized Routes or Data**  
   Based on traffic conditions, user routines, or hazard locations, it returns optimized routing instructions or relevant data.

4. **Stores Data**  
   All hazard reports, user routines, and simulation settings are stored in a database using SQLAlchemy.

---

## ⚙️ Tech Used

- **Flask** – to create REST APIs  
- **SQLAlchemy** – to manage the database  
- **Google Maps API** – for traffic and routing data  
- **Docker** – for easy deployment  
- **JSON/CSV** – to handle static and live datasets  

---

## 📁 Key Features

- Route optimization using live traffic
- Daily routine planning and storage
- Hazard alert reporting and visualization
- Support for fleet simulation
- Easy API integration with frontend

---

## 🧪 How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python run.py
