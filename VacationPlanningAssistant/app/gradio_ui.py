import logging
import leafmap.foliumap as leafmap
import gradio as gr
from app.agent import Agent
from app.google_maps_client import GoogleMapsClient
from app.map_generator import MapGenerator

VALID_MESSAGE = "Plan is valid"
DEFAULT_QUERY = "I want to do a 5 day road trip from San Francisco to Las Vegas. I want to visit pretty coastal towns along HW1 and then mountain views in southern California"

logging.basicConfig(level=logging.INFO)

class GradioUi(object):
    def __init__(
        self,
        open_ai_key,
        gmaps_api_key
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self.travel_agent = Agent(open_ai_api_key=open_ai_key)
        self.google_maps_client = GoogleMapsClient(gmaps_api_key=gmaps_api_key)
        self.map_generator = MapGenerator()
    
    @staticmethod
    def validation_message(validiation_agent_response):
        if validiation_agent_response["plan_is_valid"].lower() == "no":
            validation_body = validiation_agent_response["updated_request"]
            validation_header = "The query is not valid in its current state. Here is a suggestion from the model: \n"
            validation = validation_header + validation_body
        else:
            validation = VALID_MESSAGE
        return validation
    
    def generate_leafmap(self, query):
        self.logger.info("Generating the leaf map")
        itinerary, trip, validation_result = self.travel_agent.suggest_travel(query)

        validation_string = self.validation_message(validation_result)

        if validation_string != VALID_MESSAGE:
            # return default generic leaf map
            itinerary = "No valid itinerary"
            map_html = self.generate_generic_leafmap()
        else:
            # return leaf map with route
            trip_dict = self.google_maps_client.build_trip_dict(trip["start"],
                                                                 trip["end"],
                                                                 waypoints=trip["waypoints"])
            route = self.google_maps_client.compute_routes(trip_dict=trip_dict, transit_type=trip.get("transit"), start_time=trip.get("start_time"))
            map_html = self.map_generator.generate_map(route=route)
        self.logger.info("Returning the leaf map, itinerary, and validation result")
        return map_html, itinerary, validation_string

    @staticmethod
    def generate_generic_leafmap():
        map = leafmap.Map(location=(0,0), tiles="OpenStreetMap", zoom_start=3)
        return map.to_gradio()
    
    def display_ui(self):
        self.logger.info("Generating the UI")
        app = gr.Blocks()
        generic_map = self.generate_generic_leafmap()

        with app:
            gr.Markdown("## Generate travel suggestions")
            with gr.Row():
                # make column 1 within row 1
                with gr.Column():
                    text_input_map = gr.Textbox(
                       DEFAULT_QUERY, label="Travel query", lines=4
                    )

                    query_validation_text = gr.Textbox(
                        label="Query validation information", lines=2
                    )
                
                # make column 2 within row 1
                with gr.Column():
                    map_output = gr.HTML(generic_map, label="Travel map")

                    itinerary_output = gr.Textbox(
                        value="Your itinerary will appear here",
                        label="Itinerary suggestion",
                        lines=3,
                    )
            
            map_button = gr.Button("Generate")
        
            map_button.click(
                self.generate_leafmap,
                inputs=[text_input_map],
                outputs=[map_output, itinerary_output, query_validation_text],
            )
    
        # run the app
        self.logger.info("Running the app to display the UI")
        app.launch()