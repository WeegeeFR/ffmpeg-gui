#Author: WeegeeFR
#Date: 6/19/2025
#Description: Class handling tkinter GUI

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from pathlib import Path

#important global variables
valid_photo_types = [
    ('Valid photo files', '*.png *.jpg *.jpeg'),
]
valid_video_types = [
    ('Valid video files', '*.mp4 *.wmv')
]
valid_audio_types = [
    ('valid audio files', '*.mp3 *.wav')
]

class GUI:
    #init function, used to make default window and variables
    def __init__(self):
        #define main window variables
        self.root = tk.Tk()
        self.root.title = self.root.title("FFmpeg GUI")
        self.root.geometry("600x400") 
        self.frame = tk.Frame(self.root)
        self.frame.grid()

        #define important tkinter variables
        self.media_type = tk.StringVar()
        self.file_type = tk.StringVar()
        self.input_directory = tk.StringVar()
        self.output_directory = tk.StringVar()
        self.input_file_label = tk.StringVar()
        self.output_file_label = tk.StringVar()

        self.input_directory.set("/")
        self.output_directory.set("/")
        self.media_type.set("Photo")
        self.file_type.set("File")
        self.input_file_label.set("No file selected.")
        self.output_file_label.set("No file selected.")

    def choose_file(self, label_type):
        #choose valid files to show based on
        valid_directory = valid_photo_types
        if (self.media_type.get() == "Video"):
            valid_directory = valid_video_types
        elif (self.media_type.get() == "Audio"):
            valid_directory = valid_audio_types
        #open file/directory ask
        new_directory = None
        if (self.file_type.get() == "File" and label_type == "Input"):
            new_directory = filedialog.askopenfilename(title="Select a file", initialdir=self.input_directory, filetypes=valid_directory)
        else:
            new_directory = filedialog.askdirectory(title="Select a folder", initialdir=self.input_directory)
        #if new directory, update variables
        if new_directory:
            file_name = Path(new_directory).name
            if label_type == "Input":
                self.input_directory.set(new_directory)
                self.input_file_label.set(file_name)
            else:
                self.output_directory.set(new_directory)
                self.output_file_label.set(file_name)
                print(self.input_directory.get())
                print(self.output_directory.get())

    #function used to create all major buttons
    def create_gui(self):
        #create radio buttons for file type
        file_label = tk.Label(self.frame, text="File Type: ").grid(column=0, row=0, padx=0, pady=10)
        folder_radio = tk.Radiobutton(self.frame, text="Folder", variable=self.file_type, value="Folder").grid(column=2, row=0, padx=0, pady=10)
        file_radio = tk.Radiobutton(self.frame, text="Single File", variable=self.file_type, value="File").grid(column=1, row=0, padx=0, pady=10)

        #create radio buttons for media type
        starting_label = tk.Label(self.frame, text="Media Type: ").grid(column=0, row=1, padx=0, pady=10)
        photo_radio = tk.Radiobutton(self.frame, text="Photo", variable=self.media_type, value="Photo").grid(column=1, row=1, padx=0, pady=10)
        video_radio = tk.Radiobutton(self.frame, text="Video", variable=self.media_type, value="Video").grid(column=2, row=1, padx=0, pady=10)
        audio_radio = tk.Radiobutton(self.frame, text="Audio", variable=self.media_type, value="Audio").grid(column=3, row=1, padx=0, pady=10)

        #create buttons/labels for input and output directories
        input_label = tk.Label(self.frame, text="Choose input files: ").grid(column=0, row=2, padx=5, pady=10)
        input_file = tk.Button(self.frame, text="Open File", command=lambda: self.choose_file("Input")).grid(column=1, row=2)
        input_file_label = tk.Label(self.frame, textvariable=self.input_file_label).grid(column=2, row=2, padx=5, pady=10)#used to show name of input file/folder
        
        output_label = tk.Label(self.frame, text="Choose output directory ").grid(column=0, row=3, padx=5, pady=10)
        output_file = tk.Button(self.frame, text="Open File", command=lambda: self.choose_file("Output")).grid(column=1, row=3)
        output_file_label = tk.Label(self.frame, textvariable=self.output_file_label).grid(column=2, row=3, padx=5, pady=10)#used to show name of the output folder

        #dropdown for desired filetype for conversion, only gives valid types depending on selected media type

        #dropdowns for codec to use, depending on file type given
        
        

    #function used to start main gui loop
    def start_gui(self):
        self.create_gui()
        self.root.mainloop()
