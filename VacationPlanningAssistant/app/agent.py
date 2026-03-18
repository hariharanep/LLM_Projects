import logging
import time
from langchain_openai import ChatOpenAI
from langchain_classic.chains import LLMChain, SequentialChain
from app.validation_prompt_template import ValidationTemplate
from app.itinerary_prompt_template import ItineraryTemplate
from app.parsing_prompt_template import ParsingTemplate

logging.basicConfig(level=logging.INFO)

class Agent(object):
    def __init__(
        self,
        open_ai_api_key,
        model="gpt-3.5-turbo",
        temperature=0
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.openai_key = open_ai_api_key

        self.chat_model = ChatOpenAI(model=model, temperature=temperature, openai_api_key=self.openai_key)
        self.validation_prompt = ValidationTemplate()
        self.itinerary_prompt = ItineraryTemplate()
        self.parser_prompt = ParsingTemplate()
        self.validation_chain = self._set_up_validation_chain()
        self.travel_plan_chain = self._set_up_generate_travel_plan_chain()
    
    def _set_up_generate_travel_plan_chain(self):
        # set up LLMChain to get the travel plan as a string
        travel_agent = LLMChain(
            llm=self.chat_model,
            prompt=self.itinerary_prompt.chat_prompt,
            output_key="agent_suggestion",
        )

        # set up LLMChain to extract the waypoints as a JSON object
        parser_agent = LLMChain(
            llm=self.chat_model,
            prompt=self.parser_prompt.chat_prompt,
            output_key="trip",
        )

        # overall chain allows us to call the travel_agent and parser_agent in
        # sequence, with labelled outputs.
        overall_chain = SequentialChain(
            chains=[travel_agent, parser_agent],
            input_variables=["query", "format_instructions"],
            output_variables=["agent_suggestion", "trip"],
        )
        return overall_chain

    def _set_up_validation_chain(self):
        # make validation agent chain
        validation_agent = LLMChain(
            llm=self.chat_model,
            prompt=self.validation_prompt.chat_prompt,
            output_parser=self.validation_prompt.parser,
            output_key="validation_output"
        )

        # add to sequential chain 
        overall_chain = SequentialChain(
            chains=[validation_agent],
            input_variables=["query", "format_instructions"],
            output_variables=["validation_output"]
        )

        return overall_chain
    
    def suggest_travel(self, query):
        self.logger.info("Suggesting Travel")
        t1 = time.time()
        
        validation_result = self.validate_travel(query)
        if validation_result["plan_is_valid"].lower() == "no":
            self.logger.warning("User request was not valid!")
            print("\n######\n Travel plan is not valid \n######\n")
            print(validation_result["updated_request"])
            return None, None, validation_result
        
        self.logger.info("Query is valid")
        travel_plan_result = self.generate_travel_plan(query)
        trip_suggestion = travel_plan_result["agent_suggestion"]
        trip = travel_plan_result["trip"]
        t2 = time.time()
        self.logger.info("Total time to suggest travel: {}".format(round(t2 - t1, 2)))
        return trip_suggestion, trip, validation_result
        
    def validate_travel(self, query):
        self.logger.info("Validating query")
        t1 = time.time()
        self.logger.info(
            "Calling validation (model is {}) on user input".format(
                self.chat_model.model_name
            )
        )
        validation_result = self.validation_chain(
            {
                "query": query,
                "format_instructions": self.validation_prompt.parser.get_format_instructions()
            }
        )

        validation_result = validation_result["validation_output"].dict()
        t2 = time.time()
        self.logger.info("Time to validate request: {}".format(round(t2 - t1, 2)))
        return validation_result

    def generate_travel_plan(self, query):
        self.logger.info("Generating travel plan")
        t1 = time.time()
        self.logger.info(
            "Calling travel plan generation (model is {}) on user input".format(
                self.chat_model.model_name
            )
        )

        travel_plan_result = self.travel_plan_chain(
            {
                "query": query,
                "format_instructions": self.parser_prompt.parser.get_format_instructions()
            }
        )
        travel_plan_result["trip"] = self.parser_prompt.parser.parse(travel_plan_result["trip"])

        t2 = time.time()
        self.logger.info("Time to generate travel plan: {}".format(round(t2 - t1, 2)))
        return travel_plan_result