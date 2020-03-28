Project Explanation:
This project uses the algorithm described in Clifford A. Reiter's paper: "A local cellular model for snow crystal growth" (citation below) to generate scientifically-modeled snowflakes using alpha, beta, and gamma coefficients. In the app the alpha coefficient remains constant and beta and gamma change to produce differently shaped coefficients. You can make the snowflakes in the Generate mode by inputing beta and gamma as the user or in the Catch mode where snowflake's parameters are randomly assigned and the user "catches" the snowflakes by clicking on them. In these two modes the snowflakes can be saved to the used saved snowflake library and then seen by clicking on "See Saved Snowflakes". A screen will pop up where the user can go through the pages of snowflakes they saved in both Catch and Generate modes. These snowflakes can then be used in the Draw mode, which a paint-like module in which a user can select a snowflake from the library of saved snowflakes. Snowflakes are added from the saved library and then can be placed, rotated, and deleted. At any time the user can export the image they created as a png by clicking on Export and being prompted to a file saving screen.

Necessary Libraries and Downloads:
Running on Python 3.6 which is shipped with pip (needed to install Image)
The following Python libraries need to be installed to run the program:
tkinter.simpledialog, tkinter.messagebox, tkinter.filedialog, and Image from PIL
To install Image run "pip install Image" in a python shell or command line.
Additionally the user must have Ghostscript installed with the path specified to be able to export images in the app. Ghostscript can be installed here: https://www.ghostscript.com/download/

Running Project:
Extract the zip file and then run the snowflakeMain.py file further instructions are in the program

Snowflake Algorithm Explanataion:
The snowflake is built from a hexagonal grid, where each hexagonal cell has an initial state of ?, except for the center, which has a state of 1. Note: a cell is considered frozen if it’s state is greater than or equal to 1. The next term Reiter uses is receptive cells, which denote the cells that are frozen or are adjacent to cell that is frozen. At a certain interval  , the state of all the cells is calculated based upon two internal variables,  , which model the diffusion of water and amount of vapor added to the cells, respectively. The two variable values are determined by equations based on whether the current cell is receptive or not. The equation for   is a scaled average of the state of its immediate neighbors added to the previous   value. This is calculated for all the cells. The equation for   is a linear equation that adds the current ? value, where ? is the current amount of vapor at a certain iteration. Once a cell’s state reaches the threshold of 1, it is denoted as frozen and all new neighbors are added to the collection of receptive cells. 
Reiters algorithm is implemented in the app with a constant alpha of 1 and 500 iterations on a 25-layered grid. In addition an algoirithm was written to more efficiently draw the snowflakes by keeping only the boundary points whenever a hexagon cell changes states from un-frozen to frozen. This algorithm uses the number of hexagons that share a given point in the grid to determine if a point is a boundary point or not as well as keeping the list of boundary points in order.

Citation
Clifford A. Reiter, A local cellular model for snow crystal growth, In Chaos, Solitons & Fractals, Volume 23, Issue 4, 2005, Pages 1111-1119, ISSN 0960-0779, https://doi.org/10.1016/j.chaos.2004.06.071.
(http://www.sciencedirect.com/science/article/pii/S0960077904003741)
