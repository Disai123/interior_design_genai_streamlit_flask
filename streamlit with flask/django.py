import base64
import os
import json
import jwt
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from openai import OpenAI
from interior_design.agent import Agent, Task, InputType, OutputType
from interior_design.openai_model import OpenAIModel
from interior_design.arch import SequentialFlow
from .database import SQLiteDB

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
expertise = "Interior Desinger"
task = Task("Image Generation")
input_type = InputType("Text")
output_type = OutputType("Image")
agent = Agent(expertise, task, input_type, output_type)
api_key = OPENAI_API_KEY
jwt_secret = "my_sampe_token"
db = SQLiteDB()

def checkQuota(user):
    user_details = db.get_user_data(user)
    quota = user_details[1]
    count = user_details[2]
    if quota != 'FREE':
        return True, count, quota
    else:
        if 0 < count <= 10:
            return True, count, quota
        else:
            return False, count, quota

# This is for the generation of the image from the text
@csrf_exempt
def genAIPrompt2(request):
    if request.method == "POST":
        model = OpenAIModel(api_key=api_key, model="dall-e-2")
        sequential_flow = SequentialFlow(agent, model)
        selected_style = request.POST["selected_style"]
        selected_room_color = request.POST["selected_room_color"]
        selected_room_type = request.POST["selected_room_type"]
        number_of_room_designs = request.POST["number_of_room_designs"]
        additional_instructions = request.POST["additional_instructions"]
        username = request.POST["username"]
        stat, count, quota = checkQuota(username)
        if stat:
            prompt = f"Generate a Realistic looking Interior design with the following instructions: style: {selected_style}, Room Color: {selected_room_color}, Room type: {selected_room_type}, Number of designs: {number_of_room_designs}, Instructions: {additional_instructions}"
            image_url = sequential_flow.execute(prompt)
            print(image_url)
            if quota == "FREE":
                db.update_count(username)
                count -= 1
            return HttpResponse(json.dumps({"image": image_url, "status": "Success", "count": count}),
                                content_type="application/json")
        else:
            return HttpResponse(json.dumps({"image": "NA", "status": "Quota limit exceeded", "count": count}),
                                content_type="application/json")

# This is for the conversion of the three images to the single image.
@csrf_exempt
def generateImage(request):
    if request.method == "POST":
        model = OpenAIModel(api_key=api_key, model="dall-e-2")
        sequential_flow = SequentialFlow(agent, model)
        selected_style = request.FILES["selected_style"]
        selected_room_color = request.FILES["selected_room_color"]
        selected_room_type = request.FILES["selected_room_type"]
        s_style = base64.b64encode(selected_style.read()).decode('utf-8')
        s_room_c = base64.b64encode(selected_room_color.read()).decode('utf-8')
        s_room_t = base64.b64encode(selected_room_type.read()).decode('utf-8')
        user_name = jwt.decode(request.headers['token'], key=jwt_secret, algorithms=["HS256", ])["usename"]
        stat, count, quota = checkQuota(user_name)
        if stat:
            prompt = f"Generate a final Image based on the 3 input images provided: Image_1={s_style}, Image_2={s_room_c}, " \
                     f"Image_3={s_room_t}"
            image_url = sequential_flow.execute(prompt)
            if quota == "FREE":
                db.update_count(user_name)
                count -= 1
            return HttpResponse(json.dumps({"image": image_url, "status": "Success", "count": count}),
                                content_type="application/json")
        else:
            return HttpResponse(json.dumps({"image": "NA", "status": "Quota limit exceeded", "count": count}),
                                content_type="application/json")