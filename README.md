*This is for 2025 Supercell AI Hackathon*

# RiddleSense

**An AI-powered lateral thinking puzzle game that adapts to your play style and guides you through the mystery with personalized, context-aware hints.**

## What is RiddleSense?

RiddleSense reimagines the traditional "Lateral Thinking Puzzle" (known as "Turtle Soup" in some Asian countries) by integrating a responsive AI assistant that understands the player's progress and provides tailored guidance. Our project transforms a classic puzzle format into an engaging, AI-enhanced experience that responds dynamically to each player's unique approach to solving mysteries.

## The Core Innovation

At the heart of RiddleSense is an AI system that:
- **Understands game context** - Tracks player questions, prior hints, and puzzle progress
- **Adapts responses** based on player behavior - offering more support when stuck, subtle guidance when making progress
- **Maintains narrative immersion** by responding in-character while still being helpful
- **Personalizes the puzzle experience** for each player's problem-solving style

## How It Works

1. **Choose Your Challenge**: Players select from various difficulty levels and themes
2. **Engage With the Mystery**: A puzzling scenario is presented where the solution isn't immediately obvious
3. **Ask Questions**: Players interact with our AI assistant through natural language questions
4. **Receive Contextual Guidance**: The AI provides hints that become progressively more helpful based on:
   - Previous questions asked
   - Time spent on the puzzle
   - Current progress toward the solution
   - Player engagement signals

## Technical Stack

- **Frontend**: Vue.js 3 with Vite and Element Plus for a responsive, modern UI
- **Backend**: Python-Flask server managing game state and AI interactions
- **AI Integration**: Gemini API with sophisticated prompt engineering for context-aware responses

## Project Structure

- `frontend/`: Vue.js application built with Vite
- `backend/`: Python Flask API that interfaces with Google's Gemini AI

## Setup Instructions

### Backend Setup

1. Navigate to the backend folder:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt --break-system-packages
   ```

3. Create a `.env` file in the backend directory with your Google Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. Start the Flask server:
   ```bash
   python -m flask run
   ```
   The backend will be available at http://localhost:5000

### Frontend Setup

1. Navigate to the frontend folder:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at http://localhost:5173

## Features

- Variety of puzzles with different difficulty levels and themes
- AI assistant that provides contextual hints and guidance
- Responsive design that works well on both desktop and mobile devices
- Modern UI with animations and visual effects

## Future Directions

We envision expanding RiddleSense to incorporate:
- A growing library of puzzles across diverse themes and difficulty levels
- Advanced player analytics to further refine AI assistance patterns
- Multiplayer modes where groups can collaborate to solve particularly challenging mysteries

## How to Play

1. Start the game to receive a lateral thinking puzzle
2. Ask yes/no questions to uncover more information about the situation
3. Try to solve the mystery by guessing what happened
4. The AI will guide you with hints if you're on the right track
5. Solve puzzles to earn points!

## Gameplay Flow

1. AI generates a puzzle with hidden solution based on selected difficulty and theme
2. Player asks questions that can be answered with Yes/No/Irrelevant
3. AI provides contextual guidance based on player's progress
4. Player solves the puzzle or can view the solution if needed
5. Play again with new challenges
