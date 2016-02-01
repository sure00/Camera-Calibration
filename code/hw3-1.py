from Tkinter import *
from tkFileDialog import askopenfilename
import Image, ImageTk

if __name__ == "__main__":
    root = Tk()

    L1 = Label(root, text ="WordPt Coordinate")
    L1.pack(side = TOP)
    E1 = Entry(root, bd=3)
    E1.pack(side = TOP)

    root.minsize(586,636)

    #setting up a tkinter canvas with scrollbars
    frame = Frame(root, bd=2, relief=SUNKEN)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    canvas = Canvas(frame, bd=0)
    canvas.grid(row=0, column=0, sticky=N+S+E+W)

    frame.pack(fill=BOTH,expand=1)

    #adding the image
    File = "../data/cube.jpg"
    ImgPtFile = "../data/my-imagePt.txt"
    WdPtFile = "../data/my-worldPt.txt"
    imfd = open(ImgPtFile, 'w+')
    wdfd = open(WdPtFile, 'w+')
    img = ImageTk.PhotoImage(Image.open(File))
    canvas.create_image(0,0,image=img,anchor="nw")
    canvas.config(scrollregion=canvas.bbox(ALL))

    #function to be called when mouse is clicked
    def printcoords(event):
        #outputting x and y coords to console
        canvas.create_rectangle(event.x-8,event.y-8,event.x+8,event.y+8, outline='Red',width = 3)

        lines = [str(event.x)," ",str(event.y),'\n']
        # Write image point to file
        imfd.writelines(lines)
        imfd.seek(0,2)

        # Write word point to image
        Word_point = E1.get()
        wdfd.writelines(Word_point)
        wdfd.writelines('\n')
        wdfd.seek(0,2)
        print (event.x,event.y)

    #mouseclick event
    canvas.bind("<Button 1>",printcoords)

    root.mainloop()