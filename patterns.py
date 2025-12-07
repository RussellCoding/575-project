import pandas as pd
import os
from datetime import datetime, timedelta
from collections import Counter, defaultdict

def analyze_person(person_id, df):
    #in this we will find the favorite restaurants, busiest days, avg meal lenghts, top cities, typical meal times, weekly freq
    patterns = {}#this is the patterns dict that will be returned
    
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.day_name()
    #this is getting the starting hour
    df['hour'] = df['start_time'].apply(lambda x: int(x.split(':')[0]))
    
    # what there favortie is
    restaurant_counts = df['restaurant'].value_counts()
    patterns['favorite_restaurants'] = restaurant_counts.head(5).to_dict()
    
    #what daus are buisy
    dow_counts = df['day_of_week'].value_counts()
    patterns['busiest_days'] = dow_counts.to_dict()
    
    # avg meal lenght
    avg_duration = df.groupby('meal')['duration_minutes'].mean().to_dict()
    patterns['avg_duration_by_meal'] = avg_duration
    
    # what city they eat in the most, this is intresting because it shows where they spend most of there time
    city_counts = df['city'].value_counts()
    patterns['top_cities'] = city_counts.head(5).to_dict()
    
    # #when they usually eat(typ meal times)
    # meal_times = df.groupby('meal')['hour'].apply(lambda x: {
    #     'avg': round(x.mean(), 1),
    #     'min': x.min(),
    #     'max': x.max()
    # }).to_dict()
    # patterns['meal_time_patterns'] = meal_times
    
    #how often they eat out on avg
    df['week'] = df['date'].dt.isocalendar().week
    weekly_visits = df.groupby('week').size()
    patterns['avg_visits_per_week'] = round(weekly_visits.mean(), 2)
    patterns['max_visits_in_week'] = int(weekly_visits.max())
    patterns['min_visits_in_week'] = int(weekly_visits.min())
    #return the dict
    return patterns

#in this we will combine what we find
def find_group_patterns(all_data):
      
    combined_df = pd.concat(all_data.values(), ignore_index=True)
    totals = len(combined_df)
 
    top_restaurants = combined_df['restaurant'].value_counts().head(10)
 
    top_cities = combined_df['city'].value_counts().head(5)
  
    meal_totals = combined_df['meal'].value_counts()
 

def main():
    people = ['64', '67', '68', '69', '70', '175', '177', '179', '181', '182',
    '258', '269', '272', '273', '276', '328', '336', '338', '343', '344']
    
    all_data = {}
    all_patterns = {}
    
    for person in people:
        cleaned_file = f"output/cleaned_visits_{person}.csv"
        
        if not os.path.exists(cleaned_file):#if not there
            continue
        
        df = pd.read_csv(cleaned_file)
        
        if len(df) == 0:
            continue
        
        df['person_id'] = person
        all_data[person] = df
        
        #this will get the persons patters then add it to a total
        patterns = analyze_person(person, df)
        all_patterns[person] = patterns
        

    
    #this will take all the data found from persons and input it to get an avg for it
    if all_data:
        find_group_patterns(all_data)
        with open('pattern_summary.txt', 'w') as f:
            f.write("restaurant visit analysis\n")
            
            #this is per person
            for person, patterns in all_patterns.items():
                f.write(f"\n\n")
                f.write(f"Person {person}\n")
                
                f.write(f"\naverage visits per week: {patterns['avg_visits_per_week']}\n")
                
                f.write(f"\ntop restaurants:\n")
                for i, (restaurant, count) in enumerate(patterns['favorite_restaurants'].items(), 1):
                    f.write(f"  {i}. {restaurant} - {count} times\n")
                
                # f.write(f"\nmeal times:\n")
                # for meal, times in patterns['meal_time_patterns'].items():
                #     if isinstance(times, dict):
                #         avg_hour = int(times['avg'])
                #         avg_minute = int((times['avg'] - avg_hour) * 60)
                #         avg_time = f"{avg_hour:02}:{avg_minute:02}"
                #         f.write(f"  {meal}: usually around {avg_time} (earliest {times['min']}:00, latest {times['max']}:00)\n")
                #     #f.write(f"  {meal}: usually around {int(times['avg'])}:00 (earliest {times['min']}:00, latest {times['max']}:00)\n")  i couldnt get this to work for the life of me
                
                f.write(f"\nbusiest days:\n")
                for day, count in sorted(patterns['busiest_days'].items(), key=lambda x: x[1], reverse=True)[:3]:
                    f.write(f"  {day}: {count} visits\n")
                
                f.write(f"\ncities visited:\n")
                for city, count in patterns['top_cities'].items():
                    f.write(f"  {city} - {count} times\n")
                
                f.write(f"\naverage time spent:\n")
                for meal, duration in patterns['avg_duration_by_meal'].items():
                    f.write(f"  {meal}: {duration:.0f} min\n")
                
                f.write(f"\n\n")
            
            #find group pattern
            combined_df = pd.concat(all_data.values(), ignore_index=True)
            
            f.write(f"\n\n")
            f.write(f"overall group patterns\n")
            f.write(f"\n\n")
            
            f.write(f"most popular restaurants:\n")
            top_restaurants = combined_df['restaurant'].value_counts().head(10)
            for i, (restaurant, count) in enumerate(top_restaurants.items(), 1):
                f.write(f"  {i}. {restaurant} - {count} total visits\n")
            
            f.write(f"\nmost visited cities:\n")
            top_cities = combined_df['city'].value_counts().head(5)
            for city, count in top_cities.items():
                f.write(f"  {city}: {count} visits\n")
            
            f.write(f"\nmeal breakdown:\n")
            meal_totals = combined_df['meal'].value_counts()
            for meal, count in meal_totals.items():
                f.write(f"  {meal}: {count} ({count/len(combined_df)*100:.0f}%)\n")
            
            f.write(f"\navgs:\n")
            f.write(f"  -visits per person: {len(combined_df) / len(all_data):.1f}\n")
            f.write(f"  -unique restaurants per person: {combined_df.groupby('person_id')['restaurant'].nunique().mean():.1f}\n")
            f.write(f"  -visit duration: {combined_df['duration_minutes'].mean():.0f} min\n")
            
            
        print("saved to: pattern_summary.txt")

if __name__ == "__main__":
    main()