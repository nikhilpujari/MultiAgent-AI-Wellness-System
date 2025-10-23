# AI Wellness Multi-Agent System - Build Guide
## "Build an Autonomous Multi-Agent Workflow in 15 Minutes"

---

## 🎯 PART 1: PROJECT OVERVIEW & PLANNING (2 minutes)

### System Goal
Create an AI wellness assistant with specialized agents for fitness, nutrition, and health advice, featuring:
- Intelligent routing based on user queries
- Personalized responses using user profiles
- RAG (Retrieval Augmented Generation) for knowledge-based answers
- Comprehensive tracking and analytics dashboard

### Architecture Overview
```
User Query → Router Agent → Specialized Agent → Response
                ↓
        [Fitness] [Nutrition] [Health] [General]
                ↓
        Profile + RAG Context → Personalized Response
```

### Agents We'll Build
1. **Router Agent** - LLM-powered query classification
2. **Fitness Coach** - Workout advice and exercise guidance
3. **Nutrition Specialist** - Meal planning and dietary advice
4. **Doctor Avatar** - Health concerns with medical disclaimers
5. **General Agent** - Out-of-domain query handler

### User Flow
1. User enters query in Streamlit chat
2. Router classifies intent (fitness/nutrition/health/misc)
3. Appropriate agent processes with user profile + RAG context
4. Concise, personalized response returned
5. Data logged for analytics dashboard

### Tech Stack
- **LangGraph** - Multi-agent workflow orchestration
- **Streamlit** - Web interface
- **SQLModel** - Database ORM
- **OpenAI** - LLM for agents and routing
- **FAISS** - Vector search for RAG
- **SQLite** - Local database

---

## 📁 PART 2: PROJECT STRUCTURE SETUP (1 minute)

### Prompt for GPT:
```
Create the following folder structure for an AI wellness multi-agent system:

ai-wellness/
├── app/
│   ├── main_streamlit.py
│   ├── api.py
│   └── config.py
├── agents/
│   ├── router.py
│   ├── fitness_coach.py
│   ├── nutrition_specialist.py
│   ├── doctor_avatar.py
│   ├── graph.py
│   └── run_graph.py
├── tools/
│   ├── db.py
│   ├── rag.py
│   ├── nutrition_calculator.py
│   └── profile_analyzer.py
├── data/seed_docs/
│   ├── fitness.txt
│   ├── nutrition.txt
│   └── medical.txt
├── storage/
│   └── app.db
├── .env
└── requirements.txt

Create empty files with basic docstrings explaining their purpose.
```

---

## 🔧 PART 3: CORE DEPENDENCIES & CONFIG (1 minute)

### Prompt for requirements.txt:
```
Create a requirements.txt file for an AI wellness multi-agent system using:
- Streamlit for web interface
- LangGraph for multi-agent workflows
- SQLModel for database ORM
- OpenAI for LLM integration
- FAISS for vector search
- Python-dotenv for environment variables
- Pandas for data manipulation

Include all necessary dependencies with appropriate versions.
```

### Prompt for config.py:
```
Create app/config.py with:
- Environment variable loading using dotenv
- Settings class with OpenAI API key, chat model, embedding model, database URL
- Default values for all configurations
- Clean, production-ready structure
```

### Prompt for .env template:
```
Create a .env file template with:
- OPENAI_API_KEY placeholder
- CHAT_MODEL (default: gpt-4o-mini)
- EMBEDDING_MODEL (default: text-embedding-3-small)
- DATABASE_URL (default: sqlite:///storage/app.db)
- DEBUG flag
```

---

## 🗄️ PART 4: DATABASE MODELS (2 minutes)

### Prompt for database schema:
```
Create tools/db.py with SQLModel classes for an AI wellness system:

Required tables:
1. **UserProfile** - Complete user health profile with:
   - Basic info: age, gender, height, weight
   - Health info: conditions, medications, allergies, stress level
   - Goals: primary goal, target weight, fitness experience
   - Calculated: BMI, body age, daily calorie goal
   - Timestamps: created_at, updated_at

2. **DailyNutrition** - Meal tracking with:
   - User, date, meal_type (breakfast/lunch/dinner)
   - Food items, calories, macros (protein, carbs, fat, fiber)

3. **WorkoutSession** - Exercise logging with:
   - User, date, workout_type, exercise_name
   - Duration, calories burned, intensity, notes

4. **Meal** & **Workout** - Legacy simple tracking tables

Include:
- Proper field types and constraints
- Timezone-aware datetime defaults
- Database initialization function
- Session management helper
```

