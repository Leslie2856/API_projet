from pydantic import BaseModel

class Country(BaseModel):         # definition de notre model de donnée
    country: str
    Region: str
    Happiness_Rank: int
    Happiness_Score: float
    Standard_Error: float
    Economy_GDP_per_Capita: float
    Family: float
    Health_Life_Expectancy: float
    Freedom: float
    Trust_Government_Corruption: float
    Generosity: float
    Dystopia_Residual: float
