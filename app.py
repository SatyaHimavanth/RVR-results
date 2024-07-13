from flask import Flask, render_template, request
import re
import os
from dotenv import load_dotenv
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from collections import defaultdict
from pymongo import MongoClient

load_dotenv()

grade_to_points = {
    'A+': 10,
    'A': 9,
    'B': 8,
    'C': 7,
    'D': 6,
    'E': 5,
    'F': 0
}

credits_r20_cse = {
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

def calculate_results(reg_no):
    tot_gpa = {}
    cumulative_gpa = {}
    results = {}
    name = ""
    no_of_requests = 0
    while no_of_requests < 3:
        no_of_requests += 1
        
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
                
            driver.get("https://rvrjcce.ac.in/examcell/results/regnoresultsR.php")
            input_element = driver.find_element(By.CSS_SELECTOR, 'input[type="text"][style*="font-size:14px; color:red; width:100px;"]')
            input_element.send_keys(reg_no)
            driver.implicitly_wait(10)
            div_element = driver.find_element(By.ID, 'txtHint')
            retrieved_text = div_element.text
            match = re.search(r"Name : (.+)", retrieved_text)
            name = match.group(1)
            if "NOT FOUND" in retrieved_text:
                return "Invalid reg no", {}, {}, {}
            
            pattern = re.compile(r'Semester (\w+) \[.*?\](.*)')
            matches = pattern.findall(retrieved_text)
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
                for sub in results[sem].keys():
                    sem_gpa += credits_r20_cse[sem][sub]*grade_to_points[results[sem][sub]]
                sem_gpa = sem_gpa/sum(credits_r20_cse[sem].values())
                tot_gpa[sem] = sem_gpa
                cur_cred = sum(credits_r20_cse[sem].values())
                sum_of_tot_cred += cur_cred
                sum_of_gpa_cred = 0
                for sem, gpa in tot_gpa.items():
                    sum_of_gpa_cred += sum(credits_r20_cse[sem].values())*gpa
                cumulative_gpa[sem] = round(sum_of_gpa_cred/sum_of_tot_cred, 2)
        except Exception as error:
            print("Failed to reach server", error)
            
        if cumulative_gpa:
            break
    else:
        return "server down", {}, {}, {}
    for key in tot_gpa:
        tot_gpa[key] = round(tot_gpa[key], 2)
    return name, results, tot_gpa, cumulative_gpa

def store_results(name, reg_no, results, tot_gpa, cumulative_gpa):
    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    database = os.getenv('DB')
    collection = os.getenv('COLLECTION')
    url = "mongodb+srv://"+user+":"+password+"@studentresults.o3jkbq0.mongodb.net/?retryWrites=true&w=majority&appName=StudentResults"
    
    client = MongoClient(url)
    db = client[database]
    collection = db[collection]
    filter = {"reg_no": reg_no}
    document_data = {
        "$set": {
            "reg_no": reg_no,
            "name": name,
            "results": results,
            "tot_gpa": tot_gpa,
            "cumulative_gpa": cumulative_gpa
        }
    }
    collection.update_one(filter, document_data, upsert=True)
    client.close()
    
def reteive_previous_search_results(reg_no):
    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    database = os.getenv('DB')
    collection = os.getenv('COLLECTION')
    url = "mongodb+srv://"+user+":"+password+"@studentresults.o3jkbq0.mongodb.net/?retryWrites=true&w=majority&appName=StudentResults"
    
    client = MongoClient(url)
    db = client[database]
    collection = db[collection]
    prev_result = collection.find_one({"reg_no": reg_no})
    return prev_result
    
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    reg_no = request.form['input_text']
    name, results, tot_gpa, cumulative_gpa = calculate_results(reg_no)
    if name == "Invalid reg no":
        return "Invalid reg no"
    elif name == "server down":
        prev_result = reteive_previous_search_results(reg_no)
        if not prev_result:
            return "Server down, No saved results found"
        else:
            name = prev_result.get("name")
            reg_no = prev_result.get("reg_no")
            results = prev_result.get("results")
            tot_gpa = prev_result.get("tot_gpa")
            cumulative_gpa = prev_result.get("cumulative_gpa")
            return render_template('result.html', name=name, reg_no=reg_no, results=results, tot_gpa=tot_gpa, cumulative_gpa=cumulative_gpa, results_type="last saved")
        
    else:
        store_results(name, reg_no, results, tot_gpa, cumulative_gpa)
    return render_template('result.html', name=name, reg_no=reg_no, results=results, tot_gpa=tot_gpa, cumulative_gpa=cumulative_gpa, results_type="")



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)