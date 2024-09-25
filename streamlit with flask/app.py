from flask import Flask, request, jsonify
from flask_cors import CORS
from Interior_design.agent import Agent, Task, InputType, OutputType
from Interior_design.openai_model import OpenAIModel
from Interior_design.arch import SequentialFlow

app = Flask(__name__)
CORS(app)

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

@app.route('/api/generate_image', methods=['POST'])
def generate_image():
    data = request.json
    api_key = data.get('api_key')
    style = data.get('style')
    room = data.get('room')
    instructions = data.get('instructions')
    
    initialize_agent_and_model(api_key)
    prompt = f"Generate a Real Interior design with the following instructions: style: {style}, Room type: {room}, Instructions: {instructions}"
    image_url = sequential_flow.execute(prompt)
    
    return jsonify({'image_url': image_url})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
