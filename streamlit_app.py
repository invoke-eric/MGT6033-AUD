import streamlit as st
import json
import re
import logging
logger = logging.getLogger(__name__)

QUIZ_OPTIONS = [
    "3.1", "3.2", "3.3", "3.4", "3.5", "3A", "3B", "3C",
    "4.1a", "4.1b", "4.1c", "4.2a", "4.2b", "4.2c", "4.3", "4A", "4B", "4C",
    "5.1", "5.2a", "5.2b", "5.3a", "5.3b", "5.4", "5A", "5B",
    "6.1", "6.2", "6.3", "6.4", "6.5", 
    "7.1a", "7.1b", "7.2", "7.3a", "7.3b"
]

DEMO_QUIZ_OPTIONS = [
    "3A", "3B", "3C",
    "4A", "4B", "4C",
    "5A", "5B",
    
]

def parse_questions(json_data):
    questions = []
    for section in json_data.get("sections", []):
        for q_data in section.get("questions", []):
            question_text = q_data.get("question")
            # Remove the pattern **(any alphabetical string) ** from the question string
            question_text = re.sub(r'\*\*\s*\((\s*[a-zA-Z]+\s*)\)\s*\*\*', '', question_text)
            # Remove patterns like (text, text):
            question_text = re.sub(r'\(([\w\s,]+)\):\s*', '', question_text)
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

def load_qa_files(selected_item):
    week_number = selected_item[0] # Extract the first character as the week number
    base_path = f"questions/Week {week_number}/"

    if selected_item in DEMO_QUIZ_OPTIONS:
        questions_file = f"{base_path}{selected_item} demo questions.json"
        answers_file = f"{base_path}{selected_item} demo answers.json"
    else:
        questions_file = f"{base_path}{selected_item} questions.json"
        answers_file = f"{base_path}{selected_item} answers.json"

    with open(questions_file, "r") as f:
        questions_data = json.load(f)
    with open(answers_file, "r") as f:
        answers_data = json.load(f)
    return questions_data, answers_data

def main():
    st.title("Quiz App")

    # Initialize session state
    if 'user_choices' not in st.session_state:
        st.session_state.user_choices = {}
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    if 'selected_quiz' not in st.session_state:
        st.session_state.selected_quiz = QUIZ_OPTIONS[0] # Default to the first option

    # Quiz selection
    selected_quiz_new = st.selectbox(
        "Select a quiz:",
        QUIZ_OPTIONS,
        index=QUIZ_OPTIONS.index(st.session_state.selected_quiz)
    )

    if selected_quiz_new != st.session_state.selected_quiz:
        st.session_state.selected_quiz = selected_quiz_new
        st.session_state.quiz_submitted = False
        st.session_state.user_choices = {}
        # Clear individual question choices from session state
        for key in list(st.session_state.keys()):
            if key.startswith('q') and key.endswith('_selected_options'):
                del st.session_state[key]
        st.rerun()

    # Load questions and answers
    try:
        questions_data, answers_data = load_qa_files(st.session_state.selected_quiz)
    except FileNotFoundError:
        st.error(f"Question or answer JSON file not found for {st.session_state.selected_quiz}. Make sure the paths are correct.")
        return
    except json.JSONDecodeError:
        st.error(f"Error decoding JSON file for {st.session_state.selected_quiz}. Please check the file format.")
        return

    questions = parse_questions(questions_data)
    correct_answers = parse_answers(answers_data)
    logger.info(f"questions loaded, {len(questions)} is size, {questions[0]} is first element")
    logger.info(f"answers loaded, {len(correct_answers.items())} is size")

    # Filter out questions that do not have corresponding answers
    initial_question_count = len(questions)
    questions = [q for q in questions if q["number"] in correct_answers]
    if len(questions) < initial_question_count:
        dropped_count = initial_question_count - len(questions)
        logger.info(f"Dropped {dropped_count} questions due to missing answers.")

    if not questions:
        st.warning("No questions found in the JSON file or no answers for existing questions.")
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
            is_checked = st.checkbox(
                opt,
                key=checkbox_key,
                value=(opt[0].lower() in st.session_state.get(f'q{q["number"]}_selected_options', [])),
                disabled=st.session_state.quiz_submitted
            )
            
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
