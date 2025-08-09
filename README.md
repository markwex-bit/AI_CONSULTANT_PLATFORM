# AI Consultant Platform

A comprehensive Flask web application that provides AI readiness assessments for businesses, generates detailed reports, handles payments, and manages consultation appointments.

## Features

- **AI Readiness Assessment**: Evaluate company's AI readiness with detailed scoring
- **Report Generation**: Generate professional PDF reports with recommendations
- **Payment Processing**: Integrated Stripe payment processing
- **Appointment Scheduling**: Book consultation appointments
- **Admin Dashboard**: Manage assessments and view analytics
- **SaaS Solutions Database**: Comprehensive database of AI tools and solutions
- **LLM Integration**: Dynamic content generation using OpenAI or Anthropic APIs

## Quick Start

### Prerequisites

- Python 3.8+
- pip
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI_Consultant_Platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   # Edit .env with your actual values
   ```

5. **Initialize the database**
   ```bash
   python -c "from app import init_db; init_db()"
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## Environment Variables

Create a `.env` file with the following variables:

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Application Configuration
FLASK_ENV=development
DEBUG=True

# LLM Configuration (Optional - for dynamic content generation)
# Choose one provider: 'openai' or 'anthropic'
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

## LLM Integration

The platform now includes LLM-powered dynamic content generation for enhanced report personalization:

### Features
- **Dynamic Opportunity Descriptions**: AI-generated personalized descriptions based on company context
- **Hybrid Tool Selection Intelligence**: AI-powered selection prioritizing your approved tools, with external recommendations when needed
- **Multi-Provider Support**: Works with OpenAI GPT or Anthropic Claude
- **Graceful Fallback**: Uses base descriptions and default tool selection if LLM is unavailable
- **Context-Aware**: Incorporates company industry, size, challenges, and technology stack
- **Visual Indicators**: External tools are marked with an asterisk (*) in reports for easy identification
- **Tool Portfolio Expansion**: Discovers new tools for specific use cases to expand your offerings
- **Admin Monitoring Trends**: Comprehensive analytics dashboard showing assessment trends, industry distribution, AI score distribution, tool recommendation patterns, and revenue tracking

### Testing
Run the LLM integration tests:
```bash
# Test opportunity descriptions
python test_llm.py

# Test tool selection intelligence
python test_tool_selection.py

# Test hybrid tool selection (approved + external)
python test_hybrid_tool_selection.py

# Test external tool recommendations with asterisk indicator
python test_external_tools_demo.py

# Test monitoring trends dashboard
python test_monitoring_trends.py

# Complete demo of both features
python demo_complete_llm.py
```

### Hybrid Tool Selection Strategy
The system uses a smart approach to tool recommendations:

1. **Priority to Approved Tools**: First looks at your `saas_tools_database.json` for suitable tools
2. **External Tool Discovery**: When approved tools don't fully meet client needs, suggests external tools
3. **Visual Indicators**: External tools are marked with an asterisk (*) in reports for easy identification
4. **Portfolio Expansion**: External tools are clearly marked, allowing you to evaluate and add them to your database
5. **Client Value**: Ensures clients get the best recommendations regardless of your current tool portfolio

This approach helps you:
- Leverage your existing tool partnerships
- Discover new tools for specific industries/use cases
- Expand your offerings strategically
- Provide maximum value to clients

### Admin Dashboard & Monitoring Trends
Access the admin dashboard at `/admin` to monitor platform usage and trends:

**📊 Assessment Overview**
- Total assessments and monthly trends
- Average AI readiness scores
- Report generation tracking

**🏭 Industry Distribution**
- Visual breakdown of client industries
- Percentage distribution with progress bars
- Identify target markets and opportunities

**🎯 AI Score Distribution**
- High (80-100), Medium (50-79), Low (0-49) score ranges
- Color-coded distribution cards
- Track client readiness levels

**🛠️ Tool Recommendation Trends**
- External tool recommendation patterns
- Portfolio gap analysis by category
- Expansion opportunity identification

**🔗 External Tool Analysis**
- Count of external tools recommended
- Most requested tool categories
- Portfolio expansion opportunities

**💰 Revenue Tracking**
- Total revenue potential calculations
- Average deal size metrics
- Conversion rate analysis

### Configuration
Set your preferred LLM provider and API key in the `.env` file:
```env
LLM_PROVIDER=openai  # or 'anthropic'
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## Project Structure

```
AI_Consultant_Platform/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── models.py              # Database models and operations
├── llm_service.py         # LLM integration service
├── test_llm.py           # LLM integration test script
├── test_tool_selection.py # Tool selection intelligence test
├── test_hybrid_tool_selection.py # Hybrid tool selection test
├── test_external_tools_demo.py # External tool recommendations demo
├── test_monitoring_trends.py # Monitoring trends dashboard test
├── demo_llm.py           # LLM integration demonstration
├── demo_complete_llm.py  # Complete LLM features demo
├── requirements.txt       # Python dependencies
├── saas_tools_database.json  # AI tools database
├── templates/             # HTML templates
├── reports/              # Generated PDF reports
├── report_templates/     # Report templates
└── venv/                 # Virtual environment
```

## API Endpoints

### Assessment
- `POST /submit_assessment` - Submit new assessment
- `GET /api/assessments` - Get all assessments
- `GET /api/assessment/<id>` - Get specific assessment

### Reports
- `POST /generate_report` - Generate PDF report
- `GET /download_report/<id>` - Download report

### Payments
- `POST /create_payment_intent` - Create Stripe payment intent
- `GET /payment/<id>` - Payment page

### Appointments
- `POST /book_appointment` - Book consultation appointment

## Database Schema

### Assessments Table
- Company information (name, industry, size)
- Contact details (name, email, phone)
- Assessment data (challenges, tech level, budget)
- AI score and opportunities
- Timestamps

### Appointments Table
- Assessment reference
- Client information
- Appointment date/time
- Status tracking

### Payments Table
- Assessment reference
- Stripe payment details
- Amount and status

## Security Considerations

- ✅ Environment variables for sensitive data
- ✅ Input validation and sanitization
- ✅ SQL injection prevention with parameterized queries
- ✅ Proper error handling
- ⚠️ Add CSRF protection
- ⚠️ Implement rate limiting
- ⚠️ Add authentication for admin routes

## Deployment

### Production Checklist

1. **Security**
   - Change default secret key
   - Use HTTPS
   - Set up proper firewall rules
   - Enable CSRF protection

2. **Database**
   - Use PostgreSQL instead of SQLite
   - Set up database backups
   - Configure connection pooling

3. **Monitoring**
   - Set up logging
   - Monitor application performance
   - Set up error tracking

4. **Scaling**
   - Use WSGI server (Gunicorn)
   - Set up reverse proxy (Nginx)
   - Consider containerization (Docker)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, email support@aiconsultant.com or create an issue in the repository.
# AI_CONSULTANT_PLATFORM
