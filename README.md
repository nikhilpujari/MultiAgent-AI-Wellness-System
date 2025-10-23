# 🏃‍♂️ AI Wellness Multi-Agent System

An intelligent wellness assistant powered by multiple specialized AI agents that provide personalized fitness, nutrition, and health guidance through a modern web interface.

## 🌟 Features

### 🤖 Multi-Agent Architecture
- **Router Agent**: Intelligently classifies user queries and routes them to the appropriate specialist
- **Fitness Coach**: Provides personalized workout advice and exercise guidance
- **Nutrition Specialist**: Offers meal planning and dietary recommendations
- **Doctor Avatar**: Handles health concerns with proper medical disclaimers
- **General Agent**: Manages out-of-domain queries with helpful redirects

### 📊 Comprehensive Tracking
- **User Profiles**: Complete health profiles with BMI calculation and body age analysis
- **Meal Logging**: Daily nutrition tracking with calorie and macro counting
- **Workout Sessions**: Exercise logging with duration and intensity tracking
- **Analytics Dashboard**: Visual insights and progress tracking

### 🧠 Smart Knowledge Base
- **RAG System**: Retrieval-Augmented Generation using FAISS vector search
- **Curated Content**: Expert-reviewed fitness, nutrition, and health information
- **Personalized Responses**: Context-aware advice based on user profiles

### 🎨 Modern Interface
- **Streamlit Web App**: Clean, responsive chat interface
- **Real-time Workflow**: Live agent routing and processing visibility
- **Multi-page Dashboard**: Profile management, logging, and analytics

## 🏗️ Architecture

```
User Query → Router Agent → Specialized Agent → Personalized Response
                ↓
    [Fitness] [Nutrition] [Health] [General]
                ↓
    User Profile + RAG Context → Tailored Advice
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

1. **Clone and setup environment**
```bash
git clone <repository-url>
cd ai-wellness
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

4. **Initialize knowledge base**
```bash
python -c "from tools.rag import build_index; build_index()"
```

5. **Run the application**
```bash
streamlit run app/main_streamlit.py
```

Visit `http://localhost:8501` to access the application.

## 📁 Project Structure

```
ai-wellness/
├── app/                    # Web application
│   ├── main_streamlit.py  # Main Streamlit interface
│   ├── api.py             # FastAPI endpoints
│   └── config.py          # Configuration management
├── agents/                 # AI agents
│   ├── router.py          # Query classification
│   ├── fitness_coach.py   # Fitness specialist
│   ├── nutrition_specialist.py # Nutrition expert
│   ├── doctor_avatar.py   # Health advisor
│   ├── graph.py           # LangGraph workflow
│   └── run_graph.py       # Workflow execution
├── tools/                  # Utilities
│   ├── db.py              # Database models
│   ├── rag.py             # Vector search system
│   ├── nutrition_calculator.py # Nutrition analysis
│   └── profile_analyzer.py # Health insights
├── data/                   # Knowledge base
│   └── seed_docs/         # Expert content
│       ├── fitness.txt
│       ├── nutrition.txt
│       └── medical.txt
└── storage/               # Data persistence
    └── app.db            # SQLite database
```

## 🎯 Usage Examples

### Chat Interface
- **Fitness**: "I want to start working out but I'm a beginner"
- **Nutrition**: "What should I eat for breakfast to lose weight?"
- **Health**: "I've been feeling anxious lately, any tips?"
- **General**: "What's the weather like?" (redirected appropriately)

### Profile Management
- Complete health questionnaire
- BMI and body age calculation
- Goal setting and tracking
- AI-powered health insights

### Tracking & Analytics
- Log meals with automatic nutrition calculation
- Record workout sessions with intensity tracking
- View progress charts and trends
- Weekly summaries and recommendations

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI, SQLModel
- **AI/ML**: OpenAI GPT-4, LangChain, LangGraph
- **Database**: SQLite
- **Vector Search**: FAISS
- **Data Processing**: Pandas, NumPy

## 🔧 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key_here
EMBEDDING_MODEL=text-embedding-3-small
DB_URL=sqlite:///storage/app.db
ENVIRONMENT=production
```

### Customization
- **Knowledge Base**: Add documents to `data/seed_docs/`
- **Agents**: Modify agent behavior in `agents/` directory
- **UI**: Customize Streamlit interface in `app/main_streamlit.py`

## 📈 Features in Detail

### Intelligent Routing
The router agent uses OpenAI's language model to classify user queries with high accuracy, falling back to keyword-based classification for reliability.

### Personalized Responses
Each agent considers the user's profile, health conditions, goals, and preferences when generating responses, ensuring relevant and safe advice.

### Knowledge Integration
The RAG system searches through curated health and fitness content to provide evidence-based recommendations alongside AI-generated advice.

### Comprehensive Tracking
Users can log meals, workouts, and health metrics, with the system providing analytics and insights to support their wellness journey.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This application provides general wellness information and should not replace professional medical advice. Always consult with healthcare providers for medical concerns.

## 🆘 Support

For questions or issues:
1. Check the [BUILD_GUIDE.md](BUILD_GUIDE.md) for detailed setup instructions
2. Review the troubleshooting section below
3. Open an issue on GitHub

### Common Issues
- **OpenAI API errors**: Verify your API key in `.env`
- **Database issues**: Delete `storage/app.db` to reset
- **RAG index problems**: Rebuild with `python -c "from tools.rag import build_index; build_index()"`

---

Built with ❤️ for better health and wellness through AI