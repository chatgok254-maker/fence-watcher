import subprocess
import sys
import numpy as np

def install(package):
    """ Installs missing python packages at runtime """
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install opencv, mediapipe, and simpleaudio if missing
try:
    import cv2
except ImportError:
    install("opencv-python")
    import cv2

try:
    import mediapipe as mp
except ImportError:
    install("mediapipe")
    import mediapipe as mp

try:
    import simpleaudio as sa
except ImportError:
    install("simpleaudio")
    import simpleaudio as sa

# setup pose detector and alarm
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()  # Corrected from pose() to Pose()
mp_drawing = mp.solutions.drawing_utils

# load alarm sound (the alarm.wav file must be present )
try:
    wave_obj = sa.WaveObject.from_wave_file("alarm.wav")
except Exception:
    print("No alarm.wav file found. Please place one on this folder.")
    wave_obj = None

# start video feed

from pytube import YouTube

#paste the url of the youtube video here
youtube_url = ''

try:
  yt = YouTube(youtube_url)
#get the highest resolution stream with both video and audio

stream = yt.streams.get_highest_resolution()
print(f"Downloading: {yt.title}...")
stream.download(filename='test_video.mp4')
print("Download complete!")

except Exception as e:
       print(f"An error occured during download: {e}") 

cap = cv2.VideoCapture('test_video.mp4')

jump_threshold = 100 # how much upward motion counts as jump
prev_y = None
alarm_on = False

print("Fence Jumper Detector Running... Press ESC To Exit.")

while True:
    ret, frame = cap.read()
    if not ret:
       break

    # The flip operation was corrected to be inside the loop
    # and moved up slightly for better logic flow.
    # frame = cv2.flip(frame, -1) # Uncomment this if you need to flip vertically and horizontally
    
    h, w, _  = frame.shape
    rgb  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(rgb)

    if result.pose_landmarks:
       left_hip =  result.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y * h
       right_hip = result.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].y * h
       avg_hip_y = (left_hip + right_hip) / 2
       mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
       
       # detect jump
       if prev_y is not None:
          if prev_y - avg_hip_y > jump_threshold:
             cv2.putText(frame, "Intruder jump Detected!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3) 
             if wave_obj and not alarm_on:
                wave_obj.play()
                alarm_on = True
          
          else:
               alarm_on = False # Corrected 'false' to 'False'
       
       prev_y = avg_hip_y # Moved out of the 'else' block
       
    cv2.imshow("Fence Jumper Detector AI", frame)
    
    # Corrected 'cv2.waitkey' to 'cv2.waitKey'
    if cv2.waitKey(1) & 0xFF == 27: # ESC key
       break
       
cap.release()
cv2.destroyAllWindows()