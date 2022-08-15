import streamlit as st
from PIL import Image
import os
import plotly.express as px
from utils.trips_dataframe import generate_trips_df


df, dict_images, dict_locations_df, set_persons, label_text_to_trip_directory, label_text_to_location_directory = generate_trips_df()

st.set_page_config(page_title="Trip photo map", page_icon="🌎", layout="wide", initial_sidebar_state="expanded")

# Side bar
st.sidebar.title("Whose?")
chosen_member = st.sidebar.radio("Choose a person:", list(set_persons) + ["All"])

if chosen_member == "All":
    pass
else:
    df = df[df[chosen_member] == True]

# Main window
# st.dataframe(df)
#
# expander = st.expander("MapBox")
# expander.map(df)
#
# expander = st.expander("Plotly")
# fig = px.scatter_geo(df,
#                      lat="latitude",
#                      lon="longitude",
#                      # color="name",
#                      size="time_spent",
#                      hover_name="label_text", # column added to hover information
#                      projection="natural earth"
#                      )
# expander.plotly_chart(fig, use_container_width=True)
st.title("Trip photo map")
fig = px.scatter_mapbox(df,
                        lat="latitude",
                        lon="longitude",
                        color="rgb",
                        size="time_spent",
                        hover_name="label_text",
                        hover_data={"region": False, "time_spent": False, "latitude": False, "longitude":False},
                        custom_data=["region"],
                        height=600,
                        zoom=1,
                        color_discrete_map="identity"
                        )
fig.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig, use_container_width=True)

chosen_trip = st.selectbox("Choose a trip:", ["No trip selected"] + list(df["label_text"]))

if chosen_trip == "No trip selected":
    pass
else:
    trip_directory_name = label_text_to_trip_directory[chosen_trip]
    df_current_trip = dict_locations_df[trip_directory_name]
    # st.dataframe(df_current_trip)
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
                            # zoom=1,
                            color_discrete_map="identity"
                            )
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)

    chosen_location = st.selectbox("Choose a location:", ["No location selected"] + list(df_current_trip["location"]))

    if chosen_location == "No location selected":
        pass
    else:
        location_directory_name = label_text_to_location_directory[trip_directory_name][chosen_location]
        images_current_location = dict_images[trip_directory_name][location_directory_name]
        current_working_directory = os.getcwd()
        for img in images_current_location:
            single_image = f"{current_working_directory}\\trips\\{trip_directory_name}\\{location_directory_name}\\{img}"
            image = Image.open(single_image)
            st.image(image)