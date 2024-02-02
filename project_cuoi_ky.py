import tkinter
import tkinter as tk
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import PhotoImage
import subprocess
import cv2
from PIL import ImageTk, Image

# Tạo 1 hàm để chạy chương trình chính
def openFile():
    subprocess.Popen(["python", "main1.py"])

# Tạo cửa sổ giao diệnq
root  = tk.Tk()
root.title("Crowd Behaviour Analysis")
# kích thước giao diện
root.geometry("1050x600") 
# Với topmost, widget luôn đứng trước mọi cửa sổ khác, do đó để false để giao diện luôn đứng sau các của sổ khác
root.attributes("-topmost", False)
root["bg"] = "white" # nền của giao diện
# import ảnh, dùng PIL, sau đó đặt ảnh đó làm background
back = PhotoImage(file = 'logo1.png')
anh = Label(root, image = back)
anh.place(x = 0, y = 0)

#Tạo frame 1 với layout pack
frame1 = tk.Frame(master = root, bg = 'white')
frame1.pack(padx = 10, pady = (95, 5), fill = 'both', expand = False)

# Tạo các label và vị trí hiển thị trên frame1
lbl1 = tkinter.Label(master = frame1, text = 'MACHINE VISION',
                       font = ('Segoe UI', 16, 'bold'), bg = 'white', fg = 'black')
lbl1.pack(padx = 30, pady = (20, 5))
lbl2 = tkinter.Label(master = frame1, text = 'TOPIC',
                       font = ('Segoe UI', 12, 'bold'), bg = 'white', fg = 'black')
lbl2.pack(padx = 30, pady = (0, 5))
lbl3 = tkinter.Label(master = frame1, text = 'CROWD ANALYSIS AND DETERMINE ACTIONS OF THE OBJECTS',
                       font = ('Segoe UI', 22, 'bold'), bg = 'white', fg = 'black')
lbl3.pack(padx = 30, pady = (0, 5))

# Tạo nút mở file và chạy code dùng hàm ...
btn1 = tkinter.Button(master = frame1, text = 'START', command = openFile, font = ('Helvetica', 14, 'bold'), 
                      fg = 'black', bg = 'white', highlightthickness = 2, height = 1, width = 10)
btn1.pack(padx = 50, pady = 20)

# Tạo frame 2 với layout grid, chia thành các dòng, các cột 
frame2 = tk.Frame(master = root, bg = 'white')
frame2.pack(padx = 10, pady = (0, 20), fill = 'both', expand = True)

# Tạo menu grid layout ở frame 2
frame2.columnconfigure((0, 1, 2, 3,4, 5), weight = 1) # weight: độ dày của đường kẻ chia frame thành các ô
frame2.rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9), weight = 1)

# Tạo các label và hiển thị ở frame 2, các dòng này được cho dồn ở phía trái cột 2
lbl4 = tkinter.Label(master = frame2, text = 'Lecturer: Mr. Nguyen Van Thai', 
                      font = ('Helvetica', 12), bg = 'white', fg = 'black')
lbl4.grid(row = 1, column = 1, sticky = 'w')
lbl5 = tkinter.Label(master = frame2, text = 'Group of Mechatronic Engineering Technology students:', 
                      font = ('Helvetica', 12), bg = 'white', fg = 'black')
lbl5.grid(row = 2, column = 1, sticky = 'w')
lbl6 = tkinter.Label(master = frame2, text = 'Trinh Minh Tri           20146288', 
                      font = ('Helvetica', 12), bg = 'white', fg = 'black')
lbl6.grid(row = 3, column = 1, sticky = 'w')
lbl7 = tkinter.Label(master = frame2, text = 'Cao Minh Quan       20146202', 
                      font = ('Helvetica', 12), bg = 'white', fg = 'black')
lbl7.grid(row = 4, column = 1, sticky = 'w')
lbl8 = tkinter.Label(master = frame2, text = 'Phan Thi My Hang   20146249', 
                      font = ('Helvetica', 12), bg = 'white', fg = 'black')
lbl8.grid(row = 5, column = 1, sticky = 'w')

root.mainloop()