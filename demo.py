# # Import required libraries
# import getpass
# import speech_recognition as sr
# import spacy
# import imaplib
# import email
# from email.header import decode_header
# import pyttsx3

# # Function: Recognize speech and convert it to text
# def recognize_speech():
#     recognizer = sr.Recognizer()
#     with sr.Microphone() as source:
#         print("Listening for your command...")
#         audio = recognizer.listen(source)
#         try:
#             command = recognizer.recognize_google(audio)
#             print(f"You said: {command}")
#             return command
#         except sr.UnknownValueError:
#             print("Sorry, I couldn't understand that.")
#             return None
#         except sr.RequestError:
#             print("Error with the speech recognition service.")
#             return None

# # Function: Process the spoken command using NLP
# def process_command(command):
#     nlp = spacy.load("en_core_web_sm")
#     doc = nlp(command)
#     entities = {ent.label_: ent.text for ent in doc.ents}
#     numbers = [int(token.text) for token in doc if token.like_num]  # Extract numbers
#     print(f"Extracted Entities: {entities}")
#     print(f"Numbers in Command: {numbers}")
#     return entities, numbers

# # Function: Fetch emails (latest N or by keyword/sender)
# def fetch_emails(email_user, email_pass, search_criteria="ALL", limit=1):
#     try:
#         # Connect to the email server
#         mail = imaplib.IMAP4_SSL("imap.gmail.com")
#         mail.login(email_user, email_pass)
#         mail.select("inbox")

#         # Search emails based on criteria
#         status, messages = mail.search(None, search_criteria)
#         email_ids = messages[0].split()

#         if not email_ids:
#             print("No emails found matching the criteria.")
#             return "No emails found."

#         # Fetch the latest N emails
#         email_contents = []
#         for i in email_ids[-limit:]:
#             res, msg = mail.fetch(i, "(RFC822)")
#             for response in msg:
#                 if isinstance(response, tuple):
#                     msg = email.message_from_bytes(response[1])
#                     subject, encoding = decode_header(msg["Subject"])[0]
#                     if isinstance(subject, bytes):
#                         subject = subject.decode(encoding if encoding else "utf-8")

#                     # Get email body
#                     if msg.is_multipart():
#                         for part in msg.walk():
#                             if part.get_content_type() == "text/plain":
#                                 body = part.get_payload(decode=True).decode()
#                                 email_contents.append(f"Subject: {subject}\nBody: {body[:300]}...")
#                     else:
#                         body = msg.get_payload(decode=True).decode()
#                         email_contents.append(f"Subject: {subject}\nBody: {body[:300]}...")

#         mail.logout()
#         return email_contents

#     except Exception as e:
#         print("Error fetching email:", e)
#         return ["Unable to fetch your email."]

# # Function: Convert text to speech
# def speak_text(text):
#     engine = pyttsx3.init()
#     engine.say(text)
#     engine.runAndWait()

# # Function: Handle search criteria for emails
# def determine_search_criteria(entities):
#     if "PERSON" in entities:
#         sender = entities["PERSON"]
#         return f'(FROM "{sender}")'
#     elif "ORG" in entities:
#         sender = entities["ORG"]
#         return f'(FROM "{sender}")'
#     return "ALL"

# # Main program
# if __name__ == "__main__":
#     # Step 1: Prompt for email and password
#     print("Please enter your email credentials:")
#     email_user = input("Email: ")
#     email_pass = getpass.getpass("Password: ")  # Hides password input for security

#     # Step 2: Recognize speech
#     user_command = recognize_speech()

#     if user_command:
#         # Step 3: Process the command with NLP
#         entities, numbers = process_command(user_command)

#         # Determine how many emails to fetch
#         limit = numbers[0] if numbers else 1

#         # Step 4: Determine search criteria
#         search_criteria = determine_search_criteria(entities)

#         # Step 5: Fetch and read emails based on criteria
#         if "email" in user_command.lower():
#             print("Fetching your emails...")
#             speak_text("Fetching your emails...")
#             emails = fetch_emails(email_user, email_pass, search_criteria=search_criteria, limit=limit)

#             for i, email_content in enumerate(emails, start=1):
#                 print(f"\nEmail {i}:\n{email_content}")
#                 speak_text(f"Email {i}: {email_content}")
#         else:
#             print("Command not recognized. Please mention 'email' in your command.")
#             speak_text("Command not recognized. Please mention 'email' in your command.")


# # fyiv dmqb zdyl jtcu