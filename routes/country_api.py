from fastapi import APIRouter, HTTPException
import json
from fastapi.responses import JSONResponse
from models.country import Country
from config.db import mycollection
from typing import List
from bson.objectid import ObjectId
from starlette import responses as _responses
from schemas.country_schemas import *


country_api = APIRouter()

######################################## POST ##########################################

# Page d'acceuille
@country_api.get("/", tags=["Countries"])
async def home():
    """
    Returns:
    On redirige vers /redoc pour voir la documentation de l'API.
    redirect: Une redirection vers /redoc.
    """
    return _responses.RedirectResponse(url='/redoc') 


# Documentation de l'endpoint insert_country
@country_api.post("/insert_country/", response_model=dict, tags=["Countries"])
async def insert_country(country: Country):
    """
    Insère un nouveau document de pays dans la collection MongoDB.

    Parameters:
    - country (Country): Un objet Country contenant les informations du pays à insérer.

    Returns:
    dict: Un dictionnaire contenant un message de confirmation.
    """
    country_dict = dict(country)
    mycollection.insert_one(country_dict)
    
    return {"message": "Country inserted successfully"}



######################################## PUT ##########################################

# Documentation de l'endpoint update_country
@country_api.put("/update_country/{id}", response_model=dict, tags=["Countries"])
async def update_country(id: str, country: Country):
    """
    Met à jour les informations d'un pays dans la collection MongoDB.

    Parameters:
    - id (str): L'ID du document de pays à mettre à jour.
    - country (Country): Un objet Country contenant les nouvelles informations du pays.

    Returns:
    dict: Un dictionnaire contenant un message de confirmation.
    """
    country_dict = dict(country)
    updated_country = updateCountry(id, country_dict, mycollection)
    if updated_country is not None:
        return {"message": "Country updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Country not found")


######################################## DELETE ##########################################

# Documentation de l'endpoint delete_country
@country_api.delete("/delete_country/{id}", response_model=dict, tags=["Countries"])
async def delete_country(id: str):
    """
    Supprime un document de pays de la collection MongoDB.

    Parameters:
    - id (str): L'ID du document de pays à supprimer.

    Returns:
    dict: Un dictionnaire contenant un message de confirmation.
    """
    deleted_country = mycollection.delete_one({"_id": ObjectId(id)})
    if deleted_country.deleted_count == 1:
        return {"message": "Country deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Country not found")
    


######################################## GET ##########################################

# Documentation de l'endpoint get_countries
@country_api.get("/countries_info/", response_model=dict, tags=["Countries"])
async def get_countries():
    """
    Récupère toutes les informations des pays depuis la collection MongoDB et les renvoie au format JSON.

    Returns:
    JSONResponse: Un objet JSONResponse contenant les données des pays au format JSON.
    """
    df = getAllCountries(mycollection)
    return JSONResponse(content=df.to_dict(orient="records"))

# Endpoint pour récupérer les informations d'un pays par son nom
@country_api.get("/country/{name}", response_model=dict, tags=["Countries"])
async def get_country_by_name(name: str):
    """
    Récupère les informations d'un pays depuis la collection MongoDB par son nom.

    Parameters:
    - name (str): Le nom du pays à récupérer.

    Returns:
    dict: Un dictionnaire représentant les informations du pays.
    """
    df = getCountry(name, mycollection)
    if df is not None:
        return df.to_dict(orient="records")[0]
    else:
        raise HTTPException(status_code=404, detail="Country not found")


# Documentation de l'endpoint get_countries_search

@country_api.get("/countries_search/{name}", response_model=List[Country], tags=["Countries"])
async def search_countries_by_name(name: str):
    """
    Recherche des pays dont le nom correspond partiellement au nom fourni.

    Parameters:
    - name (str): Le nom partiel à rechercher.

    Returns:
    List[Country]: Une liste d'objets Country correspondant aux critères de recherche.
    """
    countries = list(mycollection.find({"country": {"$regex": name, "$options": "i"}}))
    return countries

# Documentation de l'endpoint get_countries_by_region
@country_api.get("/countries_by_region/{region}", response_model=List[Country], tags=["Countries"])
async def get_countries_by_region(region: str):
    """
    Récupère des pays appartenant à une région spécifique.

    Parameters:
    - region (str): Le nom de la région à rechercher.

    Returns:
    List[Country]: Une liste d'objets Country correspondant à la région spécifiée.
    """
    countries = list(mycollection.find({"Region": region}))
    return countries


# Documentation de l'endpoint get_happiness_scores_stats
@country_api.get("/happiness_scores_stats/", response_model=dict, tags=["Countries"])
async def get_happiness_scores_stats():
    """
    Calcule des statistiques sur les scores de bonheur des pays.

    Returns:
    dict: Un dictionnaire contenant les statistiques calculées (moyenne, médiane, écart-type, etc.).
    """
    pipeline = [
        {"$group": {
            "_id": None,
            "avgHappinessScore": {"$avg": "$Happiness_Score"},
            "minHappinessScore": {"$min": "$Happiness_Score"},
            "maxHappinessScore": {"$max": "$Happiness_Score"},
            "stdDevHappinessScore": {"$stdDevPop": "$Happiness_Score"}
        }}
    ]
    stats = list(mycollection.aggregate(pipeline))
    return stats[0] if stats else {}


