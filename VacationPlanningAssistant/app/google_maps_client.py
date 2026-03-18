import googlemaps
import logging
from datetime import datetime, timedelta
import requests
import time

logging.basicConfig(level=logging.INFO)

class GoogleMapsClient(object):
    def __init__(
        self,
        gmaps_api_key
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.gmaps_client = googlemaps.Client(key=gmaps_api_key)
    
    def build_trip_dict(self, start, end, waypoints):
        self.logger.info("Building trip Dictionary")
        trip_dict = {}
        trip_dict["start"] = self.gmaps_client.geocode(start)[0]
        trip_dict["end"] = self.gmaps_client.geocode(end)[0]
    
        if waypoints:
            for i, waypoint in enumerate(waypoints):
                trip_dict["waypoint_{}".format(i)] = self.gmaps_client.geocode(waypoint)[0]

        self.logger.info("Successfully built trip Dictionary")
        return trip_dict
    
    def compute_routes(self, trip_dict, transit_type=None, start_time=None):
        self.logger.info("Computing routes with Google Routes Service")
        t1 = time.time()

        try:
            start_time = datetime.fromisoformat(start_time)
        except (ValueError, TypeError):
            start_time = datetime.now() + timedelta(days=1)

        if not transit_type:
            transit_type = "DRIVE"

        start_place_id = trip_dict["start"]["place_id"]
        end_place_id = trip_dict["end"]["place_id"]
        intermediates = [
            {"placeId": trip_dict[k]["place_id"]} for k in trip_dict if "waypoint" in k
        ]

        url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.gmaps_client.key,
            "X-Goog-FieldMask": "routes.legs.startLocation,routes.legs.endLocation,routes.legs.duration,routes.legs.distanceMeters,routes.legs.steps.polyline,routes.polyline,routes.optimizedIntermediateWaypointIndex",
        }
        body = {
            "origin": {"placeId": start_place_id},
            "destination": {"placeId": end_place_id},
            "intermediates": intermediates,
            "travelMode": transit_type,
            "optimizeWaypointOrder": True,
            "routingPreference": "TRAFFIC_AWARE",
            "departureTime": start_time.isoformat() + "Z",
            "units": "METRIC",
        }

        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
        result = response.json()
        route = result["routes"][0]
        t2 = time.time()
        self.logger.info("Total time taken to compute routes with Google Routes Service: {}".format(round(t2 - t1, 2)))
        return route
