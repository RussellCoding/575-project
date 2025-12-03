import pandas as pd
import folium
from folium.plugins import TimestampedGeoJson
from datetime import datetime, timedelta
import json
import os

#config for the files
INPUT_CSV = "raw_visits.csv" #update later, need a way to do this per person
OUTPUT_CLEAN_CSV = "cleaned_visits.csv"
OUTPUT_MAP = "daily_map.html"


#figure out what meal it is based on the time they go
def classify_meal(dt):
    hour = dt.hour
    if 5 <= hour < 11:
        return "Breakfast"
    elif 11 <= hour < 16:
        return "Lunch"
    elif 16 <= hour < 22:
        return "Dinner"
    return "Late Night / Other"


#______CLEANING_____
def clean_data(df):
    rows = []

    for i, row in df.iterrows():
        start = datetime.fromisoformat(row["start"])
        end = datetime.fromisoformat(row["end"])
        duration_min = (end - start).total_seconds() / 60

        outlet_info = row["outlet info"]
        # parse format: Pandas(COMPANY_NAME='...', CITY='...', LATITUDE=..., LONGITUDE=...)
        info = {}

        try:
            inside = outlet_info[outlet_info.index("(")+1: outlet_info.rindex(")")]
            parts = inside.split(",")
            for p in parts:
                key, val = p.split("=")
                key = key.strip()
                val = val.strip().strip("'")
                info[key] = val
        except:
            info = {}

        rows.append({
            "date": start.date().isoformat(),
            "start_time": start.time().isoformat(timespec="minutes"),
            "end_time": end.time().isoformat(timespec="minutes"),
            "duration_minutes": round(duration_min, 2),
            "meal": classify_meal(start),
            "restaurant": info.get("COMPANY_NAME", ""),
            "city": info.get("CITY", ""),
            "latitude": float(info.get("LATITUDE", "0")),
            "longitude": float(info.get("LONGITUDE", "0")),
        })

    return pd.DataFrame(rows)


#_________MAP____________
def build_daily_map(clean_df):
    #sort the days
    days = sorted(clean_df["date"].unique())

    # make a foluim map, i put this in seattle because thats where most of the population in the state is
    m = folium.Map(location=[47.60, -122.33], zoom_start=12)

    # geojson features
    features = []

    for day in days:
        day_df = clean_df[clean_df["date"] == day]

        for _, row in day_df.iterrows():
            start_dt = f"{row['date']}T{row['start_time']}:00"
            end_dt = f"{row['date']}T{row['end_time']}:00"

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [row["longitude"], row["latitude"]],
                },
                "properties": {
                    "time": start_dt,
                    "popup": (
                        f"<b>{row['restaurant']}</b><br>"
                        f"{row['city']}<br>"
                        f"Meal: {row['meal']}<br>"
                        f"Start: {row['start_time']}<br>"
                        f"End: {row['end_time']}<br>"
                        f"Duration: {row['duration_minutes']} minutes"
                    ),
                    "icon": "circle",
                    "iconstyle": { #did some googling to find this stuff 
                        "color": "red",
                        "fillColor": "red",
                        "fillOpacity": 0.7,
                        "radius": 6
                    }
                }
            }

            features.append(feature)

    #wrap it 
    data = {
        "type": "FeatureCollection",
        "features": features
    }

    TimestampedGeoJson(
        data,
        period="PT1H",
        add_last_point=True,
        auto_play=False,
        loop=False,
        max_speed=1,
        time_slider_drag=True,
    ).add_to(m)

    m.save(OUTPUT_MAP)
    print(f"made html day by day map: {OUTPUT_MAP}")


#______MAIN_____
def main():
    df = pd.read_csv(INPUT_CSV)

    print("cleanig it now")
    clean_df = clean_data(df)

    clean_df.to_csv(OUTPUT_CLEAN_CSV, index=False)
    print(f"saved the data to → {OUTPUT_CLEAN_CSV}")

    print("map being made")
    build_daily_map(clean_df)

    print("last message if you see this it works")


if __name__ == "__main__":
    main()
