import streamlit as st
import google.generativeai as genai
import json
import os
from datetime import datetime
import uuid
from config import *

# Configure Google Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'conversation_state' not in st.session_state:
        st.session_state.conversation_state = CONVERSATION_STATES["GREETING"]
    if 'candidate_data' not in st.session_state:
        st.session_state.candidate_data = DEFAULT_CANDIDATE.copy()
        st.session_state.candidate_data['session_id'] = str(uuid.uuid4())
        st.session_state.candidate_data['timestamp'] = datetime.now().isoformat()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_tech_stack' not in st.session_state:
        st.session_state.current_tech_stack = []
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'generated_questions' not in st.session_state:
        st.session_state.generated_questions = []
    if 'input_counter' not in st.session_state:
        st.session_state.input_counter = 0

# Streamlit Page Configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def is_consent_positive(user_input):
    """Check if user input indicates positive consent"""
    consent_keywords = [
        'yes', 'y', 'yeah', 'yep', 'sure', 'ok', 'okay', 'proceed', 'continue', 
        'go ahead', 'start', 'begin', 'ready', 'let\'s go', 'lets go', 'fine', 
        'alright', 'agree', 'accept', 'let\'s do this', 'lets do this'
    ]
    
    user_input_lower = user_input.lower().strip()
    
    # Check for exact matches or partial matches
    for keyword in consent_keywords:
        if keyword in user_input_lower:
            return True
    
    return False

def is_consent_negative(user_input):
    """Check if user input indicates negative consent"""
    negative_keywords = [
        'no', 'n', 'nope', 'not now', 'maybe later', 'stop', 'cancel', 
        'don\'t want', 'dont want', 'refuse', 'decline', 'not interested'
    ]
    
    user_input_lower = user_input.lower().strip()
    
    for keyword in negative_keywords:
        if keyword in user_input_lower:
            return True
    
    return False

# Main App
def main():
    """Main application function"""
    init_session_state()
    
    # App Header
    st.title(APP_TITLE)
    st.markdown(f"*{APP_DESCRIPTION}*")
    st.divider()
    
    # Check API key
    if not GOOGLE_API_KEY:
        st.error("❌ Google API key not found. Please set GOOGLE_API_KEY in your .env file.")
        st.stop()
    
    # Create two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Chat Interface")
        chat_container = st.container()
        
        # Display chat history
        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "assistant":
                    st.markdown(f"🤖 **TalentScout Assistant:** {message['content']}")
                else:
                    st.markdown(f"👤 **You:** {message['content']}")
        
        # User input with unique key to force refresh
        user_input = st.text_input(
            "Type your message here...", 
            key=f"user_input_{st.session_state.input_counter}", 
            placeholder="Type your response..."
        )
        
        # Create columns for buttons
        btn_col1, btn_col2 = st.columns([1, 4])
        
        with btn_col1:
            send_clicked = st.button("Send", type="primary")
        
        # Handle input
        if send_clicked and user_input and user_input.strip():
            handle_user_input(user_input.strip())
            # Increment counter to create new input field
            st.session_state.input_counter += 1
            st.rerun()
    
    with col2:
        st.subheader("📋 Candidate Information")
        display_candidate_info()
        
        # Admin controls
        st.subheader("🔧 Controls")
        if st.button("Reset Conversation", type="secondary"):
            reset_conversation()
            st.rerun()
        
        if st.button("Save Data", type="secondary"):
            save_candidate_data()
            st.success("Data saved successfully!")

