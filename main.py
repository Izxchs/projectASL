import tkinter as tk
import cv2
import pickle
import numpy as np
import mediapipe as mp
import time
import enchant
import json
from tkinter import Canvas, Toplevel
from tkinter import messagebox
from PIL import Image, ImageTk

n_w = None
ne_wi = None
model_data = pickle.load(open('model/model.p', 'rb'))
gesture_model = model_data['model']

gesture_labels = {
    0: 'next', 1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h', 9: 'i',
    10: 'j', 11: 'k', 12: 'l', 13: 'm', 14: 'n', 15: 'o', 16: 'p', 17: 'q', 18: 'r', 19: 's',
    20: 't', 21: 'u', 22: 'v', 23: 'w', 24: 'x', 25: 'y', 26: 'z', 27: 'option1', 28: 'option2',
    29: 'option3', 30: 'backspace'
}

mp_hands = mp.solutions.hands
hand_detector = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

common_words = []
with open("jsonFile/suggestData.json", "r") as j_file:
    common_words=json.load(j_file)


english_dictionary = enchant.Dict("en_US")

def generate_suggestions(current_word):
    current_word = current_word.lower()
    sug = []
    for word in common_words:
        if word.startswith(current_word):
            sug.append(word)

    dictionary_suggestions = english_dictionary.suggest(current_word)
    #for i in range(0, 3):
    for i in range(3 if len(dictionary_suggestions)>3 else len(dictionary_suggestions)):
        if dictionary_suggestions[i] != 0:
            dictionary_suggestions[i] = dictionary_suggestions[i].lower()
        else:
            break
    
    return sug[:3] + dictionary_suggestions[:3]

# Function for starting the webcam
def start_webcam(canvas, width, height, text_display, suggestion_fields, predchar):
    webcam = cv2.VideoCapture(0)
    webcam.set(3, width)
    webcam.set(4, height)

    detected_text = ""
    last_prediction_time = time.time()
    current_character = None

    def update_frame():
        nonlocal detected_text, last_prediction_time, current_character
        ret, frame = webcam.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            detection_results = hand_detector.process(rgb_frame)
            hand_data = []
            x_coords, y_coords = [], []

            if detection_results.multi_hand_landmarks:
                for landmarks in detection_results.multi_hand_landmarks:
                    x_coords = [lm.x for lm in landmarks.landmark]
                    y_coords = [lm.y for lm in landmarks.landmark]

                    x_min, y_min = min(x_coords), min(y_coords)
                    for lm in landmarks.landmark:
                        hand_data.extend([lm.x - x_min, lm.y - y_min])

                if len(detection_results.multi_hand_landmarks) == 1:
                    hand_data.extend([0] * 42)

                if len(hand_data) == 84:
                    if time.time() - last_prediction_time >= 2:#changed 1 to 2 <<<----LOOOKKKKK HERRREEEE
                        prediction = gesture_model.predict([np.asarray(hand_data)])
                        predicted_label = gesture_labels[int(prediction[0])]
                        predchar.delete(0, tk.END)
                        predchar.insert(0, predicted_label)

                        if predicted_label == "next" and current_character:
                            detected_text += current_character
                            text_display.delete(0, tk.END)
                            text_display.insert(0, detected_text)

                            last_word = detected_text.split()[-1] if detected_text else ""
                            suggestions = generate_suggestions(last_word)
                            for i, field in enumerate(suggestion_fields):
                                field.delete(0, tk.END)
                                field.insert(0, suggestions[i] if i < len(suggestions) else "")

                            current_character = None
                        elif predicted_label == "backspace":
                            detected_text = detected_text[:-1].strip()
                            text_display.delete(0, tk.END)
                            text_display.insert(0, detected_text)
                        elif predicted_label in ["option1", "option2", "option3"]:
                            option_index = int(predicted_label[-1]) - 1
                            suggestion = suggestion_fields[option_index].get()
                            if suggestion:
                                words = detected_text.split()
                                if words:
                                    words[-1] = suggestion
                                else:
                                    words.append(suggestion)
                                detected_text = " ".join(words) + " "
                                text_display.delete(0, tk.END)
                                text_display.insert(0, detected_text)
                        elif predicted_label not in ["next", "backspace", "option1", "option2", "option3"]:
                            current_character = predicted_label

                        last_prediction_time = time.time()

            # Convert the OpenCV frame to an image that Tkinter can display
            canvas_image = Image.fromarray(rgb_frame)
            canvas_image_tk = ImageTk.PhotoImage(image=canvas_image)
            canvas.create_image(0, 0, anchor=tk.NW, image=canvas_image_tk)
            canvas.image = canvas_image_tk

        canvas.after(10, update_frame)

    update_frame()



def help():
    global n_w
    if n_w is None or not n_w.winfo_exists():  # this checks window is closed or not
        n_w = Toplevel()
        n_w.title("ASL image")
        n_w.geometry("700x648")
        n_w.resizable(False, False)
        ogimage = Image.open("images/ASL_Alphabet.jpg")
        img = ImageTk.PhotoImage(ogimage)

        label = tk.Label(n_w, text="Asl_Alphabets", image=img)
        label.image = img
        label.pack()
    else:
        messagebox.showerror('Easter egg', 'nah just an Error: Window already exists')

