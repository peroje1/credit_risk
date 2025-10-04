# **Project Overview**


---

## **1. Extract & Load**

- Reads input CSV files from the **`data/`** folder:
  - `customer.csv`
  - `credit_bureau.csv`
  - `income.csv`
  - `overdue.csv`
- Loads all files into a **MySQL** database named **`credit_risk`**.
- Database schema is defined in **`sql/01_schema.sql`**.

---

## **2. Transform & Calculate**

- Cleans and validates raw data.
- Applies business rules to calculate **risk scores** and **probabilities** for each customer:
  - Adjusts missing or invalid income (`income = 3000` if none).
  - Uses installment count, overdue days, gender, and other features.
- Stores the final results in the **`risk_results`** table.

---

## **3. Run Modes**

---

### **Docker Mode**
- Runs the full ETL process automatically once.
- The container exits after completion, but the **MySQL database remains active** for inspection.

### **Manual Mode**
- Can be executed locally using Python and MySQL (without Docker).



## **4. Database Access**

---

- The MySQL container persists data even after the ETL finishes.
- To access the database, run the following command in your terminal (note, you should change container name zadatak_petar_nikic-db-1 if it's different on your end):

```bash
docker exec -it zadatak_petar_nikic-db-1 mysql -u risk_user -p credit_risk

```

# Setup & Run Guide

---

### There are 2 options to run, manual and with docker/docker compose:

# Docker:

---

1.	Requirements Docker and Docker compose
2.	How to run:

- Clone or unzip the project.

- Navigate into the project folder then run: docker compose up --build

- This will start the MySQL database (sql/01_schema.sql), run the Python pipeline (src/main.py) and load all the csv files into data/ folder.

- When the pipeline finishes, the app container will exit.

-	To inspect the database run inside the docker: docker exec -it <container_name> mysql -u risk_user -p credit_risk (Password: StrongPass123!) Also change the <container_name> in the name of the db.
From here SQL commands can be used to inspect the database.

# Manual:

---

   1. ### Install Requirements
- Install Python 3.10+
- Install MySQL Server 8+ and ensure it is running
- Install dependencies with: pip install -r requirements.txt

This will install:
- pandas
-	SQLAlchemy	
-	PyMySQL (lets SQLAlchemy connect to MySQL)
-	cryptography (required by PyMySQL)

   2. ### Create MySQL Database and User or use own.
Example:
```
CREATE DATABASE credit_risk;
CREATE USER 'risk_user'@'localhost' IDENTIFIED BY 'StrongPass123!';
GRANT ALL PRIVILEGES ON credit_risk.* TO 'risk_user'@'localhost';
FLUSH PRIVILEGES;
```

You can test the connection with the databse with the provided script „connection_check.py“

   3. ### Run the provided SQL script to create tables in MySQL. 
Script is located in sql/01_schema.sql

   4. ### Configure config.json file with own mysql user/password and file paths:
```
{
  "customer_csv": "data/customer.csv",
  "credit_csv": "data/credit_bureau.csv",
  "income_csv": "data/income.csv",
  "overdue_csv": "data/overdue.csv",
  "mysql_connection":"mysql+pymysql://risk_user:StrongPass123!@localhost:3306/credit_risk"
}
```
5.	## To run the script manually: 

 ### In the terminal run the: python -m src.main   

This will do the whole pipeline

Should look like this:
```
app-1  | MySQL is up - executing command
app-1  | 1111111111111
app-1  | mysql+pymysql://risk_user:StrongPass123!@db:3306/credit_risk?ssl_disabled=true
app-1  | 1111111111111
app-1  | [RUN] Pipeline start for 2024-12-31
app-1  | 1111111111111
app-1  | mysql+pymysql://risk_user:StrongPass123!@db:3306/credit_risk?ssl_disabled=true
app-1  | 1111111111111
app-1  | [LOAD] customer: 19873 rows for 2024-12-31
app-1  | [LOAD] credit_bureau: 9838 rows for 2024-12-31
app-1  | [LOAD] income: 170435 rows for 2024-12-31
app-1  | [LOAD] overdue: 1978 rows for 2024-12-31
app-1  | All tables loaded.
app-1  | [CALC] Model calculation finished and results archived for 2024-12-31.
app-1  | [RUN] Done.
app-1 exited with code 0
```

### From then on you can querry the database.