def handle_user_input(user_input):
    """Handle user input based on conversation state"""
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Check for exit keywords
    if any(keyword in user_input.lower() for keyword in EXIT_KEYWORDS):
        st.session_state.conversation_state = CONVERSATION_STATES["CONCLUSION"]
        bot_response = generate_conclusion()
        st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
        st.session_state.conversation_state = CONVERSATION_STATES["ENDED"]
        return
    
    # Handle based on current state
    current_state = st.session_state.conversation_state
    
    if current_state == CONVERSATION_STATES["GREETING"]:
        # Check for consent with improved logic
        if is_consent_positive(user_input):
            bot_response = "Excellent! Let's start with your basic information. Could you please tell me your full name?"
            st.session_state.conversation_state = CONVERSATION_STATES["COLLECT_NAME"]
        elif is_consent_negative(user_input):
            bot_response = "I understand. If you change your mind and would like to proceed with the screening, just let me know!"
            st.session_state.conversation_state = CONVERSATION_STATES["ENDED"]
        else:
            # If unclear, ask for clarification
            bot_response = "I'd like to confirm - are you ready to proceed with the screening process? Please respond with 'yes' to continue or 'no' if you'd prefer not to proceed at this time."
    
    elif current_state == CONVERSATION_STATES["COLLECT_NAME"]:
        # Check if user is just saying yes/no instead of providing name
        if is_consent_positive(user_input) and len(user_input.split()) < 2:
            bot_response = "I need your actual full name, not just confirmation. Please provide your first and last name (for example: John Smith)."
        elif len(user_input.split()) >= 2 and not user_input.lower() in ['yes', 'no', 'ok', 'okay']:
            st.session_state.candidate_data['name'] = user_input
            first_name = user_input.split()[0]
            bot_response = f"Thank you, {first_name}! Now, could you please provide your email address?"
            st.session_state.conversation_state = CONVERSATION_STATES["COLLECT_EMAIL"]
        else:
            bot_response = "Could you please provide your full name with both first and last name? (Example: Jane Doe)"
    
    elif current_state == CONVERSATION_STATES["COLLECT_EMAIL"]:
        if is_consent_positive(user_input) and '@' not in user_input:
            bot_response = "I need your actual email address, not just confirmation. Please provide your email (for example: john@email.com)."
        elif '@' in user_input and '.' in user_input and len(user_input) > 5:
            st.session_state.candidate_data['email'] = user_input
            bot_response = "Great! What's your phone number?"
            st.session_state.conversation_state = CONVERSATION_STATES["COLLECT_PHONE"]
        else:
            bot_response = "Please provide a valid email address (for example: john@example.com)"
    
    elif current_state == CONVERSATION_STATES["COLLECT_PHONE"]:
        if is_consent_positive(user_input) and not any(char.isdigit() for char in user_input):
            bot_response = "I need your actual phone number, not just confirmation. Please provide your phone number (for example: +1-555-123-4567)."
        elif any(char.isdigit() for char in user_input) and len(user_input.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')) >= 10:
            st.session_state.candidate_data['phone'] = user_input
            bot_response = "Perfect! How many years of professional experience do you have in technology?"
            st.session_state.conversation_state = CONVERSATION_STATES["COLLECT_EXPERIENCE"]
        else:
            bot_response = "Please provide a valid phone number with at least 10 digits."
    
    elif current_state == CONVERSATION_STATES["COLLECT_EXPERIENCE"]:
        if is_consent_positive(user_input) and not any(char.isdigit() for char in user_input) and 'entry' not in user_input.lower():
            bot_response = "I need the actual number of years of experience, not just confirmation. Please tell me how many years (for example: '3 years' or 'entry level')."
        elif any(char.isdigit() for char in user_input) or 'entry' in user_input.lower() or 'fresh' in user_input.lower() or 'beginner' in user_input.lower():
            st.session_state.candidate_data['experience'] = user_input
            bot_response = "Excellent! What position or role are you interested in applying for?"
            st.session_state.conversation_state = CONVERSATION_STATES["COLLECT_POSITION"]
        else:
            bot_response = "Please specify the number of years of experience (for example: '3 years', '5', or 'entry level')"
    
    elif current_state == CONVERSATION_STATES["COLLECT_POSITION"]:
        if is_consent_positive(user_input) and len(user_input.split()) < 2:
            bot_response = "I need to know the specific position you're interested in, not just confirmation. Please tell me the role (for example: 'Software Developer' or 'Data Scientist')."
        else:
            st.session_state.candidate_data['position'] = user_input
            bot_response = "Thank you! What's your current location or preferred work location?"
            st.session_state.conversation_state = CONVERSATION_STATES["COLLECT_LOCATION"]
    
    elif current_state == CONVERSATION_STATES["COLLECT_LOCATION"]:
        if is_consent_positive(user_input) and len(user_input.split()) < 2:
            bot_response = "I need to know your actual location, not just confirmation. Please tell me your city/state or preferred work location."
        else:
            st.session_state.candidate_data['location'] = user_input
            bot_response = generate_tech_stack_prompt()
            st.session_state.conversation_state = CONVERSATION_STATES["COLLECT_TECH_STACK"]
    
    elif current_state == CONVERSATION_STATES["COLLECT_TECH_STACK"]:
        if is_consent_positive(user_input) and len(user_input.split()) < 3:
            bot_response = """I need to know your actual technical skills, not just confirmation. Please list specific technologies you work with. For example:

**"I work with Python, React, MySQL, and AWS"**

Or be more detailed:
- Programming languages: Python, JavaScript
- Frameworks: React, Django  
- Databases: MySQL, MongoDB
- Cloud: AWS, Docker"""
        else:
            # Parse the tech stack properly
            tech_stack = parse_tech_stack(user_input)
            if tech_stack and len(tech_stack) > 0:
                st.session_state.candidate_data['tech_stack'] = tech_stack
                st.session_state.current_tech_stack = tech_stack
                bot_response = generate_technical_questions(tech_stack)
                st.session_state.conversation_state = CONVERSATION_STATES["TECHNICAL_QUESTIONS"]
            else:
                bot_response = """I didn't catch specific technologies from your response. Could you please list specific technologies you work with? For example:

**"I work with Python, React, MySQL, and AWS"**

Or list them by category:
- Programming languages: Python, JavaScript, Java, etc.
- Frameworks: React, Django, Spring, etc.  
- Databases: MySQL, MongoDB, PostgreSQL, etc.
- Cloud platforms: AWS, Azure, Google Cloud, etc."""
    
    elif current_state == CONVERSATION_STATES["TECHNICAL_QUESTIONS"]:
        handle_technical_answer(user_input)
        bot_response = get_next_technical_question()
    
    elif current_state == CONVERSATION_STATES["ENDED"]:
        # If conversation has ended but user wants to restart
        if is_consent_positive(user_input):
            reset_conversation()
            bot_response = handle_greeting()
            st.session_state.conversation_state = CONVERSATION_STATES["COLLECT_NAME"]
        else:
            bot_response = "Our conversation has ended. If you'd like to start a new screening, please use the Reset Conversation button or say 'yes' to restart."
    
    else:
        bot_response = "I'm not sure how to help with that. Could you please provide the information I asked for?"
    
    # Add bot response to chat history
    st.session_state.chat_history.append({"role": "assistant", "content": bot_response})

def handle_greeting():
    """Generate initial greeting"""
    prompt = """
    You are TalentScout's Hiring Assistant. Greet the candidate professionally and briefly explain that you'll be conducting an initial screening by gathering their information and asking technical questions based on their skills. Ask for their consent to proceed. Keep it friendly and concise.
    """
    
    try:
        response = model.generate_content(prompt, generation_config=GENERATION_CONFIG)
        return response.text
    except Exception as e:
        return "Hello! I'm TalentScout's Hiring Assistant. I'm here to conduct an initial screening by gathering your information and asking some technical questions based on your skills. Are you ready to proceed?"

def generate_tech_stack_prompt():
    """Generate prompt for tech stack collection"""
    return """Now I'd like to learn about your technical skills. Please list the specific technologies you work with, including:

• **Programming languages** you're proficient in (e.g., Python, JavaScript, Java)
• **Frameworks and libraries** you've used (e.g., React, Django, Spring Boot)  
• **Databases** you've worked with (e.g., MySQL, MongoDB, PostgreSQL)
• **Cloud platforms** you have experience with (e.g., AWS, Azure, Google Cloud)
• **Development tools** you're familiar with (e.g., Git, Docker, Jenkins)

**Example response:** "I work with Python, React, PostgreSQL, and AWS"

Please mention only technologies you feel confident discussing in a technical interview."""

def parse_tech_stack(user_input):
    """Parse and extract technologies from user input"""
    mentioned_tech = []
    user_input_lower = user_input.lower()
    
    all_technologies = get_all_technologies()
    
    for tech in all_technologies:
        if tech.lower() in user_input_lower:
            mentioned_tech.append(tech)
    
    # If no recognized technologies, try to extract from common patterns
    if not mentioned_tech:
        # Look for common technology patterns
        words = user_input.replace(',', ' ').replace('.', ' ').split()
        for word in words:
            word_clean = word.strip().title()
            if len(word_clean) > 2:  # Avoid very short words
                mentioned_tech.append(word_clean)
    
    return mentioned_tech[:5] if mentioned_tech else []  # Limit to 5 technologies

def generate_technical_questions(tech_stack):
    """Generate technical questions based on tech stack"""
    if not tech_stack:
        return "I notice you didn't mention specific technologies I recognize. Could you please clarify what programming languages or frameworks you work with?"
    
    primary_tech = tech_stack[0]  # Focus on the first technology mentioned
    tech_list = ', '.join(tech_stack[:3])  # Show up to 3 technologies
    
    prompt = f"""
    You are a technical interviewer for TalentScout. A candidate has mentioned they work with: {tech_list}
    
    Generate a practical, screening-level technical question focused on {primary_tech}. The question should:
    - Test real-world application knowledge
    - Be appropriate for initial screening (not too basic, not too advanced)
    - Be specific and clear
    - Allow the candidate to demonstrate their experience
    
    Present just one question in a conversational, encouraging tone.
    """
    
    try:
        response = model.generate_content(prompt, generation_config=GENERATION_CONFIG)
        questions = response.text
        st.session_state.generated_questions = [questions]
        st.session_state.current_question_index = 0
        return f"Great! I can see you have experience with {tech_list}. Let me ask you some technical questions to better understand your expertise.\n\n{questions}"
    except Exception as e:
        return f"Great! I see you work with {tech_list}. Let's start with a question about {primary_tech}: Can you describe a recent project where you used {primary_tech} and what challenges you faced?"

def handle_technical_answer(user_input):
    """Store technical answer"""
    question_key = f"question_{st.session_state.current_question_index + 1}"
    st.session_state.candidate_data['technical_responses'][question_key] = user_input

def get_next_technical_question():
    """Get next technical question or conclude"""
    st.session_state.current_question_index += 1
    
    if st.session_state.current_question_index >= MAX_QUESTIONS_PER_TECH:
        st.session_state.conversation_state = CONVERSATION_STATES["CONCLUSION"]
        return generate_conclusion()
    
    # Generate next question for different technology if available
    tech_stack = st.session_state.current_tech_stack
    if len(tech_stack) > st.session_state.current_question_index:
        current_tech = tech_stack[st.session_state.current_question_index]
    else:
        current_tech = tech_stack[0]  # Fallback to first technology
    
    prompt = f"""
    Generate a different technical question about {current_tech} for a candidate screening. 
    This is question {st.session_state.current_question_index + 1} of {MAX_QUESTIONS_PER_TECH}.
    Make it practical and different from previous questions. Keep it conversational.
    """
    
    try:
        response = model.generate_content(prompt, generation_config=GENERATION_CONFIG)
        return f"Thank you for that answer. Here's my next question:\n\n{response.text}"
    except Exception as e:
        return "Thank you for that answer. Can you tell me about a challenging technical problem you've solved recently and how you approached it?"

def generate_conclusion():
    """Generate conclusion message"""
    name = st.session_state.candidate_data.get('name', 'there')
    first_name = name.split()[0] if name else 'there'
    return f"""Thank you {first_name} for taking the time to complete this initial screening! 

I've gathered all the necessary information about your background and technical skills. Here's what happens next:

✅ Our HR team will review your responses within 2-3 business days
✅ If your profile matches our current opportunities, we'll contact you via email to schedule a detailed interview
✅ Feel free to reach out to us at careers@talentscout.com if you have any questions

We appreciate your interest in working with TalentScout. Have a great day!"""

def display_candidate_info():
    """Display collected candidate information"""
    candidate = st.session_state.candidate_data
    
    if candidate['name']:
        st.write(f"**Name:** {candidate['name']}")
    if candidate['email']:
        st.write(f"**Email:** {candidate['email']}")
    if candidate['phone']:
        st.write(f"**Phone:** {candidate['phone']}")
    if candidate['experience']:
        st.write(f"**Experience:** {candidate['experience']}")
    if candidate['position']:
        st.write(f"**Position:** {candidate['position']}")
    if candidate['location']:
        st.write(f"**Location:** {candidate['location']}")
    if candidate['tech_stack']:
        st.write(f"**Tech Stack:** {', '.join(candidate['tech_stack'])}")
    
    # Progress indicator
    completed_fields = sum(1 for field in ['name', 'email', 'phone', 'experience', 'position', 'location'] 
                          if candidate[field])
    progress = completed_fields / 6
    st.progress(progress, text=f"Profile Completion: {int(progress * 100)}%")

def save_candidate_data():
    """Save candidate data to JSON file"""
    try:
        # Load existing data
        candidates = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                candidates = json.load(f)
        
        # Add current candidate
        candidates.append(st.session_state.candidate_data)
        
        # Save back to file
        with open(DATA_FILE, 'w') as f:
            json.dump(candidates, f, indent=2)
            
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")

def reset_conversation():
    """Reset conversation to beginning"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()

# Auto-start conversation
if __name__ == "__main__":
    main()
    
    # Auto-start greeting if chat is empty
    if not st.session_state.chat_history and st.session_state.conversation_state == CONVERSATION_STATES["GREETING"]:
        greeting = handle_greeting()
        st.session_state.chat_history.append({"role": "assistant", "content": greeting})
        st.rerun()
