import os
import tkinter as tk
from tkinter import scrolledtext
import cv2
from PIL import Image, ImageTk
import random
import datetime
import speech_recognition as sr
import pyttsx3
import threading
import _thread as thread
import time
from PIL import Image, ImageTk
from PIL import ImageSequence

class Llama:
    # Class variable to store generated responses across all instances
    generated_responses = set()

    def __init__(self, model_path, seed):
        # Implement the initialization of your Llama class here
        pass

    def generate(self, input_tokens, top_k, top_p, temp, repeat_penalty):
        print(f"Received input tokens: {input_tokens}")

        # Remove "### Human:" and "### Assistant:" tokens from the input
        input_tokens = [token for token in input_tokens if token not in [b'###', b'Human:', b'Assistant:']]

        # Convert input tokens to a string for uniqueness check
        input_key = self.detokenize(input_tokens).decode('utf-8', errors='replace')

        # Check if the response has been generated before
        if input_key in Llama.generated_responses:
            # If the response has been generated before, return an empty response
            return []
        
        # Add the input key to the set of generated responses
        Llama.generated_responses.add(input_key)

        # Echo the modified user's input as the response
        response = input_tokens

        return response

    def tokenize(self, text):
        # Implement the tokenization logic of your Llama class here
        # This is a simple example where we split the text into words
        return text.split()

    def detokenize(self, tokens):
        # Implement the detokenization logic of your Llama class here
        # This is a simple example where we join the tokens into a string
        return b" ".join(tokens)

    def token_eos(self):
        # Implement the logic to get the end-of-sequence token of your Llama class here
        pass

# Global variables
model_path = "llama-2-7b-chat.Q5_K_M.gguf"
version = "1.00"
ai_image_path = r"C:\Users\idles\OneDrive\Desktop\UAT\AI Class\AI Final\Pictures\ChatbotFemale.gif"
ai_image_talking_1_path = r"C:\Users\idles\OneDrive\Desktop\UAT\AI Class\AI Final\Pictures\ChatbotFemale.gif"  # Replace with the actual path
ai_image_talking_2_path = r"C:\Users\idles\OneDrive\Desktop\UAT\AI Class\AI Final\Pictures\ChatbotFemale.gif"  # Replace with the actual path

# Function to load the language model
def load_model():
    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"ERROR: The model path is not valid! Please check the path in the main.py file.")

    print("Loading model...")
    # Generate a random seed for the model
    seed = random.randint(1, 2**31)
    # Create and return a Llama language model
    llama_model = Llama(model_path=model_path, seed=seed)

    print("Model loaded successfully.")
    return llama_model

# Modify the generate_response function to use the class variable
def generate_response(model, input_tokens, prompt_input_text, text_area_display, engine, ai_image_label):
    # Display user input in the text area
    text_area_display.insert(tk.INSERT, f'\n\nUser: {prompt_input_text}\n')
    # Display chatbot prompt in the text area
    text_area_display.insert(tk.INSERT, "\n\nPikaPikaOver9000:")

    # Generate response tokens from the model
    response_tokens = model.generate(input_tokens, top_k=40, top_p=0.95, temp=0.72, repeat_penalty=1.1)

    # Initialize an empty response string
    response_text = ""
    # Iterate through the response tokens
    for token in response_tokens:
        try:
            # Decode the token and append to the response text
            word = model.detokenize([token]).decode('utf-8', errors='replace')
            response_text += word + ' '

            # Display the response text in the text area
            text_area_display.delete(1.0, tk.END)  # Clear previous content
            text_area_display.insert(tk.END, response_text + '\n')
            # Update the tkinter window
            root.update_idletasks()

            # Break the loop when the end of the sequence is reached
            if token == model.token_eos():
                break

        except UnicodeDecodeError as e:
            # Handle decoding errors by replacing invalid characters
            print(f"UnicodeDecodeError: {e}")
            response_text += " "  # Replace invalid characters with a space

    # Display the AI picture
    display_ai_picture(ai_image_label, ai_image_talking_1_path, is_speaking=True)  # Change the path as needed

    # Speak the response using the text-to-speech engine
    engine.say(response_text)
    threading.Thread(target=engine.runAndWait).start()

    # Speak the response using the text-to-speech engine in a separate thread
    thread.start_new_thread(run_speech_engine, (response_text, engine))


    # Display the AI picture without the talking effect
    display_ai_picture(ai_image_label, ai_image_path, is_speaking=False)  # Change the path as needed

def display_ai_picture(ai_image_label, ai_image_talking_path, is_speaking=True):
    try:
        # Load the AI image for talking effect
        ai_image_talking = Image.open(ai_image_talking_path)

        # Convert the image to a format compatible with Tkinter
        ai_image_tk_talking = ImageTk.PhotoImage(image=ai_image_talking)

        # Display the talking animation
        if is_speaking:
            ai_image_label.config(image=ai_image_tk_talking)
            ai_image_label.image = ai_image_tk_talking
            root.update_idletasks()
            root.after(200, lambda: display_ai_picture(ai_image_label, ai_image_talking_path, not is_speaking))
        else:
            # If not speaking, display the default image
            ai_image = Image.open(ai_image_path)
            ai_image_tk = ImageTk.PhotoImage(image=ai_image)
            ai_image_label.config(image=ai_image_tk)
            ai_image_label.image = ai_image_tk

    except Exception as e:
        print(f"Error displaying AI picture: {e}")

