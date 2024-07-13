from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os
import re
from collections import defaultdict

grade_to_points = {
    'A+': 10,
    'A': 9,
    'B': 8,
    'C': 7,
    'D': 6,
    'E': 5,
    'F': 0
}

credits = {
    'I': {
        "Sub1": 3,
        "Sub2": 3,
        "Sub3": 3,
        "Sub4": 3,
        "Lab1": 1.5,
        "Lab2": 1.5,
        "Lab3": 3,
        "Lab4": 1.5,
        "Lab5": 0
    },
    'II': {
        "Sub1": 3,
        "Sub2": 3,
        "Sub3": 3,
        "Sub4": 3,
        "Sub5": 2,
        "Lab1": 1.5,
        "Lab2": 1,
        "Lab3": 1.5,
        "Lab4": 1.5,
        "Lab5": 0
    },
    'III': {
        "Sub1": 3,
        "Sub2": 3,
        "Sub3": 3,
        "Sub4": 3,
        "Sub5": 3,
        "Lab1": 1.5,
        "Lab2": 1.5,
        "Lab3": 1.5,
        "Lab4": 2,
        "Lab5": 0
    },
    'IV': {
        "Sub1": 3,
        "Sub2": 3,
        "Sub3": 3,
        "Sub4": 3,
        "Sub5": 3,
        "Lab1": 1.5,
        "Lab2": 1.5,
        "Lab3": 1.5,
        "Lab4": 2,
        "Lab5": 0
    },
    'V': {
        "Sub1": 3,
        "Sub2": 3,
        "Sub3": 3,
        "Sub4": 3,
        "Sub5": 3,
        "Lab1": 1.5,
        "Lab2": 1.5,
        "Lab3": 1.5,
        "Lab4": 2
    },
    'VI': {
        "Sub1": 3,
        "Sub2": 3,
        "Sub3": 3,
        "Sub4": 3,
        "Sub5": 3,
        "Lab1": 1.5,
        "Lab2": 1.5,
        "Lab3": 1.5,
        "Lab4": 2
    },
    'VII': {
        "Sub1": 3,
        "Sub2": 3,
        "Sub3": 3,
        "Sub4": 3,
        "Sub5": 3,
        "Sub6": 3,
        "Lab1": 3,
        "Lab2": 2
    },
    'VIII': {
        "Lab1": 12
    }
}

tot_gpa = {}
cumulative_gpa = {}
results = {}


while True:
    try:
        current_path = os.getcwd()
        chrome_path = os.path.join(current_path, "chromedriver.exe")

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        service = Service(chrome_path)

        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as error:
            print("Driver version is invalid", error)
            
        driver.get("https://rvrjcce.ac.in/examcell/results/regnoresultsR.php")
        input_element = driver.find_element(By.CSS_SELECTOR, 'input[type="text"][style*="font-size:14px; color:red; width:100px;"]')
        input_element.send_keys('y20cs179')
        time.sleep(1)

        div_element = driver.find_element(By.ID, 'txtHint')
        retrieved_text = div_element.text
        match = re.search(r"Name : (.+)", retrieved_text)
        print(match.group(1))
        print(retrieved_text)
        pattern = re.compile(r'Semester (\w+) \[.*?\](.*)')
        matches = pattern.findall(retrieved_text)
        print(matches)
        subjects = ["Sub1", "Sub2", "Sub3", "Sub4", "Sub5", "Sub6", "Sub7"]
        labs = ["Lab1", "Lab2", "Lab3", "Lab4", "Lab5", "Lab6"]

        grades = defaultdict(dict)

        for match in matches:
            semester = match[0]
            grades_list = match[1].split()
            for i, grade in enumerate(grades_list):
                if i < len(subjects):
                    subject = subjects[i]
                else:
                    subject = labs[i - len(subjects)]
                grades[semester][subject] = grade

        grades = dict(grades)
        for semester, subjects in grades.items():
            results[semester] = {}
            for subject, grade in subjects.items():
                if grade != "--":
                    results[semester][subject] = grade
        
        sum_of_tot_cred = 0
        for sem in results.keys():
            sem_gpa = 0
            print(sem)
            for sub in results[sem].keys():
                sem_gpa += credits[sem][sub]*grade_to_points[results[sem][sub]]
            # sem_gpa = round(sem_gpa/sum(credits[sem].values()), 2)
            sem_gpa = sem_gpa/sum(credits[sem].values())
            tot_gpa[sem] = sem_gpa
            cur_cred = sum(credits[sem].values())
            sum_of_tot_cred += cur_cred
            sum_of_gpa_cred = 0
            for sem, gpa in tot_gpa.items():
                sum_of_gpa_cred += sum(credits[sem].values())*gpa
            cumulative_gpa[sem] = round(sum_of_gpa_cred/sum_of_tot_cred, 2)
    except Exception as error:
        print("Failed to reach server", error)
        
    if cumulative_gpa:
        break
        
print(results)
print(tot_gpa)
print(cumulative_gpa)