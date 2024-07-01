from pymongo import MongoClient


url = "mongodb+srv://lesliesawadogo2856:passer@apicluster.zdcfaov.mongodb.net/?retryWrites=true&w=majority&appName=APICluster"


client = MongoClient(url)

db = client['API_Database']
mycollection = db['API_collection']