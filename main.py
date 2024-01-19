# Project:  MusicDownloader&Burner
# Author:   Carlos Rodriguez
# Date:     December 26, 2023
# Purpose:  Download a song and burn it to a cd
import datetime
import os
import re
import subprocess
import tkinter.messagebox
import urllib.request
import customtkinter
from tkinter import filedialog
from anyascii import anyascii
from pytube import YouTube

# Set the path to the directory containing ffprobe.exe (change this to your ffprobe path)
# os.environ["PATH"] += os.pathsep + r"\ffmpeg-6.1.1\bin"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x500")
        self.title("Liz's Music Burner")
        self.configure(fg_color='pink')
        self.number_of_songs = 0
        self.pb_value = 0
        self.titlevid = ""
        custom_font = ("Comic Sans MS", 14, "bold")

        # CTkButton for search
        self.search_btn = customtkinter.CTkButton(self, command=self.search_song, fg_color='yellow', text_color='black', border_color='black', border_width=1, text='Search')
        self.search_btn.place(x=270, y=310)

        # CTkButton for burning
        self.burn_btn = customtkinter.CTkButton(self, command=self.burn_music_to_cd, fg_color='yellow', text_color='black', border_color='black', border_width=1, text='Burn')
        self.burn_btn.place(x=270, y=350)

        # CTkButton for browsing music folder
        self.music_folder_btn = customtkinter.CTkButton(self, command=self.music_folder, fg_color='yellow', text_color='black', border_color='black', border_width=1, text='Music')
        self.music_folder_btn.place(x=430, y=310)

        # CTkButton for Erasing disc
        self.playlists_btn = customtkinter.CTkButton(self, command=self.erase_disc, fg_color='yellow', text_color='black', border_color='black', border_width=1, text='Erase')
        self.playlists_btn.place(x=430, y=350)

        # CTkButton for Deleting all song selected
        self.delete_song_btn = customtkinter.CTkButton(self, command=self.delete_all_songs, fg_color='yellow', text_color='black', border_color='black', border_width=1, text='Delete All')
        self.delete_song_btn.place(x=50, y=310)

        # CTkButton for Help
        self.help_btn = customtkinter.CTkButton(self, command=self.help_message, fg_color='yellow', text_color='black', border_color='black', border_width=1, text='Help')
        self.help_btn.place(x=430, y=20)

        # CTkLabel keep track of mb's
        self.size_lbl = customtkinter.CTkLabel(self, width=30, height=20, bg_color='black', text_color='pink', text='0 MB/700 MB')
        self.size_lbl.place(x=110, y=420)

        # CTkEntry for searchable item
        self.song_name = customtkinter.CTkEntry(self, border_width=1, border_color='black', placeholder_text='Enter Song Name Here', width=300)
        self.song_name.place(x=20, y=20)

        #CTkTextbox
        self.songs_txb = customtkinter.CTkTextbox(self, width=560, font=custom_font, border_color='black', border_width=2, fg_color='pink', text_color='black', wrap='none', scrollbar_button_color='black', scrollbar_button_hover_color='yellow')
        self.songs_txb.place(x=20, y=80)
        self.get_songs()

        # CTkProgressBar show how much data is available on disc ** based on music folder **
        self.burn_pb = customtkinter.CTkProgressBar(self, determinate_speed=float(1), progress_color='pink', fg_color='black', mode='determinate', border_width=2, border_color='black', width=200)
        self.burn_pb.place(x=50, y=400)
        self.burn_pb.set(0)
        #print(self.get_connected_drives_os())

        # update label & progress bar
        if self.get_folder_size():
            self.search_btn.configure(state='disabled')
            self.burn_btn.configure(state='disabled')

    def search_song(self):
        name_song = self.song_name.get()  # Grabs song name from CTkEntry
        name_song_list = []

        if name_song.find(',') != -1:
            while name_song.find(',') != -1:
                name_song_list.append(name_song[:name_song.find(',')])
                name_song = name_song[name_song.find(',')+1:]
            name_song_list.append(name_song)
        else:
            name_song_list.append(name_song)

        for x in name_song_list:
            try:
                # update progress bar self.burn_pb.set(float(1/len(name_song_list)))
                search_query = "https://www.youtube.com/results?search_query={}".format(x.replace(" ", "+").replace("&", "and"))        # used to search the song on YouTube
                html = urllib.request.urlopen(anyascii(search_query))                           # get request
                response = html.read()                                                          # response text
                video_ids = re.findall(r"watch\?v=(\S{11})", str(response))                     # find all occurrences of text watch\?v= response save as the video id's
                watch_link = "https://www.youtube.com/watch?v=" + video_ids[1]                  # attach video id to link to get complete video url
                #vid = pytube.YouTube(watch_link)                                                # using pytube set vid to YouTube video with desired url
                #song_title = vid.title                                                          # grab video title with .title function
                self.download_music(watch_link)                                                 # call download funtion with link to video as an arg followed by the title of song
                if self.get_folder_size():                                                      # update label and progress bar
                    self.search_btn.configure(state='disabled')
                    self.burn_btn.configure(state='disabled')
                    self.custom_msg('STORAGE FULL OR OVER', 'PLEASE REMOVE A SONG FROM THE MUSIC DIRECTORY')
            except Exception as e:
                tkinter.messagebox.showwarning("Search Error!", str(e))
        name_song_list.clear()

    def download_music(self, watch_link):
        try:
            yt = YouTube(str(watch_link))  # url input from user
            try:
                # get the audio stream
                audio = yt.streams.filter(only_audio=True, abr='160kbps').first()           # get stream
                # download the audio stream to a file
                self.titlevid = yt.title.replace("|", "").replace("\"", "").replace("/", "").replace(":", "").replace("*", "").replace("?", "").replace("<", "").replace(">", "")
                # Get rid of unicode
                self.titlevid = ''.join([i if ord(i) < 128 else '-' for i in self.titlevid])
                # download the song
                audio_file = audio.download(output_path='music\\', filename=self.titlevid+'.webm')          # WebM  download
                self.get_songs()

                try:
                    subprocess.run(['ffmpeg',
                                    '-i', audio_file,
                                    '-c:a', 'pcm_s16le',
                                    '-ar', '44100',
                                    '-f', 'wav',
                                    os.getcwd() + '/music/'+self.titlevid+'.wav'])
                    print("Conversion successful!")
                    os.remove(os.getcwd() + '/music/' + self.titlevid+'.webm')
                except Exception as e:
                    print(f"Conversion failed: {e}")

            except Exception as e:
                self.custom_msg(f"{yt.title} failed to download", str(e))

        except Exception as e:
            self.custom_msg("Download Error!", str(e))

    def format_seconds_to_time(self, seconds):
        # Convert seconds to timedelta
        time_delta = datetime.timedelta(seconds=seconds)
        # Calculate milliseconds from the fractional part of seconds
        milliseconds = int(time_delta.microseconds / 1000)  # Extract milliseconds from timedelta
        # Convert timedelta to a datetime object
        time_obj = datetime.datetime(1, 1, 1) + time_delta
        # Format the datetime object as hours:minutes:seconds:milliseconds
        formatted_time = time_obj.strftime('%M:%S') + f':{milliseconds:02d}'
        return formatted_time

    def burn_music_to_cd(self):
        list_songs = os.listdir('music\\')
        try:
            files_to_burn = os.getcwd() + '\\music\\*.wav'                  # Replace with your ISO file path
            cdrtools_path = "cdrtools/cdrecord.exe"      # Update this with your ImgBurn installation path
            device_name = "0,0,0"                                           # cd write device id

            index = 0
            # Create a cue file however it  doesn't currently use the custom titles
            for songs in list_songs:
                # get length of tracks
                args = ("ffprobe", "-show_entries", "format=duration", "-i", f"music/{songs}")
                popen = subprocess.Popen(args, stdout=subprocess.PIPE)
                popen.wait()
                output = popen.stdout.read().decode()
                output = output[output.find('=') + 1:output.find('[/FORMAT]')]
                length = self.format_seconds_to_time(int(float(output)))
                file_name = f'{songs}'  # Replace this with your audio file name
                tracks = [songs, 'Artist', length]
                self.create_cue_file(file_name, tracks, index, file_name[:-4])
                index += 1

            # Create the command to burn audio files to a blank CD
            # Command to burn data to a disc
            burn_command = [
                cdrtools_path,
                f"dev={device_name}",
                "-v",  # Command for writing data
                "-dao",
                "-pad",
                "cuefile=music/output.cue"
                #"-audio", "music/*.wav"
            ]

            try:
                subprocess.run(burn_command, check=True)
                self.custom_msg("SUCCESS!", 'Burning process finished!')
                os.remove("music/output.cue")
            except subprocess.CalledProcessError as e:
                self.custom_msg("ERROR!", e)
                os.remove("music/output.cue")

        except Exception as e:
            self.custom_msg("ERROR!", str(e))
            os.remove("music/output.cue")

    def create_cue_file(self, file_name, track_list, index, TITLE):
        cue_content = f'''\
FILE "{file_name}" WAVE
REM FILE-DECODED-SIZE {track_list[2]}
  TRACK 0{index+1} AUDIO
    TITLE {TITLE.replace(" ", "")}
    INDEX 01 00:00:00\n\n'''

        with open('music/output.cue', 'a') as cue_file:
            cue_file.write(cue_content)

    def update_progress_bar(self):
        for x in range(self.number_of_songs):
            self.pb_value += 1 / self.number_of_songs

    def get_songs(self):
        self.songs_txb.configure(state="normal")
        self.songs_txb.delete('0.0', 'end')
        self.number_of_songs = 0

        # ensure the music directory is available
        try:
            dir_list = os.listdir()
            if 'music' not in dir_list:
                os.mkdir('music')
        except FileExistsError as e:
            self.custom_msg("ERROR!", str(e))

        # List all items in the directory
        all_items = os.listdir('music\\')

        # Print all items (files and directories)
        for item in all_items:
            self.number_of_songs += 1
            self.songs_txb.insert(index='0.0', text=item+'\n')

        self.songs_txb.configure(state="disabled")

    def music_folder(self):
        try:
            file_path = filedialog.askopenfilename(initialdir='music/')  # Show the file dialog and return the selected file's path
            print(file_path)
            if file_path or file_path == '':
                if not self.get_folder_size():
                    self.search_btn.configure(state='normal')
                    self.burn_btn.configure(state='normal')
        except Exception as e:
            self.custom_msg("ERROR!", str(e))

    def delete_all_songs(self):
        try:
            if tkinter.messagebox.askyesno(title='DELETE MUSIC', message='You are about to delete all songs in music folder!'):
                for item in os.listdir('music/'):
                    item_path = os.path.join('music/', item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                self.get_songs()
        except Exception as e:
            self.custom_msg("ERROR!", f"Error: {e}")

    def erase_disc(self):
        cdrtools_path = "cdrtools/cdrecord.exe"  # Update this with your ImgBurn installation path
        device_name = "0,0,0"                                       # writer device ID

        # Create the command to erase files from a CD
        erase_command = [
            cdrtools_path,
            f"dev={device_name}",
            "-v",  # Command for writing data
            "blank=fast"]

        try:
            subprocess.run(erase_command, check=True)
            self.custom_msg("SUCCESS!", "Erasing process completed successfully!")
        except subprocess.CalledProcessError as e:
            self.custom_msg("FAILED TO ERASE!", f"Error: {e}")

    def custom_msg(self, title, msg):
        tkinter.messagebox.showinfo(title=title, message=msg)

    def get_folder_size(self):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk('music'):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)

        # Convert bytes to a human-readable format (optional)
        def convert_bytes(byte_size):
            size_units = ['B', 'KB', 'MB', 'GB', 'TB']
            index = 0
            while byte_size >= 1024 and index < len(size_units) - 1:
                byte_size /= 1024.0
                index += 1
            return f"{byte_size:.2f} {size_units[index]}"
        size_in_human_readable = convert_bytes(total_size)
        # update the label
        self.size_lbl.configure(text=f'{size_in_human_readable} / 700 MB')
        # update progress bar
        self.burn_pb.set(value=float(float(total_size)/700100000))
        if float(float(total_size)/700100000) > 1:
            return True
        else:
            return False

    def help_message(self):
        self.custom_msg('Help options', "BUTTONS    -   DESCRIPTION\n"
                        "-------------------------------------------------------\n"
                        "| Search\t\t| Download new song\n"
                        "| Burn\t\t| Create the cd disc\n"
                        "| Music\t\t| Open music folder\n"
                        "| Erase\t\t| Clear disc data (RW)\n"
                        "| Delete All\t| Delete all songs\n")

app = App()
app.mainloop()
