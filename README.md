# Pup_up
Using Petfinder API, displays a random "Pup_up" for adoption near you. 


***You need to enter your own API credentials to try this code.***
[You can get creditials for free here.](https://www.petfinder.com/developers/v2/docs/#using-the-api)

***Update 8/16: I updated the file slightly after reading up on some PEP 8, and noticed I forgot to add my error for an invalid zipcode. I added a feature to save pups to an SQL DB from the user interface. I plan to add an option to see dogs you've saved for those without SQL installed. ***

This was my first original program using Object Oriented Programming. I initially wrote it in procedural/functional programming and challeneged myself to translate it to OOP, which cut 50 lines and made it much easier to read. 

With this project I learned how to use an API with a token, how to display photos from an API and augmented my knowledge of OOP by creating this from scratch. 

The biggest challenges of this project: 
1. Working with an API token that expires hourly
     * Solution: automated getting the token each time program is initiated. 
2. Getting the new Tk labels not to stack on top of the previous label
     * Solution: initiated a class variable set to 'None' that updates with the first Dog class instance, and used grid_forget() if variable did not equal 'None'.
3. Avoiding index errors if no photo of dog was availble.
     * Solution: created an additional parameter with default option on the get_pic() method so that if no pics are available, it chooses a local image file to display.

**Non-standard libraies used: requests, pillow**
