import os
from typing import Annotated, Optional, List

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlalchemy import text

# Load environment variables
load_dotenv()

# Recipe Model
class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    ingredients: str
    instructions: str
    prep_time_minutes: Optional[int] = Field(default=None)
    cook_time_minutes: Optional[int] = Field(default=None)
    servings: Optional[int] = Field(default=None)


# Recipe Update Model (for partial updates)
class RecipeUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[str] = None
    instructions: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    servings: Optional[int] = None


# Database configuration from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Variável global para o engine (será criado após garantir que o banco existe)
engine = None


def ensure_database_exists():
    """Cria o banco de dados se ele não existir"""
    # Conecta ao banco padrão 'postgres' para criar o banco se necessário
    postgres_admin_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
    admin_engine = create_engine(postgres_admin_url, isolation_level="AUTOCOMMIT")
    
    try:
        with admin_engine.connect() as conn:
            # Verifica se o banco existe
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
            )
            exists = result.fetchone() is not None
            
            if not exists:
                # Cria o banco de dados
                conn.execute(text(f'CREATE DATABASE "{DB_NAME}"'))
                print(f"Database '{DB_NAME}' created successfully")
            else:
                print(f"Database '{DB_NAME}' already exists")
    except Exception as e:
        print(f"Error checking/creating database: {e}")
        # Se falhar, tenta continuar (pode ser que o banco já exista)
    finally:
        admin_engine.dispose()
    
    # Agora cria o engine para o banco de dados
    global engine
    postgres_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(postgres_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.on_event("startup")
def on_startup():
    ensure_database_exists()
    create_db_and_tables()


@app.post("/recipes/", response_model=Recipe)
def create_recipe(recipe: Recipe, session: SessionDep) -> Recipe:
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


@app.get("/recipes/", response_model=List[Recipe])
def read_recipes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> List[Recipe]:
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
