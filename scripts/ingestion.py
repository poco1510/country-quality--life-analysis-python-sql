import os
import time
from pathlib import Path
import logging

import pandas as pd
from sqlalchemy import create_engine

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
DB_PATH = BASE_DIR / "inventory.db"

LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=str(LOGS_DIR / "ingestion-db.log"),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a",
)

engine = create_engine(f"sqlite:///{DB_PATH}")


def ingest_db(df, table_name, engine):
    """Write a dataframe to a SQLite table, replacing any existing version."""
    df.to_sql(table_name, con=engine, if_exists="replace", index=False)


def load_raw_data(data_dir=None):
    """Load all CSV files in the data directory into the SQLite database."""
    start = time.time()
    source_dir = Path(data_dir) if data_dir is not None else DATA_DIR
    files = sorted(source_dir.glob("*.csv"))
    print(f"found files in data folder: {[f.name for f in files]}")

    for csv_file in files:
        print(f"processing {csv_file.name}")
        df = pd.read_csv(csv_file)
        logging.info(f"Ingesting {csv_file.name} in db")
        table_name = csv_file.stem.strip().replace(" ", "_").replace("-", "_")
        ingest_db(df, table_name, engine)

    end = time.time()
    total_time = (end - start) / 60
    logging.info("--------- Ingestion Complete ---------")
    logging.info(f"Total Time Taken: {total_time} minutes")


if __name__ == "__main__":
    load_raw_data()