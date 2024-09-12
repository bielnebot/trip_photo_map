import json
import os
import pandas as pd
import datetime
import numpy as np


def json_to_dict(file_uri):
    """
    Reads a json file and returns a dictionary
    :param file_uri: str. Eg: "C:\directory\file.json"
    :return: dict
    """

    f = open(file_uri, "r", encoding="utf-8")
    data = json.load(f)
    return data


def transform_trips_df(trips_df):
    """
    Changes the format of the data in the trips_df and
    adds a column for each member with a bool value indicating if he or she went to the trip
    :param trips_df: pandas df
    :return: pandas df
    """
    trips_df["date_start"] = trips_df["date_start"].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").date())
    trips_df["date_end"] = trips_df["date_end"].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").date())
    trips_df["rgb"] = trips_df["rgb"].apply(lambda x: f"rgb({x[0]}, {x[1]}, {x[2]})")
    trips_df["label_text"] = trips_df.apply(lambda x: f"{x.region}, {x.country} ({x.date_start.year})", axis=1)
    trips_df["time_spent"] = trips_df["date_end"] - trips_df["date_start"]
    trips_df["time_spent"] = trips_df["time_spent"].apply(lambda x: np.log10(x.days)+1) # logarithmic scale for the dot size

    # One hot encode members
    set_persons = set(trips_df["members"].sum())
    d = {person_i: [] for person_i in set_persons}
    for _, row in trips_df.iterrows():
        for person in set_persons:
            d[person].append(person in row["members"])

    return trips_df.join(pd.DataFrame(d))


def transform_locations_df(locations_df, trip_rgb, zoom=None):
    """
    Adds two columns to the locations_df (the colour and the point size)
    :param locations_df:
    :param trip_rgb:
    :return:
    """
    # locations_df["date"] = locations_df["date"].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d").date())
    locations_df["rgb"] = f"rgb({trip_rgb[0]}, {trip_rgb[1]}, {trip_rgb[2]})"
    locations_df["point_size"] = 4
    if zoom:
        locations_df["zoom"] = zoom
    return locations_df


def generate_trips_df():
    """

    :return: df_trips
    :return: dict_images
        Eg: {
            'trip1': {
                'location1': ['Image1.jpg', 'Image2.jpg'],
                'location2': ['Image6.jpg', 'Image7.jpg']
                },
            'tokyo': {
                'location1': ['Image4.jpg', 'Image5.jpg'],
                'location2': ['Image8.jpg']
                },
            'london': {
                'location1': ['Image10.jpg']
                }
            'barcelona': {
                'location1': {
                    'sublocation1': ['Image4.jpg', 'Image5.jpg'],
                    'sublocation2': ['Image6.jpg', 'Image7.jpg'],
                    },
                'location2': ['Image11.jpg', 'Image22.jpg'],
                }
            }
    :return: dict_locations_df
             Eg: {'trip1':     location        latitude    longitude
                               train station   41.41418    2.13413
                               town hall       41.37328    2.17751,
                  'tokyo': df...,
                  'london': df...}
    :return: set_persons
             Eg: {'person2', 'person1', 'person3'}
    """

    list_data_trips = []
    dict_images = {}
    dict_locations_df = {}
    dict_sub_locations_df = {}
    label_text_to_location_directory = {}

    # Working directory
    current_working_directory = os.getcwd()
    if "trips" in os.listdir():
        trips_directory = f"{current_working_directory}\\trips"
    else:
        trips_directory = f"{current_working_directory}\\sample_trips"
    list_of_trips = os.listdir(trips_directory)

    for trip in list_of_trips:
        list_data_locations = []
        dict_images[trip] = {}
        label_text_to_location_directory[trip] = {}
        dict_sub_locations_df[trip] = {}

        # Read data file
        current_trip_directory = f"{trips_directory}\\{trip}"
        current_trip_data_file = f"{current_trip_directory}\\trip_data.json"
        current_trip_data = json_to_dict(current_trip_data_file)
        list_data_trips.append(current_trip_data)

        # List of locations of that trip
        list_of_locations = os.listdir(current_trip_directory)
        list_of_locations.remove("trip_data.json")

        for location in list_of_locations:

            # Read data file
            current_location_directory = f"{current_trip_directory}\\{location}"
            current_location_data_file = f"{current_location_directory}\\location_data.json"
            current_location_data = json_to_dict(current_location_data_file)
            list_data_locations.append(current_location_data)

            if "has_sub_locations" in current_location_data.keys():
                list_data_sub_locations = []
                dict_images[trip][location] = {}
                label_text_to_location_directory[trip][location] = {}

                # List of sub-locations of that trip
                list_of_sub_locations = os.listdir(current_location_directory)
                list_of_sub_locations.remove("location_data.json")

                label_text_to_location_directory[trip][current_location_data["location"]] = location

                for sub_location in list_of_sub_locations:

                    # Read data file
                    current_sub_location_directory = f"{current_location_directory}\\{sub_location}"
                    current_sub_location_data_file = f"{current_sub_location_directory}\\location_data.json"
                    current_sub_location_data = json_to_dict(current_sub_location_data_file)
                    list_data_sub_locations.append(current_sub_location_data)

                    label_text_to_location_directory[trip][location][current_sub_location_data["location"]] = sub_location

                    # List of images of that trip
                    list_of_images = os.listdir(current_sub_location_directory)
                    list_of_images.remove("location_data.json")
                    dict_images[trip][location][sub_location] = list_of_images

                dict_sub_locations_df[trip][location] = transform_locations_df(pd.DataFrame(list_data_sub_locations), current_trip_data["rgb"], current_location_data["zoom"])
            else:
                label_text_to_location_directory[trip][current_location_data["location"]] = location
                # List of images of that trip
                list_of_images = os.listdir(current_location_directory)
                list_of_images.remove("location_data.json")
                dict_images[trip][location] = list_of_images

        # df of the locations in each trip
        dict_locations_df[trip] = transform_locations_df(pd.DataFrame(list_data_locations), current_trip_data["rgb"])

    df_trips = transform_trips_df(pd.DataFrame(list_data_trips))
    set_persons = set(df_trips["members"].sum())

    label_text_to_trip_directory = {df_trips.iloc[i]["label_text"]:list_of_trips[i]  for i in range(len(df_trips))}

    # print("All trips:")
    # print(df_trips)
    # print("\nDict of images")
    # print(dict_images)
    # print("\nEach trip")
    # print(dict_locations_df)
    # print("\nPersons:")
    # print(set_persons)
    # print(dict_images)
    # print(dict_sub_locations_df)

    return df_trips, dict_images, dict_locations_df, dict_sub_locations_df, set_persons, label_text_to_trip_directory, label_text_to_location_directory


if __name__ == "__main__":
    generate_trips_df()
