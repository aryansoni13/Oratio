from flask import Flask, request, jsonify
import pymongo
import re
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.user_routes import user_bp
from flask_cors import CORS
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from bson import ObjectId
import json

# Defer heavy/optional imports (pandas, google.generativeai and analysis utils)
ANALYSIS_AVAILABLE = False
try:
    import pandas as pd
    import google.generativeai as genai

    # Import updated utility functions (may require heavy ML deps)
    from utils.audioextraction import extract_audio_to_memory
    from utils.expressions import analyze_video_emotions
    from utils.transcription import speech_to_text_long
    from utils.vocals import predict_emotion
    from utils.vocabulary import evaluate_vocabulary

    ANALYSIS_AVAILABLE = True
except Exception:
    ANALYSIS_AVAILABLE = False

app = Flask(__name__)
CORS(app)
load_dotenv()

# Database and Services Setup
MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    raise ValueError("MONGODB_URI not set in environment variables")
client = pymongo.MongoClient(MONGO_URI)
db = client["Eloquence"]
# Collections
users_collection = db["users"]
admins_collection = db["admins"]
reports_collection = db["reports"]
overall_reports_collection = db["overall_reports"]

# Gemini client setup (only when available and API key present)
gemini_model = None
if ANALYSIS_AVAILABLE and os.environ.get("GOOGLE_API_KEY"):
    try:
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        gemini_model = genai.GenerativeModel("gemini-2.5-flash")
    except Exception:
        gemini_model = None

