"""
database/db.py
Módulo de persistência em banco de dados — SQLAlchemy + SQLite
Funcionalidade avançada: Persistência em banco
"""

import os
import pandas as pd
from sqlalchemy import (
    create_engine, Column, Integer, Float, String, text
)
from sqlalchemy.orm import declarative_base, Session

# ── Configuração ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "desemprego.db")
CSV_PATH = os.path.join(BASE_DIR, "..", "dados", "simulacao_desemprego_brasil.csv")

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Base   = declarative_base()


# ── Modelo ORM ────────────────────────────────────────────────────────────────
class IndicadorDesemprego(Base):
    __tablename__ = "indicadores"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    ano                 = Column(Integer, nullable=False)
    trimestre           = Column(Integer, nullable=False)
    data                = Column(String(10))
    regiao              = Column(String(20))
    uf                  = Column(String(2))
    populacao_ativa     = Column(Integer)
    empregados          = Column(Integer)
    desempregados       = Column(Integer)
    taxa_desemprego     = Column(Float)
    renda_media         = Column(Float)
    setor_predominante  = Column(String(30))
    vagas_formais       = Column(Integer)
    inflacao            = Column(Float)
    nivel_risco         = Column(String(15))


# ── Funções públicas ──────────────────────────────────────────────────────────
def inicializar_banco() -> None:
    """Cria as tabelas e popula o banco a partir do CSV (se ainda vazio)."""
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        total = session.execute(
            text("SELECT COUNT(*) FROM indicadores")
        ).scalar()

    if total == 0:
        df = pd.read_csv(CSV_PATH)
        df.to_sql("indicadores", con=engine, if_exists="append", index=False)
        print(f"[DB] {len(df)} registros inseridos.")
    else:
        print(f"[DB] Banco já possui {total} registros.")


def carregar_dataframe() -> pd.DataFrame:
    """Retorna todos os registros como DataFrame."""
    inicializar_banco()
    return pd.read_sql("SELECT * FROM indicadores", con=engine)


def agregar_por_ano() -> pd.DataFrame:
    sql = """
        SELECT ano,
               ROUND(AVG(taxa_desemprego), 2) AS taxa_media,
               ROUND(AVG(renda_media),     2) AS renda_media,
               SUM(desempregados)              AS total_desempregados,
               SUM(vagas_formais)              AS total_vagas,
               ROUND(AVG(inflacao),         2) AS inflacao_media
        FROM indicadores
        GROUP BY ano
        ORDER BY ano
    """
    return pd.read_sql(sql, con=engine)


def agregar_por_regiao() -> pd.DataFrame:
    sql = """
        SELECT regiao,
               ROUND(AVG(taxa_desemprego), 2) AS taxa_media,
               ROUND(AVG(renda_media),     2) AS renda_media,
               SUM(desempregados)              AS total_desempregados,
               SUM(vagas_formais)              AS total_vagas
        FROM indicadores
        GROUP BY regiao
        ORDER BY taxa_media DESC
    """
    return pd.read_sql(sql, con=engine)


def agregar_por_uf() -> pd.DataFrame:
    sql = """
        SELECT uf, regiao,
               ROUND(AVG(taxa_desemprego), 2) AS taxa_media,
               ROUND(AVG(renda_media),     2) AS renda_media,
               SUM(desempregados)              AS total_desempregados,
               SUM(vagas_formais)              AS total_vagas
        FROM indicadores
        GROUP BY uf, regiao
        ORDER BY taxa_media DESC
    """
    return pd.read_sql(sql, con=engine)


def agregar_por_setor() -> pd.DataFrame:
    sql = """
        SELECT setor_predominante,
               ROUND(AVG(taxa_desemprego), 2) AS taxa_media,
               ROUND(AVG(renda_media),     2) AS renda_media,
               COUNT(*) AS registros
        FROM indicadores
        GROUP BY setor_predominante
        ORDER BY taxa_media DESC
    """
    return pd.read_sql(sql, con=engine)


def distribuicao_risco() -> pd.DataFrame:
    sql = """
        SELECT nivel_risco,
               COUNT(*) AS quantidade,
               ROUND(AVG(taxa_desemprego), 2) AS taxa_media
        FROM indicadores
        GROUP BY nivel_risco
        ORDER BY taxa_media DESC
    """
    return pd.read_sql(sql, con=engine)
