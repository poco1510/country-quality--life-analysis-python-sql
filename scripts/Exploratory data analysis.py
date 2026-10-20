from pathlib import Path
import logging
import pandas as pd
import sqlite3

from ingestion import ingest_db

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "inventory.db"
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=str(LOGS_DIR / "get_country_analysis.log"),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a",
)


def create_country_analysis(conn):
    query = """WITH country1 AS (SELECT
                                                         [country],
                                                         [Exports of goods and services (% of GDP)],
                                                         [Purchasing Power Index],
                                                         [Safety Index],
                                                         [Health Care Index],
                                                         [Cost Of Living Index],
                                                         [Access to electricity (% of population)],
                                                         [Education: Government expenditure (% of GDP)],
                                                         [Quality Of Life Index]
                                                         FROM [soci_econ_country_profiles] SC
                                                         WHERE [Exports of goods and services (% of GDP)]>="18.7826851657717"
                                                         ORDER BY [Exports of goods and services (% of GDP)]
                                   ),
                                   country2 AS (SELECT
                                                 [govt_type],
                                                 [country_name]
                                                 FROM [Countries_Data_By_Aadarsh_Vani] AV
                                                 
                                   )
                                    SELECT
                                                    SC.[country],
                                                    SC.[Exports of goods and services (% of GDP)],
                                                    SC.[Purchasing Power Index],
                                                    SC.[Safety Index],
                                                    SC.[Health Care Index],
                                                    SC.[Cost Of Living Index],
                                                    SC.[Access to electricity (% of population)],
                                                    SC.[Education: Government expenditure (% of GDP)],
                                                    SC.[Quality Of Life Index],
                                                    AV.[govt_type]
                                    FROM country1 SC
                                    LEFT JOIN country2 AV
                                      ON SC.[country] = AV.[country_name]
                                    ORDER BY SC.[Exports of goods and services (% of GDP)]
"""
    return pd.read_sql_query(query, conn)


def clean_data(df):
    df['Education: Government expenditure (% of GDP)'] = pd.to_numeric(df['Education: Government expenditure (% of GDP)'], errors='coerce').replace(-99, 0).fillna(0)
    return df


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)

    logging.info("-----creating_country_analysis-----")
    country_analysis_df = create_country_analysis(conn)
    logging.info(country_analysis_df.head())

    logging.info("---cleaning data---")
    clean_df = clean_data(country_analysis_df)
    logging.info(clean_df.head())

    logging.info("---ingesting data---")
    ingest_db(clean_df, "country_analysis", conn)
    logging.info("---------completed------------------")   
 










