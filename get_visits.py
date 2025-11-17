from math import radians, cos, sin, asin, sqrt
import pandas as pd

# in minutes
MIN_VISIT = 15
MAX_VISIT = 150
# 60m because max radius error is 30m, so points might be 60m apart
# with a person standing still
MAX_VISIT_DIST = 60

# info about a single visit
class Visit:
    # visit_time is minutes
    def __init__(self, visit_df, visit_time):
        self.visit_start = visit_df.iloc[0].datetime
        self.visit_end = visit_df.iloc[-1].datetime
        self.visit_time = visit_time
        # calculate average lat long of this visit
        # (used to calculate distance to potential outlets)
        self.avg_lat = visit_df.latitude.mean()
        self.avg_long = visit_df.longitude.mean()
        self.outlet = None
        self.outlet_dist = float('inf')
    # toString()
    def __str__(self):
        return f"Start: {self.visit_start}, End: {self.visit_end}, \
        avg_lat: {self.avg_lat}, avg_lat: {self.avg_long}, \
        outlet: {self.outlet}, outlet_dist: {self.outlet_dist}\n"

# one of these for each of the 20 people
class Compute_Visits:
    def __init__(self, name, df, outlets_df):
        self.name = name
        self.df = self.preprocess(df)
        self.outlets_df = outlets_df
        # list of Visit objects for this person
        self.visits = []
    # preprocess the dataframe
    def preprocess(self, df):
        df = (df.loc[df['accuracy'] <= 30]
        .assign(datetime=pd.to_datetime(df['datetime']))
        [['datetime', 'latitude', 'longitude']])
        return df
    # calculate all visits to any location for valid durations
    # returns an array of Visit objects
    def calc_visits(self):
        # valid Visits
        visits = []
        # candidate visit rows
        visit_cand = []
        for row in self.df.itertuples(index=False):
            # base case
            if len(visit_cand) == 0:
                visit_cand.append(row)
                continue
            # calc distance from first in group to new row
            hav = self.haversine(row.latitude,
            row.longitude,
            visit_cand[0].latitude,
            visit_cand[0].longitude)
            # still visiting
            if hav <= MAX_VISIT_DIST:
                visit_cand.append(row)
                continue
            # person left area, visit over
            visit = self.process_visit(visit_cand)
            if visit:
                # this prints something interesting
                # print(visit)
                visits.append(visit)
            # set up for next visit iteration
            visit_cand = [row]
        self.visits = visits
    # determine if this meets the criteria of a visit
    # if it doesn't, turn False
    # if it does, return a Visit object
    def process_visit(self, visit_cand):
        # check if this is a valid visit based on time constraints
        time_diff = visit_cand[-1].datetime - visit_cand[0].datetime
        minutes_diff = time_diff.total_seconds() / 60
        is_valid = MIN_VISIT <= minutes_diff <= MAX_VISIT
        # visit immediately invalid (too long or too short)
        if not is_valid:
            return False
        # valid time range, see if there are outlet(s) near it
        visit = Visit(visit_df=pd.DataFrame(visit_cand, columns=['datetime', 'latitude', 'longitude']),
        visit_time=minutes_diff)
        for row in self.outlets_df.itertuples(index=False):
            hav = self.haversine(visit.avg_lat, visit.avg_long,
            row.LATITUDE, row.LONGITUDE)
            # find outlet that is closest to our average coords
            if hav <= 30 and hav < visit.outlet_dist:
                visit.outlet = row
                visit.outlet_dist = hav
        if not visit.outlet:
            return False
        return visit
    # Source https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
    def haversine(self, lat1, long1, lat2, long2):
        """
        Calculate the great circle distance in meters between two points 
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians 
        long1, lat1, long2, lat2 = map(radians, [long1, lat1, long2, lat2])
        # haversine formula 
        dlon = long2 - long1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371000 # radius of earth in meters
        return c * r

people = ['64', '67', '68', '69', '70', '175', '177', '179', '181', '182',
'258', '269', '272', '273', '276', '328', '336', '338', '343', '344']
outlets_df = pd.read_csv('outlets.csv')
# calc visits for each person
for person in people:
    df = pd.read_csv(f"locations/locations_{person}.csv")
    visits = Compute_Visits(person, df, outlets_df)
    visits.calc_visits()
    # this doesnt print anything interesting
    # print(f'visits for {person}:')
    # print(visits.visits)
    # print('----------')
    break # TODO: remove
