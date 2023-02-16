import cv2
import numpy as np 
import math
import pyautogui as p
import time as t
import os
import pickle
import tkinter as tk
from tkinter import filedialog
from tkinter import PhotoImage
from pygame import mixer
import speech_recognition as sr
import pyttsx3
import pyaudio
import time
from time import ctime
import webbrowser
import playsound
import os
import random
from gtts import gTTS
print('wait...')


r = sr.Recognizer()
speaker = pyttsx3.init()
def record_audio(ask = False):
#user voice record
    with sr.Microphone() as source:
        if ask:
            lee_voice(ask)
        audio = r.listen(source)
        voice_data = ''
        try:
            voice_data = r.recognize_google(audio)
            print('Recognizer voice :'+ voice_data)
        except Exception:
            print('Oops something went Wrong')
            lee_voice('Oops something went Wrong Try Again')
        return voice_data
def lee_voice(audio_string):
#Play audio text to voice
    tts = gTTS(text=audio_string, lang='en')
    r = random.randint(1, 10000000)
    audio_file = 'audio-' + str(r) + '.mp3'
    tts.save(audio_file)
    playsound.playsound(audio_file)
    print(audio_string)
    os.remove(audio_file)



#Read Camera


class Player(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        mixer.init()
        

        if os.path.exists('songs.pickle'):
            with open('songs.pickle', 'rb') as f:
                self.playlist = pickle.load(f)
        else:
            self.playlist=[]

        self.current = 0
        self.paused = True
        self.played = False

        self.create_frames()
        self.track_widgets()
        self.control_widgets()
        self.tracklist_widgets()
        self.audio_listener()
        
        
        lee_voice('Welcome to playon')
        

    def create_frames(self):
        self.configure(bg="#006466")
        self.track = tk.LabelFrame(self, text='Song Track',
					font=("gilroy",15,"bold"),
					bg="#144552",fg="white",bd=2,relief=tk.RIDGE)
        self.track.config(width=410,height=300)
        self.track.grid(row=0, column=0, padx=10,pady=20)

        self.tracklist = tk.LabelFrame(self, text=f'PlayList - {str(len(self.playlist))}',
							font=("gilroy",15,"bold"),
							bg="#144552",fg="white",bd=2,relief=tk.RIDGE)
        self.tracklist.config(width=500,height=300)
        self.tracklist.grid(row=0, column=1, rowspan=4, pady=20)

        self.controls = tk.LabelFrame(self,
							font=("gilroy",15,"bold"),
							bg="#144552",fg="white",bd=2,relief=tk.RIDGE)
        self.controls.config(width=410,height=80)
        self.controls.grid(row=1, column=0, padx=10)

        self.audi = tk.LabelFrame(self, text='audio input activity',
									   font=("gilroy", 15, "bold"),
									   bg="#144552", fg="white", bd=2, relief=tk.RIDGE)
        self.audi.config(width=410, height=100)
        self.audi.grid(row=4, column=0,pady=20)
        self.audibtn = tk.LabelFrame(self,
									   font=("gilroy", 15, "bold"),
									   bg="#144552", fg="black", bd=2, relief=tk.RIDGE)
        self.audibtn.config(width=450, height=100)
        self.audibtn.grid(row=4, column=1)

    def gesture(self):
        self.cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        def nothing(x):
            pass
        #window name
        cv2.namedWindow("Color Adjustments",cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Color Adjustments", (300, 300)) 
        cv2.createTrackbar("Thresh", "Color Adjustments", 0, 255, nothing)

        #COlor Detection Track

        cv2.createTrackbar("Lower_H", "Color Adjustments", 0, 255, nothing)
        cv2.createTrackbar("Lower_S", "Color Adjustments", 0, 255, nothing)
        cv2.createTrackbar("Lower_V", "Color Adjustments", 0, 255, nothing)
        cv2.createTrackbar("Upper_H", "Color Adjustments", 255, 255, nothing)
        cv2.createTrackbar("Upper_S", "Color Adjustments", 255, 255, nothing)
        cv2.createTrackbar("Upper_V", "Color Adjustments", 255, 255, nothing)


        while True:
            _,frame = self.cap.read()
            frame = cv2.flip(frame,2)
            frame = cv2.resize(frame,(600,500))
            # Get hand data from the rectangle sub window
            cv2.rectangle(frame, (0,1), (300,500), (255, 0, 0), 0)
            crop_image = frame[1:500, 0:300]
            
            #Step -2
            hsv = cv2.cvtColor(crop_image, cv2.COLOR_BGR2HSV)
            #detecting hand
            l_h = cv2.getTrackbarPos("Lower_H", "Color Adjustments")
            l_s = cv2.getTrackbarPos("Lower_S", "Color Adjustments")
            l_v = cv2.getTrackbarPos("Lower_V", "Color Adjustments")

            u_h = cv2.getTrackbarPos("Upper_H", "Color Adjustments")
            u_s = cv2.getTrackbarPos("Upper_S", "Color Adjustments")
            u_v = cv2.getTrackbarPos("Upper_V", "Color Adjustments")
            #Step -3
            lower_bound = np.array([l_h, l_s, l_v])
            upper_bound = np.array([u_h, u_s, u_v])
            
            #Step - 4
            #Creating Mask
            mask = cv2.inRange(hsv, lower_bound, upper_bound)
            #filter mask with image
            filtr = cv2.bitwise_and(crop_image, crop_image, mask=mask)
            
            #Step - 5
            mask1  = cv2.bitwise_not(mask)
            m_g = cv2.getTrackbarPos("Thresh", "Color Adjustments") #getting track bar value
            ret,thresh = cv2.threshold(mask1,m_g,255,cv2.THRESH_BINARY)
            dilata = cv2.dilate(thresh,(3,3),iterations = 6)
            
            #Step -6
            #findcontour(img,contour_retrival_mode,method)
            cnts,hier = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            
            
            try:
                #print("try")
                 #Step -7
                 # Find contour with maximum area
                cm = max(cnts, key=lambda x: cv2.contourArea(x))
                #print("C==",cnts)
                epsilon = 0.0005*cv2.arcLength(cm,True)
                data= cv2.approxPolyDP(cm,epsilon,True)
            
                hull = cv2.convexHull(cm)
                
                cv2.drawContours(crop_image, [cm], -1, (50, 50, 150), 2)
                cv2.drawContours(crop_image, [hull], -1, (0, 255, 0), 2)
                
                #Step - 8
                # Find convexity defects
                hull = cv2.convexHull(cm, returnPoints=False)
                defects = cv2.convexityDefects(cm, hull)
                count_defects = 0
                #print("Area==",cv2.contourArea(hull) - cv2.contourArea(cm))
                for i in range(defects.shape[0]):
                    s,e,f,d = defects[i,0]
                   
                    start = tuple(cm[s][0])
                    end = tuple(cm[e][0])
                    far = tuple(cm[f][0])
                    #Cosin Rule
                    a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                    b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                    c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                    angle = (math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 180) / 3.14
                    #print(angle)
                    # if angle <= 50 draw a circle at the far point
                    if angle <= 50:
                        count_defects += 1
                        cv2.circle(crop_image,far,5,[255,255,255],-1)
                
                print("count==",count_defects)
                
                #Step - 9 
                # Print number of fingers
                if count_defects == 0:
                    
                    cv2.putText(frame, " nothing", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255),2)
                elif count_defects == 1:
                    
                    self.pause_song()
                    cv2.putText(frame, "Play/Pause", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255), 2)
                elif count_defects == 2:
                    self.next_song()
                    
                    cv2.putText(frame, "NEXT", (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255), 2)
                elif count_defects == 3:
                    self.prev_song()
                    
                    cv2.putText(frame, "PREVIOUS", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255), 2)
                elif count_defects == 4:
                    cv2.putText(frame, "END TASK", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,(0,0,255), 2)
                    break
                else:
                    print('nothing')
                    pass
                   
            except:
                pass
            #step -10    
            cv2.imshow("Thresh", thresh)
            #cv2.imshow("mask==",mask)
            cv2.imshow("filter==",filtr)
            cv2.imshow("Result", frame)

            key = cv2.waitKey(25) &0xFF    
            if key == 27: 
                break
        self.cap.release()
        cv2.destroyAllWindows()
        
    def clicked(self):
        print("working...")
        
        self.songlistn = tk.Label(self.audi, font=("gilroy", 8),
                                      bg="white", fg="dark blue")
        self.songlistn['text'] = 'listening....'
        self.songlistn.config(width=60, height=6)
        self.songlistn.grid(row=1, column=1, padx=10)
        voice_data = record_audio()
        voice_data = voice_data.lower()
        if 'previous' in voice_data:
            lee_voice('Playing previous song')
            self.songlistn['text'] = 'Playing previous song'
            print(voice_data)
            self.prev_song()

        elif 'next' in voice_data:
            lee_voice('Playing next song')
            self.songlistn['text'] = 'Playing next song'
            print(voice_data)
            self.next_song()

        elif 'pause' in voice_data:
            lee_voice('pausing song')
            self.songlistn['text'] = 'pausing song'
            print(voice_data)
            self.pause_song()

        elif 'resume' in voice_data:
            lee_voice('continuing song')
            self.songlistn['text'] = 'continue song'
            print(voice_data)
            self.pause_song()

        #elif 'volume' in voice_data:
         #   print('vol')
          #  self.change_volume()
            
        elif 'play' in voice_data:
            s=voice_data.replace('play ','')
            lee_voice('Playing '+s)
            s=s.lower()
            self.songlistn['text'] = 'Playing '+s
            for i in range (len(self.playlist)):
                find=self.playlist[i].split('/')[5].lower()
                print(find)
                print(s)
                if s in find :
                    self.current=i
                    print(self.current)
                    break
            print(self.current)
            mixer.music.load(self.playlist[self.current])
            self.songtrack['anchor'] = 'w'
            self.songtrack['text'] = os.path.basename(self.playlist[self.current])

            self.pause['image'] = play
            self.paused = False
            self.played = True
            self.list.activate(self.current)
            self.list.itemconfigure(self.current, bg='sky blue')

            mixer.music.play()
            
            
            
             #self.s=self.voice_data.replace('play','')
             
             #songlistn['text'] = self.voice_data
        elif 'exit' in voice_data:
            lee_voice('Thanks have a good day ')
            end()
            
        else:
            lee_voice('unable to here say again')
            self.songlistn['text'] ='unable to here say again'
            self.clicked()

    def track_widgets(self):
        self.canvas = tk.Label(self.track, image=img)
        self.canvas.configure(width=400, height=240)
        self.canvas.grid(row=0,column=0,pady=10)

        self.songtrack = tk.Label(self.track, font=("gilroy",16,"bold"),
						bg="white",fg="#4D194D")
        self.songtrack['text'] = 'Just Play It On MP3 Player'
        self.songtrack.config(width=30, height=1)
        self.songtrack.grid(row=1,column=0,padx=10,pady=10)

    def control_widgets(self):
        self.loadSongs = tk.Button(self.controls, bg='#272640', fg='white', font=10)
        self.loadSongs['text'] = 'Load Songs'
        self.loadSongs['command'] = self.retrieve_songs
        self.loadSongs.grid(row=0, column=0, padx=10)

        self.prev = tk.Button(self.controls, image=prev)
        self.prev['command'] = self.prev_song
        self.prev.grid(row=0, column=1)

        self.pause = tk.Button(self.controls, image=pause)
        self.pause['command'] = self.pause_song
        self.pause.grid(row=0, column=2)

        self.next = tk.Button(self.controls, image=next_)
        self.next['command'] = self.next_song
        self.next.grid(row=0, column=3)

        self.volume = tk.DoubleVar(self)
        self.slider = tk.Scale(self.controls, from_ = 0, to = 10, orient = tk.HORIZONTAL)
        self.slider['variable'] = self.volume
        self.slider.set(8)
        mixer.music.set_volume(0.8)
        self.slider['command'] = self.change_volume
        self.slider.grid(row=0, column=4, padx=5)


    def tracklist_widgets(self):
        self.scrollbar = tk.Scrollbar(self.tracklist, orient=tk.VERTICAL)
        self.scrollbar.grid(row=0,column=1, rowspan=5, sticky='ns', padx=(0,10), pady=10)

        self.list = tk.Listbox(self.tracklist, selectmode=tk.SINGLE,
                     yscrollcommand=self.scrollbar.set, selectbackground='#4D194D')
        self.enumerate_songs()
        self.list.config(height=23, width=30)
        self.list.bind('<Double-1>', self.play_song)

        self.scrollbar.config(command=self.list.yview)
        self.list.grid(row=0, column=0, rowspan=5, padx=(10,0), pady=10)

    def audio_listener(self):
        self.btn = tk.Button(self.audibtn, text='Speak', font=('gilroy', 15, 'bold'),
        bg='#272640', fg='white', command=self.clicked)
        #self.btn.config(width=5,height=5)
        self.btn.grid(row=4, column=0,padx=12,pady=14)
        self.btn2 = tk.Button(self.audibtn, text='Gesture control', font=('gilroy', 15,
        'bold'), bg='#272640', fg='white', command=self.gesture).grid(row=5, column=0,padx=5,pady=2)
        #, rowspan=3, pady=5)


    def retrieve_songs(self):
        self.songlist = []
        directory = filedialog.askdirectory()
        for root_, dirs, files in os.walk(directory):
                for file in files:
                    if os.path.splitext(file)[1] == '.mp3':
                        path = (root_ + '/' + file).replace('\\','/')
                        self.songlist.append(path)

        with open('songs.pickle', 'wb') as f:
            pickle.dump(self.songlist, f)
        self.playlist = self.songlist
        self.tracklist['text'] = f'PlayList - {str(len(self.playlist))}'
        self.list.delete(0, tk.END)
        self.enumerate_songs()

    def enumerate_songs(self):
        for index, song in enumerate(self.playlist):
            self.list.insert(index, os.path.basename(song))


    def play_song(self, event=None):
        if event is not None:
            self.current = self.list.curselection()[0]
            for i in range(len(self.playlist)):
                self.list.itemconfigure(i, bg="white")

        print(self.playlist[self.current])
        mixer.music.load(self.playlist[self.current])
        self.songtrack['anchor'] = 'w'
        self.songtrack['text'] = os.path.basename(self.playlist[self.current])

        self.pause['image'] = play
        self.paused = False
        self.played = True
        self.list.activate(self.current)
        self.list.itemconfigure(self.current, bg='sky blue')

        mixer.music.play()

    def pause_song(self):
        if not self.paused:
            self.paused = True
            mixer.music.pause()
            self.pause['image'] = pause
        else:
            if self.played == False:
                self.play_song()
            self.paused = False
            mixer.music.unpause()
            self.pause['image'] = play

    def prev_song(self):
        if self.current > 0:
            self.current -= 1
        else:
            self.current = 0
        self.list.itemconfigure(self.current + 1, bg='white')
        self.play_song()

    def next_song(self):
        if self.current < len(self.playlist) - 1:
            self.current += 1
        else:
            self.current = 0
        self.list.itemconfigure(self.current - 1, bg='white')
        self.play_song()

    def change_volume(self, event=None):
        self.v = self.volume.get()
        mixer.music.set_volume(self.v / 10)

# ----------------------------- Main -------------------------------------------

root = tk.Tk()
width= 700#root.winfo_screenwidth()
height = 600#root.winfo_screenheight()

root.geometry('%dx%d'%(width,height))
root.configure(bg="#006466")
# root.attributes('-fullscreen',True)
root.wm_title('PlayOn')

img = PhotoImage(file='images/Music8.gif')
next_ = PhotoImage(file = 'images/next.png')
prev = PhotoImage(file='images/prev.png')
play = PhotoImage(file='images/ply.png')
pause = PhotoImage(file='images/pause.png')
icon=PhotoImage(file="images/icon.png")
root.iconphoto(False,icon)


app = Player(master=root)
app.mainloop()
time.sleep(1)

speaker.runAndWait()
# ----------------------------- End -------------------------------------------


