import json
import os


def get_all_questions():
    questions = []
    for root, dirs, files in os.walk("./questions"):
        for filename in files:
            with open(f'./questions/{filename}', 'r') as f:
                data = json.load(f)
            questions.append(data)
    return questions


def get_all_code_problem():
    questions = []
    for root, dirs, files in os.walk("./code"):
        for filename in files:
            with open(f'./questions/{filename}', 'r') as f:
                data = json.load(f)
            questions.append(data)
    return questions
