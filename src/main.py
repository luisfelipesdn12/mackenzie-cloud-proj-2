import os
from pathlib import Path
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


# Recipe Create Model (for creating new recipes - without id)
class RecipeCreate(SQLModel):
    name: str
    description: Optional[str] = None
    ingredients: str
    instructions: str
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    servings: Optional[int] = None


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
    # Fix PostgreSQL sequence if it's out of sync
    fix_sequence()


def fix_sequence():
    """Sincroniza a sequência do PostgreSQL com o máximo ID existente"""
    try:
        with Session(engine) as session:
            # Verifica se a tabela existe
            table_exists = session.exec(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'recipe')")
            ).first()
            
            if not table_exists:
                return
            
            # Busca o maior ID na tabela
            result = session.exec(text("SELECT COALESCE(MAX(id), 0) FROM recipe")).first()
            max_id = result if result is not None else 0
            
            # Verifica se a sequência existe e atualiza
            seq_exists = session.exec(
                text("SELECT EXISTS (SELECT FROM pg_sequences WHERE sequencename = 'recipe_id_seq')")
            ).first()
            
            if seq_exists:
                # Atualiza a sequência para o próximo valor disponível
                session.exec(text(f"SELECT setval('recipe_id_seq', {max_id}, true)"))
                session.commit()
                print(f"PostgreSQL sequence synchronized to {max_id}")
    except Exception as e:
        print(f"Error fixing sequence (this is usually OK if table is new): {e}")


def is_table_empty() -> bool:
    """Verifica se a tabela recipe está vazia"""
    try:
        with Session(engine) as session:
            # Tenta buscar o primeiro registro
            result = session.exec(select(Recipe).limit(1)).first()
            return result is None
    except Exception as e:
        # Se a tabela não existir ainda, considera como vazia
        print(f"Error checking if table is empty: {e}")
        return True


def initialize_sample_data():
    """Executa o script initialize.sql para popular dados iniciais, apenas se a tabela estiver vazia"""
    if not is_table_empty():
        print("Recipe table is not empty, skipping data initialization")
        return
    
    sql_file = Path(__file__).parent / "initialize.sql"
    
    if not sql_file.exists():
        print("initialize.sql not found, skipping data initialization")
        return
    
    try:
        with engine.begin() as conn:
            # Lê o arquivo SQL
            sql_content = sql_file.read_text(encoding='utf-8')
            
            # Remove comentários (linhas que começam com --)
            lines = []
            for line in sql_content.split('\n'):
                stripped = line.strip()
                if stripped and not stripped.startswith('--'):
                    lines.append(line)
            
            # Junta as linhas e divide por ponto e vírgula
            full_sql = '\n'.join(lines)
            # Remove o último ponto e vírgula se existir (pode estar no final do arquivo)
            full_sql = full_sql.rstrip(';').strip()
            
            if full_sql:
                # Executa o comando SQL completo
                # O context manager engine.begin() faz commit automaticamente
                conn.execute(text(full_sql))
                print("Sample data initialized successfully")
            else:
                print("No SQL commands found in initialize.sql")
                
    except Exception as e:
        print(f"Error initializing sample data: {e}")
        # Não levanta exceção para não impedir o startup da aplicação


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.on_event("startup")
def on_startup():
    ensure_database_exists()
    create_db_and_tables()
    initialize_sample_data()


@app.post("/recipes/", response_model=Recipe)
def create_recipe(recipe: RecipeCreate, session: SessionDep) -> Recipe:
    # Convert RecipeCreate to Recipe (id will be auto-generated by database)
    recipe_data = recipe.model_dump()
    # Explicitly set id to None to ensure database auto-generates it
    recipe_data['id'] = None
    db_recipe = Recipe(**recipe_data)
    session.add(db_recipe)
    session.commit()
    session.refresh(db_recipe)
    return db_recipe


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
