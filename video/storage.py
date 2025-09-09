from playsound import playsound

# Use a raw string literal to ensure the path is interpreted correctly.
audio_path = r"C:\Users\dines\OneDrive\Desktop\ingen dynamics\Security_System\low-battery-alert-sfx-345413.mp3"

try:
    playsound(audio_path)
    print("Siren played successfully!")
except Exception as e:
    print("Error playing siren:", e)
