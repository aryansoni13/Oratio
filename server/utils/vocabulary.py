import os
import google.generativeai as genai


def evaluate_vocabulary(transcription, context):
    # Initialize the Gemini model
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Context: {context}
    Script: {transcription}
    
    Evaluate the following speech based on vocabulary. Provide a short report covering:
    - Vocabulary: Assess the richness, appropriateness, and clarity of the words used.
    - Highlight if the speech uses engaging and varied language or if it is repetitive or overly simple.
    - Do not include any scores in the report.
    """
    
    try:
        response = model.generate_content(prompt)
        evaluation = response.text
        print(evaluation)
        return evaluation
    except Exception as e:
        print(f"Error generating vocabulary evaluation: {str(e)}")
        return "Unable to evaluate vocabulary at this time."