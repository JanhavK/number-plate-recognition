# number-plate-recognition
uses image processing to find the number plate in an image provided <br>
• This project was made using Python<br>
• I decided to make it a challenge on this project and apply algorithms to manipulate the pixel arrays of an image to identify numberplates in images.<br>
• I first converted the colored image provided into a greyscale one and then stretched the pixel color values to be in a 1-256 scale across the image.<br>
• I then computed the mean of the pixels in a 5x5 box to blur the image.<br>
• I then stretched it once again and threshed the image.<br>
• I then applied various rounds of dilution and erotion to make the number plate stand out from the rest of the image.<br>
• Lastly I created a DFS binary tree and made every since object on the screen numbered so that I could determine which object has a ratio of a common numberplate and the most amount of pixels attached.<br>
• Once I found the number plate I extended the program to put a box around this number plate, determine the numberplate as text, crop out the numberplate, find the color of the car and blur the license plate.<br>
• I found this project fun to undertake, applying the formulas I gained in a course I had just completed on computer graphics and virtual lighting was quite satisfying.
