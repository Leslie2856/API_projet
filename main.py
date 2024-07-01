from fastapi import FastAPI
from routes.country_api import country_api

app = FastAPI()


app.include_router(country_api)


#if __name__ == "__main__":
 #   import uvicorn
  #  uvicorn.run(app, host="127.0.0.1", port=8000)