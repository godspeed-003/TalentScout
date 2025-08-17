# This file is deprecated in the rapid development plan
# All settings have been moved to config.py for single-file architecture
# This file can be deleted or kept empty for reference

# Redirect to main config for compatibility
from config import *

# Legacy compatibility class (empty)
class Settings:
    pass

settings = Settings()
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "500"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Application Configuration
    APP_TITLE = "TalentScout Hiring Assistant"
    APP_DESCRIPTION = "AI-powered chatbot for initial candidate screening"
    
    # Data Configuration
    DATA_DIR = "data"
    CANDIDATES_FILE = "candidates.json"
    
    # Security Configuration
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "1800"))  # 30 minutes
    
    # Conversation Configuration
    MAX_QUESTIONS_PER_TECH = 5
    MIN_QUESTIONS_PER_TECH = 3
    CONVERSATION_TIMEOUT = 1800  # 30 minutes
    
    # Supported Technologies
    SUPPORTED_TECH_STACKS: Dict[str, List[str]] = {
        "programming_languages": [
            "Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", 
            "PHP", "Ruby", "Swift", "Kotlin", "TypeScript"
        ],
        "frameworks": [
            "React", "Angular", "Vue.js", "Django", "Flask", "FastAPI",
            "Spring Boot", "Express.js", "Laravel", "Ruby on Rails"
        ],
        "databases": [
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite",
            "Oracle", "SQL Server", "Cassandra", "DynamoDB"
        ],
        "cloud_platforms": [
            "AWS", "Google Cloud", "Azure", "Heroku", "Vercel",
            "DigitalOcean", "Firebase"
        ],
        "tools": [
            "Git", "Docker", "Kubernetes", "Jenkins", "Terraform",
            "Ansible", "Nginx", "Apache", "Elasticsearch"
        ]
    }
    
    # Conversation Exit Keywords
    EXIT_KEYWORDS = [
        "exit", "quit", "bye", "goodbye", "end", "stop", 
        "finish", "done", "terminate"
    ]
    
    @classmethod
    def get_all_technologies(cls) -> List[str]:
        """Get all supported technologies as a flat list"""
        all_tech = []
        for category in cls.SUPPORTED_TECH_STACKS.values():
            all_tech.extend(category)
        return sorted(list(set(all_tech)))

settings = Settings()
