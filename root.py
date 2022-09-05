import sqlite3
import tkinter as tk
from dog import Dog

pup = None


class Root(tk.Tk):

    def __init__(self):
        """Create and place initial window and buttons."""
        tk.Tk.__init__(self)
        self.second_frame = None
        self.winfo_toplevel().title("Random Pup-Up!")
        self.title2 = tk.Label(text='A random pup up for\nadoption near you!', font=("Courier", 14, "bold"))
        self.title2.grid(row=0, column=1, pady=(10, 0), padx=10)
        self.zip_label = tk.Label(text="Enter your 5-digit\nzipcode", font=("Courier", 11))
        self.zip_label.grid(row=2, column=1, padx=10)
        self.zip_entry = tk.Entry(self)
        self.zip_entry.grid(row=1, column=1)
        self.link = tk.Label(text="See your previously saved pups", fg="blue", cursor="hand2")
        self.link.grid(row=5, column=1, padx=10)
        self.link.bind("<Button-1>", lambda e: self.create_new_window())
        tk.Button(text="1 pup comin' up!", command=self.create).grid(row=4, column=1)

    def create(self):
        """Forget previous dog's grid to prevent photo stacking, if applicable, and get new random dog."""
        global pup
        if pup:
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
        """Create new window to view database records."""
        top = tk.Toplevel(self)
        top.title("Your Saved Pups")
        main_frame = tk.Frame(top, width=500, height=500)
        main_frame.pack(fill='both', expand=1)
        my_canvas = tk.Canvas(main_frame, width=550, height=500)
        my_canvas.pack(side='left', fill='both', expand=1)
        scroll = tk.Scrollbar(main_frame, orient='vertical', command=my_canvas.yview)
        scroll.pack(side='right', fill='both')
        my_canvas.configure(yscrollcommand=scroll.set)
        my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))
        self.second_frame = tk.Frame(my_canvas)
        my_canvas.create_window((0, 0), window=self.second_frame, anchor="sw")
        self.see_saved(self.second_frame)

    def see_saved(self, second_frame):
        """Display dogs previously saved."""
        saved = sqlite3.connect('saved_doggos.db')
        c = saved.cursor()
        c.execute('SELECT *, oid FROM dogs')
        database_pups = c.fetchall()
        if database_pups:
            for record in database_pups:
                tk.Label(second_frame, text=
                f"""Name: {str(record[1])}     Breed: {str(record[2])}\nLocation: {str(record[3])}, {str(record[4])}    Date saved: {str(record[0])}
                {str(record[5])}""", font=("Courier", 10), wraplength=500, padx=10).pack(anchor='w')
                link = tk.Label(second_frame, text=f'Link: {str(record[6])}', font=("Courier", 10), fg='blue',
                                cursor='hand2', wraplength=500)
                link.pack()
                link.bind("<Button-1>", lambda e: Dog.callback(self, record[6]))
                tk.Button(second_frame, text=f"Unsave {record[1]}",
                          command=lambda record=record: self.delete(record[6])).pack(pady=(0, 20))
        else:
            tk.Label(second_frame, text="You haven't saved any dogs yet.", font=("Courier", 10), wraplength=500,
                     padx=10).pack()
        saved.commit()
        saved.close()
