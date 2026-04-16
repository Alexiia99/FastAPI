import requests
import random
import time
import sys

API_URL = "http://localhost:8000/predict"

def send_normal_data(n=20):
    """Distribución similar al entrenamiento"""
    print(f"Enviando {n} predicciones normales...")
    for i in range(n):
        requests.post(API_URL, json={
            "Age": random.randint(25, 55),
            "BusinessTravel": random.randint(0, 2),
            "DailyRate": random.randint(500, 1000),
            "Department": random.randint(0, 2),
            "DistanceFromHome": random.randint(1, 20),
            "Education": random.randint(1, 5),
            "EducationField": random.randint(0, 5),
            "EnvironmentSatisfaction": random.randint(1, 4),
            "Gender": random.randint(0, 1),
            "HourlyRate": random.randint(40, 100),
            "JobInvolvement": random.randint(1, 4),
            "JobLevel": random.randint(1, 5),
            "JobRole": random.randint(0, 8),
            "JobSatisfaction": random.randint(1, 4),
            "MaritalStatus": random.randint(0, 2),
            "MonthlyIncome": random.randint(3000, 10000),
            "MonthlyRate": random.randint(10000, 20000),
            "NumCompaniesWorked": random.randint(0, 5),
            "OverTime": random.randint(0, 1),
            "PercentSalaryHike": random.randint(10, 20),
            "PerformanceRating": random.randint(3, 4),
            "RelationshipSatisfaction": random.randint(1, 4),
            "StockOptionLevel": random.randint(0, 3),
            "TotalWorkingYears": random.randint(5, 20),
            "TrainingTimesLastYear": random.randint(1, 5),
            "WorkLifeBalance": random.randint(1, 4),
            "YearsAtCompany": random.randint(2, 15),
            "YearsInCurrentRole": random.randint(1, 10),
            "YearsSinceLastPromotion": random.randint(0, 5),
            "YearsWithCurrManager": random.randint(1, 10)
        })
        time.sleep(0.2)
    print(f"✅ {n} predicciones normales enviadas")

def send_drifted_data(n=20):
    """Distribución muy diferente al entrenamiento"""
    print(f"Enviando {n} predicciones con drift...")
    for i in range(n):
        requests.post(API_URL, json={
            "Age": random.randint(55, 80),
            "BusinessTravel": random.randint(0, 2),
            "DailyRate": random.randint(100, 300),
            "Department": random.randint(0, 2),
            "DistanceFromHome": random.randint(25, 50),
            "Education": random.randint(1, 5),
            "EducationField": random.randint(0, 5),
            "EnvironmentSatisfaction": random.randint(1, 4),
            "Gender": random.randint(0, 1),
            "HourlyRate": random.randint(20, 40),
            "JobInvolvement": random.randint(1, 4),
            "JobLevel": random.randint(1, 5),
            "JobRole": random.randint(0, 8),
            "JobSatisfaction": random.randint(1, 4),
            "MaritalStatus": random.randint(0, 2),
            "MonthlyIncome": random.randint(1000, 2500),
            "MonthlyRate": random.randint(1000, 5000),
            "NumCompaniesWorked": random.randint(5, 10),
            "OverTime": random.randint(0, 1),
            "PercentSalaryHike": random.randint(10, 20),
            "PerformanceRating": random.randint(3, 4),
            "RelationshipSatisfaction": random.randint(1, 4),
            "StockOptionLevel": random.randint(0, 3),
            "TotalWorkingYears": random.randint(25, 40),
            "TrainingTimesLastYear": random.randint(1, 5),
            "WorkLifeBalance": random.randint(1, 4),
            "YearsAtCompany": random.randint(20, 35),
            "YearsInCurrentRole": random.randint(10, 20),
            "YearsSinceLastPromotion": random.randint(5, 15),
            "YearsWithCurrManager": random.randint(10, 20)
        })
        time.sleep(0.2)
    print(f"⚠️ {n} predicciones con drift enviadas")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "normal"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    if mode == "normal":
        send_normal_data(n)
    elif mode == "drift":
        send_drifted_data(n)
    else:
        print("Uso: python scripts/simulate_drift.py [normal|drift] [n]")