#Author: WeegeeFR
#Date: 6/25/2025
#Description: Class to handle ffmpeg logic used by gui
class ffmpeg_logic:
    # init function, used to make default window and variables
    def __init__(self, input_directory, output_directory, media_type, desired_type):
        # needed variables for conversion
        self.converting = True# used to signify if conversion process is done
        self.current_file = None

        self.input_directory = input_directory
        self.output_directory = output_directory
        self.media_type = media_type
        self.desired_type = desired_type

    # function used to validate certain info such as directories before converting
    def validate(self):
        print("Yippee")
    # function used to convert a single file
    def convert_single_file(self):
        print("Yippee")
    # function used to convert a folder of files
    def convert_folder(self):
        print("yippee")