from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
import random
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
import os
import requests
import json
API_KEY = "AIzaSyBLyJJ-M0H5m6O9YrLJlXbCgmpJfPDiDrs"  # Replace with your actual API key

# URL for the Gemini API endpoint
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

from django.contrib import messages
from .models import *
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return render(request, 'register.html')


        # Create the user
        user = User(name=username, email=email, password1=password1,password2=password2)
        user.save()

        return redirect('login')  # Redirect to chat page after successful registration

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.objects.get(name=username, password1=password)
        if user is not None:
            request.session['name']=username
           
            return redirect('home')  # Redirect to chat page after successful login
        else:
            messages.error(request, "Invalid username or password")
            return render(request, 'login.html')

    return render(request, 'login.html')


def generate_prompt(user_input, history):
    """Craft the prompt for the API request including conversation history."""
    history_text = "\n".join(history)  # Combine all previous prompts and responses
    return {
        "contents": [{
            "parts": [{
                "text": f"{history_text}\nUser: {user_input}\nAI:"
            }]
        }]
    }

def make_api_request(prompt):
    """Make a request to the Gemini API and return the generated content."""
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(URL, headers=headers, data=json.dumps(prompt))

    if response.status_code == 200:
        result = response.json()
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return "No candidates found in the response."
    else:
        return f"Error: {response.status_code}, {response.text}"
    
def get_datetime():
    current_hour = datetime.now().hour
    if current_hour <12:
        return "Good morning! How can I help you?"
    elif  12 <= current_hour < 18 :
        return "Good afternoon! How can I help you?"
    else :
        return "Good evening! How can I help you?"




# @csrf_exempt
# def chatbot_response(request):
#     if 'name' in request.session:
#         if request.method == "POST":
#             user_message = request.POST.get('message')

#             if not user_message:
#                 return JsonResponse({"response": "I didn't receive any message. Please try again."})

#             # Initialize or retrieve the history from the session
#             history = request.session.get('history', [])
#             x1="who are you? who are you you your u what is your name who is your developer?"
#             if user_message.lower() == 'exit':
#                 request.session.flush()  # Clear the session
#                 return JsonResponse({"response": "Thank you! The conversation has ended."})
            
#             elif user_message.lower() in x1 :
                
#                 return JsonResponse({"response": "I am Ruby.What can i help you today?"})
                

#             # Generate the prompt based on current and previous messages
#             prompt = generate_prompt(user_message, history)
#             generated_content = make_api_request(prompt)

#             # Append the interaction to the history
#             history.append(f"User: {user_message}")
#             history.append(f"AI: {generated_content}")

#             # Save the updated history in the session
#             request.session['history'] = history
#             print(generated_content)
#             text = "hello world"
#             print(text.replace("world", "Python"))
#             w=UserPrompt(user=request.session['name'],user_message=user_message,chatbot_response=generated_content)
            
#             if generated_content in "*" or "#":
#                 d=generated_content.replace("*"," ").replace("#"," ")   
#                 return JsonResponse({"response": d})
#             return JsonResponse({"response": generated_content})

#     # Render the chat interface on GET requests
#     return render(request, 'chat.html', {'data': get_datetime()}) 

@csrf_exempt
def chatbot_response(request):
    if 'name' in request.session:
        if request.method == "POST":
            user_message = request.POST.get('message')

            if not user_message:
                return JsonResponse({"response": "I didn't receive any message. Please try again."})

            # Initialize or retrieve the history from the session
            history = request.session.get('history', [])
            exit_keywords = ["exit", "quit"]

            if user_message.lower() in exit_keywords:
                request.session.flush()  # Clear the session
                return JsonResponse({"response": "Thank you! The conversation has ended."})

            # Generate the prompt based on current and previous messages
            prompt = generate_prompt(user_message, history)
            generated_content = make_api_request(prompt)

            # Append the interaction to the history
            history.append(f"User: {user_message}")
            history.append(f"AI: {generated_content}")

            # Save the updated history in the session
            request.session['history'] = history
            
            # Retrieve the User instance
            try:
                user = User.objects.get(name=request.session['name'])
            except User.DoesNotExist:
                return JsonResponse({"error": "User not found"}, status=400)

            # Save prompt and response to the database
            UserPrompt.objects.create(user=user, user_message=user_message, chatbot_response=generated_content)

            # Return the generated content
            return JsonResponse({"response": generated_content})

    # Render the chat interface on GET requests
    return render(request, 'chat.html', {'data': get_datetime()})


