import os
import google.generativeai as gen_ai
from dotenv import load_dotenv
import nltk
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import string
from nltk.corpus import stopwords
import pickle
import json
import re
from google.generativeai.types import GenerationConfig
from flask import Flask, request, jsonify
from flask_cors import CORS

# Download necessary NLTK data
nltk.download("popular", quiet=True)

# Load environment variables
load_dotenv()

# Configure Google Gemini-Flash AI model
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Get API key from environment variables
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('models/gemini-2.0-flash-lite')

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up directory for storing assignment data
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    
PEER_ANSWERS_DIR = os.path.join(DATA_DIR, "peer_answers")
if not os.path.exists(PEER_ANSWERS_DIR):
    os.makedirs(PEER_ANSWERS_DIR)
    
MODEL_ANSWERS_DIR = os.path.join(DATA_DIR, "model_answers")
if not os.path.exists(MODEL_ANSWERS_DIR):
    os.makedirs(MODEL_ANSWERS_DIR)
    
RUBRICS_DIR = os.path.join(DATA_DIR, "rubrics")
if not os.path.exists(RUBRICS_DIR):
    os.makedirs(RUBRICS_DIR)

# Load the plagiarism detection model and vectorizer
try:
    plagiarism_model = pickle.load(open('model.pkl', 'rb'))
    tfidf_vectorizer = pickle.load(open('tfidf_vectorizer.pkl', 'rb'))
    print("Plagiarism detection models loaded successfully.")
except FileNotFoundError:
    print("Error: Plagiarism detection model or vectorizer file not found.")
    plagiarism_model = None
    tfidf_vectorizer = None

def save_assignment_data(assignment_id, data_type, content):
    """Save assignment-related data to file system for future reference"""
    if data_type == "model_answer":
        directory = MODEL_ANSWERS_DIR
    elif data_type == "rubric":
        directory = RUBRICS_DIR
    elif data_type == "peer_answer":
        directory = PEER_ANSWERS_DIR
    else:
        raise ValueError(f"Invalid data type: {data_type}")
        
    # Create a unique filename based on assignment ID
    filename = os.path.join(directory, f"{assignment_id}_{data_type}.json")
    
    # Save the data
    with open(filename, 'w') as file:
        json.dump({"content": content}, file)
        
    return filename

def load_assignment_data(assignment_id, data_type):
    """Load previously saved assignment data"""
    if data_type == "model_answer":
        directory = MODEL_ANSWERS_DIR
    elif data_type == "rubric":
        directory = RUBRICS_DIR
    elif data_type == "peer_answers":
        directory = PEER_ANSWERS_DIR
        # For peer answers, we need to load all files with the assignment ID
        peer_answers = []
        pattern = f"{assignment_id}_peer_answer_*.json"
        import glob
        files = glob.glob(os.path.join(directory, pattern))
        for file_path in files:
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    peer_answers.append(data["content"])
            except Exception as e:
                print(f"Error loading peer answer from {file_path}: {str(e)}")
        return peer_answers
    else:
        raise ValueError(f"Invalid data type: {data_type}")
    
    # For single file data types
    filename = os.path.join(directory, f"{assignment_id}_{data_type}.json")
    if not os.path.exists(filename):
        return None
        
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            return data["content"]
    except Exception as e:
        print(f"Error loading {data_type} for assignment {assignment_id}: {str(e)}")
        return None

def preprocess_text(text):
    """Preprocesses text by removing punctuation, converting to lowercase, and removing stop words."""
    if not text:
        return ""
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = text.lower()
    stop_words = set(stopwords.words("english"))
    text = " ".join(word for word in text.split() if word not in stop_words)
    return text

