## Data and Method
This project used sentinel-2 satellite images and boundaries of a few selected study areas in polygon geojson format. Sentinel-2 is the land monitoring mission from the EU Copernicus Programme that consists of the constellation of twin satellites Sentinel-2A and 2B. They provide fine-resolution optical imageries with global coverage and a revisit time of 5 days with satellite constellation. (Earth Online European Space Agency, 2014). Sentinel 2 images have a range of spatial resolutions, but we used the bands with 10m resolutions in this project.

The backend was developed using Flask python. The downloading and processing of images are carried out by functions in the main file. The “app.py” file is the flask application created to extract data from the database. The front end, which enables the visualization of the results was developed using HTML, CSS and JavaScript. The web map interface incorporates Leaflet, which is an open-source JavaScript library.
## Installation

First thing is to create the environment in your computer for that you have to install Miniconda, pgAdmin, and VS code.

Miniconda : https://youtu.be/oHHbsMfyNR4

pgAdmin : https://youtu.be/0n41UTkOBb0

VS Code : https://youtu.be/JPZsB_6yHVo

After installaltion you have to open the Anaconda prompt and run the line of code to create the environment.
Note: Downlaod our full folder "Crop-Health-Monitoring" and make sure you are creating the environment in our downloaded folder.
```bash
  conda create -n project
```
project is the name of the environment, then you have to activate your project with this command. 
```bash
  conda activate project
```
Then, you have to run that line of code to in all teh libaraies which we need to run that app. 
```bash
  conda install --file requirements.txt -c conda-forge
```


## How to run the APP
Follow these steps to run the app.

1. you just need to change the Bounding boxes coordinates according to requirements.

2. Ensure you have login credentials. If not register on Sentinel Hub to get that.Copy your credentials into the required python files. There is Obtain.py files whih allow you to get access token after having your credenitals 

4. Update the credentials  of the database and table in the required python files (main.py and app.py)

5. Run the "main.py"




#### Working
main.py file did these steps
1. Create the folders in your localhost to downloaded bands, Cliped images and processed Indices.
2. Look the S2 images for your study area  according to your given time period then download the specific bands (Band-2348) instead of whole image and put them in the folder "download" (main.py will create that folder automatically)
3. Getting the specifc metadata for downloaded image and upload that data in database.
4. Clip the bands with your uploaded geoJSON files (Study area) put these clip bands in the folder "processed"(main.py will create that folder automatically)
5. Calculate the indices and put these indices in the folder "indices" (main.py will create that folder automatically)


## Database Connection
by running main.py file after getting database name and password of postgres it will create a table in that database named as polygon_features


Note: If you change the table name or database name, you have to change also in main.py
#### Working
This sql file will create the database, create the postgis extension for the database and table for the metadata of the S2 Imgaes.
## Outputs and visualization
### Outputs
The downloaded, processed bands and indices are stored on the local Disk and can be visualized using any suitable software application. The image metadata are contained in the PostgreSQL dB. The image metadata and the footprint of the images can be visualized using the web map interface.
### Visualization
Follow these steps to visualized this web map
1. Update the credentials of the database in app.py 

2. Run the app.py file and open the localhost link.







#### Working
The web map interface functionalities include an attribute pop-up when clicking on the footprint polygon, a button to display or hide the bar chart, and a .
## Future updates:
We will update this web app
1. Calculate the indices from multiple images and make it more interactive
2. Instead of changing code you can add bounding boxes on front end only 
3. Centralized database system.
4. Multi-temporal vegetation indices analysis and comparison in web dashboard.

Web visualization of multi-temporal indices line plot.
It is pertinent to state that this app is developed for educational and research purposes. Future updates will be made if it will be suitable for commercial purposes
## Authors
1. Ammar Yousaf :
He earned a bachelor's degree in GIS from NUST, Islamabad, Pakistan and now he is pursuing a master's degree in Geospatial Technologies at NOVA IMS, Universidade NOVA de Lisboa, Portugal.

2. Muhammad Qasim :
He is also pursuing a master's degree in Geospatial Technologies at NOVA IMS, Universidade NOVA de Lisboa, Portugal.

3. Flavio Vata :
 he is also pursuing a master's degree in Geospatial Technologies at NOVA IMS, Universidade NOVA de Lisboa, Portugal.

