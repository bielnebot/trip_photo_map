import streamlit as st
from PIL import Image, ImageOps
import os
import plotly.express as px
from utils.trips_dataframe import generate_trips_df
import random


def plot_images_and_videos(images_current_location, uri):
    """
    Plots the images and videos of
    :param images_current_location: list of the files of the current directory
    :param uri: tuple with the directory structure to the current location
    :return:
    """

    if len(uri) == 2:
        trip_directory_name, location_directory_name = uri
        half_way_uri = f"{trip_directory_name}\\{location_directory_name}"
    else:
        trip_directory_name, location_directory_name, sub_location_directory_name = uri
        half_way_uri = f"{trip_directory_name}\\{location_directory_name}\\{sub_location_directory_name}"

    random.shuffle(images_current_location)
    current_working_directory = os.getcwd()
    main_trip_directory = "trips" if "trips" in os.listdir() else "sample_trips"
    st.write(f"{len(images_current_location)} files")
    for img in images_current_location:
        single_image = f"{current_working_directory}\\{main_trip_directory}\\{half_way_uri}\\{img}"

        is_video = False
        if img.endswith("mp4") or img.endswith("MP4"):
            is_video = True

        if is_video:
            video_file = open(single_image, "rb")
            video_bytes = video_file.read()
            st.video(video_bytes)
        else:
            image_file = Image.open(single_image)
            image_file = ImageOps.exif_transpose(image_file)
            st.image(image_file)

            # Custom caption
            caption_text = img.rsplit(".", maxsplit=1)[0]
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

# Main window
st.title("Trip photo map")

# Trip map (1st level)
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

# Dropdown select (old)
# chosen_trip = st.selectbox("Choose a trip:", ["No trip selected"] + list(df["label_text"].sort_values()))

# Location (2nd level)
st.write(f"## {chosen_trip}")
if chosen_trip == "No trip selected":
    pass
else:
    trip_directory_name = label_text_to_trip_directory[chosen_trip]
    df_current_trip = dict_locations_df[trip_directory_name]
    # st.dataframe(df_current_trip)
    list_of_sub_locations = [f"`{i}`" for i in df_current_trip["location"]]
    st.write(f"({len(df_current_trip)})"+", ".join(list_of_sub_locations))
    fig = px.scatter_mapbox(df_current_trip,
                            lat="latitude",
                            lon="longitude",
                            color="rgb",
                            size="point_size",
                            hover_name="location",
                            hover_data={"location": False, "latitude": False, "longitude":False, "point_size": False},
                            # custom_data=["region"],
                            height=500,
                            # width=600,
                            zoom=int(df[df["label_text"] == chosen_trip]["zoom"]),
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
                plot_images_and_videos(images_current_location,(trip_directory_name,location_directory_name,sub_location_directory_name))
        else:
            plot_images_and_videos(images_current_location,(trip_directory_name,location_directory_name))
