from DataGeneration import DatabaseHandler
from MapboxAPIWrapper import MapboxAPIWrapper
import math


class DataGenerator:

    def __init__(self):
        self.stops = []
        self.handler = DatabaseHandler(full=False)
        self.wrapper = MapboxAPIWrapper()

    def initialize(self, db='db.sqlite3', api_key='api_key.txt'):
        """
        Initializes the DataGenerator. Connects to the database, collects all
        stops from the database, and initializes the API wrapper.

        Args:
        db (str): File path to the sqlite3 database.
        api_key (str): File path to a text file containing an API key.
        """
        self.handler = self._get_database_handler(db)
        self.stops = self.handler.get_all_stops()
        self.wrapper = self._get_api_wrapper(api_key)

    def begin(self, stops_per_address=5):
        """
        Begins collection of distances to closest stops from each address.
        Stores each address-stop pair and associated walking distance and time
        in the routes table of the database.

        Args:
        stops_per_address (int): Number of stops per address used to query the
            api for walking distance. The stops selected are the closest stops
            to the address by straight line distance. Default value is 5.
        """
        address_generator = self.handler.get_address_generator()
        for address in address_generator:
            closest_stops = self._get_closest_locations(address,
                                                        self.stops,
                                                        n=stops_per_address)
            for stop in closest_stops:
                result = self.wrapper.get_distance_from_api(address, stop)
                self.handler.add_route(address.id,
                                       stop.id,
                                       result["distance"],
                                       result["time"])

    def _get_database_handler(self, db_file_name='db.sqlite3'):
        handler = DatabaseHandler(db_file_name)
        return handler

    def _get_api_wrapper(self, api_key_file = 'api_key.txt'):
        wrapper = MapboxAPIWrapper()
        wrapper.load_api_key_from_file(api_key_file)
        return wrapper

    def _get_closest_locations(self, source, destinations, n):
        location_list = []
        for destination in destinations:
            distance = math.sqrt((source.latitude - destination.latitude)**2 +
                                 (source.longitude - destination.longitude)**2)
            location_list.append((distance, destination))
        return [loc[1] for loc in sorted(location_list)[0:n]]
