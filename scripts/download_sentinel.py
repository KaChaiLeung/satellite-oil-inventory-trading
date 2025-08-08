import datetime
import pystac_client
from pystac.extensions.eo import EOExtension as eo
import planetary_computer
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import os
from pathlib import Path


import config


def get_s2l2a_data():

    start_dt = datetime.date(config.PROJECT_START[0], config.PROJECT_START[1], config.PROJECT_START[2])
    end_dt = datetime.date(config.PROJECT_END[0], config.PROJECT_END[1], config.PROJECT_END[2])
    wednesdays = []
    assets = ["B02", "B03", "B04", "B08", "SCL", "B11", "B12", "AOT"]

    while not start_dt.weekday() == 2:
        start_dt += datetime.timedelta(days=1)
    
    while start_dt <= end_dt:
        wednesdays.append(start_dt)
        start_dt += datetime.timedelta(days=7)

    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    with ThreadPoolExecutor(max_workers=10) as executor:
        summaries = list(executor.map(lambda d: query_single_day(d, catalog, assets),
                                      wednesdays
                                ))
    
    df = pd.DataFrame(summaries)
    
    ROOT = Path(__file__).resolve().parent.parent
    output_dir = ROOT / "data" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "sentinel_summary.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved summary to {csv_path}")
    

def query_single_day(day, catalog, assets):

    win_start = (day - datetime.timedelta(days=config.TIME_DELTA_DAYS)).isoformat()
    time_string = f"{win_start}T00:00:00Z/{day.isoformat()}T14:00:00Z"

    search = catalog.search(
        collections=["sentinel-2-l2a"],
        intersects=config.AOI_BBOX,
        datetime=time_string,
        query={"eo:cloud_cover": {"lt": 60}},
        sortby=["datetime"]
    )

    items = list(search.item_collection())
    collection = "sentinel-2-l2a"
    cc = 60
    
    if not items:
        search = catalog.search(
            collections=["sentinel-2-l2a"],
            intersects=config.AOI_BBOX,
            datetime=time_string,
            query={"eo:cloud_cover": {"lt": 80}},
            sortby=["datetime"]
        )

        items = list(search.item_collection())
        collection = "sentinel-2-l2a"

        if not items:
            search = catalog.search(
                collections=["sentinel-2-l1c"],
                intersects=config.AOI_BBOX,
                datetime=time_string,
                query={"eo:cloud_cover": {"lt": 60}},
                sortby=["datetime"]
            )

            items = list(search.item_collection())
            collection = "sentinel-2-l1c"

            if not items:
                collection = None
    
    filtered_items = [item for item in items if item.properties.get("eo:cloud_cover", 1000) < 60]

    if filtered_items:
        best_item = min(filtered_items, key=lambda item: item.properties["eo:cloud_cover"])
        return {
            "day": day,
            "found_item": True,
            "cloud_cover": best_item.properties["eo:cloud_cover"],
            "collection": collection,
            "id": best_item.id,
            "assets": {k: best_item.assets[k].href for k in assets},
            "bbox": best_item.geometry,
            "platform": best_item.properties["platform"]
        }
    else:
        return {
            "day": day,
            "found_item": False,
            "cloud_cover": None,
            "collection": None,
            "id": None,
            "assets": None,
            "bbox": None,
            "platform": None
        }


if __name__ == "__main__":
    get_s2l2a_data()