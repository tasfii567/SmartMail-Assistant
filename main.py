import os
import pickle
import base64
import datetime
import pyttsx3
import speech_recognition as sr
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import customtkinter as ctk
from tkinter import messagebox

# Scope for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Function to convert text to speech
def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Authenticate user
def authenticate_user():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                messagebox.showerror("Error", "'credentials.json' not found.")
                exit()
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# Fetch emails
def fetch_emails(search_query, max_emails=5):
    try:
        service = build('gmail', 'v1', credentials=authenticate_user())
        results = service.users().messages().list(userId='me', q=search_query, maxResults=max_emails).execute()
        messages = results.get('messages', [])

        if not messages:
            return ["No emails found."]

        email_contents = []
        for i, msg_data in enumerate(messages, start=1):
            msg = service.users().messages().get(userId='me', id=msg_data['id'], format='full').execute()
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
            sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown Sender")

            # Extract email body
            body = "No readable content found."
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                        break

            email_content = f"Email {i} from {sender}:\nSubject: {subject}\nBody: {body[:300]}...\n"
            email_contents.append(email_content)

        return email_contents
    except HttpError as error:
        return [f"An error occurred: {error}"]

# GUI Class
class EmailAssistantApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Voice Email Assistant")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")

        # Title Label
        self.title_label = ctk.CTkLabel(self, text="Voice Email Assistant", font=("Arial", 24, "bold"))
        self.title_label.pack(pady=20)

        # Buttons Frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10)

        # Buttons for commands
        self.today_button = ctk.CTkButton(self.button_frame, text="Read Today's Emails", command=self.read_today_emails)
        self.today_button.grid(row=0, column=0, padx=10)

        self.yesterday_button = ctk.CTkButton(self.button_frame, text="Read Yesterday's Emails", command=self.read_yesterday_emails)
        self.yesterday_button.grid(row=0, column=1, padx=10)

        self.specific_button = ctk.CTkButton(self.button_frame, text="Emails from Sender", command=self.fetch_specific_sender)
        self.specific_button.grid(row=0, column=2, padx=10)

        self.logout_button = ctk.CTkButton(self.button_frame, text="Log Out", command=self.logout)
        self.logout_button.grid(row=0, column=3, padx=10)

        # Text Box to Display Emails
        self.textbox = ctk.CTkTextbox(self, width=700, height=300, font=("Arial", 12))
        self.textbox.pack(pady=20)

        # Speech Command Button
        self.speech_button = ctk.CTkButton(self, text="Voice Command", command=self.speech_command)
        self.speech_button.pack(pady=10)

    # Command Functions
    def read_today_emails(self):
        self.display_emails("after:{}".format(datetime.date.today()))

    def read_yesterday_emails(self):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        self.display_emails(f"after:{yesterday} before:{datetime.date.today()}")

    def fetch_specific_sender(self):
        sender = ctk.CTkInputDialog(text="Enter sender's email address:", title="Sender Email").get_input()
        if sender:
            self.display_emails(f"from:{sender}")

    def speech_command(self):
        command = self.recognize_speech()
        if "today" in command:
            self.read_today_emails()
        elif "yesterday" in command:
            self.read_yesterday_emails()
        elif "log out" in command:
            self.logout()
        else:
            speak_text("Command not recognized.")

    def logout(self):
        if os.path.exists("token.pickle"):
            os.remove("token.pickle")
            speak_text("Logged out successfully.")
            messagebox.showinfo("Logout", "Logged out successfully.")
        else:
            messagebox.showinfo("Logout", "No active session found.")

    def display_emails(self, search_query):
        emails = fetch_emails(search_query)
        self.textbox.delete("1.0", "end")
        for email in emails:
            self.textbox.insert("end", email + "\n\n")
            speak_text(email[:150])  # Speak partial email content

    def recognize_speech(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            speak_text("Listening for your command...")
            try:
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio)
                return command.lower()
            except sr.UnknownValueError:
                messagebox.showerror("Error", "Could not understand your speech.")
                return ""
            except sr.RequestError:
                messagebox.showerror("Error", "Speech service error.")
                return ""

# Run the App
if __name__ == "__main__":
    app = EmailAssistantApp()
    app.mainloop()
    
    
    
