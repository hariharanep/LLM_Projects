import logging
from googlemaps.convert import decode_polyline
import folium
import leafmap.foliumap as leafmap

logging.basicConfig(level=logging.INFO)

class MapGenerator(object):
    def __init__(
        self
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
    
    def generate_map(self, route):
        self.logger.info("Generating map from provided route")

        overall_route = decode_polyline(route["polyline"]["encodedPolyline"])

        map = leafmap.Map(location=[overall_route[0]["lat"], overall_route[0]["lng"]], tiles="OpenStreetMap", zoom_start=6)

        for i, leg in enumerate(route["legs"]):
            # Markers
            folium.Marker(
                location=(leg["startLocation"]["latLng"]["latitude"], leg["startLocation"]["latLng"]["longitude"]),
                icon=folium.Icon(color="red", icon="info-sign"),
            ).add_to(map)
            if i == len(route["legs"]) - 1:
                folium.Marker(
                    location=(leg["endLocation"]["latLng"]["latitude"], leg["endLocation"]["latLng"]["longitude"]),
                    icon=folium.Icon(color="red", icon="info-sign"),
                ).add_to(map)

            # Route segment with distance/duration
            leg_coords = [(p["lat"], p["lng"]) for step in leg["steps"] for p in decode_polyline(step["polyline"]["encodedPolyline"])]
            f_group = folium.FeatureGroup(f"Leg {i+1}: {leg['distanceMeters']/1000:.1f} km / {int(leg['duration'].rstrip('s'))//60} min")
            folium.PolyLine(
                leg_coords,
                color="blue",
                weight=4,
                tooltip=f'Leg {i+1}: {leg["distanceMeters"]/1000:.1f} km / {int(leg["duration"].rstrip("s"))//60} min',
            ).add_to(f_group)
            f_group.add_to(map)

        folium.LayerControl().add_to(map)

        self.logger.info("Retuning generated map")
        return map.to_gradio()
