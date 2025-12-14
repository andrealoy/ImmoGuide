# core/data_loader.py

import pandas as pd 
from core.cleaner import SeLogerDataProcessor

def load_city_dataframe(city: str) -> pd.DataFrame:
    processor = SeLogerDataProcessor()
    return processor.run(city_name=city, output_path=f"data/{city}_clean.csv")
