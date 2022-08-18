import json
import requests
import random
import webbrowser
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
import sqlite3
import html
from datetime import date


class Dog:

    @staticmethod
    def get_access_token(url, client_id, client_secret):
        """Automatically refresh the access token."""
        response = requests.post(url, data={"grant_type": "client_credentials"}, auth=(client_id, client_secret))
        return response.json()['access_token']

    # Enter your own API credentials here.
    CLIENT_ID = ''
    CLIENT_SECRET = ''
    TOKEN_URL = 'https://api.petfinder.com/v2/oauth2/token'
    URL_BASE = "https://api.petfinder.com/v2/animals"
    TOKEN = get_access_token(TOKEN_URL, CLIENT_ID, CLIENT_SECRET)
    HEADER = {"Authorization": f"Bearer {TOKEN}"}

    def __init__(self, user_zipcode):
        """Create attributes and place dog-specific labels."""
        self.url = f"?type=dog&size=small,medium,large,xlarge&location={user_zipcode}&distance=10"
        self.data = requests.get(Dog.URL_BASE + self.url, headers = Dog.HEADER).json()
        self.random_dog = self.is_valid()
        self.base = self.data['animals'][self.random_dog]
        self.description= self.base['description']
        self.description = self.description.replace("&#39;", "'")
        self.breed = self.base['breeds']['primary']
        self.biotext = html.unescape(f"""Name: {self.base['name']}\nDescription: {self.description}
             Age: {self.base['age']}, Primary Breed: {self.breed}
             Currently in: {self.base['contact']['address']['city']}, {self.base['contact']['address']['state']}""")
        self.image_list = self.base['photos']
        self.image_index = 0

        # dog-specific labels and buttons
        self.create_image_label()
        self.bio = tk.Label(text=self.biotext, wraplength = 300)
        self.bio.grid(row = 6, column = 0, columnspan = 3)
        self.link = tk.Label(text=f"         Click here to adopt        \n        {self.base['name']} or see the full bio!        ", fg="blue", cursor="hand2")
        self.link.grid(row=7, column =1, padx = 15)
        self.link.bind("<Button-1>", lambda e: self.callback(self.base['url']))
        tk.Button(text = '<<', command = self.toggle_image).grid(row = 8, column = 0)
        tk.Button(text = '>>', command = lambda: self.toggle_image(forward = True)).grid(row = 8, column = 2)
        save = tk.Button(text = f"Save this pup to file" , command = self.export).grid(row = 8, column = 1)

    def create_image_label(self):
        """Check if an image is available for the dog and call pic with 'image' or 'no image'."""
        try:
            self.image_url = self.image_list[self.image_index]['medium']
            self.image1 = self.get_pic(self.image_index)
        except: # Exeption occurs if no images of dog provided.
            self.image1 = self.get_pic(self.image_index, False)


    def get_pic(self, index, image = True):
        """Get photo of dog based on index."""
        if image:
            self.image_url = self.image_list[index]['medium']
            u = requests.get(self.image_url)
            self.photo = ImageTk.PhotoImage(Image.open(BytesIO(u.content)))
        else: # if no image of dog, use 'noimage.jpg' file.
            self.photo = ImageTk.PhotoImage(Image.open('noimage.jpg'))
        self.image_label = tk.Label(image = self.photo)
        self.image_label.grid(row=9, column = 0, columnspan = 3)
        self.image_label.image = self.photo

    def toggle_image(self, forward = False):
        """Delete old image label and toggle images based on button selection if more images exist."""
        if self.image_list: # Toggle buttons do nothing if empty list.
            if forward:
                self.image_index=  self.image_index + 1 if self.image_index < len(self.image_list) - 1 else 0
            else:
                self.image_index = self.image_index - 1 if self.image_index > 0 else len(self.image_list) - 1
            self.image_label.grid_forget()
            self.get_pic(self.image_index)

    def is_valid(self):
        """Checks if dogs exist in zipcode."""
        try:
            return random.randint(0, len(self.data['animals']) - 1)
        except:
            self.image_label = tk.Label(text = "Invalid Zipcode or no dogs near\n you. Please try again.", fg = 'red')
            self.image_label.grid(row=7, column = 0, columnspan = 3)
            save.grid_forget()
            raise ValueError("Invalid User Zipcode")

    def callback(self, url):
        """Open adoption URL."""
        webbrowser.open_new_tab(url)

    def export(self): 
        """Create a table if needed and save a dog to the database if not already saved."""
        saved = sqlite3.connect('saved_doggos.db')
        c = saved.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS dogs (date_saved text,
            name text,
            breed text,
            location_city text,
            location_state text,
            description text,
            link text,
            UNIQUE(link))""")

        c.execute("INSERT OR IGNORE INTO dogs VALUES (:date, :name, :breed, :location_city, :location_state, :description, :link)",
        {'date': date.today(),
        'name': self.base['name'],
        'breed': self.breed,
        'location_city': self.base['contact']['address']['city'],
        'location_state': self.base['contact']['address']['state'],
        'description': self.description,
        'link': self.base['url']})
        saved.commit()
        saved.close()


class Root(tk.Tk):

    def __init__(self):
        """Create and place initial window and buttons."""
        tk.Tk.__init__(self)
        self.winfo_toplevel().title("Random Pop-Up!")
        self.title2 = tk.Label(text = 'A random pup up for\nadoption near you!', font = ("Courier", 14, "bold"))
        self.title2.grid(row=0, column = 1, pady = (10,0), padx = 10)
        self.zip_label = tk.Label(text = "Enter your 5-digit\nzipcode", font = ("Courier", 11))
        self.zip_label.grid(row = 2, column = 1, padx = 10)
        self.zip_entry = tk.Entry(self)
        self.zip_entry.grid(row = 1, column = 1)
        self.link = tk.Label(text="See your previously saved pups", fg="blue", cursor="hand2")
        self.link.grid(row=5, column =1, padx = 10)
        self.link.bind("<Button-1>", lambda e: self.create_new_window())
        tk.Button(text="1 pup comin' up!", command = self.create).grid(row = 4, column = 1)

    def create(self):
        """Forget previous dog's grid to prevent photo stacking, if applicable, and get new random dog."""
        global pup
        if pup != None:
            pup.image_label.grid_forget()
            pup.bio.grid_forget()
            pup.link.grid_forget()
        pup = Dog(self.zip_entry.get())

    def delete(self, id):
        """Delete a saved record by URL (primary key)."""
        saved = sqlite3.connect('saved_doggos.db')
        c = saved.cursor()
        c.execute(f"""DELETE FROM dogs WHERE link = (?);""", (id,))
        saved.commit()
        saved.close()

    def create_new_window(self):
        """Create new window to view database"""
        top= tk.Toplevel(self)
        top.title("Your Saved Pups")
        main_frame = tk.Frame(top, width=500, height=500)
        main_frame.pack(fill = 'both', expand = 1)
        my_canvas = tk.Canvas(main_frame, width=550, height=500)
        my_canvas.pack(side = 'left', fill = 'both', expand = 1)
        scroll = tk.Scrollbar(main_frame, orient = 'vertical', command = my_canvas.yview )
        scroll.pack(side= 'right', fill = 'both')
        my_canvas.configure(yscrollcommand=scroll.set)
        my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion = my_canvas.bbox("all")))
        self.second_frame = tk.Frame(my_canvas)
        my_canvas.create_window((0,0), window=self.second_frame, anchor="sw")
        self.see_saved(self.second_frame)

    def see_saved(self, second_frame):
        """Display saved dogs information and option to remove from saved dog database."""
        saved = sqlite3.connect('saved_doggos.db')
        c = saved.cursor()
        c.execute('SELECT *, oid FROM dogs')
        database_pups = c.fetchall()
        if database_pups:
            for record in database_pups:
                tk.Label(second_frame, text=
                f"""Name: {str(record[1])}     Breed: {str(record[2])}\nLocation: {str(record[3])}, {str(record[4])}    Date saved: {str(record[0])} \n{str(record[5])}""", font = ("Courier", 10), wraplength = 500, padx = 10).pack(anchor = 'w')
                linky = tk.Label(second_frame, text= f'Link: {str(record[6])}', font = ("Courier", 10), fg='blue', cursor = 'hand2', wraplength = 500)
                linky.pack()
                linky.bind("<Button-1>", lambda e: Dog.callback(self,record[6]))
                tk.Button(second_frame, text=f"Unsave {record[1]}", command = lambda record= record: self.delete(record[6])).pack(pady = (0, 20))
        else:
            tk.Label(second_frame, text= "You haven't saved any dogs.", font = ("Courier", 10), wraplength = 500, padx = 10).pack()
        saved.commit()
        saved.close()

pup = None
Root().mainloop()
