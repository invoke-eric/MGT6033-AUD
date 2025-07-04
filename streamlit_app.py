import streamlit as st
import json
import re
import logging
logger = logging.getLogger(__name__)

def parse_questions(json_data):
    questions = []
    for section in json_data.get("sections", []):
        for q_data in section.get("questions", []):
            question_text = q_data.get("question")
            options_dict = q_data.get("options", {})
            options = [f"{key}. {value}" for key, value in options_dict.items()]
            questions.append({
                "number": q_data.get("number"),
                "text": f"{q_data.get('number')}. {question_text}",
                "options": options,
                "type": q_data.get("type")
            })
    return questions

def parse_answers(json_data):
    answers = {}
    for section in json_data.get("sections", []):
        for a_data in section.get("questions", []):
            question_number = a_data.get("number")
            answer_string = a_data.get("question", "")
            # Extract letters from "Correct Answer(s): A, B"
            match = re.search(r'\*?\*?Correct Answer(?:s)?:\*?\*? ([A-D, ]+)', answer_string)
            if match:
                correct_options = [opt.strip().lower() for opt in match.group(1).split(',')]
                answers[question_number] = correct_options
    return answers

def main():
    st.title("Quiz App")

    # Initialize session state
    if 'user_choices' not in st.session_state:
        st.session_state.user_choices = {}
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False

    # Load questions and answers
    try:
        with open("questions/Week 3/3.1 questions.json", "r") as f:
            questions_data = json.load(f)
        with open("questions/Week 3/3.1 answers.json", "r") as f:
            answers_data = json.load(f)
    except FileNotFoundError:
        st.error("Question or answer JSON file not found. Make sure the paths are correct.")
        return
    except json.JSONDecodeError:
        st.error("Error decoding JSON file. Please check the file format.")
        return

    questions = parse_questions(questions_data)
    correct_answers = parse_answers(answers_data)
    logger.info(f"questions loaded, {len(questions)} is size, {questions[0]} is first element")
    logger.info(f"answers loaded, {len(correct_answers.items())} is size")


    if not questions:
        st.warning("No questions found in the JSON file.")
        return

    # Display all questions
    for i, q in enumerate(questions):
        st.write(q["text"])
        
        # Initialize session state for this question's choices if not present
        if f'q{q["number"]}_selected_options' not in st.session_state:
            st.session_state[f'q{q["number"]}_selected_options'] = []

        current_question_choices = []
        for opt_idx, opt in enumerate(q["options"]):
            checkbox_key = f"q{q['number']}_opt{opt_idx}"
            is_checked = st.checkbox(opt, key=checkbox_key, disabled=st.session_state.quiz_submitted)
            
            if is_checked:
                current_question_choices.append(opt[0].lower())
        
        # Store the current state of choices for this question in session state
        st.session_state[f'q{q["number"]}_selected_options'] = current_question_choices

        # Display feedback if quiz has been submitted
        if st.session_state.quiz_submitted:
            correct_opts = correct_answers.get(q["number"], [])
            user_choices = st.session_state.get(f'q{q["number"]}_selected_options', [])
            
            is_correct = set(user_choices) == set(correct_opts)
            is_partially_correct = not is_correct and any(c in correct_opts for c in user_choices)

            if is_correct:
                st.success(f"Question {q['number']}: Correct!")
            elif is_partially_correct:
                st.warning(f"Question {q['number']}: Partially Correct.")
            else:
                st.error(f"Question {q['number']}: Incorrect.")
            st.info(f"Correct Answer(s): {', '.join([s.upper() for s in correct_opts])}")
        st.markdown("---") # Separator for questions

    # Single Submit All Answers button
    if st.button("Submit All Answers", disabled=st.session_state.quiz_submitted):
        st.session_state.quiz_submitted = True
        st.rerun() # Rerun to display results

    if st.session_state.quiz_submitted:
        if st.button("Restart Quiz"):
            st.session_state.quiz_submitted = False
            st.session_state.user_choices = {} # Clear all user choices
            # Clear individual question choices from session state
            for q in questions:
                if f'q{q["number"]}_selected_options' in st.session_state:
                    del st.session_state[f'q{q["number"]}_selected_options']
            st.rerun()

if __name__ == "__main__":
    main()
