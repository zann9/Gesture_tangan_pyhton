import cv2
import mediapipe as mp
import pyttsx3
import threading
import math

# inisiasi
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# variabel status gesture
sequence = []  # simpan urutan gesture

# fungsi TTS (pakai thread + engine baru biar bisa diulang)
def speak(text):
    def run():
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")

        # pilih suara cewek (cek dulu index di print voices)
        if len(voices) > 1:
            engine.setProperty("voice", voices[1].id)  # biasanya 1 = female di Windows
        else:
            engine.setProperty("voice", voices[0].id)  # fallback

        engine.setProperty("rate", 150)   # lebih lambat biar jelas
        engine.setProperty("volume", 2.0)

        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=run, daemon=True).start()


def distance(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)



# fungsi mengenali gesture
def recognizeGesture(hand_landmarks):
    ujung_jempol = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    ujung_telunjuk = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    ujung_jaritengah = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ujung_jarimanis = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    ujung_jarikelingking = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

    pip_index = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
    pip_middle = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
    pip_ring = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP]
    pip_pinky = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP]

    # Halo 
    if (ujung_telunjuk.y < pip_index.y and
        ujung_jaritengah.y < pip_middle.y and
        ujung_jarimanis.y < pip_ring.y and
        ujung_jarikelingking.y < pip_pinky.y):
        return "hello"

    # Nama 
    if (ujung_telunjuk.y < pip_index.y and
        ujung_jaritengah.y < pip_middle.y and
        ujung_jarimanis.y > pip_ring.y and
        ujung_jarikelingking.y > pip_pinky.y):
        return "my name is"

    # Saya 
    if (ujung_jempol.y < ujung_telunjuk.y and
        ujung_jempol.y < ujung_jaritengah.y and
        ujung_jempol.y < ujung_jarimanis.y and
        ujung_jempol.y < ujung_jarikelingking.y):
        return "fauzan"
    

    # Huruf Fauzan
    jarak = distance(ujung_jempol, ujung_telunjuk)
    if (jarak < 0.05 and
        ujung_jaritengah.y < pip_middle.y and
        ujung_jarimanis.y < pip_ring.y and
        ujung_jarikelingking.y < pip_pinky.y):
        return "you can call me zann"
    
    #KELINGKING 
    if (ujung_jarikelingking.y < ujung_telunjuk.y and
        ujung_jarikelingking.y < ujung_jaritengah.y and
        ujung_jarikelingking.y < ujung_jarimanis.y and
        ujung_jarikelingking.y < ujung_jempol.y):
        return "hello guys"

    return None


# Kamera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

with mp_hands.Hands(min_detection_confidence=0.7,
                    min_tracking_confidence=0.7) as hands:
    

    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                gesture = recognizeGesture(hand_landmarks)

                if gesture:
                    cv2.putText(frame, gesture, (50, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    # simpan sequence jika berbeda
                    if not sequence or sequence[-1] != gesture:
                        sequence.append(gesture)

                # pengucapan disini
                if sequence and sequence[-1] == "hello":
                    speak("hello")
                    sequence = []

                elif sequence and sequence[-1] == "my name is":
                     speak("my name is")
                     sequence = []
                    
                elif sequence and sequence[-1] == "fauzan":
                    speak("fauzan")
                    sequence = []
                  
                elif sequence and sequence[-1] == "you can call me zann":
                    speak("you can call me zann")
                    sequence = []

                elif sequence and sequence[-1] == "hello guys":
                    speak("hello guys")
                    sequence = []
        else:
            sequence = []  # reset kalau tangan hilang dari kamera

        cv2.imshow("Gesture TTS", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC buat keluar
            break

cap.release()
cv2.destroyAllWindows()
