import pandas
import math
from scipy.spatial import distance

with open("CA_City_Data.csv", 'r') as csvfile:
    city = pandas.read_csv(csvfile)

INPUT_CITY = 'Banning'

# Select the Input City from our dataset
selected_city = city[city["City"] == INPUT_CITY].iloc[0]

# Choose only the numeric columns (we'll use these to compute euclidean distance)
cdistance_columns = ['Population', 'Area in square miles - Land area']

def ceuclidean_distance(row):
    inner_value = 0
    for k in cdistance_columns:
        inner_value += (row[k] - selected_city[k]) ** 2
    return math.sqrt(inner_value)

# Select only the numeric columns from the City dataset
city_numeric = city[cdistance_columns]

# Normalize all of the numeric columns
city_normalized = (city_numeric - city_numeric.mean()) / city_numeric.std()

# Fill in NA values in city_normalized
city_normalized.fillna(0, inplace=True)

# Find the normalized vector for the input city.
input_city_normalized = city_normalized[city["City"] == INPUT_CITY]

# Find the distance between the input city and all other cities.
ceuclidean_distances = city_normalized.apply(lambda row: distance.euclidean(row, input_city_normalized), axis=1)

# Create a new dataframe with distances.
cdistance_frame = pandas.DataFrame(data={"dist": ceuclidean_distances, "idx": ceuclidean_distances.index})
cdistance_frame.sort_values("dist", inplace=True)


# Find the most similar city to input (the lowest distance to the input is the input itself, the second smallest is the most similar non-input city)
csecond_smallest = cdistance_frame.iloc[1]["idx"]

index_list = [1, 2, 3, 4, 5]

for i in index_list:
    csecond_smallest = cdistance_frame.iloc[i]["idx"]
    print(city.loc[int(csecond_smallest)]["City"])
