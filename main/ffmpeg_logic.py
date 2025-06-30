#Author: WeegeeFR
#Date: 6/25/2025
#Description: Class to handle ffmpeg logic used by gui
import os
import subprocess
import re
from pathlib import Path

class ffmpeg_logic:
    # init function, used to make default window and variables
    def __init__(self, file_type, media_type, desired_type, input_string, output_string):
        # needed variables for conversion
        self.converting = False# used to signify if conversion process is done
        self.finished = False
        self.current_file = "None"
        self.current_file_name = "None"
        self.current_time = "00:00:00.00"
        self.file_queue = []# file name in folder
        self.file_type = file_type
        self.media_type = media_type
        self.desired_type = desired_type
        self.valid = self.setup_logic(input_string, output_string) #variable to make sure logic is valid
    
    # function used to validate certain info and fill file queue, will return true if everything happens as expected.
    def setup_logic(self, input_string, output_string):
        valid = True
        print("starting logic setup")
        self.input_directory = input_string
        self.output_directory = output_string
        # check if both directories are valid
        if (Path(self.input_directory).exists() and Path(self.output_directory).is_dir()):
            print("both directories are directories")
            # if file, only append the single file path, otherwise append the whole folder to queue
            if (self.file_type == "File"):
                print("single file we good")
                self.file_queue.append(self.input_directory)
            else:
                 # go through each file and add path to queue
                 for filename in os.listdir(self.input_directory):
                    self.file_queue.append(os.path.join(self.input_directory, filename))
        else:
            valid = False
        return valid
    
    # function used to convert a file in the queue
    def convert_file(self):
        # mark as converting, check and make sure theres a path in the file queue
        self.converting = True
        if len(self.file_queue) > 0:
            self.current_file = self.file_queue.pop()
            command = self.get_current_command()
            # start subprocess
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            # only do this for audio and videos as they're longer conversions
            if (self.media_type != "Photo"):
                self.current_time = "00:00:00.00"
                # this reads the output from ffmpeg and gets current time being encoded
                for line in process.stderr:
                    match = re.search(r"time=(\d{2}:\d{2}:\d{2}\.\d{2})", line)
                    if match:
                        current_time = match.group(1)
        else:
            # if not, signal that there's no more files to be converted
            self.finished = True
        self.converting = False
    
    def get_current_command(self):
        command = []
        # get the base commands for each type of media
        if (self.media_type == "Photo" or self.media_type == "Audio"):
            command = ['ffmpeg', '-i', self.current_file]
            # make the new directory for the converted file for the command
        elif (self.media_type == "Video"):
            command = ['ffmpeg', '-i', self.current_file, '-c:v', 'libx265', '-c:a', 'copy']
        # make the new directory for the converted file for the command
        base_name = os.path.basename(self.current_file)
        file_name = os.path.splitext(base_name)[0]
        self.current_file_name = file_name
        new_output_file = "/" + file_name + self.desired_type
        new_output_directory = self.output_directory + new_output_file
        command.append(new_output_directory)
        return command


    # getters for the gui
    def get_valid(self):
        return self.valid
    def get_finished(self):
        return self.finished
    def get_converting(self):
        return self.converting
    def get_current_file(self):
        return self.current_file
    def get_current_time(self):
        return self.current_time