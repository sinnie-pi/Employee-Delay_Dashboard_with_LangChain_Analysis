
import json
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers.json import JsonOutputParser
from pydantic import BaseModel, Field

def report_analyzer(weekly_data,rank=3):
    # Set up the JSON output parser
    parser = JsonOutputParser()


    output_format = """
    ```json
    {
        "field_1":{ 
                    "Rank" : 1,
                    "Average violation count" : "<average violation for that week.>",
                    "Areas of Concern": "<Your observation on the field and areas of concern found along with feedback>",
                    "Reason": "<Why you think that it is should be in first place and why it is concerning>"
                    },
        "field_2":{ 
                    "Rank" : 2,
                    "Average violation count" : "<average violation for that week.>",
                    "Areas of Concern": "<Your observation on the field and areas of concern found along with feedback>",
                    "Reason": "<Why you think that it is should be in second place and why it is concerning>"
                    },
        "field_3":{ 
                    "Rank" : 3,
                    "Average violation count" : "<average violation for that week.>",
                    "Areas of Concern": "<Your observation on the field and areas of concern found along with feedback>",
                    "Reason": "<Why you think that it is should be in third place and why it is concerning>"
                    },
        ....
    }
    ```
    """
    column_description = """
    Here are the description of the columns present in the json data: 
    {
        "shift_id": ID of that shift.

        "date": Date of that report. 

        "meal_break": A delay occurred because an employee's meal break was longer than scheduled.

        "hot_seat": There was a delay during the transition between employees at the same workstation.

        "shift_change": The handover from one employee's shift to the next caused a delay.

        "no_operator": The employee needed to operate equipment was not available.

        "refueling": The process of refueling an equipment caused a delay.

        "unscheduled_maintenance": An unexpected equipment breakdown required maintenance, leading to a delay.

    }
    """
    # Create prompt template with variables
    prompt = PromptTemplate(
        template="""You are an HR performance analyst. Below is weekly employee delay data with shift IDs:
    You will be provided with a weekly data and which will have this columns structure
    {column_description}
    You have to understand the data and look into the top three problem areas. 
    For example 0 of a field means no person has violated that field and 1 means 1 person have violated.
    You have to look into the entire weekly data and determine whether the violated fields are concerning or not and have to order them according to their impact.
    For example frequent violation of shift change may be due to some natural calamities throughout the week. But frequent violation of hot seat or meal break might be a concerning as that might have occurred due to unpunctuality.
    You also have to provide a reason behind why you choose that field is more concerning compared to others and why you choose to rank them in the order you placed
    Do not focus only on the average count of violation. Also try to understand the reason behind that and impact or consequences of that. Greater average value always does not indicate greater concern. 
    Fields depending upon external factors or unforeseen circumstances are lesser impactful than fields depending on internal factors
    You have to respond in the following Json format:
    {output_format}

    Here is the weekly data:

    {weekly_data}

    You have to generate top {rank} fields for this data.
    
    The output should only contain the json format mentioned. No other text is expected with the json.
    """,
        input_variables=[ "weekly_data", "column_description", "output_format","rank"],
        
    )
    # Initialize LangChain ChatOpenAI with OpenRouter
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        model="meta-llama/llama-3.3-70b-instruct",

    )

    # Create messages
    chain = prompt | llm | parser

    # Get completion
    input_data = {
        "weekly_data": json.dumps(weekly_data, indent=2),
        "column_description": column_description,
        "output_format": output_format,
        "rank":rank,
    }

    # Invoke the chain
    result = chain.invoke(input_data)

    return result