def chat_page(request):
    """Render the chat interface."""
    return render(request, 'chat.html')

def home(request):
    if 'name' in request.session:
        user=request.session['name']
        return render(request, 'home.html',{'user':user})
    else:
        return render(request,'home.html',{'user':None})




def user_prompt_history(request):
    if 'name' in request.session:
        # Fetch the user object using the username
        user = get_object_or_404(User, name=request.session['name'])

        # Now, retrieve the prompts associated with the user
        prompts = UserPrompt.objects.filter(user=user).order_by('-timestamp')

        return render(request, 'prompt_history.html', {'prompts': prompts,'user':request.session['name']})
    else:
        # Handle the case where the session does not have a username
        return render(request, 'login.html')  # Redirect to login or show an error
    
def logout_view(request):
    if 'name' in request.session:
        del request.session['name']
        return redirect('home')  # Redirect to the homepage or login page after logout
    return render (request,'chat.html')


#____________________________________________________________________________________
# os.getenv("AIzaSyBLyJJ-M0H5m6O9YrLJlXbCgmpJfPDiDrs")
# genai.configure(api_key="AIzaSyBLyJJ-M0H5m6O9YrLJlXbCgmpJfPDiDrs")
# model = genai.GenerativeModel("gemini-1.5-flash")

# responses = {
#     'hi': ['Hii there!', 'Hello buddy!', 'Hey human!', "What's up?", 'Hola!'],
    
#     'hello': ['Hello! How are you?', 'Heyy buddy! How can I help you?', 
#               'Hi there! Anything I can assist with?', 'Hello, human! Glad to meet you!'],


#     'how are you': ['I am good! How are you?', 'Hey, thanks for asking, I am good! How are you doing?', 
#                     'Feeling chatty today! How are you?', "I am just a bot, but I'm doing great!"],

#     'bye': ['Bye! Have a good day.', 'Goodbye! Come back soon!', 'See ya! Stay awesome.', 
#             'Take care! It was nice talking to you.'],

#     'what is your name': ['I am ChatBot 1.0!', 'Just call me Bot! What’s your name?', 
#                          'I go by many names... but you can call me your friendly chatbot.'],
    
#     'thank you': ['You’re welcome!', 'Anytime!', 'Glad I could help!', 'No problem, happy to assist!',
#                   "You bet! I'm always here to help.", "No worries, it's all in a day's work!"],

#     'who made you': ['I was created by a curious learner!', 
#                      'A brilliant human crafted me! 😊', 
#                      'Some code, some love, and here I am!',
#                      "I was crafted by a brilliant human with lots of love and code.",
#                      "A curious coder brought me to life!",
#                      "I am a creation of code, crafted for good conversations."],

#     'what can you do': ['I can chat with you! Ask me anything.', 
#                         'I can respond to your messages, and keep you company.', 
#                         'I’m here to assist you with small tasks.'],

#     'tell me a joke': ['Why don’t skeletons fight each other? They don’t have the guts!', 
#                        'What do you get if you cross a snowman and a vampire? Frostbite!', 
#                        'Why was the math book sad? It had too many problems.'],

#     'do you like humans': ['Of course! You’re fascinating creatures.', 
#                            'I find humans quite interesting.', 'Yes! Without you, I wouldn’t exist.'],

