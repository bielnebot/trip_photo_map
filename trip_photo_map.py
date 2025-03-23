import streamlit as st
from PIL import Image, ImageOps
import os
import plotly.express as px
from utils.trips_dataframe import generate_trips_df
import random


def display_media(random_order, images_current_location, uri):
    """
    Displays the images, videos and audios
    :param random_order: bool
    :param images_current_location: list of the files of the current directory
    :param uri: tuple with the directory structure to the current location
    """

    if len(uri) == 2:
        trip_directory_name, location_directory_name = uri
        half_way_uri = f"{trip_directory_name}\\{location_directory_name}"
    else:
        trip_directory_name, location_directory_name, sub_location_directory_name = uri
        half_way_uri = f"{trip_directory_name}\\{location_directory_name}\\{sub_location_directory_name}"

    if random_order:
        random.shuffle(images_current_location)
    current_working_directory = os.getcwd()
    main_trip_directory = "trips" if "trips" in os.listdir() else "sample_trips"
    st.write(f"{len(images_current_location)} files")

    # Iterate over every file
    for file in images_current_location:
        file_i = f"{current_working_directory}\\{main_trip_directory}\\{half_way_uri}\\{file}"

        # If it's video
        if file.endswith("mp4") or file.endswith("MP4") or file.endswith("MOV") or file.endswith("mov"):
            video_file = open(file_i, "rb")
            video_bytes = video_file.read()
            st.video(video_bytes)
        # If it's audio
        elif file.endswith("mp3") or file.endswith("MP3"):
            st.audio(file_i, format="audio/mp3")
        # If it's image
        else:
            image_file = Image.open(file_i)
            image_file = ImageOps.exif_transpose(image_file)
            st.image(image_file)

        # Custom caption
        caption_text = file.rsplit(".", maxsplit=1)[0]
        font_color = "black"
        font_size = 24
        caption_html = f"""
            <div style='text-align: center;'>
                <p style='color: {font_color}; font-size: {font_size}px; '>{caption_text}</p>
            </div>
        """
        st.markdown(caption_html, unsafe_allow_html=True)


# Read files
df, dict_images, dict_locations_df, dict_sub_locations_df, set_persons, label_text_to_trip_directory, label_text_to_location_directory = generate_trips_df()

# Page title
st.set_page_config(page_title="Trip photo map", page_icon="🌎", layout="wide", initial_sidebar_state="expanded")

# Side bar
side_bar_image = "side_bar_image" if "trips" in os.listdir() else "sample_side_bar_image"
st.sidebar.image(f"utils/{side_bar_image}.jpg")
st.sidebar.title("Whose?")
chosen_member = st.sidebar.radio("Choose a person:", list(set_persons) + ["All"])

if chosen_member == "All":
    pass
else:
    df = df[df[chosen_member] == True]

skip_first_level = st.sidebar.checkbox("Show sub-locations")
random_order = st.sidebar.checkbox("Randomise order")
# Build a df with the sub-locations for the skip_first_level mode
first_level_points = None
for label_text_i in df["label_text"]:
    rows_i = dict_locations_df[label_text_to_trip_directory[label_text_i]]
    if first_level_points is None:
        first_level_points = rows_i
    else:
        first_level_points = first_level_points.append(rows_i, ignore_index=True)

# Main window
st.title("Trip photo map")

# Trip map (1st level)
if not skip_first_level:
    fig = px.scatter_mapbox(df,
                            lat="latitude",
                            lon="longitude",
                            color="rgb",
                            size="time_spent",
                            hover_name="label_text",
                            hover_data={"region": False, "time_spent": False, "latitude": False, "longitude":False},
                            custom_data=["region"],
                            height=600,
                            zoom=2,
                            color_discrete_map="identity"
                            )
    fig.update_traces(hoverlabel=dict(font_size=20, font_color="black", bgcolor="white"))
    fig.update_layout(mapbox_style="open-street-map")
    # st.plotly_chart(fig, use_container_width=True)

    chosen_trip = "No trip selected"
    # Interactive click
    event_data = st.plotly_chart(fig, on_select="rerun")
    # st.write(event_data)
    if len(event_data["selection"]["points"]) == 1:
        chosen_trip = event_data["selection"]["points"][0]["hovertext"]
    st.write(f"## {chosen_trip}")
