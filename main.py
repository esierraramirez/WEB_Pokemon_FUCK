from os.path import exists

from fastapi import FastAPI, HTTPException
from model import PokemonBase, PokemonResponse, PokemonUpdate
import csv
import os

app = FastAPI()

CSV_FILE = "pokedex.csv"

def save_csv(pokemon:PokemonBase):
    pokedex_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a+", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=pokemon.model_dump().keys())
        if not pokedex_exists:
            writer.writeheader()
        writer.writerow(pokemon.model_dump())

##pokedex = []

@app.post("/pokemon")
async def catch_pokemon(pokemon: PokemonBase):
    ##pokedex.append(pokemon)
    save_csv(pokemon)
    return {"Pokemon capturado": PokemonResponse(**pokemon.model_dump())}


@app.get("/pokemon", response_model=list[PokemonResponse])
async def show_all_pokemon():
    pokemons=[]
    with open(CSV_FILE, newline="") as file:
        reader = csv.DictReader(file)
        for p in reader:
            pokemons.append(PokemonBase(**p))
    return pokemons


@app.get("/pokemon/{id}", response_model=PokemonResponse)
async def show_pokemon(id: int):
    with open(CSV_FILE, newline="") as file:
        reader = csv.DictReader(file)
        for p in reader:
            if int(p["id"]) == id:
                return PokemonResponse(**p)
    raise HTTPException(status_code=404, detail="Pokemon no capturado aún")


@app.patch("/pokemon/{id}", response_model=PokemonResponse)
async def update_pokemon(id: int, pokemon_update: PokemonUpdate):
    if not os.path.exists(CSV_FILE):
        raise HTTPException(status_code=404, detail="Pokedex vacía") #Comprobacion de que el archivo existe, si no existe, se asume que la pokedex esta vacia

    pokemons = []
    updated_pokemon = None

    with open(CSV_FILE, newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames or ["id", "name", "tipo", "level"]
        for row in reader:
            if int(row["id"]) == id:
                data = row.copy()
                data["level"] = str(pokemon_update.level)
                row = data
                updated_pokemon = row
            pokemons.append(row)

    if updated_pokemon is None:
        raise HTTPException(status_code=404, detail="Pokemon no capturado aún")

    with open(CSV_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(pokemons)

    return PokemonResponse(**updated_pokemon)

@app.get("/")
async def root():
    return {"message": "Hello in Pycharm"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
