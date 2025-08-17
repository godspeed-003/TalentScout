# TalentScout Hiring Assistant Chatbot 🤖

An intelligent AI-powered chatbot designed for initial candidate screening in technology recruitment. Built with **Streamlit** and **Google Gemini 2.0 Flash**, this application automates the hiring process by gathering candidate information and generating relevant technical questions based on their tech stack.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Technical Architecture](#technical-architecture)
- [Installation & Setup](#installation--setup)
- [Usage Guide](#usage-guide)
- [Prompt Engineering](#prompt-engineering)
- [Data Handling & Privacy](#data-handling--privacy)
- [File Structure](#file-structure)
- [API Integration](#api-integration)
- [Challenges & Solutions](#challenges--solutions)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Project Overview

The **TalentScout Hiring Assistant** is a sophisticated chatbot that streamlines the initial screening process for technology recruitments. It intelligently conducts conversations with candidates, collects essential information, and generates tailored technical questions based on their declared technology stack.

### Key Objectives
- **Automate Initial Screening**: Reduce manual effort in candidate screening
- **Personalized Assessment**: Generate questions specific to candidate's tech stack
- **Data Collection**: Systematically gather candidate information
- **Consistent Experience**: Provide standardized screening for all candidates
- **Time Efficiency**: Process multiple candidates simultaneously

## ✨ Features

### Core Functionality
- 🎯 **Intelligent Greeting & Introduction**: Professional onboarding experience
- 📝 **Comprehensive Information Gathering**: Collects name, email, phone, experience, position, location, and tech stack
- 🔧 **Dynamic Technical Question Generation**: Creates 3-5 relevant questions based on candidate's technologies
- 💬 **Context-Aware Conversations**: Maintains conversation flow and handles follow-ups
- 🛡️ **Robust Input Validation**: Ensures data quality and handles edge cases
- 🚪 **Graceful Exit Handling**: Responds to conversation-ending keywords
- 💾 **Data Persistence**: Saves candidate information in structured JSON format

### User Interface
- 🖥️ **Clean Streamlit Interface**: Intuitive two-column layout
- 📊 **Real-time Progress Tracking**: Visual indication of profile completion
- 💬 **Chat History**: Complete conversation log
- 🎛️ **Admin Controls**: Reset conversation and save data functionality
- 📱 **Responsive Design**: Works on different screen sizes

### Advanced Features
- 🔄 **Session Management**: Maintains state across interactions
- 🎨 **Input Field Management**: Dynamic input clearing after each message
- 🔍 **Technology Recognition**: Parses and validates tech stack mentions
- 📈 **Progress Indicators**: Shows completion percentage
- 🗂️ **Structured Data Storage**: Organized candidate information with timestamps

## 🏗️ Technical Architecture

### Technology Stack
- **Frontend**: Streamlit 1.28.1
- **AI Model**: Google Gemini 2.0 Flash Lite
- **Backend**: Python 3.8+
- **Data Storage**: JSON files
- **Environment Management**: python-dotenv
- **Data Processing**: pandas

### Model Configuration
```python
MODEL_NAME = "models/gemini-2.0-flash-lite"
GENERATION_CONFIG = {
    "temperature": 0.6,
    "top_p": 0.8,
    "top_k": 40
}
```

### Conversation States
The application manages conversation flow through defined states:
- `GREETING` → `COLLECT_NAME` → `COLLECT_EMAIL` → `COLLECT_PHONE` → `COLLECT_EXPERIENCE` → `COLLECT_POSITION` → `COLLECT_LOCATION` → `COLLECT_TECH_STACK` → `TECHNICAL_QUESTIONS` → `CONCLUSION` → `ENDED`

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key
- Git (for cloning)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd agi
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Using uv (recommended)
uv venv --python 3.8
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or using conda
conda create -n talentscout python=3.8
conda activate talentscout
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Google Gemini API key:
   ```bash
   GOOGLE_API_KEY=your_actual_google_gemini_api_key_here
   ```

### Step 5: Run the Application
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## 📖 Usage Guide

### For Candidates
1. **Access the Application**: Navigate to the provided URL
2. **Initial Consent**: Respond positively to the greeting to begin screening
3. **Provide Information**: Answer each question accurately:
   - Full name (first and last)
   - Valid email address
   - Phone number with at least 10 digits
   - Years of experience (or "entry level")
   - Desired position/role
   - Current/preferred location
   - Technical skills and technologies
4. **Technical Assessment**: Answer the generated technical questions
5. **Completion**: Receive confirmation and next steps information

### For Recruiters/Administrators
1. **Monitor Progress**: View real-time candidate information in the sidebar
2. **Save Data**: Click "Save Data" to persist candidate information
3. **Reset Session**: Use "Reset Conversation" to start fresh
4. **Access Data**: Find saved candidate data in `data/candidates.json`

### Example Conversation Flow
```
🤖 Assistant: Hello! I'm TalentScout's Hiring Assistant...
👤 Candidate: yes
🤖 Assistant: Excellent! Let's start with your basic information. Could you please tell me your full name?
👤 Candidate: John Smith
🤖 Assistant: Thank you, John! Now, could you please provide your email address?
```

## 🎨 Prompt Engineering

### Design Philosophy
Our prompt engineering strategy focuses on creating natural, context-aware conversations that gather accurate information while maintaining a professional tone.

### Key Prompt Categories

#### 1. Greeting & Consent
```python
prompt = """
You are TalentScout's Hiring Assistant. Greet the candidate professionally 
and briefly explain that you'll be conducting an initial screening...
"""
```

#### 2. Information Gathering
- **Validation-First Approach**: Each field has specific validation criteria
- **Example-Driven Prompts**: Provide clear examples of expected input
- **Error Handling**: Graceful handling of invalid or unclear responses

#### 3. Technical Question Generation
```python
prompt = f"""
Based on the candidate's tech stack: {tech_list}
Generate a practical, screening-level technical question focused on {primary_tech}...
"""
```

### Optimization Strategies
- **Temperature Control**: Low temperature (0.6) for consistent responses
- **Context Preservation**: Maintain conversation history for coherent flow
- **Fallback Mechanisms**: Handle unexpected inputs gracefully
- **Technology Recognition**: Parse various ways candidates might mention technologies

## 🔒 Data Handling & Privacy

### Data Structure
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-123-4567",
  "experience": "5 years",
  "position": "Software Developer",
  "location": "New York",
  "tech_stack": ["Python", "React", "PostgreSQL"],
  "technical_responses": {
    "question_1": "Candidate's answer...",
    "question_2": "Candidate's answer...",
    "question_3": "Candidate's answer..."
  },
  "timestamp": "2024-01-15T10:30:45.123456",
  "session_id": "unique-session-identifier"
}
```

### Privacy Measures
- **Local Storage**: Data stored locally in JSON format
- **Session Management**: Unique session IDs for each interaction
- **Data Validation**: Input sanitization and validation
- **Temporary Storage**: No permanent cloud storage of sensitive data
- **GDPR Compliance**: Structured for easy data deletion and modification

### Security Features
- **Input Validation**: Prevents injection attacks
- **Session Isolation**: Each conversation is isolated
- **Error Handling**: No sensitive information in error messages
- **Environment Variables**: API keys stored securely

## 📁 File Structure

```
d:\AI\agent\intern\agi\
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── README.md                  # Project documentation
├── data/                      # Data storage directory
│   └── candidates.json        # Candidate information storage
├── config/                    # Legacy configuration (deprecated)
│   └── settings.py           # Compatibility layer
└── chatbot/                   # Prompt templates (reference)
    └── prompts.py            # Prompt engineering templates
```

## 🔌 API Integration

### Google Gemini Integration
```python
import google.generativeai as genai

# Configuration
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

# Generation
response = model.generate_content(prompt, generation_config=GENERATION_CONFIG)
```

### Supported Technologies
The chatbot recognizes and generates questions for:
- **Programming Languages**: Python, JavaScript, Java, C++, C#, Go, PHP, Ruby, TypeScript
- **Frontend**: React, Angular, Vue.js, HTML/CSS, Bootstrap, Tailwind CSS
- **Backend**: Django, Flask, FastAPI, Express.js, Spring Boot, Node.js
- **Databases**: MySQL, PostgreSQL, MongoDB, Redis, SQLite, Firebase
- **Cloud**: AWS, Google Cloud, Azure, Docker, Kubernetes, Heroku
- **Tools**: Git, Jenkins, Nginx, Linux, REST APIs, GraphQL

## 🤔 Challenges & Solutions

### Challenge 1: Input Field Persistence
**Problem**: Streamlit input fields retained values after submission, causing confusion.
**Solution**: Implemented dynamic key generation with `input_counter` to force field clearing.

### Challenge 2: Conversation State Management
**Problem**: Maintaining context across user interactions and handling various input types.
**Solution**: Created comprehensive state machine with validation functions and fallback mechanisms.

### Challenge 3: Flexible Consent Recognition
**Problem**: Users express consent in various ways ("yes ok", "sure", "let's proceed").
**Solution**: Developed `is_consent_positive()` function with extensive keyword matching.

### Challenge 4: Technology Stack Parsing
**Problem**: Candidates mention technologies in different formats and styles.
**Solution**: Multi-layer parsing approach with predefined technology lists and fuzzy matching.

### Challenge 5: API Rate Limiting
**Problem**: Potential rate limiting with Gemini API during high usage.
**Solution**: Implemented error handling and fallback responses for API failures.

## 🚀 Future Enhancements

### Planned Features
- 🌍 **Multilingual Support**: Support for multiple languages
- 😊 **Sentiment Analysis**: Gauge candidate emotions during conversation
- 📊 **Analytics Dashboard**: Insights into candidate responses and patterns
- 🔄 **Integration APIs**: Connect with ATS systems and HR platforms
- 📱 **Mobile Optimization**: Enhanced mobile experience
- 🎯 **Advanced Question Pool**: Larger database of technical questions
- 🔍 **Resume Parsing**: Upload and parse resume information
- 📧 **Email Integration**: Automated follow-up emails

### Performance Optimizations
- **Caching**: Implement response caching for common questions
- **Asynchronous Processing**: Handle multiple candidates simultaneously
- **Database Integration**: Move from JSON to proper database
- **Load Balancing**: Support for high-traffic scenarios

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the Repository**
2. **Create Feature Branch**: `git checkout -b feature/new-feature`
3. **Commit Changes**: `git commit -m "Add new feature"`
4. **Push to Branch**: `git push origin feature/new-feature`
5. **Create Pull Request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings for new functions
- Include tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support & Contact

For questions, issues, or suggestions:
- **Create an Issue**: Use GitHub issues for bug reports
- **Email**: careers@talentscout.com
- **Documentation**: Refer to this README and code comments

---

**Built with ❤️ for efficient technology recruitment**

*Last Updated: January 2024*