def adel():#window that is used to add and delete into list
    global ne_wi
    if ne_wi is None or not ne_wi.winfo_exists():  # this checks window is closed or not
        ne_wi = Toplevel()
        ne_wi.title("ADEL")
        ne_wi.geometry("700x500")
        ne_wi.resizable(False, False)
        ne_wi.configure(bg="#F95454")
        tk.Label(ne_wi, text="Recommendation Updater", font=("Arial", 18, "bold"),bg="#F95454",fg="#243642").place(relx = 0.5, rely = 0.3, anchor = "center")
        

        usrinp = tk.Text(ne_wi, font=("Arial", 14), height=3, width=50, wrap="word", bd=3, bg="#f3f3f3")
        usrinp.place(relx = 0.5, rely = 0.45, anchor = "center")

        def show_error(msg,fontColor):
            error_label = tk.Label(ne_wi, text=msg, fg=fontColor, font=("Helvetica", 12))
            error_label.place(relx = 0.5, rely = 0.56, anchor = "center")
            return
        
        def get_input():
            value=usrinp.get("1.0","end-1c")
            value=value.lower()

            if len(common_words) > 400:
                show_error('Input Error: You have reached max limit',"black")
                #messagebox.showerror('Input Error', 'You have reached max limit')
                return
            
            elif len(value) == 0:
                show_error('Input Error: Input cannot be empty',"black")
                #messagebox.showerror('Input Error', 'Input cannot be empty')
                return
            
            elif ' ' in value:
                show_error('Input Error: no space charecter nor multiple words allowed',"black")
                #messagebox.showerror('Input Error', 'no space charecter nor multiple words allowed')
                return
            
            elif len(value) > 50:
                show_error('Input Error: no more than 50 charecter per word',"black")
                #messagebox.showerror('Input Error', 'no more than 50 charecter per word')
                return
            
            elif value in common_words:
                show_error('Input Error: word already exits',"black")
                #messagebox.showerror('Input Error', 'word already exits')
                return
            
            else:
                common_words.append(value)
                with open("jsonFile/suggestData.json", "w") as suggestfile:
                    json.dump(common_words,suggestfile, indent=2)
                show_error('Input Success: yea the word is added',"green")
                return
        
        def get_default():
            response=messagebox.askokcancel("askokcancel", "Want to continue?")
            if response:
                default_val=[]
                with open("jsonFile/default.json", "r") as default_file:
                    default_val=json.load(default_file)
                with open("jsonFile/suggestData.json", "w") as main_file:
                        json.dump(default_val,main_file, indent=2)
            else:
                return    

        addbutton = tk.Button(ne_wi, height=2, width=15, text="ADD", command=get_input)
        addbutton.place(relx = 0.18, rely = 0.64, anchor = "center")
        default = tk.Button(ne_wi, height=2, width=15, text="Default", command=get_default)
        default.place(relx = 0.37, rely = 0.64, anchor = "center")
        
        
        #json.dump(common_words,json_file, indent=2)
        

    else:
        messagebox.showerror('Easter egg', 'nah just an Error: Window already exists')




def create_ui():
    app = tk.Tk()
    app.title("Sign Language to Text Conversion")
    app.geometry("900x700")
    app.resizable(False, False)
    app.configure(bg="#BCCCDC")
    #app.attributes('-fullscreen', True) #to make this full screen
    #app.bind("<Escape>", lambda e: app.attributes('-fullscreen', False))#pressing esc will exit(full scrn not proper rn)

    def create_circular_button(parent, text, command, x, y):
        button_canvas = Canvas(parent, width=50, height=50, highlightthickness=0, bg=app["bg"])
        button_canvas.place(relx=x, rely=y)
        button_canvas.create_oval(2, 2, 50, 50, fill="#010f1e", outline="")#outline
        #button_canvas.create_oval(2, 2, 50, 50, fill="#010f1e", outline="")#shadow
        button_canvas.create_oval(5, 5, 45, 45, fill="#1167b1", outline="")
        button_canvas.create_text(25, 25, text=text, fill="#FADA7A", font=("Arial", 14, "bold"))
        button_canvas.bind("<Button-1>", lambda event: command())

    create_circular_button(app, "?", help, x=0.82, y=0.1)
    create_circular_button(app, "+", adel, x=0.9, y=0.1)


    tk.Label(app, text="Sign Language to Text Conversion", bg="#BCCCDC",fg="#000009",font=("Arial", 18, "bold")).pack(pady=20)

    webcam_canvas = Canvas(app, width=500, height=350, bg="#000009", bd=4)
    webcam_canvas.place(relx=0.5, rely=0.4, anchor="center")

    predchar = tk.Entry(app, font=("Arial", 14), relief="raised", width=10, justify="center", bd=3, bg="#F8FAFC",fg="#0A3981")
    predchar.place(relx=0.5, rely=0.69, anchor="center")

    text_display = tk.Entry(app, font=("Arial", 14), relief="solid", width=40, justify="center", bd=3, bg="#f3f3f3")
    text_display.place(relx=0.5, rely=0.75, anchor="center")

    suggestion_fields = [
        tk.Entry(app, font=("Arial", 12), width=15, justify="center", relief="solid") for _ in range(3)
    ]
    for i, field in enumerate(suggestion_fields):
        field.place(relx=0.3 + i * 0.2, rely=0.85, anchor="center")

    start_webcam(webcam_canvas, 640, 480, text_display, suggestion_fields, predchar)

    app.mainloop()

create_ui()