---

## 🧠 PART 5: RAG SYSTEM (2 minutes)

### Prompt for RAG implementation:
```
Create tools/rag.py with a FAISS-based RAG system:

Features needed:
- Embed text chunks using OpenAI embeddings
- Build FAISS index from documents in data/seed_docs/
- Search function that returns top-k relevant chunks
- Index persistence (save/load from files)
- Document chunking by paragraphs
- Metadata tracking for source files

Functions:
- embed_texts(texts) - Get embeddings from OpenAI
- build_index() - Process all docs and create FAISS index
- search(query, k=3) - Find relevant chunks for query

Use text-embedding-3-small model and normalize vectors for cosine similarity.
```

### Prompt for seed documents:
```
Create three knowledge base files:

1. **data/seed_docs/fitness.txt** - Comprehensive fitness guide with:
   - Exercise fundamentals and safety
   - Workout types (cardio, strength, flexibility)
   - Progressive overload principles
   - Recovery and rest importance
   - Sample workout routines
   - Motivation and mindset tips

2. **data/seed_docs/nutrition.txt** - Complete nutrition guide with:
   - Balanced diet principles
   - Macronutrient roles and sources
   - Meal planning strategies
   - Hydration guidelines
   - Sample meal plans
   - Sustainable eating habits

3. **data/seed_docs/medical.txt** - Health information with:
   - General wellness guidelines
   - Common conditions and remedies
   - Mental health and stress management
   - Sleep hygiene practices
   - When to seek professional help
   - Important medical disclaimers

Each file should be 200-300 words with actionable, evidence-based content.
```

---

## 🤖 PART 6: INTELLIGENT ROUTER AGENT (2 minutes)

### Prompt for router agent:
```
Create agents/router.py with an intelligent LLM-powered router:

Requirements:
- RouterAgent class with classify() method
- Use OpenAI to classify queries into: fitness, nutrition, health, misc
- Detailed classification prompt with clear category definitions
- Fallback keyword-based classification if LLM fails
- Comprehensive keyword lists for each domain
- Logging with streamlit st.write() for visibility
- Temperature=0.1 for consistent classification
- Error handling and graceful fallbacks

The router should handle queries like:
- "I want to start working out" → fitness
- "What should I eat for breakfast?" → nutrition  
- "I'm feeling anxious" → health
- "What's the weather?" → misc

Include extensive keyword lists and robust error handling.
```

---

## 👥 PART 7: SPECIALIZED AGENTS (3 minutes)

### Prompt for fitness coach:
```
Create agents/fitness_coach.py with a personalized fitness coach:

FitnessCoachAgent class with:
- respond(user, message) method
- User profile integration for personalized advice
- RAG context search for fitness knowledge
- Concise responses (2-3 sentences max)
- Workout logging to database
- Streamlit logging for workflow visibility
- Safety-first approach with proper form emphasis
- Goal-oriented advice based on user profile

The agent should:
- Pull user's fitness level, goals, and health conditions
- Search RAG for relevant fitness context
- Generate personalized, actionable advice
- Log the interaction as a workout entry
- Be encouraging and motivational
```

### Prompt for nutrition specialist:
```
Create agents/nutrition_specialist.py with a certified nutrition coach:

NutritionAgent class with:
- respond(user, message) method  
- User profile integration (calorie goals, allergies, health conditions)
- RAG context search for nutrition knowledge
- Concise, helpful responses (2-3 sentences max)
- Meal logging to database
- Consideration of dietary restrictions and goals
- Practical meal suggestions and tips
- Sustainable habit focus

The agent should provide specific, actionable nutrition advice tailored to the user's goals and restrictions.
```

### Prompt for doctor avatar:
```
Create agents/doctor_avatar.py with a health information assistant:

DoctorAgent class with:
- respond(question, user) method
- Strong medical disclaimers
- User profile integration for context
- RAG search for health information
- Concise, empathetic responses
- Clear guidance on when to seek professional help
- Focus on general wellness and common concerns
- Never provide specific medical diagnoses

Include prominent disclaimer: "⚠️ I'm not a doctor. This is educational only."
```

---

## 🕸️ PART 8: LANGGRAPH WORKFLOW (2 minutes)

### Prompt for graph orchestration:
```
Create agents/graph.py with LangGraph workflow orchestration:

Components needed:
1. **GraphState** - Pydantic model with user and messages
2. **Node functions** - Wrapper functions for each agent
3. **Routing logic** - Dynamic routing based on intent
4. **Graph builder** - Construct and compile the workflow

Workflow:
- Entry point: router_node
- Conditional routing to: fitness_node, nutrition_node, doctor_node, general_node
- All nodes end at END
- Handle message passing correctly (get original user message, not routing decision)
- Include general_node for misc queries with re-routing capability

Create build_graph() function that returns compiled workflow.
```

