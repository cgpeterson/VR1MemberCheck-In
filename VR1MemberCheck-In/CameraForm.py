import os
import time
import tkinter as tk

import PIL.Image
import PIL.ImageTk
import cv2
import numpy as np
import imutils

import Processing


class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self, selected=None):
        # offset the capture to one frame before the desired frame before reading
        if selected is not None:
            if selected != 0:
                selected -= 1
            self.vid.set(cv2.CAP_PROP_POS_FRAMES, selected)
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (None, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


class Form:
    def __init__(self, video_source=0):
        self.save_folder = 'data/'

        # capture flag and image
        self.window = None
        self.isAlive = True
        self.frame = None
        self.cur_img = None

        # Load flag
        self.isLoaded = False

        # Create initial window
        self.root = tk.Tk()
        self.root.title('VR1 Member Check-In')

        # Add Icon
        if not (os.path.exists(r'Art/design.ico')):
            fileico = r'Art/design.png'
            ico = PIL.Image.open(fileico)
            ico.save('Art/design.ico', format= 'ICO', sizes=[(32,32)])
        self.root.iconbitmap('Art/design.ico')

        # create opencv object
        self.cv = Processing.ComputerVision()

        # set login info
        self.cv.login()

        # video source (you can change the defined video source here)
        self.video_source = video_source
        self.vid = MyVideoCapture(self.video_source)

        # Create a canvases that can fit the above video source size
        self.canvas = tk.Canvas(self.root, width=400, height=300, bg="#628395")

        # Place widgets
        self.canvas.pack(padx=5, pady=5, side=tk.LEFT)
        
        # Update will be called after every delay
        self.delay = 15
        self.update()

        self.root.resizable(False, False)
        self.root.mainloop()

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if not ret:
            print("No Video Source Retrieved")
            return -1

        # Clean the frame to see just the target size of frame is 400x300pts
        self.frame, mask = self.cv.CleanUp(frame)

        # Find QR code
        data = self.cv.detect(mask)

        # Place the next frame of the video into the window
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.frame))
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        # if image has not been captured yet
        if self.isAlive and self.window is not None:
            # Display image
            self.capture_canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            

        # if data is found freeze image until processing is complete
        if data is not None:
            self.name, self.number, self.age, self.memLength, self.isPaid = self.cv.memberCheck(data)
            cur_member_folder = self.save_folder + self.number
            # minimize the main window
            self.root.iconify()
            if not (os.path.exists(cur_member_folder)) and self.isAlive:
                if self.window is None:
                    # start the profile capture window
                    self.window = tk.Toplevel()
                    self.window.title('VR1 Member Picture')
                    self.window.iconbitmap('art/design.ico')

                    # Create a canvases that can fit the above video source size
                    self.capture_canvas = tk.Canvas(self.window, width=400, height=300)

                    # Create a capture button
                    self.btn_img = PIL.Image.open(r'art/camera.png')
                    resized_img = self.btn_img.resize((32, 32))
                    self.btn_img = PIL.ImageTk.PhotoImage(resized_img)
                    self.capture_btn = tk.Button(self.window, command=self.__stopped, image=self.btn_img)

                    # Place widgets
                    self.capture_canvas.pack(padx=5, pady=5)
                    self.capture_btn.pack(padx=5, pady=5)
            elif not isinstance(self.cur_img, PIL.ImageTk.PhotoImage):
                file_name = cur_member_folder + '/' + self.name + '.png'
                file_name = file_name.replace(' ', '_')
                self.cur_img = PIL.Image.open(file_name)
                self.isLoaded = True
            
        if self.cur_img is not None and not isinstance(self.cur_img, PIL.ImageTk.PhotoImage):
            self.popUp_info(self.name, self.number, self.age, self.memLength, self.isPaid)

        self.root.after(self.delay, self.update)

    def popUp_info(self, _name, _number, _age, _memlength, isPaid):
        # Start the profile info window
        self.profile_window = tk.Toplevel()
        title_string = 'VR1 Member ' + _number + ': ' + _name 
        self.profile_window.title(title_string)
        self.profile_window.iconbitmap('Art/design.ico')

        # Create profile pic canvas
        if not self.isLoaded:
            img = imutils.resize(self.cur_img, width=200)
            self.cur_img = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img))
        else:
            self.cur_img = PIL.ImageTk.PhotoImage(self.cur_img)
        self.profile_img_frame = tk.Frame(self.profile_window, width=205, height=200)
        self.profile_img_canvas = tk.Canvas(self.profile_img_frame, width=200, height=150)

        # Name, Age, Membership Number, and Length of Membership
        self.border_frame = tk.Frame(self.profile_window, bd=4, bg='black')
        self.info_frame = tk.Frame(self.border_frame, bd=0)
        self.first_name, self.last_name = _name.split()
        self.firstn_label = tk.Label(self.info_frame, text='First Name: ', font='Helvetica 10 bold')
        self.firstn = tk.Label(self.info_frame, text=self.first_name, font='Helvetica 8')
        self.lastn_label = tk.Label(self.info_frame, text='Last Name: ', font='Helvetica 10 bold')
        self.lastn = tk.Label(self.info_frame, text=self.last_name, font='Helvetica 8')
        self.age_label = tk.Label(self.info_frame, text='Age: ', font='Helvetica 10 bold')
        self.age = tk.Label(self.info_frame, text=_age, font='Helvetica 8')
        self.memNum_label = tk.Label(self.info_frame, text='Member Number: ', font='Helvetica 10 bold')
        self.memNum = tk.Label(self.info_frame, text=_number, font='Helvetica 8')
        self.memLen_label = tk.Label(self.info_frame, text='Membership Length: ', font='Helvetica 10 bold')
        self.memLen = tk.Label(self.info_frame, text=_memlength, font='Helvetica 8')

        # Payment status label
        if isPaid:
            color = 'green'
            pay_text = 'Paid in Full'
        else:
            color = 'red'
            pay_text = 'Payment Needed'
        self.profile_img_frame['bg'] = color
        self.profile_img_canvas['bg'] = color
        self.payment_label = tk.Label(self.profile_img_frame, bd=4, bg=color, text=pay_text)

        # Place widgets on window
        self.profile_img_frame.pack()
        self.border_frame.pack(padx=5, pady=5)

        # Place label on image and image in frame
        self.profile_img_canvas.pack()
        self.payment_label.pack()

        # Place widgets in info frame
        self.info_frame.pack()
        self.firstn_label.grid(column=0, row=0)
        self.firstn.grid(column=1, row=0)
        self.lastn_label.grid(column=2, row=0)
        self.lastn.grid(column=3, row=0)
        self.age_label.grid(column=4, row=0)
        self.age.grid(column=5, row=0)
        self.memNum_label.grid(column=0, row=1)
        self.memNum.grid(column=1, row=1)
        self.memLen_label.grid(column=2, row=1)
        self.memLen.grid(column=3, row=1)

        # Place image in canvas
        self.profile_img_canvas.create_image(0, 0, image=self.cur_img, anchor=tk.NW)

        # Closing proceedure
        self.profile_window.protocol("WM_DELETE_WINDOW", self.profile_close)

    def profile_close(self):
        # Close the profile id card
        self.profile_window.destroy()
        self.isAlive = True
        # Bring main window back up
        self.root.deiconify()
        # Create a folder for the profile if one doesn't exist
        savefolder_member = self.save_folder + self.number
        if not os.path.isdir('data'):
            os.mkdir('data')
        if not os.path.isdir(savefolder_member):
            os.mkdir(savefolder_member)
        file_name = self.name + ".png"
        new_file_name = file_name.replace(' ', '_')
        new_file_path = os.path.join(savefolder_member, new_file_name)
        imgpil = PIL.ImageTk.getimage(self.cur_img)
        img = imgpil.save( new_file_path, "PNG" )

    def __stopped(self):
        # Set stopped flag
        self.isAlive = False
        # Store image
        self.cur_img = self.frame
        self.window.destroy()
        self.window = None
