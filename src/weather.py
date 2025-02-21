from typing import Literal
import os
import requests
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

load_dotenv()
# Define the tools for the agent to use
@tool
def search(query: str):
    """Get current weather for a location using OpenMeteo API."""
    # Extract city name from query
    query = query.lower()
    if "weather" in query:
        query = query.replace("weather", "").strip()
    if "in" in query:
        query = query.split("in")[-1].strip()
    
    try:
        # First get coordinates for the city using Nominatim (OpenStreetMap) geocoding
        geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=1&language=en&format=json"
        location_response = requests.get(geocoding_url)
        location_data = location_response.json()
        
        if not location_data.get('results'):
            return f"Could not find location: {query}"
            
        location = location_data['results'][0]
        lat = location['latitude']
        lon = location['longitude']
        city_name = location['name']
        
        # Get weather data using coordinates
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&temperature_unit=fahrenheit"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()
        
        temp = weather_data['current']['temperature_2m']
        weather_code = weather_data['current']['weather_code']
        
        # Convert weather code to description
        weather_descriptions = {
            0: "clear sky",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "foggy",
            48: "depositing rime fog",
            51: "light drizzle",
            53: "moderate drizzle",
            55: "dense drizzle",
            61: "slight rain",
            63: "moderate rain",
            65: "heavy rain",
            71: "slight snow fall",
            73: "moderate snow fall",
            75: "heavy snow fall",
            77: "snow grains",
            80: "slight rain showers",
            81: "moderate rain showers",
            82: "violent rain showers",
            85: "slight snow showers",
            86: "heavy snow showers",
            95: "thunderstorm",
            96: "thunderstorm with slight hail",
            99: "thunderstorm with heavy hail",
        }
        
        description = weather_descriptions.get(weather_code, "unknown conditions")
        
        return f"In {city_name}, it's {temp}°F with {description}."
        
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"


tools = [search]

tool_node = ToolNode(tools)

model = ChatAnthropic(model="claude-3-5-sonnet-latest", temperature=0).bind_tools(tools)

def should_continue(state: MessagesState) -> Literal["tools"] | str:
    messages = state['messages']
    last_message = messages[-1]
    # If the LLM makes a tool call, then we route to the "tools" node
    if last_message.tool_calls:
        return "tools"
    # Otherwise, we stop (reply to the user)
    return END


# Define the function that calls the model
def call_model(state: MessagesState):
    messages = state['messages']
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


# Define a new graph
workflow = StateGraph(MessagesState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.add_edge(START, "agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("tools", 'agent')

# Initialize memory to persist state between graph runs
checkpointer = MemorySaver()

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable.
# Note that we're (optionally) passing the memory when compiling the graph
app = workflow.compile(checkpointer=checkpointer)

# Use the agent
final_state = app.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in Miami"}]},
    config={"configurable": {"thread_id": 42}}
)
print(final_state["messages"][-1].content)