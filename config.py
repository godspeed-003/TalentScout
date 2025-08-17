import os
from dotenv import load_dotenv

load_dotenv()

# Google Gemini API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
MODEL_NAME = "models/gemini-2.0-flash-lite"  # Using fastest model for development
TEMPERATURE = 0.6
TOP_P = 0.8
TOP_K = 40

# App Configuration
APP_TITLE = "TalentScout Hiring Assistant"
APP_DESCRIPTION = "AI-powered chatbot for candidate screening using Google Gemini"

# Data
DATA_FILE = "data/candidates.json"
DATA_DIR = "data"

# Create data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Conversation
MAX_QUESTIONS_PER_TECH = 3
EXIT_KEYWORDS = ["exit", "quit", "bye", "goodbye", "done", "stop", "finish", "end"]

# Supported Technologies (simplified list for rapid development)
TECH_CATEGORIES = {
    "Programming Languages": ["Python", "JavaScript", "Java", "C++", "C#", "Go", "PHP", "Ruby", "TypeScript"],
    "Frontend": ["React", "Angular", "Vue.js", "HTML/CSS", "Bootstrap", "Tailwind CSS"],
    "Backend": ["Django", "Flask", "FastAPI", "Express.js", "Spring Boot", "Node.js"],
    "Databases": ["MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Firebase"],
    "Cloud": ["AWS", "Google Cloud", "Azure", "Docker", "Kubernetes", "Heroku"],
    "Tools": ["Git", "Jenkins", "Nginx", "Linux", "REST APIs", "GraphQL"]
}

# Conversation States for flow management
CONVERSATION_STATES = {
    "GREETING": "greeting",
    "COLLECT_NAME": "collect_name",
    "COLLECT_EMAIL": "collect_email", 
    "COLLECT_PHONE": "collect_phone",
    "COLLECT_EXPERIENCE": "collect_experience",
    "COLLECT_POSITION": "collect_position",
    "COLLECT_LOCATION": "collect_location",
    "COLLECT_TECH_STACK": "collect_tech_stack",
    "TECHNICAL_QUESTIONS": "technical_questions",
    "CONCLUSION": "conclusion",
    "ENDED": "ended"
}

def get_all_technologies():
    """Get flattened list of all technologies"""
    all_tech = []
    for category in TECH_CATEGORIES.values():
        all_tech.extend(category)
    return sorted(all_tech)

# Generation Configuration for Gemini (based on reference file)
GENERATION_CONFIG = {
    "temperature": TEMPERATURE,
    "top_p": TOP_P,
    "top_k": TOP_K
}

# Default candidate data structure
DEFAULT_CANDIDATE = {
    "name": "",
    "email": "",
    "phone": "",
    "experience": "",
    "position": "",
    "location": "",
    "tech_stack": [],
    "technical_responses": {},
    "timestamp": "",
    "session_id": ""
}