# Documentation de l'endpoint get_countries_ranked_by_happiness
@country_api.get("/countries_ranked_by_happiness/", response_model=List[Country], tags=["Countries"])
async def get_countries_ranked_by_happiness():
    """
    Récupère les pays classés par leur score de bonheur dans l'ordre décroissant.

    Returns:
    List[Country]: Une liste d'objets Country classés par score de bonheur décroissant.
    """
    countries = list(mycollection.find().sort("Happiness_Score", -1))
    return countries


# Documentation de l'endpoint get_countries_by_trust
@country_api.get("/countries_by_trust/{threshold}", response_model=List[Country], tags=["Countries"])
async def get_countries_by_trust(threshold: float):
    """
    Récupère les pays avec un indice de confiance gouvernementale supérieur à une valeur donnée.

    Parameters:
    - threshold (float): La valeur de seuil pour l'indice de confiance gouvernementale.

    Returns:
    List[Country]: Une liste d'objets Country avec un indice de confiance gouvernementale supérieur au seuil spécifié.
    """
    countries = list(mycollection.find({"Trust_Government_Corruption": {"$gt": threshold}}))
    return countries


# Endpoint pour récupérer les pays avec un score de bonheur supérieur à un seuil spécifié
@country_api.get("/countries_happiness_above/{threshold}", response_model=List[Country], tags=["Countries"])
async def get_countries_happiness_above(threshold: float):
    """
    Récupère les pays avec un score de bonheur supérieur à un seuil donné.

    Parameters:
    - threshold (float): Le seuil de score de bonheur à comparer.

    Returns:
    List[Country]: Une liste de pays avec un score de bonheur supérieur au seuil spécifié.
    """
    countries = list(mycollection.find({"Happiness_Score": {"$gt": threshold}}))
    return countries

# Endpoint pour récupérer les pays dont le score de bonheur est compris entre h1 et h2
@country_api.get("/countries_happiness/{h1}/{h2}", response_model=List[dict], tags=["Countries"])
async def get_countries_by_happiness(h1: float, h2: float):
    """
    Récupère les pays dont le score de bonheur est compris entre deux valeurs spécifiques.

    Parameters:
    - h1 (float): Valeur inférieure du score de bonheur.
    - h2 (float): Valeur supérieure du score de bonheur.

    Returns:
    List[dict]: Une liste de dictionnaires représentant les pays avec le score de bonheur dans la plage spécifiée.
    """
    df = getCountriesHappinessH1H2(h1, h2, mycollection)
    return df.to_dict(orient="records")

# Endpoint pour récupérer la moyenne mondiale des scores de bonheur
@country_api.get("/world_average_happiness/", response_model=dict, tags=["Countries"])
async def get_world_average_happiness():
    """
    Calcule la moyenne mondiale des scores de bonheur des pays.

    Returns:
    dict: Un dictionnaire représentant la moyenne mondiale des scores de bonheur.
    """
    df = getWorldAverageHappiness(mycollection)
    if not df.empty:
        return df.to_dict(orient="records")[0]
    else:
        return {}

# Endpoint pour le pays avec le score de bonheur le plus bas:
@country_api.get("/least_happy_country", response_model=List[Country], tags=["Countries"])
async def get_least_happy_country():
    """
    Récupère le pays avec le score de bonheur le plus bas.

    Returns:
    List[Country]: Une liste contenant le pays avec le score de bonheur le plus bas.
    """
    df = getLeastHappyCountry(mycollection)
    return df.to_dict(orient="records")

#Endpoint pour le pays avec le score de bonheur le plus élevé
@country_api.get("/most_happy_country", response_model=List[Country], tags=["Countries"])
async def get_most_happy_country():
    """
    Récupère le pays avec le score de bonheur le plus élevé.

    Returns:
    List[Country]: Une liste contenant le pays avec le score de bonheur le plus élevé.
    """
    df = getMostHappyCountry(mycollection)
    return df.to_dict(orient="records")


#Endpoint pour le nombre de pays dont le score de bonheur est supérieur à la moyenne:
@country_api.get("/countries_happiness_above_avg", response_model=dict, tags=["Countries"])
async def get_countries_happiness_above_avg():
    """
    Récupère le nombre de pays dont le score de bonheur est supérieur à la moyenne mondiale.

    Returns:
    dict: Un dictionnaire contenant le nombre de pays et la moyenne mondiale.
    """
    nb_countries, avg = getNbCountriesHappinessSupAvg(mycollection)
    return {"nbCountries": nb_countries, "avgHappinessScore": avg}


#Endpoint pour le nombre de pays dont le score de bonheur est inférieur à la moyenne:
@country_api.get("/countries_happiness_below_avg", response_model=dict, tags=["Countries"])
async def get_countries_happiness_below_avg():
    """
    Récupère le nombre de pays dont le score de bonheur est inférieur à la moyenne mondiale.

    Returns:
    dict: Un dictionnaire contenant le nombre de pays et la moyenne mondiale.
    """
    nb_countries, avg = getNbCountriesHappinessInfAvg(mycollection)
    return {"nbCountries": nb_countries, "avgHappinessScore": avg}
