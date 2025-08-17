# TalentScout Hiring Assistant Chatbot - Rapid Development Plan (12 Hours)

## Project Overview
Develop an intelligent Hiring Assistant chatbot for TalentScout recruitment agency using basic Streamlit interface and Google Gemini 2.0 Flash for rapid deployment.

## Simplified Project Structure
```
d:\AI\agent\intern\agi\
├── app.py                 # Main Streamlit application (ALL-IN-ONE)
├── config.py             # Simple configuration
├── data/
│   └── candidates.json   # Candidate data storage
├── requirements.txt      # Essential dependencies only
├── README.md            # Basic documentation
└── .env.example         # Environment variables template
```

## Rapid Implementation Timeline (12 Hours)

### Phase 1: Foundation Setup (2 hours)
- [x] Minimal project structure
- [x] Essential dependencies
- [x] Basic configuration with Gemini
- [x] Environment setup

### Phase 2: Core Streamlit App (4 hours)
- [ ] Single-file Streamlit application
- [ ] Session state management
- [ ] Basic conversation flow
- [ ] Information collection forms
- [ ] Simple chat interface

### Phase 3: Gemini Integration & Prompts (3 hours)
- [ ] Google Gemini API integration
- [ ] Hardcoded prompt templates
- [ ] Tech stack question generation
- [ ] Basic conversation logic

### Phase 4: Data Handling (1.5 hours)
- [ ] JSON file storage
- [ ] Basic data validation
- [ ] Simple candidate data structure

### Phase 5: Testing & Polish (1.5 hours)
- [ ] Manual testing
- [ ] Basic error handling
- [ ] README documentation
- [ ] Demo preparation

## Streamlined Technical Stack
- **Frontend**: Basic Streamlit (no custom CSS)
- **Backend**: All-in-one Python file
- **LLM**: Google Gemini 2.0 Flash Lite (fastest & free)
- **Data**: Simple JSON file
- **Deployment**: Local only

## MVP Features (Must Have)
1. ✅ Basic chat interface
2. ✅ Information gathering (name, email, experience, tech stack)
3. ✅ Tech stack based question generation
4. ✅ Conversation flow management
5. ✅ Data persistence

## Nice-to-Have (If Time Permits)
- Input validation
- Better error messages
- Conversation history
- Export functionality

## Removed Features (For Speed)
- ❌ Custom styling/CSS
- ❌ Complex UI components
- ❌ Advanced security measures
- ❌ Unit tests
- ❌ Cloud deployment
- ❌ Multiple file architecture
- ❌ Advanced prompt engineering
- ❌ Sentiment analysis
- ❌ Multilingual support

## Success Criteria (12-Hour MVP)
- ✅ Working Streamlit app
- ✅ Collects candidate information
- ✅ Generates tech questions using Gemini
- ✅ Maintains conversation state
- ✅ Saves data to JSON
- ✅ Basic documentation

## Development Strategy
- **Hour 1-2**: Setup Gemini and configuration
- **Hour 3-6**: Core app development
- **Hour 7-9**: Gemini integration and prompts
- **Hour 10-11**: Data handling and testing
- **Hour 12**: Documentation and final polish
- Comprehensive documentation

## Risk Mitigation
- **Technical Risks**: Use established libraries, implement fallbacks
- **Time Constraints**: Focus on core features first, bonus features later
- **API Limitations**: Implement local model fallbacks
- **Data Privacy**: Built-in compliance from start
