import pandas as pd
from bson.objectid import ObjectId


# Fonction pour transformer un document en dictionnaire
def countryEntity(item) -> dict:
    return {
        "id": str(item["_id"]),
        "country": item["country"],
        "Region": item["Region"],
        "Happiness_Rank": item["Happiness_Rank"],
        "Happiness_Score": item["Happiness_Score"],
        "Standard_Error": item["Standard_Error"],
        "Economy_GDP_per_Capita": item["Economy_GDP_per_Capita"],
        "Family": item["Family"],
        "Health_Life_Expectancy": item["Health_Life_Expectancy"],
        "Freedom": item["Freedom"],
        "Trust_Government_Corruption": item["Trust_Government_Corruption"],
        "Generosity": item["Generosity"],
        "Dystopia_Residual": item["Dystopia_Residual"]
    }
# Fonction pour transformer une liste de documents en liste de dictionnaires
def countriesEntity(entity) -> list:
    return [countryEntity(item) for item in entity]

# Fonction pour sérialiser un dictionnaire
def serializeDict(x) -> dict:
    return {**{i: str(x[i]) for i in x if i == '_id'}, **{i: x[i] for i in x if i != '_id'}}

# Fonction pour sérialiser une liste de dictionnaires
def serializeList(entity) -> list:
    return [serializeDict(x) for x in entity]


# Modifier les données d'un pays
def updateCountry(id, newCountryData, mycollection):
    for key, value in newCountryData.items():
        if key in ["country", "Region", "Happiness_Rank", "Happiness_Score", "Standard_Error",
                   "Economy_GDP_per_Capita", "Family", "Health_Life_Expectancy", "Freedom",
                   "Trust_Government_Corruption", "Generosity", "Dystopia_Residual"] and value != "":
            upt_co = mycollection.find_one_and_update({"_id": ObjectId(id)}, {"$set": {str(key): value}})
    return upt_co
    
    
# Fonction pour récupérer les pays dont le score de bonheur est compris entre h1 et h2
def getCountriesHappinessH1H2(h1, h2, mycollection):
    h1 = float(h1)
    h2 = float(h2)
    countries = mycollection.find({"Happiness_Score": {"$gte": h1, "$lte": h2}})
    data = []
    for country in countries:
        country_data = {
            "Country": country["country"],
            "Happiness_Score": country.get("Happiness_Score")
        }
        data.append(country_data)
    df = pd.DataFrame(data)
    return df

# Obtenir la moyenne des scores de bonheur des pays
def getWorldAverageHappiness(mycollection):
    worldAverageHappiness = mycollection.aggregate([
        {"$group": {
            "_id": "World_Average_Happiness",
            "avgHappinessScore": {"$avg": "$Happiness_Score"}
        }}
    ])
    data = []
    for country in worldAverageHappiness:
        country_data = {
            "avgHappinessScore": country.get("avgHappinessScore")
        }
        data.append(country_data)
    df = pd.DataFrame(data)
    return df

# Récupérer toutes les données de la collection
def getAllCountries(mycollection):
    countries = mycollection.find({})
    colonnes_a_convertir = ["Happiness_Rank", "Happiness_Score", "Standard_Error", "Economy_GDP_per_Capita",
                            "Family", "Health_Life_Expectancy", "Freedom", "Trust_Government_Corruption",
                            "Generosity", "Dystopia_Residual"]
    df = pd.DataFrame(serializeList(countries))
    df[colonnes_a_convertir] = df[colonnes_a_convertir].astype(str)
    return df

# Récuperer une ligne spécifique de la collection en fonction du nom du pays
def getCountry(countryName, mycollection):
    # On récupère le pays
    country = mycollection.find_one({"country": countryName}, {"_id": 0})
    if country:
        # On met les données dans un dataframe
        df = pd.DataFrame(serializeDict(country), index=[0])
        return df
    else:
        return None

# Trouver le pays avec le score de bonheur le plus bas
def getLeastHappyCountry(mycollection):
    country = mycollection.find_one(sort=[("Happiness_Score", 1)])
    data = []
    if country:
        country_data = {
            "Country": country["country"],
            "Happiness_Score": country.get("Happiness_Score")
        }
        data.append(country_data)
    df = pd.DataFrame(data)
    return df

# Trouver le pays avec le score de bonheur le plus élevé
def getMostHappyCountry(mycollection):
    country = mycollection.find_one(sort=[("Happiness_Score", -1)])
    data = []
    if country:
        country_data = {
            "Country": country["country"],
            "Happiness_Score": country.get("Happiness_Score")
        }
        data.append(country_data)
    df = pd.DataFrame(data)
    return df

# Fonction pour recevoir n'importe quelle requête d'agrégation et retourner le résultat dans un dataframe
def getAggregationRequest(aggregation, mycollection):
    countries = mycollection.aggregate(aggregation)
    df = pd.DataFrame(serializeList(countries))
    return df

# Fonction pour recevoir n'importe quelle requête "find" et retourner le résultat dans un dataframe
def getFindRequest(query, mycollection):
    if len(query) == 1:
        countries = mycollection.find(query[0])
    elif len(query) == 2:
        countries = mycollection.find(query[0], query[1])   
    df = pd.DataFrame(serializeList(countries))
    return df

# Fonction pour recevoir n'importe quelle requête 'distinct' et retourner le résultat dans un dataframe
def getDistinctRequest(distinct, mycollection):
    if len(distinct) == 1:
        countries = mycollection.distinct(distinct[0])
    elif len(distinct) == 2:
        countries = mycollection.distinct(distinct[0], distinct[1])
    elif len(distinct) == 3:
        countries = mycollection.distinct(distinct[0], distinct[1], distinct[2])
    df = pd.DataFrame(countries)
    return df

# Fonction pour trouver le nombre de pays dont le score de bonheur est supérieur à la moyenne
def getNbCountriesHappinessSupAvg(mycollection):
    avg = mycollection.aggregate([
        {"$group": {
            "_id": "World_Average_Happiness",
            "avg": {"$avg": "$Happiness_Score"}
        }}
    ])
    avg = list(avg)
    avg = avg[0]["avg"]
    nbCountries = mycollection.count_documents({"Happiness_Score": {"$gte": avg}})
    return nbCountries, avg

# Fonction pour trouver le nombre de pays dont le score de bonheur est inférieur à la moyenne
def getNbCountriesHappinessInfAvg(mycollection):
    avg = mycollection.aggregate([
        {"$group": {
            "_id": "World_Average_Happiness",
            "avg": {"$avg": "$Happiness_Score"}
        }}
    ])
    avg = list(avg)
    avg = avg[0]["avg"]
    nbCountries = mycollection.count_documents({"Happiness_Score": {"$lte": avg}})
    return nbCountries, avg