import streamlit as st
import psycopg2

# Establish a connection to the PostgreSQL database
# connection = psycopg2.connect(database="questo", user="postgres", password="xtc.qq10mnc", port=5432)

# URI for connecting to the PostgreSQL database
uri = "postgresql://postgres:IagPlmeshhHlaZXGxfTpTolhdbkaVOXO@autorack.proxy.rlwy.net:46248/railway"
# Establish the connection using the URI
connection = psycopg2.connect(uri)

class Admin:
    def __init__(self):
        pass     

    def add_survey(self, survey_name):
        cursor = connection.cursor()
        insert_query = "INSERT INTO surveys (survey_name) VALUES (%s) RETURNING id, survey_name;"
        cursor.execute(insert_query, (survey_name,))
        survey_info = cursor.fetchone()  # Fetching the survey ID and name
        connection.commit()
        cursor.close()
        return survey_info  # Return survey ID and name

    def add_question(self, survey_id, type_id, question, options=None):
        cursor = connection.cursor()
        insert_question_query = "INSERT INTO questions (survey_id, type_id, question) VALUES (%s, %s, %s) RETURNING id, question;"
        cursor.execute(insert_question_query, (survey_id, type_id, question))
        question_info = cursor.fetchone()  # Fetching the question ID and text

        if type_id in (1, 2):  # Multiple Choice or Checkbox
            if options and len(options) == 4:  # Must provide exactly 4 options
                for option in options:
                    insert_options_query = "INSERT INTO options (question_id, option_text) VALUES (%s, %s);"
                    cursor.execute(insert_options_query, (question_info[0], option))
            else:
                st.error("Error: For Multiple Choice or Checkbox, exactly 4 options are required.")
                connection.rollback()
                return None
            
        elif type_id == 4:  # Rating
            rating_options = [str(i) for i in range(1, 6)]  # Rating options 1 to 5
            for option in rating_options:
                insert_options_query = "INSERT INTO options (question_id, option_text) VALUES (%s, %s);"
                cursor.execute(insert_options_query, (question_info[0], option))
        
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
            "rating_range": "1 to 5" if type_id == 4 else None
        }

    def get_question_types(self):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM question_type;")  # Ensure to query the correct table
        question_types = cursor.fetchall()
        cursor.close()
        return question_types

    def get_survey_name(self, survey_id):
        cursor = connection.cursor()
        cursor.execute("SELECT survey_name FROM surveys WHERE id = %s;", (survey_id,))
        survey_name = cursor.fetchone()[0]
        cursor.close()
        return survey_name

    def get_question_type_name(self, type_id):
        cursor = connection.cursor()
        cursor.execute("SELECT question_type FROM question_type WHERE id = %s;", (type_id,))
        question_type_name = cursor.fetchone()[0]
        cursor.close()
        return question_type_name

def main():
    st.title("Survey Management System")
    
    admin = Admin()

    # Step 1: Create Survey
    if 'survey_info' not in st.session_state:
        st.subheader("Step 1: Create a Survey")
        survey_name = st.text_input("Enter the survey name:")
        
        if st.button("Create Survey"):
            if survey_name:
                survey_info = admin.add_survey(survey_name)
                st.session_state.survey_info = survey_info  # Save survey info in session state
                st.session_state.questions = []  # Initialize questions list
                st.success(f"Survey created: ID = {survey_info[0]}, Name = {survey_info[1]}")
            else:
                st.error("Please enter a survey name.")

    # Step 2: Add Questions
    elif 'questions' in st.session_state:
        survey_info = st.session_state.survey_info
        st.subheader("Step 2: Add Questions to Survey")
        st.write(f"Survey ID: {survey_info[0]}, Survey Name: {survey_info[1]}")
        
        question_types = admin.get_question_types()
        question_type_names = {qtype[0]: qtype[1] for qtype in question_types}
        selected_type_id = st.selectbox("Select Question Type:", options=list(question_type_names.keys()), format_func=lambda x: question_type_names[x])
        
        question_text = st.text_input("Enter the question text:")
        
        options = []
        if selected_type_id in (1, 2):  # Multiple Choice or Checkbox
            st.write("Enter 4 options (press enter after each):")
            for i in range(4):
                option = st.text_input(f"Option {i + 1}:", key=f"option_{i}")
                if option:
                    options.append(option)
        
        # Add question button
        if st.button("Add Question"):
            if question_text:
                created_question_info = admin.add_question(survey_info[0], selected_type_id, question_text, options)
                
                if created_question_info:
                    st.session_state.questions.append(created_question_info)  # Add question info to list
                    st.success("Question added successfully!")
                else:
                    st.error("Failed to add the question.")
            else:
                st.error("Please enter a question text.")

        # Show questions added so far
        if st.session_state.questions:
            st.subheader("Questions Added:")
            for i, question in enumerate(st.session_state.questions, 1):
                st.write(f"{i}. {question['question_text']} (Type: {question['type_name']})")

        # Buttons for adding another question or completing the process
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add Another Question"):
                pass  # This will remain on the same page
        with col2:
            if st.button("Complete"):
                st.session_state.step = 3  # Move to step 3

    # Step 3: Show Final Survey and Questions
    if 'step' in st.session_state and st.session_state.step == 3:
        st.subheader("Step 3: Survey Summary")
        st.write(f"Survey ID: {survey_info[0]}, Survey Name: {survey_info[1]}")
        
        st.subheader("Questions Added:")
        for i, question in enumerate(st.session_state.questions, 1):
            st.write(f"{i}. {question['question_text']} (Type: {question['type_name']})")

if __name__ == "__main__":
    main()
