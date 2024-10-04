#import zone
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import psycopg2

connection = psycopg2.connect(database="questo", user="postgres", password="xtc.qq10mnc", port=5432)

class Data:
    def __init__(self):
        pass

class Admin:
    def __init__(self):
        pass     

    def add_survey(self, survey_name):
        cursor = connection.cursor()
        insert_query = "INSERT INTO surveys (name) VALUES (%s) RETURNING surveyid, name;"
        cursor.execute(insert_query, (survey_name,))
        survey_info = cursor.fetchone()  # Fetching the survey ID and name
        connection.commit()
        cursor.close()
        return survey_info  # Return survey ID and name

    def add_question(self, survey_id, type_id, question, options=None):
        cursor = connection.cursor()
        insert_question_query = "INSERT INTO questions (surveyID, typeID, question) VALUES (%s, %s, %s) RETURNING questionID, question;"
        cursor.execute(insert_question_query, (survey_id, type_id, question))
        question_info = cursor.fetchone()  # Fetching the question ID and text

        if type_id in (1, 2):  # Multiple Choice or Checkbox
            if options and len(options) == 4:  # Must provide exactly 4 options
                insert_options_query = "INSERT INTO options (questionID, option_text) VALUES (%s, %s);"
                cursor.execute(insert_options_query, (question_info[0], options))
            else:
                print("Error: For Multiple Choice or Checkbox, exactly 4 options are required.")
                connection.rollback()
                return None
            
        elif type_id == 5:  # Rating
            rating_options = [str(i) for i in range(1, 6)]  # Rating options 1 to 5
            insert_options_query = "INSERT INTO options (questionID, option_text) VALUES (%s, %s);"
            cursor.execute(insert_options_query, (question_info[0], rating_options))
        
        connection.commit()
        cursor.close()

        # Return the survey and question information
        question_type_name = self.get_question_type_name(type_id)
        return {
            "survey_id": survey_id,
            "survey_name": self.get_survey_name(survey_id),
            "question_id": question_info[0],
            "question_text": question_info[1],
            "type_id": type_id,
            "type_name": question_type_name,
            "options": options if type_id in (1, 2) else None,
            "rating_range": "1 to 5" if type_id == 5 else None
        }

    def get_question_types(self):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM qtype;")
        question_types = cursor.fetchall()
        cursor.close()
        return question_types

    def get_survey_name(self, survey_id):
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM surveys WHERE surveyid = %s;", (survey_id,))
        survey_name = cursor.fetchone()[0]
        cursor.close()
        return survey_name

    def get_question_type_name(self, type_id):
        cursor = connection.cursor()
        cursor.execute("SELECT question_type FROM qtype WHERE id = %s;", (type_id,))
        question_type_name = cursor.fetchone()[0]
        cursor.close()
        return question_type_name

# Command-line interface
def main():
    admin = Admin()
    
    # Input survey name
    survey_name = input("Enter the survey name: ")
    survey_info = admin.add_survey(survey_name)
    survey_id = survey_info[0]  # Get survey ID
    print(f"Survey created: ID = {survey_id}, Name = {survey_info[1]}")

    all_questions = []  # List to store all created questions' information

    # Add multiple questions to the survey
    while True:
        # Get and display question types
        question_types = admin.get_question_types()
        print("\nAvailable Question Types:")
        for qtype in question_types:
            print(f"ID: {qtype[0]}, Type: {qtype[1]}")
        
        # Select question type
        type_id = int(input("\nSelect question type by ID: "))
        question_text = input("Enter the question text: ")
        
        options = None
        if type_id in (1, 2):  # Multiple Choice or Checkbox
            options = []
            print("Enter 4 options (press enter after each):")
            for i in range(4):
                option = input(f"Option {i + 1}: ")
                options.append(option)
        
        # Add question and retrieve the created question info
        created_question_info = admin.add_question(survey_id, type_id, question_text, options)
        
        if created_question_info:
            all_questions.append(created_question_info)  # Add question info to list
            print("\nCreated Question Information:")
            print(f"Survey ID: {created_question_info['survey_id']}")
            print(f"Survey Name: {created_question_info['survey_name']}")
            print(f"Question ID: {created_question_info['question_id']}")
            print(f"Question Text: {created_question_info['question_text']}")
            print(f"Question Type ID: {created_question_info['type_id']} ({created_question_info['type_name']})")
            
            if created_question_info['options']:
                print(f"Options: {', '.join(created_question_info['options'])}")
            elif created_question_info['rating_range']:
                print(f"Rating Range: {created_question_info['rating_range']}")
        
        # Ask if the user wants to add another question
        another_question = input("\nDo you want to add another question? (y/n): ").strip().lower()
        if another_question != 'y':
            break

    # Display total survey and question data
    print("\n--- Total Survey Data ---")
    print(f"Survey ID: {survey_info[0]}, Survey Name: {survey_info[1]}")
    print("\nQuestions Created:")
    for i, question in enumerate(all_questions, 1):
        print(f"\nQuestion {i}:")
        print(f"  Question ID: {question['question_id']}")
        print(f"  Question Text: {question['question_text']}")
        print(f"  Question Type: {question['type_name']}")
        
        if question['options']:
            print(f"  Options: {', '.join(question['options'])}")
        elif question['rating_range']:
            print(f"  Rating Range: {question['rating_range']}")

if __name__ == "__main__":
    main()