def detect_plagiarism_with_peers(input_text, assignment_id=None, student_id=None):
    """
    Detects plagiarism in the input text by comparing it with peer answers
    and provides detailed output.
    
    Args:
        input_text (str): The text to check for plagiarism
        assignment_id (str): The ID of the assignment
        student_id (str): The ID of the student (to avoid self-comparison)
        
    Returns:
        dict: Dictionary containing plagiarism results
    """
    if not input_text:
        return {
            "is_plagiarized": False,
            "plagiarism_score": 0,
            "plagiarized_parts": [],
            "message": "No text provided for plagiarism check."
        }
        
    if plagiarism_model is None or tfidf_vectorizer is None:
        return {
            "is_plagiarized": False,
            "plagiarism_score": 0,
            "plagiarized_parts": [],
            "message": "Plagiarism check not available due to missing models."
        }
    
    # Basic model-based plagiarism detection
    processed_text = preprocess_text(input_text)
    vectorized_text = tfidf_vectorizer.transform([processed_text])
    model_result = plagiarism_model.predict(vectorized_text)
    model_probability = plagiarism_model.predict_proba(vectorized_text)
    
    # Calculate plagiarism score (percentage) from the model
    model_plagiarism_score = round(model_probability[0][1] * 100, 2)
    
    # Load peer answers for this assignment
    peer_answers = []
    if assignment_id:
        peer_answers = load_assignment_data(assignment_id, "peer_answers")
    
    # Find plagiarized parts by comparing with peer answers
    plagiarized_parts = []
    max_similarity = 0
    most_similar_peer = None
    
    if peer_answers and isinstance(peer_answers, list) and len(peer_answers) > 0:
        # Calculate sentence level similarities
        sentences = nltk.sent_tokenize(input_text)
        input_sentences_processed = [preprocess_text(s) for s in sentences]
        
        for peer_idx, peer_answer in enumerate(peer_answers):
            # Skip comparison with own submission if student_id is provided
            peer_id = f"peer_{peer_idx+1}"
            if peer_id == student_id:
                continue
                
            peer_sentences = nltk.sent_tokenize(peer_answer)
            peer_sentences_processed = [preprocess_text(s) for s in peer_sentences]
            
            # Calculate document similarity
            input_vec = tfidf_vectorizer.transform([processed_text])
            peer_vec = tfidf_vectorizer.transform([preprocess_text(peer_answer)])
            similarity = cosine_similarity(input_vec, peer_vec)[0][0]
            
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_peer = peer_id
            
            # Find similar sentences
            for i, input_sent in enumerate(input_sentences_processed):
                if len(input_sent.split()) < 5:  # Skip very short sentences
                    continue
                    
                for j, peer_sent in enumerate(peer_sentences_processed):
                    # Calculate similarity between sentences
                    if len(peer_sent.split()) < 5:
                        continue
                        
                    sent_vec1 = tfidf_vectorizer.transform([input_sent])
                    sent_vec2 = tfidf_vectorizer.transform([peer_sent])
                    sent_similarity = cosine_similarity(sent_vec1, sent_vec2)[0][0]
                    
                    # If high similarity, mark as potentially plagiarized
                    if sent_similarity > 0.8:  # Threshold for sentence similarity
                        plagiarized_parts.append({
                            "text": sentences[i],
                            "index": i,
                            "similarity": float(sent_similarity),
                            "source": f"peer_{peer_idx+1}"
                        })
    
    # Calculate final plagiarism score
    # Combine model score with peer comparison
    peer_plagiarism_score = max_similarity * 100 if max_similarity > 0 else 0
    final_plagiarism_score = max(model_plagiarism_score, peer_plagiarism_score)
    
    # Determine if plagiarized based on score threshold
    is_plagiarized = final_plagiarism_score > 30 or len(plagiarized_parts) > 0
    
    # Construct response
    result_dict = {
        "is_plagiarized": is_plagiarized,
        "plagiarism_score": round(final_plagiarism_score, 2),
        "plagiarized_parts": plagiarized_parts,
        "most_similar_peer": most_similar_peer,
        "model_plagiarism_score": model_plagiarism_score,
        "peer_plagiarism_score": round(peer_plagiarism_score, 2),
        "message": "Plagiarism Detected" if is_plagiarized else "No Plagiarism Detected"
    }
    
    return result_dict

def generate_model_answer(assignment_text, total_marks=None):
    """Generates a model answer using Gemini."""
    prompt = (
        f"You are an expert educator creating a model answer for the following assignment question. "
        f"Please provide a comprehensive, well-structured response that would serve as an exemplary answer "
        f"for this assignment. Include all relevant information, analysis, and reasoning.\n\n"
        f"Assignment Question: {assignment_text}\n\n"
    )
    
    if total_marks:
        prompt += f"This assignment is worth {total_marks} marks in total.\n\n"
    
    prompt += "Please provide a detailed model answer that demonstrates mastery of the subject matter."
    
    chat_session = model.start_chat(history=[])
    
    generation_config = GenerationConfig(
        temperature=0.2,
        top_p=0.8,
        top_k=40
    )
    
    try:
        response = chat_session.send_message(prompt, generation_config=generation_config)
        return response.text
    except Exception as e:
        print(f"Error generating model answer: {str(e)}")
        return None

