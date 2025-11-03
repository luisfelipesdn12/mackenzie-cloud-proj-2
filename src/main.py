import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Load environment variables
load_dotenv()

# Recipe Model
class Recipe(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str | None = Field(default=None)
    ingredients: str
    instructions: str
    prep_time_minutes: int | None = Field(default=None)
    cook_time_minutes: int | None = Field(default=None)
    servings: int | None = Field(default=None)


# Recipe Update Model (for partial updates)
class RecipeUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    ingredients: str | None = None
    instructions: str | None = None
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    servings: int | None = None


# Database configuration from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Create MySQL connection string
mysql_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
engine = create_engine(mysql_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/recipes/", response_model=Recipe)
def create_recipe(recipe: Recipe, session: SessionDep) -> Recipe:
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


@app.get("/recipes/", response_model=list[Recipe])
def read_recipes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Recipe]:
    recipes = session.exec(select(Recipe).offset(offset).limit(limit)).all()
    return recipes


@app.get("/recipes/{recipe_id}", response_model=Recipe)
def read_recipe(recipe_id: int, session: SessionDep) -> Recipe:
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@app.put("/recipes/{recipe_id}", response_model=Recipe)
def update_recipe(recipe_id: int, recipe_update: RecipeUpdate, session: SessionDep) -> Recipe:
    db_recipe = session.get(Recipe, recipe_id)
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    recipe_data = recipe_update.model_dump(exclude_unset=True)
    for key, value in recipe_data.items():
        setattr(db_recipe, key, value)
    
    session.add(db_recipe)
    session.commit()
    session.refresh(db_recipe)
    return db_recipe


@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int, session: SessionDep):
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    session.delete(recipe)
    session.commit()
    return {"ok": True}


@app.get("/")
def read_root():
    return {"message": "Recipe CRUD API", "endpoints": {
        "create": "POST /recipes/",
        "read_all": "GET /recipes/",
        "read_one": "GET /recipes/{recipe_id}",
        "update": "PUT /recipes/{recipe_id}",
        "delete": "DELETE /recipes/{recipe_id}"
    }}