### Prompt for workflow runner:
```
Create agents/run_graph.py with workflow execution:

Simple interface:
- Import and compile the graph once
- run_agent(user, msg) function
- Streamlit logging for workflow visibility
- Return final agent response
- Handle errors gracefully

This should be the main entry point for the Streamlit app to interact with agents.
```

---

## 🎨 PART 9: STREAMLIT INTERFACE (2 minutes)

### Prompt for main application:
```
Create app/main_streamlit.py with a comprehensive wellness dashboard:

Required pages:
1. **Chat** - Multi-agent conversation interface
2. **Profile** - Complete user profile management
3. **Meal Logger** - Daily nutrition tracking
4. **Workout Logger** - Exercise session logging  
5. **Dashboard** - Analytics and insights

Chat page features:
- Proper chat message components (st.chat_message)
- Real-time agent workflow logging
- Clear visual distinction between user and AI
- Example prompts and clear chat button

Profile page features:
- Tabbed interface (Basic Info, Health Info, Goals, Analysis)
- BMI calculation and body age analysis
- Comprehensive health questionnaire
- AI-powered health insights and recommendations

Dashboard features:
- Calorie balance tracking (in vs out)
- 7-day nutrition and workout analytics
- Visual charts and trends
- Weekly summaries with weight change estimates

Use modern Streamlit components and clean, professional styling.
```

---

## 🔬 PART 10: ADVANCED FEATURES (Optional - if time permits)

### Prompt for profile analyzer:
```
Create tools/profile_analyzer.py with health analysis capabilities:

ProfileAnalyzer class with:
- BMI calculation and categorization
- AI-powered body age estimation
- Daily calorie needs calculation (Mifflin-St Jeor equation)
- Health score generation
- Personalized recommendations

Use OpenAI to analyze user profile and provide insights on biological age vs chronological age.
```

### Prompt for nutrition calculator:
```
Create tools/nutrition_calculator.py with AI-powered nutrition analysis:

NutritionCalculator class with:
- calculate_nutrition(food_items) method
- LLM-based calorie and macro estimation
- Realistic portion size assumptions
- JSON-formatted response with breakdown
- Error handling with fallback values

Should handle inputs like "2 eggs, 1 slice toast, orange juice" and return detailed nutrition info.
```

---

## 🚀 SETUP & RUN COMMANDS

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your OpenAI API key:
# OPENAI_API_KEY=your_actual_api_key_here
```

### 3. Initialize Database & RAG
```bash
# Build RAG index from seed documents
python -c "from tools.rag import build_index; build_index()"

# Database will be initialized automatically on first run
```

### 4. Run the Application
```bash
# Start Streamlit app
streamlit run app/main_streamlit.py

# Alternative: Run with specific port
streamlit run app/main_streamlit.py --server.port 8501
```

### 5. Optional: API Server
```bash
# Run FastAPI server (if needed)
uvicorn app.api:app --reload --port 8000
```

## 🚀 FINAL INTEGRATION CHECKLIST

### Before running:
1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Set up .env with OpenAI API key
3. ✅ Initialize database: Run app once to create tables
4. ✅ Build RAG index: `python -c "from tools.rag import build_index; build_index()"`
5. ✅ Test agent routing with sample queries

### Run the application:
```bash
streamlit run app/main_streamlit.py
```

### Test scenarios:
- "I want to start working out" → Should route to fitness coach
- "What should I eat for breakfast?" → Should route to nutrition specialist  
- "I'm feeling anxious" → Should route to doctor avatar
- "What's the weather?" → Should route to general agent

---

## 🎬 VIDEO SCRIPT OUTLINE

1. **Intro (30s)** - Show final working system
2. **Architecture (1m)** - Explain multi-agent concept
3. **Setup (2m)** - Project structure and dependencies
4. **Database (2m)** - Models and RAG system
5. **Agents (4m)** - Router and specialized agents
6. **Workflow (2m)** - LangGraph orchestration
7. **Interface (3m)** - Streamlit dashboard
8. **Demo (30s)** - Live testing and results

Total: ~15 minutes

---

This guide provides exact prompts to recreate your AI Wellness Multi-Agent System with all current features including profile management, nutrition tracking, workout logging, and comprehensive analytics dashboard.