def send_message(model, text_area_main_user_input, text_area_display, engine, ai_image_label):
    # Get user input from the text area
    user_prompt_input_text = text_area_main_user_input.get('1.0', 'end-1c').strip()
    # Encode the user input
    byte_message = user_prompt_input_text.encode('utf-8')

    # Tokenize the user input for the model
    input_tokens = model.tokenize(b"### Human: " + byte_message + b"\n ### Assistant: ")

    if input_tokens is None:
        print("Error: Input tokens are None. Please check the tokenization process.")
        return

    print("Input tokens: ", input_tokens)

    # Generate a response based on the user input
    response_tokens = model.generate(input_tokens, top_k=40, top_p=0.95, temp=0.72, repeat_penalty=1.1)

    # Initialize an empty response string
    response_text = ""
    # Iterate through the response tokens
    for token in response_tokens:
        try:
            # Decode the token and append to the response text
            word = model.detokenize([token]).decode('utf-8', errors='replace')
            response_text += word + ' '

            # Display the response text in the text area
            text_area_display.delete(1.0, tk.END)  # Clear previous content
            text_area_display.insert(tk.END, response_text + '\n')
            # Update the tkinter window
            root.update_idletasks()

            # Break the loop when the end of the sequence is reached
            if token == model.token_eos():
                break

        except UnicodeDecodeError as e:
            # Handle decoding errors by replacing invalid characters
            print(f"UnicodeDecodeError: {e}")
            response_text += " "  # Replace invalid characters with a space

    # Display the AI picture
    display_ai_picture(ai_image_label, ai_image_talking_1_path, is_speaking=True)  # Change the path as needed

    # Speak the response using the text-to-speech engine
    engine.say(response_text)
    engine.runAndWait()

    # Speak the response using the text-to-speech engine in a separate thread
    threading.Thread(target=run_speech_engine, args=(response_text, engine)).start()

    # Clear the user input text area
    text_area_main_user_input.delete('1.0', 'end')

def speech_input(model, text_area_main_user_input, recognizer, microphone, text_area_display, engine, ai_image_label):
    try:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening...")
            audio = recognizer.listen(source, timeout=5)

        print("Recognizing...")
        user_input_text = recognizer.recognize_google(audio).strip()

        # Display the recognized text in the main user input text area
        text_area_main_user_input.insert(tk.INSERT, user_input_text)

        # Tokenize the recognized text for the model
        input_tokens = model.tokenize(b"### Human: " + user_input_text.encode('utf-8') + b"\n ### Assistant: ")

        # Generate and display the response
        generate_response(model, input_tokens, user_input_text, text_area_display, engine, ai_image_label)

    except sr.UnknownValueError:
        print("Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

def run_speech_engine(response_text, engine):
    # Check if the engine is already in a running state
    if not engine._inLoop:
        # Start the engine and run the loop
        engine.startLoop(False)
        engine.say(response_text)
        engine.iterate()
        engine.endLoop()

def main():
    # Load the language model
    global model  # Ensure that 'model' is a global variable
    model = load_model()

    # Initialize the speech recognition components
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    # Initialize the text-to-speech engine
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)

    # Create the main tkinter window
    global root
    root = tk.Tk()
    root.title(f"The Pika Pika 9000 -v{version} - {datetime.datetime.now().strftime('%Y-%m-%d')}")

    # Create a label for displaying the AI picture
    ai_image_label = tk.Label(root)
    ai_image_label.pack()

    # Create a frame for displaying the conversation
    frame_display = tk.Frame(root)
    scrollbar_frame_display = tk.Scrollbar(frame_display)
    text_area_display =  scrolledtext.ScrolledText(frame_display, height=25, width=128, yscrollcommand=scrollbar_frame_display.set)
    text_area_display.config(background="#202020", foreground="#ffff33", font=("Courier", 12))
    scrollbar_frame_display.config(command=text_area_display.yview)
    text_area_display.pack(side=tk.LEFT, fill=tk.BOTH)
    scrollbar_frame_display.pack(side=tk.RIGHT, fill=tk.Y)
    frame_display.pack()

    # Create a frame for controls and information
    frame_controls = tk.Frame(root)
    model_path_label = tk.Label(frame_controls, text=f"Model Path: {model_path}", font=("Courier", 12))
    model_path_label.pack(side=tk.LEFT, padx=10)
    frame_controls.pack(fill=tk.BOTH, padx=5, pady=5)

    # Create a frame for user input
    frame_user_input = tk.Frame(root)
    frame_main_user_input = tk.Frame(root)
    scrollbar_main_user_input = tk.Scrollbar(frame_main_user_input)
    text_area_main_user_input = scrolledtext.ScrolledText(frame_main_user_input, height=5, width=128, yscrollcommand=scrollbar_main_user_input.set)
    text_area_main_user_input.config(background="#202020", foreground="#ffff33", font=("Courier", 12))
    scrollbar_main_user_input.config(command=text_area_main_user_input.yview)
    text_area_main_user_input.pack(side=tk.LEFT, fill=tk.BOTH)
    scrollbar_main_user_input.pack(side=tk.RIGHT, fill=tk.Y)
    frame_main_user_input.pack()

    # Create a button to send user-typed messages
    send_button = tk.Button(root, text="Send", command=lambda: send_message(model, text_area_main_user_input, text_area_display, engine, ai_image_label))
    send_button.pack()

    # Create a button to initiate speech input
    speech_input_button = tk.Button(root, text="Speech Input", command=lambda: speech_input(model, text_area_main_user_input, recognizer, microphone, text_area_display, engine, ai_image_label))
    speech_input_button.pack()

    # Start the tkinter event loop
    root.mainloop()

# Entry point for the application
if __name__ == "__main__":
    main()