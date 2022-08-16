import json
import requests
import random
import webbrowser
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
import sqlite3

#display saved dogs
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
        try: # test for zip code validity
            self.random_dog = random.randint(0, len(self.data['animals']) - 1)
        except:
            self.image_label = tk.Label(text = "Invalid Zipcode or no dogs near\n you. Please try again.", fg = 'red')
            self.image_label.grid(row=7, column = 0, columnspan = 3)
            save.grid_forget()
            raise ValueError("Invalid User Zipcode")
        self.base = self.data['animals'][self.random_dog]
        self.bio = tk.Label(text=f"""Name: {self.base['name']}\nDescription: {self.base['description']}
             Age: {self.base['age']}, Primary Breed: {self.base['breeds']['primary']}
             Currently in: {self.base['contact']['address']['city']}, {self.base['contact']['address']['state']}""", wraplength = 300)
        self.bio.grid(row = 5, column = 0, columnspan = 3)
        self.link = tk.Label(text=f"Click here to adopt {self.base['name']} or see the full bio!", fg="blue", cursor="hand2")
        self.link.grid(row=6, column =1)
        self.link.bind("<Button-1>", lambda e: self.callback(self.base['url']))
        self.image_list = self.base['photos']
        self.image_index = 0
        try:
            self.image_url = self.image_list[self.image_index]['medium']
            self.image1 = self.get_pic(self.image_index)
        except: # Exeption occurs if no images of dog provided.
            self.image1 = self.get_pic(self.image_index, False)
        tk.Button(text = '<<', command = self.toggle_image).grid(row = 8, column = 0)
        tk.Button(text = '>>', command = lambda: self.toggle_image(forward = True)).grid(row = 8, column = 2)
        save = tk.Button(text = f"Save this pup to file" , command = self.export).grid(row = 8, column = 1)

    def toggle_image(self, forward = False):
        """Delete old image label and toggle images based on button selection if images exist."""
        if self.image_list: # Toggle buttons do nothing if empty list.
            if forward:
                self.image_index=  self.image_index + 1 if self.image_index < len(self.image_list) - 1 else 0
            else:
                self.image_index = self.image_index - 1 if self.image_index > 0 else len(self.image_list) - 1
            self.image_label.grid_forget()
            self.get_pic(self.image_index)

    def get_pic(self, index, image = True):
        """Get photo of dog based on index."""
        if image:
            self.image_url = self.image_list[index]['medium']
            u = requests.get(self.image_url)
            self.photo = ImageTk.PhotoImage(Image.open(BytesIO(u.content)))
        else: # if no image of dog, use 'noimage.jpg' file.
            self.photo = ImageTk.PhotoImage(Image.open('noimage.jpg'))
        self.image_label = tk.Label(image = self.photo)
        self.image_label.grid(row=7, column = 0, columnspan = 3)
        self.image_label.image = self.photo

    def callback(self, url):
        """Open adoption URL if linked clicked."""
        webbrowser.open_new_tab(url)

    def export(self):
        saved = sqlite3.connect('saved_doggos.db')
        c = saved.cursor()
        c.execute("INSERT INTO dogs VALUES (:name, :breed, :location_city, :location_state, :description, :link)",
        {'name': self.base['name'],
        'breed': self.base['breeds']['primary'],
        'location_city': self.base['contact']['address']['city'],
        'location_state': self.base['contact']['address']['state'],
        'description': self.base['description'],
        'link': self.base['url']
        })
        saved.commit()
        saved.close()


class Root(tk.Tk):

    def __init__(self):
        """Create and place initial window and buttons."""
        tk.Tk.__init__(self)
        self.winfo_toplevel().title("Random Pop-Up!")
        self.title2 = tk.Label(text = 'A random pup up for adoption near you!')
        self.title2.grid(row=0, column = 1)
        self.zip_label = tk.Label(text = "Enter your 5-digit zipcode")
        self.zip_label.grid(row = 2, column = 1)
        self.zip_entry = tk.Entry(self)
        self.zip_entry.grid(row = 1, column = 1)
        tk.Button(text="1 pup comin' up!", command = self.create).grid(row = 4, column = 1)

    def create(self):
        """Forget previous dog's grid info if applicable and get new random dog."""
        global pup
        if pup != None: # Forgets labels if create method called more than once. This prevents overlapping labels.
            pup.image_label.grid_forget()
            pup.bio.grid_forget()
            pup.link.grid_forget()
        pup = Dog(self.zip_entry.get())


# create SQL DB and table if not already created
saved = sqlite3.connect('saved_doggos.db')
c = saved.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS dogs (name text,
    breed text,
    location_city text,
    location_state text,
    description text,
    link text)""")
saved.commit()
saved.close()

pup = None
Root().mainloop()
