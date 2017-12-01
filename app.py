import pandas
import math
from scipy.spatial import distance
import csv
from flask import Flask, json
from flask_cors import CORS

INPUT_CITY = 'Banning'
INPUT_CUISINE = 'American'

def ceuclidean_distance(row):
    inner_value = 0
    for k in cdistance_columns:
        inner_value += (row[k] - selected_city[k]) ** 2
    return math.sqrt(inner_value)


def find_similar_cities(cuisine):
    INPUT_CUISINE = cuisine
    
    with open("CA_City_Data.csv", 'r') as csvfile:
        city = pandas.read_csv(csvfile)

    restaurants = csv.DictReader(open('CA_Restaurants.csv', 'r'))
    restaurants_list = []
    for line in restaurants:
        restaurants_list.append(line)

    # Select the Input City from our dataset
    selected_city = city[city["City"] == INPUT_CITY].iloc[0]

    # Choose only the numeric columns (we'll use these to compute euclidean distance)
    cdistance_columns = ['Population', 'Area in square miles - Land area']

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

    similar_cities_populations = []
    similar_cities = []
    restaurant_counts_for_similar_cities = []
    rpc_values = []
    similar_cities_and_restaurant_data = []

    for i in index_list:
        csecond_smallest = cdistance_frame.iloc[i]["idx"]
        city_name = city.loc[int(csecond_smallest)]["City"]
        similar_cities_populations.append((city[city["City"] == city_name].iloc[0])['Population'])
        similar_cities.append(city_name)


    for city in similar_cities:
        n = 0  # number of restaurants
        for restaurant in restaurants_list:
            if restaurant.get('City') == city and restaurant.get('Cuisine') == INPUT_CUISINE :
                n += 1
        restaurant_counts_for_similar_cities.append(n)

    for index in range(len(similar_cities)):
        newDictObj = {}
        newDictObj['City'] = similar_cities[index]
        newDictObj['Population'] = similar_cities_populations[index]
        newDictObj['no_of_restaurants'] = restaurant_counts_for_similar_cities[index]
        newDictObj['RPC'] = (restaurant_counts_for_similar_cities[index])/(similar_cities_populations[index])
        newDictObj['Opp_Score'] = 0
        similar_cities_and_restaurant_data.append(newDictObj)

    # Calculate meu
    sum_of_rpc = 0
    for data in similar_cities_and_restaurant_data:
        sum_of_rpc += data['RPC']

    meu = sum_of_rpc/len(similar_cities_and_restaurant_data)


    # Calculate Opp_Score for each city
    for data in similar_cities_and_restaurant_data:
        Opp_Score = (meu - data['RPC'])/meu
        data['Opp_Score'] = Opp_Score

    return(sorted(similar_cities_and_restaurant_data, key=lambda k: k['Opp_Score'], reverse=True))
    # print(sorted(similar_cities_and_restaurant_data, key=lambda k: k['Opp_Score'], reverse=True))



app = Flask(__name__)
CORS(app)

@app.route("/")
def main():
    return 'OK TATA'

@app.route("/fetch-cities/<cuisine>")
def returnMainFile(cuisine):
    print(cuisine)
    list_of_cities = find_similar_cities(cuisine)
    return json.dumps(list_of_cities,encoding='UTF-8',default=str)

if __name__ == "__main__":
    app.run()
