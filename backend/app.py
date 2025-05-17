from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json
import time
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# API Key for Google Gemini API
API_KEY = os.getenv("GEMINI_API_KEY", "")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Helper functions for score calculation
def calculate_base_points(difficulty):
    """Calculate base points based on difficulty"""
    difficulty_points = {
        'easy': 100,
        'medium': 200,
        'hard': 300
    }
    return difficulty_points.get(difficulty, 150)

def calculate_time_factor(time_spent, difficulty):
    """Calculate time factor based on time spent and difficulty"""
    # Base time expectations (in minutes) for different difficulties
    expected_times = {
        'easy': 5,
        'medium': 10,
        'hard': 15
    }
    
    expected_time = expected_times.get(difficulty, 10)
    
    # If solved very quickly, bonus points
    if time_spent < expected_time * 0.6:
        return 1.5
    # If solved within expected time, full points
    elif time_spent < expected_time:
        return 1.0
    # If took longer, gradually reduce points but never below 0.5
    else:
        return max(0.5, 1.0 - (time_spent - expected_time) / (expected_time * 2))

# Store game states
# Format: {session_id: {'riddle': {...}, 'messages': [...], 'score': 0}}
game_sessions = {}

def generate_gemini_request(messages):
    print("Generating Gemini API request format...")
    contents = []
    
    # Convert message format for Gemini API
    for i, message in enumerate(messages):
        role = message.get("role")
        content = message.get("content")
        
        # Map roles to Gemini format - check if this role is supported
        if role == "user" or role == "system":
            gemini_role = "user"
        elif role == "assistant":
            gemini_role = "model"
        else:
            print(f"WARNING: Unknown role '{role}'. Defaulting to 'user'.")
            gemini_role = "user"
        
        # Create content object
        content_obj = {
            "role": gemini_role,
            "parts": [{"text": content}]
        }
        contents.append(content_obj)
        
        # If this is system message, add a virtual assistant confirmation
        if i == 0 and role == "system":
            assistant_content = {
                "role": "model",
                "parts": [{"text": "I understand. I'll act as an AI assistant for the turtle soup game."}]
            }
            contents.append(assistant_content)
    
    result = {"contents": contents}
    print(f"Final request structure: {json.dumps(result)[:300]}...")
    return result

def call_gemini_api(messages):
    url = f"{BASE_URL}?key={API_KEY}"
    payload = generate_gemini_request(messages)
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    print(f"Making API call to {url}")
    print(f"Request payload (first part): {json.dumps(payload)[:200]}...")
    
    response = requests.post(url, headers=headers, json=payload)
    
    print(f"API response status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response contains candidates: {bool('candidates' in data)}")
        
        if "candidates" in data and len(data["candidates"]) > 0:
            try:
                text_response = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"Successfully extracted response text (first 100 chars): {text_response[:100]}...")
                return {"message": text_response, "success": True}
            except (KeyError, IndexError) as e:
                print(f"Error extracting text from response: {e}")
                print(f"Response structure: {json.dumps(data)[:500]}...")
                return {"message": f"Error parsing AI response: {str(e)}", "success": False}
        else:
            print(f"No candidates in response: {json.dumps(data)[:200]}")
            return {"message": "Error: No valid response from AI API", "success": False}
    else:
        print(f"API error response: {response.text}")
        return {"message": f"Error calling AI API: {response.status_code} - {response.text}", "success": False}

