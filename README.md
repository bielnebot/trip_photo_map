![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)
[showcase_video.webm](https://github.com/user-attachments/assets/0792b36e-2650-4c01-8642-552fa1f78860)
# Trip photo map
This repository contains a [Streamlit](https://streamlit.io/) app to visualize and interact with a directory structure of images classified by location, ideal to showcase trips.
## Set up
Create a virtual environment:
```console
conda create -n NAME_OF_THE_ENVIRONEMNT python=3.9
conda activate NAME_OF_THE_ENVIRONEMNT
```
Clone the repository:
```console
git clone https://github.com/bielnebot/trip_photo_map.git
```
And install the requirements:
```console
pip install -r requirements.txt
```
## Run
To open the app, run the following command in the main directory:
```console
streamlit run trip_photo_map.py
```
**Basic usage**

| Action             | Details                                                                       |
|--------------------|-------------------------------------------------------------------------------|
| Open a location    | Click a dot in the map.                                                       |
| Reset the map view | Double click on the map to reset the view and un-select the current location. |

## How to add custom locations and images
**Step 0**
* Rename the `/sample_trips` directory to `/trips` (or create it from scratch)
* Add an image of your choice in `/utils` and rename it to `side_bar_image.jpg`

**Step 1:** create a new directory for the trip (or use one of the already existing ones as a template) and arrange the images in the locations you want:
<pre>
├── 📁trip_1
├── 📁trip_2
├── 📁trip_3
...
└── 📁my_new_trip
    ├── 📁location_1
    │   ├── 🖼️image_1.jpg
    │   ├── 🖼️image_2.jpg
    │   └── 📄location_data.json
    ├── 📁location_2
    │   ├── 🖼️image_3.jpg
    │   ├── 🎥video_1.mp4
    │   └── 📄location_data.json
    └── 📄trip_data.json
</pre>
**Step 2:** create the files `trip_data.json` and `location_data.json` for each of the locations like shown below:
### `trip_data.json`
```json
{
  "region": "Île-de-France",
  "country": "France",
  "date_start": "2024-09-12",
  "date_end": "2024-09-20",
  "members": ["person_1", "person_4", "person_5"],
  "latitude": 48.859051,
  "longitude": 2.339822,
  "rgb": [201, 10, 99],
  "zoom": 11
}
```

### `location_data.json`
```json
{
  "location": "Château de Versailles",
  "latitude": 48.804562,
  "longitude": 2.121387
}
```

Notes on the data provided:

| Field                                  | Info                                                                                                     |
|----------------------------------------|----------------------------------------------------------------------------------------------------------|
| `region`, `country`, `location`        | Text to desplay in the app for each of the trips and locations.                                          |
| `date_start`, `date_end`               | Trip duration so set the size the dots accordingly in the map and to display the year the trip was done. |
| `members`                              | Members that came to the trip to apply filters later on.                                                 |
| `latitude`, `longitude`, `rgb`, `zoom` | Location and colour of the dots and default map zoom.                                                    |


If needed, one more deeper level of hierarchy is possible. For it, organise your files like this:
<pre>
├── 📁trip_1
├── 📁trip_2
├── 📁trip_3
...
└── 📁my_new_trip
    ├── 📁location_1
    │   ....
    ├── 📁a_location_with_a_lot_of_images
    │   ├── 📁sub_location_1
    │   │   ├── 🖼️image_5.jpg
    │   │   ├── 🖼️image_6.jpg
    │   │   └── 📄location_data.json
    │   ├── 📁sub_location_2
    │   │   ├── 🖼️image_7.jpg
    │   │   ├── 🎥video_2.mp4
    │   │   └── 📄location_data.json
    │   └── 📄location_data.json
    └── 📄trip_data.json
</pre>
Then the `location_data.json` files change slightly:
### `location_data.json` for the lower level sub-locations
Same structure as before:
```json
{
  "location": "Château de Versailles",
  "latitude": 48.804562,
  "longitude": 2.121387
}
```
### `location_data.json` for the mid level locations
```json
{
  "location": "Versailles, Yvelines",
  "latitude": 48.802521,
  "longitude": 2.138454,
  "has_sub_locations": "yes",
  "zoom": 11
}
```
The `trip_data.json` files stay the same.
