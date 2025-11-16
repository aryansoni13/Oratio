import requests
import os
import json
import pandas as pd

# --- Configuration ---
FLASK_URL = "http://127.0.0.1:5000/upload"
VIDEO_PATH = r"D:\.Study\projects\Eloquence-main\Eloquence-main\videoplayback.mp4"  # Using raw string for Windows path
USER_ID = "test_user_123"
CONTEXT = "2-Minute demo"
TITLE = "demo"

def run_test():
    """
    Sends a video file to the Flask backend and prints a formatted summary of the analysis.
    """
    if not os.path.exists(VIDEO_PATH):
        print(f"Error: Test video not found at '{VIDEO_PATH}'")
        return
    
    with open(VIDEO_PATH, 'rb') as video_file:
        files = {'file': (os.path.basename(VIDEO_PATH), video_file, 'video/mp4')}
        data = {'userId': USER_ID, 'context': CONTEXT, 'title': TITLE}

        print(f"Uploading '{VIDEO_PATH}' to {FLASK_URL}...")
        
        try:
            # Added a 10-minute timeout for longer processing
            response = requests.post(FLASK_URL, files=files, data=data, timeout=600)

            print(f"Server responded with status code: {response.status_code}")

            if response.status_code == 200:
                print("\n✅ Success! Pipeline completed.")
                report = response.json()
                
                print("\n" + "="*50)
                print(f" ANALYSIS REPORT FOR: {report.get('title', 'N/A')}")
                print("="*50)

                scores = report.get('scores', {})
                print("\n--- SCORES ---")
                print(f"  - Vocabulary:  {scores.get('vocabulary', 'N/A')} / 100")
                print(f"  - Voice:       {scores.get('voice', 'N/A')} / 100")
                print(f"  - Expressions: {scores.get('expressions', 'N/A')} / 100")
                
                print("\n--- LLM-GENERATED FEEDBACK ---")
                print("\n[Vocabulary Report]")
                vocab_report = report.get('vocabulary_report', 'N/A')
                if isinstance(vocab_report, dict):
                    print(json.dumps(vocab_report, indent=2))
                else:
                    print(vocab_report)
                print("\n[Vocal Tone Report]")
                print(report.get('speech_report', 'N/A'))
                print("\n[Expression Report]")
                print(report.get('expression_report', 'N/A'))

                print("\n--- FULL TRANSCRIPTION ---")
                # MODIFIED: Removed slicing to print the full transcription
                print(report.get('transcription', 'N/A'))
                print("\n" + "="*50)

            else:
                print("\n❌ Error! The server returned an error.")
                try:
                    print(response.json())
                except json.JSONDecodeError:
                    print(response.text)

        except requests.exceptions.RequestException as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please make sure your Flask app is running and accessible.")

if __name__ == "__main__":
    run_test()