def generate_rubric(assignment_text, total_marks=None):
    """Generates a rubric using Gemini."""
    prompt = (
        f"You are an expert educator creating a comprehensive grading rubric for the following assignment. "
        f"Please develop a detailed, fair, and clear rubric that covers all aspects of evaluation.\n\n"
        f"Assignment Question: {assignment_text}\n\n"
    )
    
    if total_marks:
        prompt += (
            f"This assignment is worth {total_marks} marks in total. "
            f"Please distribute these marks across appropriate criteria in your rubric.\n\n"
        )
    
    prompt += (
        "Format the rubric with clearly defined criteria, levels of achievement, and point allocations. "
        "Make sure the rubric is comprehensive and aligned with academic standards."
    )
    
    chat_session = model.start_chat(history=[])
    
    generation_config = GenerationConfig(
        temperature=0.2,
        top_p=0.8,
        top_k=40
    )
    
    try:
        response = chat_session.send_message(prompt, generation_config=generation_config)
        return response.text
    except Exception as e:
        print(f"Error generating rubric: {str(e)}")
        return None

def generate_prompt(assignment_text, student_answer_text, model_answer_text, rubric_text, total_marks):
    """Generates an improved prompt for the Gemini model."""
    prompt = (
        f"You are an expert academic evaluator providing feedback to a student on their assignment submission. "
        f"You need to evaluate the student's answer and provide constructive, encouraging feedback. "
        f"Format your response in a structured way that helps the student understand their strengths and areas for improvement.\n\n"
        
        f"Please provide your evaluation with the following structure:\n"
        f"1. Create a JSON object at the very end of your response with these fields: "
        f"   - 'total_score': a number representing the final score\n"
        f"   - 'max_score': the maximum possible score\n"
        f"   - 'percentage': the percentage score\n"
        f"   - 'criteria_scores': an object with each criterion and its score\n\n"
        
        f"2. Before the JSON, provide a personalized evaluation with these sections:\n"
        f"   - 'Overall Assessment': A brief 2-3 sentence summary of the submission\n"
        f"   - 'Strengths': 2-3 specific strengths of the student's work\n"
        f"   - 'Areas for Improvement': 2-3 specific areas where the student could improve\n"
        f"   - 'Criterion-by-Criterion Feedback': Detailed feedback on each criterion from the rubric\n"
        f"   - 'Next Steps': Specific, actionable suggestions for how the student could improve\n\n"
        
        f"Assignment Question: {assignment_text}\n\n"
        f"Student's Answer: {student_answer_text}\n\n"
    )

    if total_marks is not None:
        prompt += f"Total marks available: {total_marks}\n\n"

    if model_answer_text:
        prompt += f"Model Answer (reference only, do not mention this directly to the student): {model_answer_text}\n\n"
        
    if rubric_text:
        prompt += f"Rubric: {rubric_text}\n\n"
        prompt += "Please evaluate strictly according to the provided rubric."
    else:
        prompt += ("No rubric provided. Please create and use a suitable rubric based on "
                  "the subject matter and academic level before evaluation.")

    prompt += ("\n\nIMPORTANT: Be encouraging and constructive in your feedback. Focus on how the student can improve rather than just what they did wrong. "
              "Use a supportive tone throughout. Remember to include the JSON object at the end of your response with the score information.")
    
    return prompt