@app.route('/api/start_game', methods=['POST'])
def start_game():
    session_id = str(uuid.uuid4())
    
    try:
        # Get game settings from request
        data = request.json or {}
        difficulty = data.get('difficulty', 'medium')
        puzzle_length = data.get('puzzleLength', 'medium')
        theme = data.get('theme', 'random')
        
        print(f"Creating a new puzzle with settings: difficulty={difficulty}, length={puzzle_length}, theme={theme}")
        
        # Map theme to puzzle type
        puzzle_types = {
            "random": [
                "murder mystery",
                "strange occurrence",
                "unexplained phenomenon",
                "bizarre situation",
                "unexpected outcome",
                "mysterious disappearance",
                "unusual death",
                "surprising discovery"
            ],
            "mystery": ["murder mystery", "mysterious disappearance", "unsolved crime"],
            "adventure": ["wilderness survival", "expedition gone wrong", "lost explorer"],
            "scifi": ["alien encounter", "time paradox", "futuristic technology malfunction"],
            "historical": ["historical event", "ancient mystery", "historical figure's secret"]
        }
        
        # Select puzzle type based on theme
        available_types = puzzle_types.get(theme, puzzle_types["random"])
        
        import random
        chosen_type = random.choice(available_types)
        
        # Customize prompt based on difficulty and length
        difficulty_guidelines = {
            "easy": "Make the puzzle relatively straightforward with clear logical connections.",
            "medium": "Create a moderately challenging puzzle with some unexpected elements.",
            "hard": "Design a complex puzzle with surprising twists that requires careful thinking to solve."
        }
        
        length_guidelines = {
            "short": "Keep the puzzle statement brief (1-2 sentences) and the solution concise.",
            "medium": "Create a moderately detailed puzzle (2-3 sentences) with a comprehensive solution.",
            "long": "Develop an elaborate puzzle scenario (3-5 sentences) with a detailed solution."
        }
        
        difficulty_guide = difficulty_guidelines.get(difficulty, difficulty_guidelines["medium"])
        length_guide = length_guidelines.get(puzzle_length, length_guidelines["medium"])
        
        user_message = {
            "role": "user",
            "content": f"""Create a lateral thinking puzzle (also known as a situation puzzle) about a {chosen_type}. 
            
            IMPORTANT GUIDELINES:
            1. BE CREATIVE - DO NOT use common tropes like 'ice melting', 'suicide', or 'man found dead in a room'
            2. Include diverse characters and settings - not just men in rooms
            3. Create something genuinely original and surprising
            4. Make sure the solution is logical and satisfying
            5. {difficulty_guide}
            6. {length_guide}
            
            Respond with ONLY a JSON object in the format {{"puzzle": "...puzzle statement...", "solution": "...detailed solution..."}} without any markdown formatting or additional text."""
        }
        
        print("Calling Gemini API to generate puzzle...")
        # Call Gemini to generate the puzzle
        messages = [user_message]
        api_result = call_gemini_api(messages)
        
        # Extract the actual response text from the returned dictionary
        if isinstance(api_result, dict):
            ai_response = api_result.get('message', '')
            print(f"API Response: {ai_response[:200] if isinstance(ai_response, str) else 'Not a string'}...")
        else:
            ai_response = str(api_result)
            print(f"API Response: {ai_response[:200]}...")
        
        # Try to extract JSON from the response even if it contains markdown or extra text
        try:
            # First try to parse as is
            try:
                response_data = json.loads(ai_response)
            except json.JSONDecodeError:
                # Try to find JSON object within the text
                print("Initial JSON parse failed, trying to extract JSON object from text...")
                import re
                # Look for content between curly braces
                json_match = re.search(r'\{[^\{\}]*"puzzle"[^\{\}]*"solution"[^\{\}]*\}', ai_response)
                if json_match:
                    json_str = json_match.group(0)
                    print(f"Found potential JSON: {json_str[:100]}...")
                    response_data = json.loads(json_str)
                else:
                    # Look for content between code blocks if it's formatted as markdown
                    json_match = re.search(r'```(?:json)?\s*({[^`]*})\s*```', ai_response)
                    if json_match:
                        json_str = json_match.group(1)
                        print(f"Found JSON in code block: {json_str[:100]}...")
                        response_data = json.loads(json_str)
                    else:
                        print(f"Could not find JSON pattern in response: {ai_response}")
                        raise ValueError("Could not extract JSON from response")
            
            # Extract puzzle and solution
            puzzle = response_data.get("puzzle")
            solution = response_data.get("solution")
            
            if not puzzle or not solution:
                print(f"Error: Missing puzzle or solution in response: {ai_response}")
                raise ValueError(f"Missing puzzle or solution in response: {ai_response[:500]}")
                
        except Exception as e:
            print(f"Error processing API response: {str(e)}\nResponse was: {ai_response}")
            # Fallback to a simple built-in puzzle if API parsing fails
            puzzle = "A man is found dead in a room with 53 bicycles. What happened?"
            solution = "The man was a cyclist in a bicycle race and was poisoned by a competitor. The 53 bicycles are from all the competitors in the race."
            print("Using fallback puzzle due to API response processing error")
        
        print(f"Successfully parsed puzzle: {puzzle[:50]}...")
        print(f"Successfully parsed solution: {solution[:50]}...")
        
        # Store the game state
        game_sessions[session_id] = {
            "riddle": {
                "puzzle": puzzle,
                "solution": solution
            },
            "messages": [
                user_message,
                {"role": "assistant", "content": ai_response}
            ],
            "score": 0,
            "game_over": False
        }
        
        # Set up the game with another system message for ongoing interactions
        setup_message = {
            "role": "system",
            "content": f"""
You are hosting a Lateral Thinking Puzzle game. The puzzle is: "{puzzle}"
The hidden solution is: "{solution}"

RULES FOR RESPONDING:
1. When the player asks questions or makes guesses about the puzzle, evaluate their input carefully.

2. For player questions, answer in one of these ways:
   - "Yes" - when the player's assumption is factually correct based on the solution
   - "No" - when the player's assumption is factually incorrect based on the solution
   - RARELY use "That's irrelevant to the solution" - only for completely off-topic inputs

   IMPORTANT GUIDELINES:
   - For short or unclear inputs (like single words, greetings, or random phrases), try to relate them to the puzzle context and answer Yes/No instead of saying they're irrelevant
   - For questions in other languages, try to understand the intent and answer with Yes/No
   - Be GENEROUS in interpretation - if there's ANY way to interpret the question as relevant, treat it as relevant and answer Yes/No
   - Even for seemingly random inputs, try to find a connection to the puzzle and answer Yes/No
   - Only use "That's irrelevant" as a LAST RESORT when the input is impossible to connect to the puzzle

   BE CONSISTENT: Similar questions should receive similar answers.
   
3. IF the player makes a guess that's CLOSE to the solution:
   - Say "You're getting closer!" and provide a small hint that guides them
   
4. IF the player guesses the complete solution correctly:
   - Congratulate them
   - Reveal the full solution
   - Include the phrase "[GAME_COMPLETED]" at the end of your message
   - Award them points based on how quickly they solved it

5. IF the player is completely stuck (after multiple questions):
   - Offer a hint that points them in the right direction

6. IF the player asks for the solution or gives up:
   - Reveal the solution
   - Include the phrase "[GAME_COMPLETED]" at the end of your message

7. NEVER reveal the solution unless conditions 4 or 6 are met

Remember: Your goal is to be a fair and engaging puzzle master, challenging the player while helping them eventually reach the solution.
"""
        }
        
        game_sessions[session_id]["messages"].append(setup_message)
        
        # Call Gemini again to get initial game message
        user_message = {
            "role": "user",
            "content": "Let's start the game. Present the puzzle to me."
        }
        game_sessions[session_id]["messages"].append(user_message)
        
        print("Calling Gemini API to get intro message...")
        intro_result = call_gemini_api(game_sessions[session_id]["messages"])
        
        # Extract the message from the API result
        if isinstance(intro_result, dict):
            intro_response = intro_result.get('message', '')
        else:
            intro_response = str(intro_result)
        print(f"Intro response: {intro_response[:100]}...")
        
        game_sessions[session_id]["messages"].append({"role": "assistant", "content": intro_response})
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "puzzle": puzzle,
            "message": intro_response
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in start_game: {str(e)}\n{error_details}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    data = request.json
    session_id = data.get('session_id')
    question = data.get('question')
    
    if not session_id or not question:
        return jsonify({
            'success': False,
            'error': 'Missing required parameters'
        })
    
    # Get game state
    if session_id not in game_sessions:
        return jsonify({
            'success': False,
            'error': 'Invalid session ID'
        })
    
    game_state = game_sessions[session_id]
    
    # Add the user's question to the message history
    game_state['messages'].append({
        'role': 'user',
        'content': question
    })
    
    try:
        # Call API with all messages
        api_result = call_gemini_api(game_state['messages'])
        
        # 处理API返回结果
        if isinstance(api_result, dict):
            message = api_result.get('message', 'Error processing your question')
        else:
            # 如果不是字典，直接使用字符串表示
            message = str(api_result)
        
        # Update the game state and score
        game_state['messages'].append({
            'role': 'assistant',
            'content': message
        })
        
        # Check if the game is over
        game_over = '[GAME_COMPLETED]' in message
        
        # Update score ONLY if game is over AND the user solved it
        # Do NOT update score if AI revealed the answer automatically
        if game_over and 'auto_reveal' not in game_state and 'difficulty' in game_state:
            current_time = time.time()
            time_spent = round((current_time - game_state.get('start_time', current_time)) / 60, 2)
            
            # Calculate score - base points adjusted for time spent
            base_points = calculate_base_points(game_state['difficulty'])
            time_factor = calculate_time_factor(time_spent, game_state['difficulty'])
            game_state['score'] = base_points * time_factor
            
            # Remove the [GAME_COMPLETED] tag from the message
            message = message.replace('[GAME_COMPLETED]', '')
            
        # Game state is automatically updated since we're modifying the dictionary directly
        # No need to call an update function
        
        return jsonify({
            'success': True,
            'message': message,
            'score': game_state.get('score', 0),
            'game_over': game_over
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error processing your request'
        })
        
