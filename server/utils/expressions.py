import cv2
from deepface import DeepFace
import pandas as pd
import warnings
import os

# Suppress TensorFlow warnings for a cleaner output
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def analyze_video_emotions(video_file_path: str, sample_rate: int = 1):
    """
    Analyzes emotions by sampling frames and summing emotion scores using DeepFace.
    Returns both a DataFrame of aggregated scores and a timeline of dominant emotions.

    Args:
        video_file_path (str): Path to the video file to be analyzed.
        sample_rate (int): The number of frames to process per second.
                           Defaults to 1.

    Returns:
        tuple (pd.DataFrame, list): 
            - DataFrame with 'Human Emotions' and 'Emotion Value from the Video'.
            - List of timeline chunks.
    """
    try:
        cap = cv2.VideoCapture(video_file_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file {video_file_path}")
            return pd.DataFrame(), []

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30.0
        frame_interval = max(1, int(fps / sample_rate))

        emotion_scores = {
            'angry': 0.0, 'disgust': 0.0, 'fear': 0.0, 'happy': 0.0,
            'sad': 0.0, 'surprise': 0.0, 'neutral': 0.0
        }
        
        timeline = []
        frame_count = 0
        chunk_idx = 0
        print(f"Starting emotion analysis for {video_file_path} at {sample_rate} FPS...")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break 
            
            if frame_count % frame_interval == 0:
                try:
                    result = DeepFace.analyze(
                        img_path=frame,
                        actions=['emotion'],
                        enforce_detection=False,
                        detector_backend='opencv',
                        silent=True
                    )
                    
                    if result and result[0]:
                        frame_emotions = result[0]['emotion']
                        for emotion, score in frame_emotions.items():
                            if emotion in emotion_scores:
                                emotion_scores[emotion] += (score / 100.0)
                        
                        dominant = result[0]['dominant_emotion']
                        current_time = frame_count / fps
                        timeline.append({
                            "start_time": current_time,
                            "end_time": current_time + (1.0 / sample_rate),
                            "emotion": dominant,
                            "chunk": chunk_idx
                        })
                        chunk_idx += 1
                except Exception:
                    pass
            
            frame_count += 1
            
        cap.release()
        print("Emotion analysis finished successfully.")

        score_comparisons = pd.DataFrame({
            'Human Emotions': [k.capitalize() for k in emotion_scores.keys()],
            'Emotion Value from the Video': list(emotion_scores.values())
        })

        return score_comparisons, timeline

    except Exception as e:
        print(f"An unexpected error occurred during emotion analysis: {e}")
        return pd.DataFrame(), []