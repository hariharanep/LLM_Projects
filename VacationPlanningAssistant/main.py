from dotenv import load_dotenv
import os
from app.gradio_ui import GradioUi

load_dotenv()
open_ai_key = os.getenv("OPENAI_API_KEY")
gmaps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

gradio_ui = GradioUi(open_ai_key=open_ai_key, gmaps_api_key=gmaps_api_key)
gradio_ui.display_ui()