else:
    chosen_trip = None
# Dropdown select (old)
# chosen_trip = st.selectbox("Choose a trip:", ["No trip selected"] + list(df["label_text"].sort_values()))

# Location (2nd level)
if chosen_trip == "No trip selected":
    pass
else:
    if not skip_first_level:
        trip_directory_name = label_text_to_trip_directory[chosen_trip]
        df_current_trip = dict_locations_df[trip_directory_name]
        list_of_sub_locations = [f"`{i}`" for i in df_current_trip["location"]]
        st.write(f"({len(df_current_trip)})"+", ".join(list_of_sub_locations))
        df_current_trip = df_current_trip
        zoom_level = int(df[df["label_text"] == chosen_trip]["zoom"])
    else:
        df_current_trip = first_level_points
        zoom_level = 2.7
    fig = px.scatter_mapbox(df_current_trip,
                            lat="latitude",
                            lon="longitude",
                            color="rgb",
                            size="point_size",
                            hover_name="location",
                            hover_data={"location": False, "latitude": False, "longitude":False, "point_size": False},
                            custom_data=["trip_directory"],
                            height=500,
                            # width=600,
                            zoom=zoom_level,
                            color_discrete_map="identity"
                            )
    fig.update_traces(hoverlabel=dict(font_size=20, font_color="black", bgcolor="white"))
    fig.update_layout(mapbox_style="open-street-map")
    # st.plotly_chart(fig, use_container_width=True)

    chosen_location = "No location selected"
    # Interactive click
    event_data = st.plotly_chart(fig, on_select="rerun")
    # st.write(event_data)
    if len(event_data["selection"]["points"]) == 1:
        chosen_location = event_data["selection"]["points"][0]["hovertext"]
        if skip_first_level:
            trip_directory_name = event_data["selection"]["points"][0]["customdata"][0]

    # Dropdown select (old)
    # chosen_location = st.selectbox("Choose a location:", ["No location selected"] + list(df_current_trip["location"].sort_values()))

    st.write(f"## {chosen_location}")
    if chosen_location == "No location selected":
        pass
    else:
        location_directory_name = label_text_to_location_directory[trip_directory_name][chosen_location]
        images_current_location = dict_images[trip_directory_name][location_directory_name]

        if isinstance(images_current_location, dict): # <-> if has sub-locations
            # Show sub-locations
            df_current_location = dict_sub_locations_df[trip_directory_name][location_directory_name]
            list_of_sub_locations = [f"`{i}`" for i in df_current_location["location"]]
            st.write(f"({len(df_current_location)})"+", ".join(list_of_sub_locations))
            fig = px.scatter_mapbox(df_current_location,
                                    lat="latitude",
                                    lon="longitude",
                                    color="rgb",
                                    size="point_size",
                                    hover_name="location",
                                    hover_data={"location": False, "latitude": False, "longitude": False,
                                                "point_size": False},
                                    # custom_data=["region"],
                                    height=500,
                                    # width=600,
                                    zoom=df_current_location["zoom"][0], # any row, column zoom
                                    color_discrete_map="identity"
                                    )
            fig.update_traces(hoverlabel=dict(font_size=20, font_color="black", bgcolor="white"))
            fig.update_layout(mapbox_style="open-street-map")

            chosen_sub_location = "No sub-location selected"
            # Interactive click
            event_data = st.plotly_chart(fig, on_select="rerun")
            # st.write(event_data)
            if len(event_data["selection"]["points"]) == 1:
                chosen_sub_location = event_data["selection"]["points"][0]["hovertext"]

            st.write(f"## {chosen_sub_location}")
            if chosen_sub_location == "No sub-location selected":
                pass
            else:
                sub_location_directory_name = label_text_to_location_directory[trip_directory_name][location_directory_name][chosen_sub_location]
                images_current_location = dict_images[trip_directory_name][location_directory_name][sub_location_directory_name]
                display_media(random_order, images_current_location,
                              (trip_directory_name, location_directory_name, sub_location_directory_name))
        else:
            display_media(random_order, images_current_location, (trip_directory_name, location_directory_name))
