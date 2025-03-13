# Julie AI Agent

## Overview
Julie is an AI agent designed to automate expert networking. It allows users to input a query and their email, searches for compliant experts on LinkedIn, ranks them, and schedules calls by emailing the user with expert details. This project is an MVP built with Python and Flask.

## Features
- Expert search via LinkedIn and internal database
- Expert ranking and filtering based on compliance criteria
- Call scheduling and availability management
- Real-time monitoring of Julie's actions
- Email notifications

## Quick Start (Local Development)

1. Clone the repository:
   ```
   git clone https://github.com/Seboliver16/julie-ai-agent.git
   cd julie-ai-agent
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Flask and dependencies:
   ```
   pip install Flask Flask-Session requests nltk
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Access the application in your browser:
   ```
   http://localhost:5000
   ```

That's it! The default configuration uses mock services so you don't need API keys to test.

## Development Notes

### Mock Services
For development, the application uses mock services by default:

- **Mock LinkedIn**: Returns sample expert data without requiring LinkedIn API credentials
- **Mock Email**: Logs emails to console instead of sending them

### Configuration
The default `config.py` is set up for development. When you're ready for production:

1. Update `config.py` with your real credentials
2. Set `USE_MOCK_LINKEDIN` and `USE_MOCK_EMAIL` to `False`

### Test Account
- Email: julieai.contact@gmail.com

## Deployment to julie.ai

### Basic Deployment Steps
1. Set up a server (AWS EC2, DigitalOcean, etc.)
2. Clone the repository and install dependencies
3. Update `config.py` with production settings
4. Set up Nginx + Gunicorn
5. Configure your domain to point to the server

### Quick Deploy Script
Run this on your server:
```
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart julie
```

## Repository Structure
- `app.py`: Main Flask application
- `utils/`: Helper modules (LinkedIn, email, database, NLP, monitoring)
- `templates/`: HTML templates
- `static/`: CSS and JavaScript files
- `requirements.txt`: Python dependencies
- `config.py`: Configuration (update for production)

## Future Enhancements
- Integration with Outlook for direct input
- Enhanced expert vetting with compliance checks
- Real-time monitoring dashboard
- Calendar integrations (Google Calendar, Outlook)
- Proprietary expert database

## License
MIT License