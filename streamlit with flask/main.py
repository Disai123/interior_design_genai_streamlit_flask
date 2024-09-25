import streamlit as st
from Interior_design.agent import Agent, Task, InputType, OutputType
from Interior_design.openai_model import OpenAIModel
from Interior_design.arch import SequentialFlow

# Initialize variables
agent = None
model = None
sequential_flow = None

def initialize_agent_and_model(api_key):
    global agent, model, sequential_flow

    # Define agent properties
    expertise = "Interior Designer"
    task = Task("Image Generation")
    input_type = InputType("Text")
    output_type = OutputType("Image")
    agent = Agent(expertise, task, input_type, output_type)
    
    # Initialize the model with the provided API key
    model = OpenAIModel(api_key=api_key, model="dall-e-2")
    sequential_flow = SequentialFlow(agent, model)

# Streamlit UI
st.title("Interior Designer")
st.sidebar.title("Configuration")

# Input field for API key
api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")

# Dropdown for interior design styles
styles = ["Modern", "Contemporary", "Minimalist", "Industrial", "Scandinavian", "Traditional", "Bohemian"]
selected_style = st.sidebar.selectbox("Select an interior design style:", styles)

# Dropdown for types of rooms
rooms = ["Living Room", "Bedroom", "Kitchen", "Bathroom", "Dining Room", "Home Office", "Kids Room"]
selected_room = st.sidebar.selectbox("Select a room type:", rooms)

# Input box for further instructions
additional_instructions = st.sidebar.text_area("Any further instructions:")

# Submit button
if st.sidebar.button("Submit"):
    if api_key:
        initialize_agent_and_model(api_key)
        
        # Combine all user inputs to form a prompt
        prompt = f"Generate a Realistic looking Interior design with the following instructions: style: {selected_style}, Room type: {selected_room}, Instructions: {additional_instructions}"

        # Generate image using the prompt
        image_url = sequential_flow.execute(prompt)
        
        # Display the generated image on the main page
        st.image(image_url, caption="")
    else:
        st.sidebar.error("Please enter a valid OpenAI API key.")
