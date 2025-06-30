#Author: WeegeeFR
#Date: 6/19/2025
#Description: Class handling tkinter GUI

import tkinter as tk
from ffmpeg_logic import ffmpeg_logic
from tkinter import filedialog
from tkinter import messagebox
from pathlib import Path

# important global variables for any object to use
valid_photo_types = [
    ('Valid photo files', '*.png *.jpg *.jpeg *.gif *.bmp *.apng'),
]
valid_video_types = [
    ('Valid video files', '*.mp4 *.wmv *.webm *.mov *.mkv *.avc *.hevc *.m4v')
]
valid_audio_types = [
    ('valid audio files', '*.mp3 *.wav *.m4a *.aac *.wma *.alac *.flac')
]

valid_photo_conversion_types = [".png", "jpg",".jpeg", ".gif", ".bmp", ".apng"]
valid_audio_conversion_types = [".mp3", ".wav", ".m4a", ".aac", ".wma", ".alac", ".flac"]
valid_video_conversion_types = [".mp4", ".wmv", ".webm", ".mov", ".mkv", ".avc", ".hevc", ".m4v"]

class GUI:
    # init function, used to make default window and variables
    def __init__(self):
        # Define main window variables
        self.root = tk.Tk()
        self.root.title = self.root.title("FFmpeg GUI")
        self.root.geometry("600x400") 
        self.frame = tk.Frame(self.root)
        self.conversion_frame = tk.Frame(self.root)

        # variable to handle the conversion update function
        self.converting = True

        # Define important tkinter variables for elements to use across the class
        self.media_type = tk.StringVar()
        self.file_type = tk.StringVar()
        self.input_directory = tk.StringVar()
        self.output_directory = tk.StringVar()
        self.input_file_label = tk.StringVar()
        self.output_file_label = tk.StringVar()
        self.desired_filetype = tk.StringVar()
        self.current_conversion = tk.StringVar()
        self.current_time = tk.StringVar()
        self.error_label = tk.StringVar()


        self.input_directory.set("None")
        self.output_directory.set("None")
        self.desired_filetype.set(' ')
        self.media_type.set("Photo")
        self.file_type.set("File")
        self.input_file_label.set("No file selected.")
        self.output_file_label.set("No file selected.")
        self.current_conversion.set("Nothing converting...")

    # Function to handle choosing fil directories
    def choose_file(self, label_type):
        # Choose valid files to show based on
        valid_directory = valid_photo_types
        if (self.media_type.get() == "Video"):
            valid_directory = valid_video_types
        elif (self.media_type.get() == "Audio"):
            valid_directory = valid_audio_types
        # Open file/directory ask
        new_directory = None
        if (self.file_type.get() == "File" and label_type == "Input"):
            new_directory = filedialog.askopenfilename(title="Select a file", initialdir=self.input_directory, filetypes=valid_directory)
        else:
            new_directory = filedialog.askdirectory(title="Select a folder", initialdir=self.input_directory)
        # if new directory, update variables
        if new_directory:
            file_name = Path(new_directory).name
            if label_type == "Input":
                self.input_directory.set(new_directory)
                self.input_file_label.set(file_name)
            else:
                self.output_directory.set(new_directory)
                self.output_file_label.set(file_name)
    
    # Function for handeling valid formats 
    def get_valid_formats(self):
        if (self.media_type.get() == "Photo"):
            return valid_photo_types
        elif (self.media_type.get() == "Video"):
            return valid_video_types
        else:
            return valid_audio_types
        
    # Function for updating dropdowns based on selected media type
    def refresh_dropdowns(self):
        # reset all old dropdowns, delete all options
        self.desired_filetype.set(' ')
        if (self.media_type.get() == "Photo"):
            self.desired_filetype_options = tk.OptionMenu(self.frame, self.desired_filetype, *valid_photo_conversion_types).grid(column=1, row=4, padx=5, pady=10)
        elif (self.media_type.get() == "Video"):
            self.desired_filetype_options = tk.OptionMenu(self.frame, self.desired_filetype, *valid_video_conversion_types).grid(column=1, row=4, padx=5, pady=10)
        else:
            self.desired_filetype_options = tk.OptionMenu(self.frame, self.desired_filetype, *valid_audio_conversion_types).grid(column=1, row=4, padx=5, pady=10)
    
    # Function to reset chosen directories if you switch input type(folder or single image)
    def refresh_directories(self):
        self.input_directory.set("None")
        self.input_file_label.set("No file selected.")

    # Function to check for errors in options menu before conversion
    def validate_options(self):
        options_error = False
        if (self.input_directory.get() == "None"):
            options_error = True
            self.error_label.set("Please choose a input directory.")
        elif (self.output_directory.get() == "None"):
            options_error = True
            self.error_label.set("Please choose a output directory.")
        elif (self.desired_filetype.get() == ' '):
            options_error = True
            self.error_label.set("Please choose a desired filetype.")
        return options_error

    # Function to handle file conversions
    def start_conversion(self):
        # validate options before starting conversion
        if self.validate_options() == False:
            self.error_label.set(" ")
            # create a ffmpeg_logic object to handle conversion
            self.ffmpeg_logic = ffmpeg_logic(self.file_type.get(), self.media_type.get(), self.desired_filetype.get(), self.input_directory.get(), self.output_directory.get())
            # only start if the logic is valid, then switch screen
            if self.ffmpeg_logic.valid == True:
                self.converting = True
                self.frame.grid_forget()
                self.conversion_frame.grid()
                self.conversion_update = self.root.after(1000, self.update_conversion)
            else:
                self.error_label.set("Error has occured with ffmpeg, please retry.")

    # Function called permanently each second, won't do anything    
    def update_conversion(self):
        # only do anything if conversion is actually happening
        if self.converting == True:
            # if theres not a file converting, make one convert
            if self.ffmpeg_logic.get_converting() == False:
                print("starting new file...")
                self.ffmpeg_logic.convert_file()
                self.current_conversion = self.ffmpeg_logic.get_current_file()
            else:
                print("updating!!!")
                self.current_conversion = self.ffmpeg_logic.get_current_file()
                self.current_time = self.ffmpeg_logic.get_current_time()
            # if all files done, update gui and stop changes in loop
            if self.ffmpeg_logic.get_finished() == True:
                print("conversion finished! stopping loop.")
                self.converting = False
                self.current_conversion = "Done!"
                self.starting_label = tk.Label(self.conversion_frame, text="Finished conversion!").grid(column=0, row=0, padx=0, pady=10)
                self.end_button = tk.Button(self.conversion_frame, text="Return to Options", command=self.end_conversion).grid(column=0, row=3)


    

    # used to switch menus on conversion end
    def end_conversion(self):
        self.converting = False
        if self.conversion_update:
            self.root.after_cancel(self.conversion_update)
        self.conversion_frame.grid_forget()
        self.frame.grid()
    
    # Function used to create all of the elements for the converison menu along with attach their functions
    def create_conversion_gui(self):
        # Create labels for current conversion status's
        self.starting_label = tk.Label(self.conversion_frame, text="Doing conversion...").grid(column=0, row=0, padx=0, pady=10)
        self.file_text_label = tk.Label(self.conversion_frame, text="Current File: ").grid(column=0, row=1, padx=0, pady=10)
        self.current_file_label = tk.Label(self.conversion_frame, textvariable=self.current_conversion).grid(column=1, row=1, padx=0, pady=10)
        self.time_text_label = tk.Label(self.conversion_frame, text="Process Time: ").grid(column=0, row=2, padx=0, pady=10)
        self.current_time_label = tk.Label(self.conversion_frame, textvariable=self.current_time).grid(column=1, row=2, padx=0, pady=10)
        # Button to end conversion early if necessary
        self.end_button = tk.Button(self.conversion_frame, text="Stop conversion", command=self.end_conversion).grid(column=0, row=3)


    # Function used to create all elements of the options menu along with attaching their functions
    def create_options_gui(self):
        # create radio buttons for file type
        file_label = tk.Label(self.frame, text="File Type: ").grid(column=0, row=0, padx=0, pady=10)
        folder_radio = tk.Radiobutton(self.frame, text="Folder", variable=self.file_type, command=self.refresh_directories, value="Folder").grid(column=2, row=0, padx=0, pady=10)
        file_radio = tk.Radiobutton(self.frame, text="Single File", variable=self.file_type, command=self.refresh_directories, value="File").grid(column=1, row=0, padx=0, pady=10)

        # create radio buttons for media type
        starting_label = tk.Label(self.frame, text="Media Type: ").grid(column=0, row=1, padx=0, pady=10)
        photo_radio = tk.Radiobutton(self.frame, text="Photo", variable=self.media_type, command=self.refresh_dropdowns, value="Photo").grid(column=1, row=1, padx=0, pady=10)
        video_radio = tk.Radiobutton(self.frame, text="Video", variable=self.media_type, command=self.refresh_dropdowns, value="Video").grid(column=2, row=1, padx=0, pady=10)
        audio_radio = tk.Radiobutton(self.frame, text="Audio", variable=self.media_type, command=self.refresh_dropdowns, value="Audio").grid(column=3, row=1, padx=0, pady=10)

        # create buttons/labels for input and output directories
        input_label = tk.Label(self.frame, text="Choose input files: ").grid(column=0, row=2, padx=5, pady=10)
        input_file = tk.Button(self.frame, text="Open File", command=lambda: self.choose_file("Input")).grid(column=1, row=2)
        input_file_label = tk.Label(self.frame, textvariable=self.input_file_label).grid(column=2, row=2, padx=5, pady=10)#used to show name of input file/folder
        
        output_label = tk.Label(self.frame, text="Choose output directory ").grid(column=0, row=3, padx=5, pady=10)
        output_file = tk.Button(self.frame, text="Open File", command=lambda: self.choose_file("Output")).grid(column=1, row=3)
        output_file_label = tk.Label(self.frame, textvariable=self.output_file_label).grid(column=2, row=3, padx=5, pady=10)#used to show name of the output folder

        # dropdown for desired filetype for conversion, only gives valid types depending on selected media type
        desired_filetype_label = tk.Label(self.frame, text="Choose desired output format").grid(column=0, row=4, padx=5, pady=10)
        self.desired_filetype_options = tk.OptionMenu(self.frame, self.desired_filetype, *valid_photo_conversion_types).grid(column=1, row=4, padx=5, pady=10)
        # button to start the conversion process and error label
        convert_button = tk.Button(self.frame, text="Start Conversion", command=self.start_conversion).grid(column=0, row=5)
        current_error_label = tk.Label(self.frame, textvariable=self.error_label).grid(column=1, row=5, padx=5, pady=10)
        
        

    # function used to start main gui loop
    def start_gui(self):
        # create all gui elements
        self.create_options_gui()
        self.create_conversion_gui()
        # grid main frame
        self.frame.grid()
        #start main loop for tkinter
        self.root.mainloop()