def check_assignment(assignment_id, assignment_text, student_answer_text, student_id=None, model_answer_text="", rubric_text="", total_marks=None):
    """Checks the assignment using Gemini-Pro and performs enhanced plagiarism check against peers."""
    
    if not assignment_text or not student_answer_text:
        return {
            "feedback": "Error: Please provide both assignment question and student answer.",
            "score_data": None,
            "plagiarism_data": None
        }

    if total_marks is not None and not str(total_marks).isdigit():
        return {
            "feedback": "Error: Please enter a valid total marks value.",
            "score_data": None,
            "plagiarism_data": None
        }

    # Check if we need to generate and save a model answer
    if not model_answer_text and assignment_id:
        # Try to load existing model answer
        existing_model_answer = load_assignment_data(assignment_id, "model_answer")
        if existing_model_answer:
            model_answer_text = existing_model_answer
        else:
            # Generate a new model answer
            model_answer_text = generate_model_answer(assignment_text, total_marks)
            if model_answer_text:
                # Save the generated model answer
                save_assignment_data(assignment_id, "model_answer", model_answer_text)
    
    # Check if we need to generate and save a rubric
    if not rubric_text and assignment_id:
        # Try to load existing rubric
        existing_rubric = load_assignment_data(assignment_id, "rubric")
        if existing_rubric:
            rubric_text = existing_rubric
        else:
            # Generate a new rubric
            rubric_text = generate_rubric(assignment_text, total_marks)
            if rubric_text:
                # Save the generated rubric
                save_assignment_data(assignment_id, "rubric", rubric_text)

    # Generate prompt for Gemini
    prompt = generate_prompt(assignment_text, student_answer_text, model_answer_text, rubric_text, total_marks)

    # Initialize chat session with Gemini
    chat_session = model.start_chat(history=[])

    # Set generation config with low temperature for consistent results
    generation_config = GenerationConfig(
        temperature=0.2,
        top_p=0.8,
        top_k=40,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    # Send the message with the generation config
    try:
        response = chat_session.send_message(prompt, generation_config=generation_config)
        feedback_text = response.text
        
        # Extract JSON score data
        # Look for JSON data at the end of the response
        json_match = re.search(r'```json\s*(.*?)\s*```', feedback_text, re.DOTALL)
        if not json_match:
            json_match = re.search(r'{[\s\S]*"total_score"[\s\S]*}', feedback_text)
            
        score_data = None
        if json_match:
            try:
                json_str = json_match.group(1) if '```json' in feedback_text else json_match.group(0)
                score_data = json.loads(json_str)
                # Remove the JSON from the feedback text
                feedback_text = re.sub(r'```json\s*(.*?)\s*```', '', feedback_text, flags=re.DOTALL)
                feedback_text = re.sub(r'{[\s\S]*"total_score"[\s\S]*}', '', feedback_text)
            except json.JSONDecodeError:
                print("Failed to parse JSON from response")
                score_data = None
        
        # Save student answer as peer answer for future plagiarism checks
        if assignment_id and student_answer_text:
            peer_filename = f"{assignment_id}_peer_answer_{student_id if student_id else 'anon_' + str(int(time.time()))}.json"
            save_path = os.path.join(PEER_ANSWERS_DIR, peer_filename)
            with open(save_path, 'w') as file:
                json.dump({"content": student_answer_text}, file)
                
        # Perform plagiarism check against peer answers
        plagiarism_data = detect_plagiarism_with_peers(student_answer_text, assignment_id, student_id)
        
        # Add plagiarism info to feedback but not the detailed data
        if plagiarism_data["is_plagiarized"]:
            feedback_text += f"\n\n**Plagiarism Alert**: Approximately {plagiarism_data['plagiarism_score']}% of your submission shows signs of plagiarism. Academic integrity is important - please ensure all work is original and properly cited."
        
        return {
            "feedback": feedback_text.strip(),
            "score_data": score_data,
            "plagiarism_data": plagiarism_data
        }
        
    except Exception as e:
        print(f"Error calling Gemini API: {str(e)}")
        return {
            "feedback": f"Error evaluating assignment: {str(e)}",
            "score_data": None,
            "plagiarism_data": None
        }

@app.route('/api/evaluate', methods=['POST'])
def evaluate_assignment():
    """API endpoint to evaluate an assignment"""
    try:
        data = request.json
        
        assignment_id = data.get('assignmentId', '')
        student_id = data.get('studentId', '')
        assignment_text = data.get('assignmentQuestion', '')
        student_answer = data.get('studentAnswer', '')
        model_answer = data.get('modelAnswer', '')
        rubric = data.get('rubric', '')
        total_marks = data.get('totalMarks')
        
        if total_marks:
            try:
                total_marks = int(total_marks)
            except ValueError:
                return jsonify({"error": "Total marks must be a number"}), 400
        
        # If no assignment ID is provided, generate one based on the question
        if not assignment_id:
            import hashlib
            assignment_id = hashlib.md5(assignment_text.encode()).hexdigest()[:10]
        
        result = check_assignment(
            assignment_id,
            assignment_text,
            student_answer,
            student_id,
            model_answer,
            rubric,
            total_marks
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/assignments/<assignment_id>/model-answer', methods=['GET'])
def get_model_answer(assignment_id):
    """API endpoint to retrieve a model answer for an assignment"""
    try:
        model_answer = load_assignment_data(assignment_id, "model_answer")
        if model_answer:
            return jsonify({"model_answer": model_answer})
        else:
            return jsonify({"error": "Model answer not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/assignments/<assignment_id>/rubric', methods=['GET'])
def get_rubric(assignment_id):
    """API endpoint to retrieve a rubric for an assignment"""
    try:
        rubric = load_assignment_data(assignment_id, "rubric")
        if rubric:
            return jsonify({"rubric": rubric})
        else:
            return jsonify({"error": "Rubric not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Fix missing import
    import time
    
    # Run the Flask app
    app.run(debug=True, port=5000)