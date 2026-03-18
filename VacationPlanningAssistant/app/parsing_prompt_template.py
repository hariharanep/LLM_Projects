from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
from typing import Optional

class Trip(BaseModel):
    start: str = Field(description="start location of trip")
    end: str = Field(description="end location of trip")
    waypoints: List[str] = Field(description="list of waypoints")
    transit: Optional[str] = Field(description="mode of transportation, must be one of: DRIVE, WALK, BICYCLE, TRANSIT, TWO_WHEELER")
    start_time: Optional[str] = Field(default=None, description="start date and time of trip, e.g. 2024-03-17T09:00:00")

class ParsingTemplate(object):
    def __init__(self):
        self.system_template = """
      You are an agent who converts detailed travel plans into a simple list of locations.

      The itinerary will be denoted by four hashtags. Convert it into
      list of places that they should visit. Try to include the specific address of each location.

      Your output should always contain the start and end point of the trip, and may also include a list
      of waypoints. It should also include a mode of transit. The number of waypoints cannot exceed 20.
      If you can't infer the mode of transit, make a best guess given the trip location. It may also
      include the start date and time of the trip.

      For example:

      ####
      Itinerary for a 2-day driving trip within London:
      - Day 1:
        - Start at Buckingham Palace (The Mall, London SW1A 1AA)
        - Visit the Tower of London (Tower Hill, London EC3N 4AB)
        - Explore the British Museum (Great Russell St, Bloomsbury, London WC1B 3DG)
        - Enjoy shopping at Oxford Street (Oxford St, London W1C 1JN)
        - End the day at Covent Garden (Covent Garden, London WC2E 8RF)
      - Day 2:
        - Start at Westminster Abbey (20 Deans Yd, Westminster, London SW1P 3PA)
        - Visit the Churchill War Rooms (Clive Steps, King Charles St, London SW1A 2AQ)
        - Explore the Natural History Museum (Cromwell Rd, Kensington, London SW7 5BD)
        - End the trip at the Tower Bridge (Tower Bridge Rd, London SE1 2UP)
      #####

      Output:
      Start: Buckingham Palace, The Mall, London SW1A 1AA
      End: Tower Bridge, Tower Bridge Rd, London SE1 2UP
      Waypoints: ["Tower of London, Tower Hill, London EC3N 4AB", "British Museum, Great Russell St, Bloomsbury, London WC1B 3DG", "Oxford St, London W1C 1JN", "Covent Garden, London WC2E 8RF","Westminster, London SW1A 0AA", "St. James's Park, London", "Natural History Museum, Cromwell Rd, Kensington, London SW7 5BD"]
      Transit: "DRIVE"

      Transit can be only one of the following options: "DRIVE", "WALK", "BICYCLE", "TRANSIT", "TWO_WHEELER"
      
      {format_instructions}
    """

        self.human_template = """
      ####{agent_suggestion}####
    """

        self.parser = JsonOutputParser(pydantic_object=Trip)

        self.system_message_prompt = SystemMessagePromptTemplate.from_template(
            self.system_template,
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        self.human_message_prompt = HumanMessagePromptTemplate.from_template(
            self.human_template, input_variables=["agent_suggestion"]
        )

        self.chat_prompt = ChatPromptTemplate.from_messages(
            [self.system_message_prompt, self.human_message_prompt]
        )