#Author: WeegeeFR
#Date: 6/25/2025
#Description: Class to handle ffmpeg logic used by gui
import os
import ffmpeg
import threading
import sys
import subprocess
from pathlib import Path

# need this for folder checks
valid_photo_conversion_types = [".png", "jpg", ".jpeg", ".webp" ".bmp", ".apng", ".ico"]
valid_audio_conversion_types = [".mp3", ".wav", ".m4a", ".aac", ".wma", ".alac", ".flac", ".ogg"]
valid_video_conversion_types = [".mp4", ".wmv", ".mov", ".mkv", ".m4v",".hevc"]

class ffmpeg_logic:
    # init function, used to make default window and variables
    def __init__(self, file_type, media_type, desired_type, input_string, output_string, gui_callback):
        # needed variables for conversion
        self.converting = False# used to signify if conversion process is done
        self.finished = False
        self.current_file = None
        self.current_file_name = None
        self.current_time = "00:00:00.00"
        self.total_duration = None
        self.current_progress = "0%"
        self.output_directory = None
        self.current_output_directory = None
        self.file_queue = []# file name in folder
        self.file_type = file_type
        self.media_type = media_type
        self.desired_type = desired_type
        self.valid = self.setup_logic(input_string, output_string) #variable to make sure logic is valid
        self.gui_callback = gui_callback # used to notify gui of info
        self.process = None  # to store the current FFmpeg process
        self.cancel_flag = threading.Event()  # to flag the cancellation request
    
    # function used to validate file extension of a file
    def validate_file(self, extension):
        if self.media_type == "Photo":
            return (extension in valid_photo_conversion_types)
        elif self.media_type == "Audio":
            return (extension in valid_audio_conversion_types)
        else:
            return (extension in valid_video_conversion_types)
    
    # function used to get the best vcodec, defaults to copy
    def get_vcodec(self):
        codec = 'copy'
        if self.desired_type == ".mp4" or self.desired_type == ".mkv" or self.desired_type == ".hevc" or self.desired_type == ".m4v":
            codec = 'libx265'
        elif self.desired_type == ".wmv":
            codec = 'wmv2'
        elif self.desired_type == ".webm":
            codec = 'vp8'
        elif self.desired_type == ".mov":
            codec = 'prores'
        return codec

    # function used to get the best acodec, defaults to copy
    def get_acodec(self):
        codec = 'copy'
        if self.desired_type == ".mp4" or self.desired_type == ".mkv" or self.desired_type == ".hevc" or self.desired_type == ".m4v":
            codec = 'aac'
        elif self.desired_type == ".wmv":
            codec = 'wmav2'
        elif self.desired_type == ".webm":
            codec = 'opus'
        elif self.desired_type == ".mov":
            codec = 'pcm_s16le'
        return codec
    
    # function used to get current seconds from a time string
    def get_current_seconds(self, time_string):
        time_parts = time_string.split(":")
        total_seconds = None
        try:
            if len(time_parts) == 3:  # hh:mm:ss.xx format
                hours = int(time_parts[0])
                minutes = int(time_parts[1])
                seconds = float(time_parts[2])
                total_seconds = (hours * 3600) + (minutes * 60) + seconds
            elif len(time_parts) == 2:  # mm:ss.xx format
                minutes = int(time_parts[0])
                seconds = float(time_parts[1])
                total_seconds = (minutes * 60) + seconds
            elif len(time_parts) == 1:  # ss.xx format
                total_seconds = float(time_parts[0])
        except ValueError:
            # handle cases where the conversion to int or float fails
            return None
        return total_seconds
    
    # function used to update current progress variable
    def update_progress(self, time_string):
        if not self.total_duration == None:
            current_seconds = self.get_current_seconds(time_string)
            if not current_seconds == None:
                current_percentage = round((current_seconds / self.total_duration) * 100, 1)
                self.current_progress = str(current_percentage) + "%"
    
    def set_total_duration(self):
        try:
            # try to probe the video file
            probe = ffmpeg.probe(self.current_file, v='error', select_streams='v:0', show_entries='stream=duration')
            # get duration from the probe data
            self.total_duration = float(probe['streams'][0]['duration'])  
        except ffmpeg.Error as e:
            self.total_duration = None
            self.current_progress = "Invalid duration"
        
    
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
                 # go through each file in path and add path to queue if valid file type
                 for filename in os.listdir(self.input_directory):
                    current_file = os.path.join(self.input_directory, filename)
                    extension = os.path.splitext(current_file)[1].lower()
                    # check current file for valid file type
                    if self.validate_file(extension):
                        self.file_queue.append(current_file)
        else:
            valid = False
        return valid
    
    # function used to convert a file in the queue
    def convert_file(self):
        # mark as converting, check and make sure theres a path in the file queue
        print("Starting conversion...")
        self.converting = True
        if len(self.file_queue) > 0:
            self.current_file = self.file_queue.pop()
            self.cancel_flag.clear()
            process = self.run_process() # start and handle process of conversion
        else:
            # if not, signal that there's no more files to be converted
            self.finished = True
            self.gui_callback("Complete", None)
    
    # function used to start halting all of the ffmpeg processes
    def cancel_conversion(self):
        if self.process:
            print("terming process...")
            try:
                print("waiting for termination...")
                self.process.terminate()  # gracefully terminate the process
                self.process.wait(timeout=5)
                print("Process terminated...")
            except subprocess.TimeoutExpired:
                # process didn't terminate in time, force kill it
                print("Termination didn't work, force killing process...")
                try:
                    self.process.kill()
                    self.process.wait()
                    print("process killed.")
                except Exception as e:
                    print(f"Error during kill: {e}")
            self.cancel_flag.set()
            # kill any lingering ffmpeg processes
            subprocess.run(["taskkill", "/f", "/im", "ffmpeg.exe"], shell=True)
            # remove the new file after process ends
            if os.path.exists(self.current_output_directory):
                try:
                    os.remove(self.current_output_directory)
                except Exception as e:
                    print(f"Failed to delete output file: {e}")
    
    # function used to start a new process for the file conversion
    def run_process(self):
        # make the new directory for the converted file for the command
        base_name = os.path.basename(self.current_file)
        file_name, _ = os.path.splitext(base_name)
        self.current_file_name = file_name
        new_output_file = file_name + self.desired_type
        self.current_output_directory = os.path.join(self.output_directory, new_output_file)
        cmd = None
        # make command to start process based on media type, compile it
        if (self.media_type == "Photo"):
            # for photo just convert 
            cmd = ffmpeg.input(self.current_file).output(self.current_output_directory).global_args('-progress', 'pipe:1').compile()
        elif (self.media_type == "Audio"):
            # for audio, track progress, but no custom settings
            self.set_total_duration()
            cmd = ffmpeg.input(self.current_file).output(self.current_output_directory).global_args('-progress', 'pipe:1').compile()
        else:
            # get best vcodec and acodec for ffmpeg to use before starting process for this
            current_vcodec = self.get_vcodec()
            current_acodec = self.get_acodec()
            self.set_total_duration()
            cmd = ffmpeg.input(self.current_file).output(self.current_output_directory, vcodec=current_vcodec, acodec=current_acodec).global_args('-progress', 'pipe:1').compile()

        # use this to start the process, using popen to hide command line windows from staying up
        if sys.platform == "win32":
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW  # flag to hide window on windows
            )
        else:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        # two variables to be used to signify when both are done
        stdout_done = threading.Event()
        stderr_done = threading.Event()
        # Capture output and callback to gui to update it
        def capture_output():
            while True:
                if self.cancel_flag.is_set():  # if the cancel flag is set, stop capturing
                    break
                output = self.process.stdout.readline()
                if output == b'' and self.process.poll() is not None:
                    break
                if output:
                    progress_info = output.decode('utf-8')
                    if "time=" in progress_info:
                        time_str = progress_info.split("time=")[1].split(" ")[0]
                        self.current_time = time_str
                        self.update_progress(time_str)
                        self.gui_callback("Update", [self.current_file_name, self.current_time, self.current_progress])
                
            stdout_done.set()
        # Capture errors
        def capture_error():
            while True:
                if self.cancel_flag.is_set():  # if the cancel flag is set, stop capturing
                    break
                error_output = self.process.stderr.readline()
                if error_output == b'' and self.process.poll() is not None:
                    break
            stderr_done.set()

        # start threads for both outputs, daemon so they terminate on completion
        threading.Thread(target=capture_output, daemon=True).start()
        threading.Thread(target=capture_error, daemon=True).start()

        # wait for said threads to be done, then callback that current conversion is finished
        def wait_for_completion():
            stdout_done.wait()
            stderr_done.wait()
            self.converting = False
            print("finished current conversion")
            self.gui_callback("Finished", None)

        # start a thread to wait for both threads to finish
        threading.Thread(target=wait_for_completion, daemon=True).start()