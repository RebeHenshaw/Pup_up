import html
import random
import sqlite3
import tkinter as tk
import webbrowser
from datetime import date
from io import BytesIO

import requests
from PIL import ImageTk, Image


class Dog:

    def get_access_token(url, client_id, client_secret):
        """Automatically refresh the access token."""
        response = requests.post(url, data={"grant_type": "client_credentials"}, auth=(client_id, client_secret))
        return response.json()['access_token']

    # Enter your own API credentials here.
    CLIENT_ID = '<Your ID>'
    CLIENT_SECRET = '<Your secret>'
    TOKEN_URL = 'https://api.petfinder.com/v2/oauth2/token'
    URL_BASE = "https://api.petfinder.com/v2/animals"
    TOKEN = get_access_token(TOKEN_URL, CLIENT_ID, CLIENT_SECRET)
    HEADER = {"Authorization": f"Bearer {TOKEN}"}

    def __init__(self, user_zipcode):
        """Create attributes and place dog-specific labels."""
        self.photo = None
        self.image_url = None
        self.link = None
        self.bio = None
        self.image_label = None
        self.url = f"?type=dog&size=small,medium,large,xlarge&location={user_zipcode}&distance=10"
        self.data = requests.get(Dog.URL_BASE + self.url, headers=Dog.HEADER).json()
        self.random_dog = self.is_valid()
        self.base = self.data['animals'][self.random_dog]
        self.description = self.base['description']
        self.description = self.description.replace("&#39;", "'")
        self.breed = self.base['breeds']['primary']
        self.biotext = html.unescape(f"""Name: {self.base['name']}\nDescription: {self.description}
             Age: {self.base['age']}, Primary Breed: {self.breed}
             Currently in: {self.base['contact']['address']['city']}, {self.base['contact']['address']['state']}""")
        self.image_list = self.base['photos']
        self.image_index = 0
        self.create_image_label()
        self.place_labels()

    def is_valid(self):
        """Checks if dogs exist in zipcode."""
        try:
            return random.randint(0, len(self.data['animals']) - 1)
        except:
            self.image_label = tk.Label(text="Invalid Zipcode or no dogs near\n you. Please try again.", fg='red')
            self.image_label.grid(row=7, column=0, columnspan=3)
            raise ValueError("Invalid User Zipcode")

    def place_labels(self):
        """Create dog-specific labels and buttons."""
        self.bio = tk.Label(text=self.biotext, wraplength=300)
        self.bio.grid(row=6, column=0, columnspan=3)
        self.link = tk.Label(
            text=f"         Click here to adopt        \n        {self.base['name']} or see the full bio!        ",
            fg="blue", cursor="hand2")
        self.link.grid(row=7, column=1, padx=15)
        self.link.bind("<Button-1>", lambda e: self.callback(self.base['url']))
        tk.Button(text='<<', command=self.toggle_image).grid(row=8, column=0)
        tk.Button(text='>>', command=lambda: self.toggle_image(forward=True)).grid(row=8, column=2)
        tk.Button(text=f"Save this pup to file", command=self.export).grid(row=8, column=1)

    def create_image_label(self):
        """Check if an image is available for the dog and call get_pic() with 'image' or 'no image'."""
        try:
            self.image_url = self.image_list[self.image_index]['medium']
            self.get_pic(self.image_index)
        except:  # Exception occurs if no images of dog provided.
            self.get_pic(self.image_index, False)

    def get_pic(self, index, image=True):
        """Get photo of dog based on index."""
        if image:
            self.image_url = self.image_list[index]['medium']
            u = requests.get(self.image_url)
            self.photo = ImageTk.PhotoImage(Image.open(BytesIO(u.content)))
        else:
            self.photo = ImageTk.PhotoImage(Image.open('noimage.jpg'))
        self.image_label = tk.Label(image=self.photo)
        self.image_label.grid(row=9, column=0, columnspan=3)
        self.image_label.image = self.photo

    def toggle_image(self, forward=False):
        """Forget previous image label and toggle images based on button selection if more images exist."""
        if self.image_list:  # Toggle buttons do nothing if empty list.
            if forward:
                self.image_index = self.image_index + 1 if self.image_index < len(self.image_list) - 1 else 0
            else:
                self.image_index = self.image_index - 1 if self.image_index > 0 else len(self.image_list) - 1
            self.image_label.grid_forget()
            self.get_pic(self.image_index)

    def callback(self, url):
        """Open adoption URL from either window."""
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

        c.execute(
            "INSERT OR IGNORE INTO dogs VALUES (:date, :name, :breed, :location_city, :location_state, :description, "
            ":link)",
            {'date': date.today(),
             'name': self.base['name'],
             'breed': self.breed,
             'location_city': self.base['contact']['address']['city'],
             'location_state': self.base['contact']['address']['state'],
             'description': self.description,
             'link': self.base['url']})
        saved.commit()
        saved.close()