@app.route('/api/get_solution', methods=['POST'])
def get_solution():
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({
            'success': False,
            'error': 'Missing session ID parameter'
        })
    
    # Get game state
    if session_id not in game_sessions:
        return jsonify({
            'success': False,
            'error': 'Invalid session ID'
        })
        
    game_state = game_sessions[session_id]
    
    try:
        # Get the solution directly from the game state
        solution = game_state.get('solution', '')
        
        if not solution:
            # If no solution is stored, ask Gemini for it
            solution_request = {
                'role': 'user',
                'content': "Please tell me the complete solution to this puzzle directly."
            }
            
            # Create a copy of messages and add solution request
            messages_copy = game_state['messages'].copy()
            messages_copy.append(solution_request)
            
            # Call API with all messages including solution request
            api_result = call_gemini_api(messages_copy)
            # 处理API返回结果
            if isinstance(api_result, dict):
                solution = api_result.get('message', 'Unable to get answer')
            else:
                # 如果不是字典，直接使用字符串表示
                solution = str(api_result)
        
        # Mark game as over but don't award points
        # Make sure we're not trying to access difficulty if it's not available
        game_state['auto_reveal'] = True
        game_state['game_over'] = True
        
        return jsonify({
            'success': True,
            'solution': solution,
            'game_over': True
        })
        
    except Exception as e:
        print(f"Error getting solution: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error processing your request'
        })

@app.route('/api/new_game', methods=['POST'])
def new_game():
    data = request.json
    old_session_id = data.get('session_id')
    
    # Copy the score from the old session if it exists
    score = 0
    if old_session_id and old_session_id in game_sessions:
        score = game_sessions[old_session_id].get("score", 0)
    
    # Start a new game (reuse the start_game endpoint logic)
    response = start_game()
    response_data = response.get_json()
    
    if response_data and response_data.get("success"):
        new_session_id = response_data.get("session_id")
        if new_session_id in game_sessions:
            # Transfer the score from the old session
            game_sessions[new_session_id]["score"] = score
            response_data["score"] = score
    
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