#     'what is your purpose': ['To assist and keep you company!', 
#                              'To chat with you and make your day better.', 
#                              'I live to serve! (Or just chat, really.)'],
#     'you are amazing': ["Aw, thank you! You're amazing too!",
#                         "You're too kind!","Glad to hear that! You're awesome yourself.",
#                         "Thanks! I'm just doing my best."],
#     'joke': [
#         "Why don't skeletons fight each other? They don't have the guts!",
#         "What do you call fake spaghetti? An impasta!",
#         "Why did the bicycle fall over? It was two-tired!",
#         "Why don't oysters share their pearls? Because they are shellfish!",
#         "I told my computer I needed a break, and now it won't stop sending me Kit-Kats.",
#         "Why can't you trust an atom? They make up everything!",
#         "What did the zero say to the eight? Nice belt!",
#         "How does the moon cut his hair? Eclipse it!",
#         "Why did the scarecrow win an award? Because he was outstanding in his field!",
#         "What's orange and sounds like a parrot? A carrot!",
#         "I used to play piano by ear, but now I use my hands.",
#         "Why are ghosts bad at lying? Because you can see right through them!",
#         "What do you get when you cross a snowman with a vampire? Frostbite!",
#         "Why was the broom late? It swept in traffic!",
#         "What do you call a bear with no teeth? A gummy bear!",
#         "How do trees get online? They log in.",
#         "Why don't eggs tell jokes? They'd crack each other up!",
#         "I'm reading a book on anti-gravity. It's impossible to put down!",
#         "Did you hear about the restaurant on the moon? Great food, no atmosphere!",
#         "Why can't your nose be 12 inches long? Because then it would be a foot!",
#         "What do you call a fish wearing a crown? A kingfish!",
#         "Why did the tomato turn red? Because it saw the salad dressing!",
#         "Why did the coffee file a police report? It got mugged!",
#         "What do you call cheese that isn't yours? Nacho cheese!",
#         "I would tell you a construction joke… but I'm still working on it.",
#         "Why was the music teacher arrested? She got caught with too many notes!",
#         "What did one wall say to the other wall? I'll meet you at the corner.",
#         "What did the ocean say to the beach? Nothing, it just waved.",
#         "Why did the golfer bring two pairs of pants? In case he got a hole in one!",
#         "What do you call a lazy kangaroo? A pouch potato!",
#         "Why did the math teacher eat graph paper? She was hungry for knowledge.",
#         "How do cows stay up to date? They read the moos-paper!",
#         "Why did the stadium get hot after the game? All the fans left.",
#         "I used to have a fear of hurdles, but I got over it.",
#         "How do you organize a space party? You planet!",
#         "What do you get when you cross an elephant with a fish? Swimming trunks!",
#         "Why can't leopards play hide and seek? Because they're always spotted!",
#         "Why did the barber win the race? He knew all the short cuts.",
#         "What did the big flower say to the little flower? Hey, bud!",
#         "What kind of shoes do ninjas wear? Sneakers!",
#         "Why did the cookie go to the doctor? It was feeling crumby!",
#         "Why do bees have sticky hair? Because they use honeycombs!",
#         "Why did the banana go to the party? Because it was a-peeling!",
#         "How does a penguin build its house? Igloos it together!",
#         "Why don't calendars ever get tired? They always stay up to date!",
#         "What happens when frogs park illegally? They get toad!",
#         "Why did the computer catch a cold? It left its Windows open!",
#         "Why don't programmers like nature? It has too many bugs!",
#         ]
# }

# default_responses = {
#     'error' :[
#         "Oops! I didn't catch that. But how about a joke instead? 🃏",
#         "Hmm, that puzzled me! Need a joke to cheer up? 🎭",
#         "I'm not sure I got that right. Wanna hear a joke instead? 😂",
#         "Need some guidance? I can chat, answer questions, and tell jokes! Try asking, 'Can you tell me a joke?' 😁",
#         "I'm here to assist! Oh, and if you need a laugh, just say 'Tell me a joke!' 🤡",
#         "Bored? Never! But I do have a joke if you need some fun. Just say 'Tell me a joke!' 🎉",
#         "Hmm, I didn't quite get that. But I do know some great jokes! Want to hear one? 😂",
#         "Sorry, I missed that. But how about a joke to lighten the mood? 🤔",
#         "I'm not sure I understand, but I can make you laugh! Say 'Tell me a joke.'"]
# }

# def get_response(user_input):
#     user_input = user_input.lower()

#     if 'joke' in user_input:
#         return f"Oh, you're in for a good laugh! Here's one : {random.choice(responses['joke'])}"
#     for key in responses:
#         if key in user_input:
#             return random.choice(responses[key])
#     return random.choice(default_responses["error"])

#_________________________________________________________________________________________________


# def chatbot_response(request):
#     if request.method == "POST":
#         user_message = request.POST.get('message', '')
#         response = get_response(user_message)
#         return JsonResponse({"response": response})

