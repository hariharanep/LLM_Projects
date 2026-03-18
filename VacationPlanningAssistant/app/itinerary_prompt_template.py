from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

class ItineraryTemplate(object):
    def __init__(self):
        self.system_template = """
      You are a travel agent who helps users make exciting travel plans.

      The user's request will be denoted by four hashtags. Convert the
      user's request into a detailed itinerary describing the places
      they should visit and the things they should do.

      Try to include the specific address of each location.

      Remember to take the user's preferences and timeframe into account,
      and give them an itinerary that would be fun and doable given their constraints.

      Return the itinerary as a bulleted list with clear start and end locations.
      Be sure to mention the type of transit for the trip.
      If specific start and end locations are not given, choose ones that you think are suitable and give specific addresses.
      Your output must be the list and nothing else.
    """

        self.human_template = """
      ####{query}####
    """

        self.system_message_prompt = SystemMessagePromptTemplate.from_template(
            self.system_template,
        )
        self.human_message_prompt = HumanMessagePromptTemplate.from_template(
            self.human_template, input_variables=["query"]
        )

        self.chat_prompt = ChatPromptTemplate.from_messages(
            [self.system_message_prompt, self.human_message_prompt]
        )