# Application Configuration
UPLOAD_FOLDER = 'Uploads'
ALLOWED_EXTENSIONS = {'mp4', 'wav', 'mp3', 'm4a'}  # Expanded to include common audio formats
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_keys_to_strings(data):
    """
    Recursively converts all numeric keys in a dictionary to strings.
    """
    if isinstance(data, dict):
        return {str(k): convert_keys_to_strings(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_keys_to_strings(item) for item in data]
    else:
        return data

def convert_objectid_to_string(data):
    """
    Recursively converts all ObjectId fields in a dictionary to strings.
    """
    if isinstance(data, dict):
        return {k: convert_objectid_to_string(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_string(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

# Register auth routes
app.register_blueprint(auth_bp)
# Register admin and user blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

@app.route('/')
def home():
    return "Hello World"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    
    context = request.form.get('context', '')
    title = request.form.get('title', 'Untitled Session')
    user_id = request.form.get('userId')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "No selected or allowed file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        mode = "video" if file.filename.rsplit('.', 1)[1].lower() == 'mp4' else 'audio'

        # In-memory audio processing
        if mode == "video":
            audio_data = extract_audio_to_memory(file_path)
            if audio_data is None:
                return jsonify({"error": "Failed to extract audio from video"}), 500
            facial_emotion_analysis = analyze_video_emotions(file_path)
        else:  # Audio mode
            audio_data = file_path  # Pass the audio file path directly
            facial_emotion_analysis = pd.DataFrame()

        # Run analysis with updated utility functions
        transcription = speech_to_text_long(audio_data)
        vocal_emotion_analysis = predict_emotion(audio_data)
        vocabulary_report = evaluate_vocabulary(transcription, context)
        
        # Convert DataFrame to string for LLM processing
        emotion_analysis_str = facial_emotion_analysis.to_string(index=False) if not facial_emotion_analysis.empty else "No facial data"

        scores = generate_scores(transcription, vocal_emotion_analysis, emotion_analysis_str)
        speech_report = generate_speech_report(transcription, context, vocal_emotion_analysis)
        expression_report = generate_expression_report(emotion_analysis_str) if mode == "video" else "No expression analysis for audio-only mode."

        # Prepare and save report
        report_data = {
            "userId": user_id,
            "title": title,
            "context": context,
            "transcription": transcription,
            "vocabulary_report": vocabulary_report,
            "speech_report": speech_report,
            "expression_report": expression_report,
            "scores": scores
        }
        result = reports_collection.insert_one(report_data.copy())
        report_data["_id"] = str(result.inserted_id)
        update_overall_reports(user_id)
        report_data = convert_objectid_to_string(report_data)

        return jsonify(report_data), 200

    except Exception as e:
        print(f"An error occurred during processing: {e}")
        return jsonify({"error": "An internal server error occurred during analysis"}), 500
    finally:
        # Cleanup: Remove uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

def update_overall_reports(user_id):
    """
    Recalculate and update the overall reports and scores for a user.
    """
    user_reports = list(reports_collection.find({"userId": user_id}))

    if not user_reports:
        return

    total_vocabulary = 0
    total_voice = 0
    total_expressions = 0
    for report in user_reports:
        total_vocabulary += report["scores"]["vocabulary"]
        total_voice += report["scores"]["voice"]
        total_expressions += report["scores"]["expressions"]

    avg_vocabulary = total_vocabulary / len(user_reports)
    avg_voice = total_voice / len(user_reports)
    avg_expressions = total_expressions / len(user_reports)

    overall_reports = generate_overall_reports(user_reports)

    overall_report_data = {
        "userId": user_id,
        "avg_vocabulary": avg_vocabulary,
        "avg_voice": avg_voice,
        "avg_expressions": avg_expressions,
        "overall_reports": overall_reports
    }

    overall_reports_collection.update_one(
        {"userId": user_id},
        {"$set": overall_report_data},
        upsert=True
    )

@app.route('/user-reports-list', methods=['GET'])
def get_user_reports_list():
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user_reports = list(reports_collection.find({"userId": user_id}))

    if not user_reports:
        return jsonify({"error": "No reports found for the user"}), 404

    user_reports = convert_objectid_to_string(user_reports)

    return jsonify(user_reports), 200

@app.route('/user-reports', methods=['GET'])
def get_user_reports():
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    overall_report = overall_reports_collection.find_one({"userId": user_id})

    if not overall_report:
        return jsonify({"error": "No overall report found for the user"}), 404

    overall_report = convert_objectid_to_string(overall_report)

    return jsonify(overall_report), 200

def generate_overall_reports(user_reports):
    """
    Generate three separate overall reports for Voice, Expressions, and Vocabulary.
    """
    # Convert ObjectId fields to strings for JSON safety
    user_reports = convert_objectid_to_string(user_reports)

    # If Gemini/analysis is available, prefer LLM-generated summaries
    if gemini_model is not None:
        try:
            voice_system_message = "You are an expert in speech analysis."
            voice_user_message = f"Reports: {json.dumps(user_reports, indent=2)}"
            voice_response = gemini_model.generate_content([voice_system_message, voice_user_message])
            voice_report = voice_response.text

            expressions_system_message = "You are an expert in facial expression analysis."
            expressions_user_message = f"Reports: {json.dumps(user_reports, indent=2)}"
            expressions_response = gemini_model.generate_content([expressions_system_message, expressions_user_message])
            expressions_report = expressions_response.text

            vocabulary_system_message = "You are an expert in language and vocabulary analysis."
            vocabulary_user_message = f"Reports: {json.dumps(user_reports, indent=2)}"
            vocabulary_response = gemini_model.generate_content([vocabulary_system_message, vocabulary_user_message])
            vocabulary_report = vocabulary_response.text
        except Exception:
            voice_report = expressions_report = vocabulary_report = "Analysis error"
    else:
        # Fallback: simple local summaries when heavy deps are not installed
        cnt = len(user_reports) if user_reports else 0
        voice_report = f"(local) Aggregated {cnt} reports — voice summary placeholder."
        expressions_report = f"(local) Aggregated {cnt} reports — expressions summary placeholder."
        vocabulary_report = f"(local) Aggregated {cnt} reports — vocabulary summary placeholder."

    return {
        "voice_report": voice_report,
        "expressions_report": expressions_report,
        "vocabulary_report": vocabulary_report,
    }



def generate_scores(transcription, audio_emotion, emotion_analysis):
    """
    Generate scores for Vocabulary, Voice, and Expressions using the LLM.
    """
    system_message = """
    You are an expert in speech analysis. Based on the provided transcription, audio emotion data, 
    and facial emotion analysis, generate scores (out of 100) for the following categories using these criteria:

    - Vocabulary: Measures the richness and relevance of words.
      - 90-100: Highly varied, sophisticated vocabulary perfectly suited to context; no repetition or clichés.
      - 70-89: Good variety and relevance; minor repetition or simplicity.
      - 50-69: Basic vocabulary; some irrelevance or overuse of simple terms.
      - 30-49: Limited variety; frequent repetition or inappropriate words.
      - 0-29: Poor, repetitive, or irrelevant vocabulary.

    - Voice: Assesses the expressiveness and emotional impact of vocal tone.
      - 90-100: Excellent expressiveness; emotions perfectly match context (e.g., enthusiastic for motivational speech).
      - 70-89: Good match and clarity; minor mismatches in tone.
      - 50-69: Average expressiveness; some unclear or mismatched emotions.
      - 30-49: Limited emotional range; frequent mismatches.
      - 0-29: Monotone or completely mismatched emotions.

    - Expressions: Evaluates the appropriateness of facial expressions.
      - 90-100: Dynamic, engaging expressions fully aligned with speech tone and context.
      - 70-89: Mostly appropriate and consistent; minor inconsistencies.
      - 50-69: Average dynamism; some mismatches with tone.
      - 30-49: Limited expressiveness; frequent inconsistencies.
      - 0-29: Inappropriate or flat expressions.

    Provide only the three scores in JSON format, like:
    {"vocabulary": 85, "voice": 78, "expressions": 90}
    """

    user_message = f"""
    Transcription: {transcription}

    Audio Emotion Data: {audio_emotion}

    Facial Emotion Analysis: {emotion_analysis}

    Provide only the JSON output with numeric scores based on the criteria.
    """

    # If Gemini is available, use it; otherwise return safe defaults
    if gemini_model is not None:
        try:
            response = gemini_model.generate_content(
                [system_message, user_message],
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.0
                )
            )
            cleaned_text = re.sub(r'```(?:json)?\s*|\s*```', '', response.text).strip()
            scores = json.loads(cleaned_text)
            for key in ['vocabulary', 'voice', 'expressions']:
                if not isinstance(scores.get(key), int) or not 0 <= scores[key] <= 100:
                    scores[key] = 0
            return scores
        except Exception as e:
            print(f"Error parsing scores: {e}")
            return {"vocabulary": 0, "voice": 0, "expressions": 0}
    else:
        # Fallback deterministic scoring (placeholders)
        return {"vocabulary": 50, "voice": 50, "expressions": 50}

def generate_speech_report(transcription, context, audio_emotion):
    system_message = f"""
    You are an expert in emotional and contextual analysis of speeches. Based on the context: "{context}", 
    evaluate if the emotions expressed in the audio match the intended purpose. Consider the following emotion data:
    {audio_emotion}.
    """
    user_message = """
    Provide a short one paragraph report on the emotional appropriateness of the speech. Focus on:
    - Emotional tone: Does the tone match the context and intended message?
    - Clarity: Is the speech clear and easy to understand?
    - Expressiveness: Does the speaker effectively convey emotions through their voice?
    - Do not include any scores in the report.
    """
    if gemini_model is not None:
        try:
            response = gemini_model.generate_content([system_message, user_message])
            return response.text
        except Exception:
            return "Analysis temporarily unavailable"
    # Fallback
    return "Analysis not available in this environment"

def generate_expression_report(emotion_analysis_str):
    """
    Generate a report based on the emotion analysis data.
    """
    system_message = f"""
    You are an expert in emotional analysis of facial expressions. Evaluate the following emotion data:
    {emotion_analysis_str}.
    """
    user_message = """
    Provide a short one paragraph report on the emotional appropriateness of the facial expressions. Focus on:
    - Emotional appropriateness: Do the facial expressions match the context and intended message?
    - Expressiveness: Are the facial expressions dynamic and engaging?
    - Consistency: Are the facial expressions consistent with the tone of the speech?
    - Do not include any scores in the report.
    """
    if gemini_model is not None:
        try:
            response = gemini_model.generate_content([system_message, user_message])
            return response.text
        except Exception:
            return "Analysis temporarily unavailable"
    return "Analysis not available in this environment"

if __name__ == '__main__':
    # On Windows the reloader can cause socket issues; run without the auto-reloader in dev here.
    app.run(host='127.0.0.1', port=5000, debug=False)