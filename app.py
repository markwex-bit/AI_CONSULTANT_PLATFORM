# app.py - Main Flask Application
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from datetime import datetime, timedelta
import json
import os
import sqlite3
import logging
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import stripe
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader
from llm_service import llm_service
from models import db_manager
from werkzeug.utils import secure_filename
import uuid
from report_generator import ReportGenerator
import random
from config import Config
REPORTS_DIR = Config.REPORTS_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration - Use environment variables for security
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_your_stripe_key')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_your_stripe_key')
stripe.api_key = STRIPE_SECRET_KEY

# Email configuration
SMTP_SERVER = os.environ.get('SMTP_SERVER', "smtp.gmail.com")
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', "your-email@gmail.com")
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', "your-app-password")
# Database setup
def init_db():
    # Use DatabaseManager to initialize the database with all enhanced fields
    db_manager.init_db()
    
    # Create appointments table
    conn = sqlite3.connect('ai_consultant.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER,
            client_name TEXT,
            client_email TEXT,
            appointment_date DATE,
            appointment_time TIME,
            status TEXT DEFAULT 'scheduled',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assessment_id) REFERENCES assessments (id)
        )
    ''')
    
    # Create payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER,
            stripe_payment_id TEXT,
            amount INTEGER,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assessment_id) REFERENCES assessments (id)
        )
    ''')
    
    conn.commit()
    conn.close()
# AI Assessment Logic
class AIAssessmentEngine:
    def __init__(self):
        # Load SaaS solutions from external file
        with open('saas_tools_database.json', 'r') as file:
            self.saas_solutions = json.load(file)
    
    def calculate_ai_score(self, assessment_data):
        score = 50  # Base score
        
        # Company size factor
        size_scores = {
            "10-50": 10, "51-100": 15, "101-250": 20, "251-500": 25
        }
        score += size_scores.get(assessment_data.get('company_size', ''), 10)
        
        # Technology readiness
        tech_scores = {
            "basic": 5, "intermediate": 15, "advanced": 25
        }
        score += tech_scores.get(assessment_data.get('current_tech', ''), 5)
        
        # Budget readiness
        budget_scores = {
            "under-25k": 5, "25k-50k": 10, "50k-100k": 15, "over-100k": 20
        }
        score += budget_scores.get(assessment_data.get('budget', ''), 5)
        
        # AI experience
        exp_scores = {
            "none": 0, "exploring": 5, "piloting": 10, "implementing": 15
        }
        score += exp_scores.get(assessment_data.get('ai_experience', ''), 0)
        
        # Timeline urgency
        timeline_scores = {
            "immediate": 15, "3-months": 10, "6-months": 5, "next-year": 0
        }
        score += timeline_scores.get(assessment_data.get('timeline', ''), 0)
        
        return min(score, 100)
    
    def generate_opportunities(self, assessment_data):
        challenges = assessment_data.get('challenges', [])
        opportunities = []
        
        challenge_mapping = {
            "customer-service": {
                "title": "Customer Service Automation",
                "description": "AI chatbots and automated response systems could handle 60-80% of routine inquiries",
                "roi": 45000,
                "solutions": self.saas_solutions.get("customer_service", [])
            },
            "document-processing": {
                "title": "Document Processing Automation",
                "description": "Automated document extraction and processing could reduce manual work by 75%",
                "roi": 32000,
                "solutions": self.saas_solutions.get("workflow_automation", [])
            },
            "data-analysis": {
                "title": "AI-Enhanced Business Intelligence",
                "description": "Natural language queries and automated insights could democratize data access",
                "roi": 28000,
                "solutions": self.saas_solutions.get("business_intelligence", [])
            }
        }
        
        for challenge in challenges:
            if challenge in challenge_mapping:
                # Generate personalized description using LLM
                base_description = challenge_mapping[challenge]["description"]
                personalized_description = llm_service.generate_personalized_opportunity_description(
                    challenge,
                    assessment_data,
                    base_description
                )
                
                # Select relevant tools using LLM
                available_tools = challenge_mapping[challenge]["solutions"]
                selected_tools = llm_service.select_relevant_tools(
                    challenge,
                    assessment_data,
                    available_tools,
                    max_tools=2
                )
                
                opportunity = challenge_mapping[challenge].copy()
                opportunity["description"] = personalized_description
                opportunity["solutions"] = selected_tools
                opportunities.append(opportunity)
        
        # Always include at least one opportunity
        if not opportunities:
            base_description = challenge_mapping["customer-service"]["description"]
            personalized_description = llm_service.generate_personalized_opportunity_description(
                "customer-service",
                assessment_data,
                base_description
            )
            
            # Select relevant tools using LLM
            available_tools = challenge_mapping["customer-service"]["solutions"]
            selected_tools = llm_service.select_relevant_tools(
                "customer-service",
                assessment_data,
                available_tools,
                max_tools=2
            )
            
            opportunity = challenge_mapping["customer-service"].copy()
            opportunity["description"] = personalized_description
            opportunity["solutions"] = selected_tools
            opportunities.append(opportunity)
        
        return opportunities
# Routes
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/assessment')
def assessment():
    return render_template('assessment.html')
@app.route('/education')
def education():
    return render_template('education.html')
@app.route('/solutions')
def solutions():
    return render_template('solutions.html')
@app.route('/roadmap')
def roadmap():
    return render_template('roadmap.html')
@app.route('/reports')
def reports():
    return render_template('reports.html')
@app.route('/api/solutions_data')
def solutions_data():
    """API endpoint to provide solutions data to frontend"""
    engine = AIAssessmentEngine()
    return jsonify(engine.saas_solutions)
@app.route('/api/assessments')
def get_assessments():
    """API endpoint to get all completed assessments"""
    try:
        conn = sqlite3.connect('ai_consultant.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, company_name, industry, first_name, last_name, email, 
                   ai_score, created_at, challenges, opportunities
            FROM assessments 
            ORDER BY created_at DESC
        ''')
        
        assessments = []
        for row in cursor.fetchall():
            assessments.append({
                'id': row[0],
                'company_name': row[1],
                'industry': row[2],
                'contact_name': f"{row[3]} {row[4]}",
                'email': row[5],
                'ai_score': row[6],
                'created_at': row[7],
                'challenges': json.loads(row[8]) if row[8] else [],
                'opportunities': json.loads(row[9]) if row[9] else []
            })
        
        conn.close()
        return jsonify({'success': True, 'assessments': assessments})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
@app.route('/api/assessment/<int:assessment_id>')
def get_assessment_details(assessment_id):
    """Get detailed assessment data for report generation"""
    try:
        conn = sqlite3.connect('ai_consultant.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM assessments WHERE id = ?
        ''', (assessment_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Assessment not found'})
        
        # Get column names for dynamic field mapping
        columns = [description[0] for description in cursor.description]
        
        # Create assessment dict with all available fields
        assessment = {}
        for i, column in enumerate(columns):
            if column in ['challenges', 'opportunities', 'current_tools', 'tool_preferences', 
                         'implementation_priority', 'security_requirements', 'compliance_needs',
                         'integration_requirements', 'success_metrics', 'risk_factors', 
                         'mitigation_strategies', 'implementation_phases', 'resource_requirements',
                         'training_needs', 'vendor_criteria', 'competitors', 'data_governance',
                         'vendor_features', 'risk_concerns', 'improvement_goals']:
                # Parse JSON arrays with better error handling
                try:
                    if row[i] and row[i].strip():
                        assessment[column] = json.loads(row[i])
                    else:
                        assessment[column] = []
                except (json.JSONDecodeError, TypeError, AttributeError):
                    # If JSON parsing fails, try to handle as comma-separated string
                    if row[i] and isinstance(row[i], str):
                        assessment[column] = [item.strip() for item in row[i].split(',') if item.strip()]
                    else:
                        assessment[column] = []
            else:
                # Regular text fields
                assessment[column] = row[i]
        
        conn.close()
        return jsonify({'success': True, 'assessment': assessment})
        
    except Exception as e:
        print(f"Error in get_assessment_details: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})
@app.route('/generate_report_from_assessment', methods=['POST'])
def generate_report_from_assessment():
    try:
        data = request.get_json()
        assessment_id = data.get('assessment_id')
        report_type = data.get('report_type', 'assessment')
        
        # Get assessment data from database
        conn = sqlite3.connect('ai_consultant.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM assessments WHERE id = ?', (assessment_id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'success': False, 'error': 'Assessment not found'})
        
        # Get column names for dynamic field mapping
        columns = [description[0] for description in cursor.description]
        assessment = dict(zip(columns, row))
        
        # Convert database row to assessment data (recompute metrics at generation time)
        assessment_data = {
            'company_name': assessment.get('company_name'),
            'industry': assessment.get('industry'),
            'company_size': assessment.get('company_size'),
            'role': assessment.get('role'),
            'challenges': assessment.get('challenges', []),
            'current_tech': assessment.get('current_tech'),
            'ai_experience': assessment.get('ai_experience'),
            'budget': assessment.get('budget'),
            'timeline': assessment.get('timeline'),
            'first_name': assessment.get('first_name'),
            'last_name': assessment.get('last_name'),
            'email': assessment.get('email'),
            'phone': assessment.get('phone')
        }
        
        conn.close()
        
        # Recompute detailed AI score and LLM-assisted opportunities now
        ai_score = calculate_detailed_ai_score(assessment_data)
        opportunities = generate_detailed_opportunities(assessment_data)

        # Save the LLM-generated opportunities back to the database
        try:
            conn = sqlite3.connect('ai_consultant.db')
            cursor = conn.cursor()
            
            # Update the assessment with the new AI score and opportunities
            cursor.execute('''
                UPDATE assessments 
                SET ai_score = ?, opportunities = ?
                WHERE id = ?
            ''', (ai_score, json.dumps(opportunities), assessment_id))
            
            conn.commit()
            conn.close()
            print(f"Updated assessment {assessment_id} with AI score {ai_score} and {len(opportunities)} opportunities")
        except Exception as e:
            print(f"Warning: Could not save opportunities to database: {str(e)}")

        # Generate HTML report based on report type
        if report_type == 'strategy':
            # Generate Strategy Blueprint Report
            report_html = generate_html_strategy_report(assessment_id, assessment, ai_score, opportunities)
        else:
            # Generate Assessment Report (default)
            report_html = generate_html_assessment_report(assessment_id, assessment_data, ai_score, opportunities)
        
        # Save the HTML report
        company_name = assessment.get('company_name', 'Unknown').replace(' ', '_').replace('/', '_')
        created_at = assessment.get('created_at', datetime.now().strftime('%Y%m%d'))
        
        filename = f"{assessment_id}_{company_name}_{report_type}_{created_at}.html"
        filename = secure_filename(filename)
        
        filepath = os.path.join(REPORTS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_html)
        
        return jsonify({
            'success': True,
            'report_html': report_html,
            'filename': filename,
            'view_url': f'/view_report/{filename}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'HTML generation failed: {str(e)}'})
@app.route('/generate_report', methods=['POST'])
def generate_report():
    try:
        data = request.get_json()
        
        # Calculate detailed AI score and LLM-assisted opportunities
        ai_score = calculate_detailed_ai_score(data)
        opportunities = generate_detailed_opportunities(data)
        
        # Use the new professional PDF generation function
        pdf_filename = generate_assessment_report(999, data, ai_score, opportunities)
        
        return jsonify({
            'success': True,
            'pdf_path': pdf_filename,
            'download_url': f'/download_pdf/{os.path.basename(pdf_filename)}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'PDF generation failed: {str(e)}'})
@app.route('/view_report/<filename>')
def view_report(filename):
    """Serve a saved HTML report"""
    try:
        filepath = os.path.join(REPORTS_DIR, filename)
        if os.path.exists(filepath):
            return send_file(filepath, mimetype='text/html')
        else:
            return jsonify({'success': False, 'error': 'Report not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/list_reports/<int:assessment_id>')
def list_reports(assessment_id):
    """List all reports for a specific assessment"""
    try:
        reports = []
        if os.path.exists(REPORTS_DIR):
            for filename in os.listdir(REPORTS_DIR):
                if filename.startswith(f"{assessment_id}_") and filename.endswith('.html'):
                    reports.append(filename)
        return jsonify({'success': True, 'reports': reports})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download_pdf/<filename>')
def download_pdf(filename):
    return send_file(f'reports/{filename}', as_attachment=True, download_name=filename)
@app.route('/submit_assessment', methods=['POST'])
def submit_assessment():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['company_name', 'first_name', 'last_name', 'email']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({'success': False, 'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data.get('email', '')):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        logger.info(f"Received assessment data for company: {data.get('company_name', 'Unknown')}")
        
        # Calculate detailed AI score and LLM-assisted opportunities
        ai_score = calculate_detailed_ai_score(data)
        opportunities = generate_detailed_opportunities(data)
        if not opportunities:
            opportunities = [{"title": "Customer Service Automation", "description": "AI chatbots could handle routine inquiries", "roi": 25000}]
        
        # Save to database using database manager with form source tracking
        assessment_data = {
            **data,
            'form_source': 'assessment',
            'assessment_completed_at': datetime.now().isoformat(),
            'report_type': 'assessment'
        }
        
        assessment_id = db_manager.save_assessment(assessment_data, ai_score, opportunities)
        
        # Generate and save HTML report
        try:
            report_html = generate_html_assessment_report(assessment_id, data, ai_score, opportunities)
            
            # Create filename with assessment details
            company_name = data.get('company_name', 'Unknown').replace(' ', '_').replace('/', '_')
            report_type = 'assessment'
            created_at = datetime.now().strftime('%Y%m%d')
            
            filename = f"{assessment_id}_{company_name}_{report_type}_{created_at}.html"
            filename = secure_filename(filename)
            
            filepath = os.path.join(REPORTS_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_html)
            
            logger.info(f"HTML report saved: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save HTML report: {str(e)}")
        
        return jsonify({
            'success': True,
            'assessment_id': assessment_id,
            'ai_score': ai_score,
            'opportunities': opportunities,
            'report_path': 'test'
        })
        
    except Exception as e:
        logger.error(f"Error processing assessment: {e}")
        return jsonify({'success': False, 'error': str(e)})
@app.route('/download_report/<int:assessment_id>')
def download_report(assessment_id):
    report_path = f'reports/assessment_{assessment_id}.pdf'
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True)
    return "Report not found", 404
@app.route('/schedule')
def schedule():
    return render_template('schedule.html')
@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    try:
        data = request.get_json()
        
        conn = sqlite3.connect('ai_consultant.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO appointments (
                assessment_id, client_name, client_email,
                appointment_date, appointment_time
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            data.get('assessment_id'),
            f"{data.get('first_name')} {data.get('last_name')}",
            data.get('email'),
            data.get('date'),
            data.get('time')
        ))
        
        appointment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Send confirmation email
        send_appointment_confirmation(data)
        
        return jsonify({'success': True, 'appointment_id': appointment_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
@app.route('/payment/<int:assessment_id>')
def payment(assessment_id):
    return render_template('payment.html', assessment_id=assessment_id)
@app.route('/create_payment_intent', methods=['POST'])
def create_payment_intent():
    try:
        data = request.get_json()
        
        # Create payment intent with Stripe
        intent = stripe.PaymentIntent.create(
            amount=75000,  # $750.00 in cents
            currency='usd',
            metadata={'assessment_id': data.get('assessment_id')}
        )
        
        return jsonify({'client_secret': intent.client_secret})
        
    except Exception as e:
        return jsonify({'error': str(e)})
# Add these routes to your app.py file (add them before the if __name__ == '__main__': line)
@app.route('/admin')
def admin():
    return render_template('admin.html')
@app.route('/api/update_assessment', methods=['POST'])
def update_assessment():
    try:
        data = request.get_json()
        assessment_id = data.get('id')
        
        # Use the DatabaseManager to update all fields
        success = db_manager.update_assessment_fields(
            int(assessment_id), 
            data,
            ai_score=int(data.get('ai_score', 0)) if data.get('ai_score') else None
        )
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to update assessment'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
@app.route('/api/delete_assessment', methods=['POST'])
def delete_assessment():
    try:
        data = request.get_json()
        assessment_id = data.get('id')
        
        conn = sqlite3.connect('ai_consultant.db')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM assessments WHERE id = ?', (assessment_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/api/batch_delete_assessments', methods=['POST'])
def batch_delete_assessments():
    try:
        data = request.get_json()
        assessment_ids = data.get('ids', [])
        
        if not assessment_ids:
            return jsonify({'success': False, 'error': 'No assessment IDs provided'})
        
        conn = sqlite3.connect('ai_consultant.db')
        cursor = conn.cursor()
        
        # Create placeholders for the IN clause
        placeholders = ','.join(['?' for _ in assessment_ids])
        query = f'DELETE FROM assessments WHERE id IN ({placeholders})'
        
        cursor.execute(query, assessment_ids)
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'deleted_count': deleted_count,
            'message': f'Successfully deleted {deleted_count} assessment(s)'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
@app.route('/api/clear_all_assessments', methods=['POST'])
def clear_all_assessments():
    try:
        conn = sqlite3.connect('ai_consultant.db')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM assessments')
        cursor.execute('DELETE FROM appointments')
        cursor.execute('DELETE FROM payments')
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
@app.route('/api/add_sample_data', methods=['POST'])
def add_sample_data():
    """Dynamically generate sample data for all fields in the assessments table"""
    try:
        conn = sqlite3.connect('ai_consultant.db')
        cursor = conn.cursor()
        
        # Get all columns from the assessments table
        cursor.execute("PRAGMA table_info(assessments)")
        columns_info = cursor.fetchall()
        columns = [col[1] for col in columns_info]  # Column names
        
        # Sample data templates
        sample_companies = [
            {
                'company_name': 'Tech Innovations Inc',
                'industry': 'technology',
                'company_size': '101-250',
                'role': 'ceo',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'email': 'jane@techinnovations.com',
                'phone': '555-0123',
                'website': 'www.techinnovations.com'
            },
            {
                'company_name': 'Metro Healthcare',
                'industry': 'healthcare',
                'company_size': '251-500',
                'role': 'it-director',
                'first_name': 'Dr. Robert',
                'last_name': 'Johnson',
                'email': 'robert@metrohealthcare.com',
                'phone': '555-0456',
                'website': 'www.metrohealthcare.com'
            },
            {
                'company_name': 'AutoParts Plus',
                'industry': 'automotive',
                'company_size': '51-100',
                'role': 'ops-manager',
                'first_name': 'Maria',
                'last_name': 'Garcia',
                'email': 'maria@autopartsplus.com',
                'phone': '555-0789',
                'website': 'www.autopartsplus.com'
            }
        ]
        
        def generate_sample_value(column_name, company_data):
            """Generate appropriate sample data based on column name"""
            if column_name == 'company_name':
                return company_data['company_name']
            elif column_name == 'industry':
                return company_data['industry']
            elif column_name == 'company_size':
                return company_data['company_size']
            elif column_name == 'role':
                return company_data['role']
            elif column_name == 'first_name':
                return company_data['first_name']
            elif column_name == 'last_name':
                return company_data['last_name']
            elif column_name == 'email':
                return company_data['email']
            elif column_name == 'phone':
                return company_data['phone']
            elif column_name == 'website':
                return company_data['website']
            elif column_name == 'challenges':
                # Use exact form checkbox values
                challenge_options = ['Customer service bottleneck', 'Data management issues', 'Process inefficiencies']
                return json.dumps(challenge_options)
            elif column_name == 'current_tools':
                # Use exact form checkbox values
                tool_options = ['CRM systems', 'Marketing automation', 'Communication tools']
                return json.dumps(tool_options)
            elif column_name == 'tool_preferences':
                # Use exact form checkbox values
                preference_options = ['Cloud-based solutions', 'Integration capabilities', 'Analytics platforms']
                return json.dumps(preference_options)
            elif column_name == 'current_tech':
                return 'intermediate'
            elif column_name == 'ai_experience':
                return 'piloting'
            elif column_name == 'budget':
                return '50k-100k'
            elif column_name == 'timeline':
                return '3-months'
            elif column_name == 'implementation_priority':
                return 'medium'
            elif column_name == 'team_availability':
                return 'part-time-dedicated'
            elif column_name == 'change_management_experience':
                return 'moderate'
            elif column_name == 'data_governance':
                # Use exact form checkbox values
                governance_options = ['Data classification', 'Access controls']
                return json.dumps(governance_options)
            elif column_name == 'security_requirements':
                # Use exact form checkbox values
                security_options = ['Encryption', 'Compliance certifications']
                return json.dumps(security_options)
            elif column_name == 'compliance_needs':
                # Use exact form checkbox values
                compliance_options = ['SOX', 'Industry-specific']
                return json.dumps(compliance_options)
            elif column_name == 'integration_requirements':
                # Use exact form checkbox values
                integration_options = ['API integration', 'Database connectivity']
                return json.dumps(integration_options)
            elif column_name == 'success_metrics':
                # Use exact form checkbox values
                metrics_options = ['Customer satisfaction', 'Efficiency improvement', 'Cost reduction']
                return json.dumps(metrics_options)
            elif column_name == 'expected_roi':
                return 'medium'
            elif column_name == 'payback_period':
                return '12-months'
            elif column_name == 'risk_factors':
                # Use exact form checkbox values
                risk_options = ['Data security', 'User adoption']
                return json.dumps(risk_options)
            elif column_name == 'mitigation_strategies':
                # Use exact form checkbox values
                mitigation_options = ['Phased implementation', 'Training programs']
                return json.dumps(mitigation_options)
            elif column_name == 'implementation_phases':
                # Use exact form checkbox values
                phase_options = ['Planning & Analysis', 'Design & Development']
                return json.dumps(phase_options)
            elif column_name == 'resource_requirements':
                # Use exact form checkbox values
                resource_options = ['Technical expertise', 'Project management']
                return json.dumps(resource_options)
            elif column_name == 'training_needs':
                # Use exact form checkbox values
                training_options = ['User training', 'Technical training']
                return json.dumps(training_options)
            elif column_name == 'vendor_criteria':
                # Use exact form checkbox values
                vendor_options = ['Cost-effectiveness', 'Technical capabilities']
                return json.dumps(vendor_options)
            elif column_name == 'competitors':
                # Use exact form checkbox values
                competitor_options = ['Direct competitors', 'Indirect competitors']
                return json.dumps(competitor_options)
            elif column_name == 'competitive_advantages':
                # Use exact form checkbox values from admin form
                competitive_options = ['Innovation capabilities', 'Customer relationships', 'Operational efficiency']
                return json.dumps(competitive_options)
            elif column_name == 'market_position':
                return 'challenger'
            elif column_name == 'vendor_features':
                # Use exact form checkbox values from admin form
                vendor_feature_options = ['Scalability', 'Customization', 'Integration capabilities']
                return json.dumps(vendor_feature_options)
            elif column_name == 'risk_tolerance':
                return 'moderate'
            elif column_name == 'risk_concerns':
                # Use exact form checkbox values from admin form
                risk_concern_options = ['Data security', 'Vendor lock-in', 'Implementation delays']
                return json.dumps(risk_concern_options)
            elif column_name == 'org_structure':
                return 'hierarchical'
            elif column_name == 'decision_process':
                return 'consultative'
            elif column_name == 'team_size':
                return '16-50'
            elif column_name == 'skill_gaps':
                # Use exact form checkbox values from admin form
                skill_gap_options = ['Technical skills', 'Data analysis', 'Change management']
                return json.dumps(skill_gap_options)
            elif column_name == 'budget_allocation':
                return 'balanced'
            elif column_name == 'roi_timeline':
                return '12-months'
            elif column_name == 'current_kpis':
                # Use exact form checkbox values from admin form
                kpi_options = ['Revenue growth', 'Customer satisfaction', 'Operational efficiency']
                return json.dumps(kpi_options)
            elif column_name == 'improvement_goals':
                # Use exact form checkbox values from admin form
                goal_options = ['Process automation', 'Data analytics', 'Customer experience']
                return json.dumps(goal_options)
            elif column_name == 'ai_score':
                return random.randint(75, 95)
            elif column_name == 'opportunities':
                opportunities = [
                    {
                        "title": "Customer Service Automation",
                        "description": "Implement AI chatbots to handle routine inquiries",
                        "roi": random.randint(30000, 40000)
                    },
                    {
                        "title": "Data Analytics & BI",
                        "description": "Deploy AI-powered analytics for better insights",
                        "roi": random.randint(30000, 40000)
                    }
                ]
                return json.dumps(opportunities)
            elif column_name == 'report_type':
                return 'assessment'
            elif column_name == 'form_source':
                return 'assessment'
            elif column_name == 'assessment_completed_at':
                return datetime.now().isoformat()
            elif column_name == 'strategy_completed_at':
                return None
            elif column_name == 'created_at':
                return datetime.now().isoformat()
            else:
                # For any other fields, return a default value
                return None
        
        # Generate sample data for each company
        for company_data in sample_companies:
            # Generate values for all columns
            values = []
            placeholders = []
            
            for column in columns:
                if column == 'id':  # Skip auto-increment field
                    continue
                values.append(generate_sample_value(column, company_data))
                placeholders.append('?')
            
            # Build dynamic INSERT query
            columns_str = ', '.join([col for col in columns if col != 'id'])
            placeholders_str = ', '.join(placeholders)
            
            query = f"INSERT INTO assessments ({columns_str}) VALUES ({placeholders_str})"
            cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': f'Added {len(sample_companies)} sample assessments with all fields populated'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/save_assessment_progress', methods=['POST'])
def save_assessment_progress():
    """Create or update an assessment record with partial data during step navigation.

    - If `assessment_id` is provided, update only the provided fields
    - If not provided, create a new assessment row and return its id
    """
    try:
        payload = request.get_json(silent=True) or {}

        # Ensure database schema (adds extended columns if missing)
        try:
            db_manager.init_db()
        except Exception:
            pass

        assessment_id = payload.pop('assessment_id', None)

        if assessment_id:
            # Update provided fields only
            db_manager.update_assessment_fields(int(assessment_id), payload)
            return jsonify({
                'success': True,
                'assessment_id': int(assessment_id)
            })
        else:
            # Create a minimal record; allow empty strings for optional fields
            # Ensure NOT NULL company_name is satisfied
            if not payload.get('company_name'):
                payload['company_name'] = ''

            new_id = db_manager.save_assessment(payload, ai_score=0, opportunities=[])
            return jsonify({
                'success': True,
                'assessment_id': int(new_id)
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/db_view')
def api_db_view():
    """Return raw assessment rows with all columns for admin DB View."""
    try:
        conn = sqlite3.connect('ai_consultant.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT * FROM assessments ORDER BY created_at DESC')
        rows = cur.fetchall()
        conn.close()

        def row_to_dict(r: sqlite3.Row):
            return {k: r[k] for k in r.keys()}

        return jsonify({
            'success': True,
            'rows': [row_to_dict(r) for r in rows]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
@app.route('/api/form_summary')
def api_form_summary():
    """Get form completion summary for all assessments"""
    try:
        conn = sqlite3.connect('ai_consultant.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                id,
                company_name,
                email,
                form_source,
                assessment_completed_at,
                strategy_completed_at,
                CASE 
                    WHEN assessment_completed_at IS NOT NULL AND strategy_completed_at IS NOT NULL 
                    THEN 'Complete (Both Forms)'
                    WHEN assessment_completed_at IS NOT NULL 
                    THEN 'Assessment Only'
                    WHEN strategy_completed_at IS NOT NULL 
                    THEN 'Strategy Only'
                    ELSE 'Incomplete'
                END as completion_status,
                created_at
            FROM assessments
            ORDER BY created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        assessments = []
        for row in rows:
            assessments.append({
                'id': row[0],
                'company_name': row[1],
                'email': row[2],
                'form_source': row[3],
                'assessment_completed_at': row[4],
                'strategy_completed_at': row[5],
                'completion_status': row[6],
                'created_at': row[7]
            })
        
        return jsonify({
            'success': True,
            'assessments': assessments
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/assessment_data')
def api_assessment_data():
    """Get only assessment form data"""
    try:
        conn = sqlite3.connect('ai_consultant.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                id,
                company_name,
                industry,
                company_size,
                role,
                website,
                challenges,
                current_tech,
                ai_experience,
                budget,
                timeline,
                first_name,
                last_name,
                email,
                phone,
                current_tools,
                tool_preferences,
                implementation_priority,
                team_availability,
                change_management_experience,
                data_governance,
                security_requirements,
                compliance_needs,
                integration_requirements,
                success_metrics,
                expected_roi,
                payback_period,
                risk_factors,
                mitigation_strategies,
                implementation_phases,
                resource_requirements,
                training_needs,
                vendor_criteria,
                pilot_project,
                scalability_requirements,
                maintenance_plan,
                assessment_completed_at
            FROM assessments
            WHERE assessment_completed_at IS NOT NULL
            ORDER BY assessment_completed_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        assessments = []
        for row in rows:
            # Helper function to safely parse JSON fields
            def safe_json_loads(value):
                if not value or value == 'None':
                    return []
                try:
                    if isinstance(value, str):
                        if value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        if value == '[]':
                            return []
                        if value == '{}':
                            return {}
                    return json.loads(value) if isinstance(value, str) else value
                except (json.JSONDecodeError, TypeError):
                    return []
            
            assessments.append({
                'id': row[0],
                'company_name': row[1],
                'industry': row[2],
                'company_size': row[3],
                'role': row[4],
                'website': row[5],
                'challenges': safe_json_loads(row[6]),
                'current_tech': row[7],
                'ai_experience': row[8],
                'budget': row[9],
                'timeline': row[10],
                'first_name': row[11],
                'last_name': row[12],
                'email': row[13],
                'phone': row[14],
                'current_tools': safe_json_loads(row[15]),
                'tool_preferences': safe_json_loads(row[16]),
                'implementation_priority': safe_json_loads(row[17]),
                'team_availability': row[18],
                'change_management_experience': row[19],
                'data_governance': safe_json_loads(row[20]),
                'security_requirements': safe_json_loads(row[21]),
                'compliance_needs': safe_json_loads(row[22]),
                'integration_requirements': safe_json_loads(row[23]),
                'success_metrics': safe_json_loads(row[24]),
                'expected_roi': row[25],
                'payback_period': row[26],
                'risk_factors': safe_json_loads(row[27]),
                'mitigation_strategies': safe_json_loads(row[28]),
                'implementation_phases': safe_json_loads(row[29]),
                'resource_requirements': safe_json_loads(row[30]),
                'training_needs': safe_json_loads(row[31]),
                'vendor_criteria': safe_json_loads(row[32]),
                'pilot_project': row[33],
                'scalability_requirements': row[34],
                'maintenance_plan': row[35],
                'assessment_completed_at': row[36]
            })
        
        return jsonify({
            'success': True,
            'assessments': assessments
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/strategy_data')
def api_strategy_data():
    """Get only strategy form data"""
    try:
        conn = sqlite3.connect('ai_consultant.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                id,
                company_name,
                email,
                competitors,
                competitive_advantages,
                market_position,
                vendor_features,
                risk_tolerance,
                risk_concerns,
                org_structure,
                decision_process,
                team_size,
                skill_gaps,
                budget_allocation,
                roi_timeline,
                current_kpis,
                improvement_goals,
                strategy_completed_at
            FROM assessments
            WHERE strategy_completed_at IS NOT NULL
            ORDER BY strategy_completed_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        assessments = []
        for row in rows:
            # Helper function to safely parse JSON fields
            def safe_json_loads(value):
                if not value or value == 'None':
                    return []
                try:
                    if isinstance(value, str):
                        if value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        if value == '[]':
                            return []
                        if value == '{}':
                            return {}
                    return json.loads(value) if isinstance(value, str) else value
                except (json.JSONDecodeError, TypeError):
                    return []
            
            assessments.append({
                'id': row[0],
                'company_name': row[1],
                'email': row[2],
                'competitors': safe_json_loads(row[3]),
                'competitive_advantages': safe_json_loads(row[4]),
                'market_position': row[5],
                'vendor_features': safe_json_loads(row[6]),
                'risk_tolerance': row[7],
                'risk_concerns': safe_json_loads(row[8]),
                'org_structure': row[9],
                'decision_process': row[10],
                'team_size': row[11],
                'skill_gaps': safe_json_loads(row[12]),
                'budget_allocation': row[13],
                'roi_timeline': row[14],
                'current_kpis': safe_json_loads(row[15]),
                'improvement_goals': safe_json_loads(row[16]),
                'strategy_completed_at': row[17]
            })
        
        return jsonify({
            'success': True,
            'assessments': assessments
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def generate_assessment_data(form_data):
    """Generate comprehensive assessment data for PDF report"""
    return generate_enhanced_assessment_data(form_data)
def generate_enhanced_assessment_data(form_data):
    """Generate enhanced assessment data for the $750 report"""
    ai_score = calculate_detailed_ai_score(form_data)
    opportunities = generate_detailed_opportunities(form_data)
    
    # Calculate sub-scores with better logic
    tech_score = min(ai_score + 5, 95)
    data_score = max(min(ai_score - 2, 90), 45)  # Ensure minimum score
    team_score = min(ai_score + 3, 92)
    process_score = ai_score
    
    # Ensure all scores are integers
    tech_score = int(tech_score)
    data_score = int(data_score)
    team_score = int(team_score)
    process_score = int(process_score)
    
    readiness_level = 'High' if ai_score >= 80 else 'Medium' if ai_score >= 60 else 'Developing'
    
    result = {
        'client_company': form_data.get('company_name', 'Your Company'),
        'primary_contact': f"{form_data.get('first_name', '')} {form_data.get('last_name', '')}".strip() or form_data.get('primary_contact', 'Contact'),
        'report_date': datetime.now().strftime('%B %d, %Y'),
        'industry': form_data.get('industry', 'Business'),
        'ai_score': ai_score,
        'readiness_level': readiness_level,
        'opportunity_count': len(opportunities),
        'total_roi_min': sum(opp.get('roi', 0) for opp in opportunities),
        'total_roi_max': sum(opp.get('roi', 0) for opp in opportunities),
        'opportunities': opportunities,
        
        # Detailed scores - these are the readiness percentages
        'tech_score': tech_score,
        'tech_status': 'Ready' if tech_score >= 75 else 'Good' if tech_score >= 60 else 'Developing',
        'tech_strengths': 'Existing digital infrastructure provides solid foundation for AI integration',
        'data_score': data_score,
        'data_status': 'Ready' if data_score >= 75 else 'Good' if data_score >= 60 else 'Developing', 
        'data_strengths': 'Structured business data available in key operational systems',
        'team_score': team_score,
        'team_status': 'Ready' if team_score >= 75 else 'Good' if team_score >= 60 else 'Developing',
        'team_strengths': 'Leadership commitment to technology adoption and team development',
        'process_score': process_score,
        'process_status': 'Ready' if process_score >= 75 else 'Good' if process_score >= 60 else 'Developing',
        'process_strengths': 'Well-documented business processes ready for optimization and automation',
    }
    
    return result

def calculate_detailed_ai_score(form_data):
    """Calculate detailed AI readiness score"""
    score = 50  # Base score
    
    # Industry bonus - fix field mapping
    industry_scores = {
        'automotive': 15, 'healthcare': 12, 'manufacturing': 18,
        'retail': 14, 'professional-services': 10, 'technology': 20
    }
    # Use 'industry' field (from database)
    industry = form_data.get('industry', '')
    score += industry_scores.get(industry, 10)
    
    # Challenges indicate opportunity - fix field mapping
    challenges = form_data.get('challenges', [])
    if isinstance(challenges, list):
        challenges_str = ' '.join(challenges).lower()
    else:
        challenges_str = str(challenges).lower()
    
    if 'manual' in challenges_str: score += 8
    if 'data' in challenges_str: score += 6
    if 'customer' in challenges_str: score += 7
    
    # Technology level
    current_tech = form_data.get('current_tech', 'basic')
    tech_scores = {'basic': 5, 'intermediate': 15, 'advanced': 25}
    score += tech_scores.get(current_tech, 5)
    
    # AI experience
    ai_exp = form_data.get('ai_experience', 'none')
    exp_scores = {'none': 0, 'exploring': 5, 'piloting': 10, 'implementing': 15}
    score += exp_scores.get(ai_exp, 0)
    
    # Budget readiness
    budget = form_data.get('budget', 'under-25k')
    budget_scores = {'under-25k': 5, '25k-50k': 10, '50k-100k': 15, 'over-100k': 20}
    score += budget_scores.get(budget, 5)
    
    # Timeline urgency
    timeline = form_data.get('timeline', 'next-year')
    timeline_scores = {'immediate': 15, '3-months': 12, '6-months': 8, 'next-year': 3}
    score += timeline_scores.get(timeline, 3)
    
    # Role influence
    role = form_data.get('role', 'other')
    role_scores = {'ceo': 10, 'coo': 8, 'it-director': 6, 'ops-manager': 4, 'other': 2}
    score += role_scores.get(role, 2)
    
    # print(f"DEBUG Score Calculation: Industry:{industry}({industry_scores.get(industry, 10)}), Challenges:{challenges_str}, Tech:{current_tech}({tech_scores.get(current_tech, 5)}), Final Score:{min(score, 100)}")
    
    return min(score, 100)



def generate_detailed_opportunities(form_data):
    """Generate detailed opportunities based on form data with realistic ROI"""
    opportunities = []
    
    # Load SaaS solutions from database
    try:
        with open('saas_tools_database.json', 'r') as file:
            saas_solutions = json.load(file)
    except:
        saas_solutions = {}
    
    # Fix field mapping - use 'challenges' instead of 'key_challenges'
    challenges = form_data.get('challenges', [])
    if isinstance(challenges, list):
        challenges_str = ' '.join(challenges).lower()
    else:
        challenges_str = str(challenges).lower()
    
    if 'customer' in challenges_str or 'service' in challenges_str:
        base_description = 'Implement AI-powered chatbots and automated response systems to handle routine customer inquiries and support requests.'
        
        # Generate personalized description using LLM
        personalized_description = llm_service.generate_personalized_opportunity_description(
            'customer-service',
            form_data,
            base_description
        )
        
        # Select relevant tools using LLM
        available_customer_service_tools = saas_solutions.get("customer_service", [])
        selected_tools = llm_service.select_relevant_tools(
            'customer-service',
            form_data,
            available_customer_service_tools,
            max_tools=2
        )
        
        # Use hardcoded ROI
        roi = 125000
        
        opportunities.append({
            'title': 'Customer Service Automation',
            'roi': roi,
            'description': personalized_description,
            'impact': 'Reduce response times by 75%, handle 60% of inquiries automatically, improve customer satisfaction scores',
            'approach': 'Start with FAQ automation, expand to complex query handling, integrate with existing CRM systems',
            'solutions': selected_tools
        })
    
    if 'manual' in challenges_str or 'document' in challenges_str:
        base_description = 'Automate repetitive business processes including data entry, document processing, and workflow management.'
        
        # Generate personalized description using LLM
        personalized_description = llm_service.generate_personalized_opportunity_description(
            'document-processing',
            form_data,
            base_description
        )
        
        # Select relevant tools using LLM
        available_workflow_tools = saas_solutions.get("workflow_automation", [])
        selected_tools = llm_service.select_relevant_tools(
            'document-processing',
            form_data,
            available_workflow_tools,
            max_tools=2
        )
        
        # Use hardcoded ROI
        roi = 150000
        
        opportunities.append({
            'title': 'Process Automation',
            'roi': roi,
            'description': personalized_description,
            'impact': 'Save 20+ hours per week per employee, reduce errors by 90%, accelerate process completion',
            'approach': 'Map current processes, identify automation opportunities, implement workflow tools with AI integration',
            'solutions': selected_tools
        })
    
    if 'data' in challenges_str or 'analysis' in challenges_str:
        base_description = 'Implement AI-powered analytics and reporting to extract actionable insights from business data.'
        
        # Generate personalized description using LLM
        personalized_description = llm_service.generate_personalized_opportunity_description(
            'data-analysis',
            form_data,
            base_description
        )
        
        # Select relevant tools using LLM
        available_bi_tools = saas_solutions.get("business_intelligence", [])
        selected_tools = llm_service.select_relevant_tools(
            'data-analysis',
            form_data,
            available_bi_tools,
            max_tools=3  # Allow more tools for BI since it's broader
        )
        
        # Use hardcoded ROI
        roi = 100000
        
        opportunities.append({
            'title': 'AI-Enhanced Business Intelligence',
            'roi': roi,
            'description': personalized_description,
            'impact': 'Faster decision-making, predictive insights, automated reporting, improved forecasting accuracy',
            'approach': 'Integrate AI analytics with existing data sources, train models on historical data, deploy interactive dashboards',
            'solutions': selected_tools
        })
    
    if 'sales-marketing' in challenges_str:
        base_description = 'Optimize sales and marketing processes with AI-powered lead scoring, automation, and analytics.'
        
        # Generate personalized description using LLM
        personalized_description = llm_service.generate_personalized_opportunity_description(
            'sales-marketing',
            form_data,
            base_description
        )
        
        # Select relevant tools using LLM
        available_sales_tools = saas_solutions.get("sales_marketing", [])
        selected_tools = llm_service.select_relevant_tools(
            'sales-marketing',
            form_data,
            available_sales_tools,
            max_tools=2
        )
        
        # Use hardcoded ROI
        roi = 200000
        
        opportunities.append({
            'title': 'Sales & Marketing Optimization',
            'roi': roi,
            'description': personalized_description,
            'impact': 'Increase lead conversion by 30%, reduce sales cycle time, improve marketing ROI',
            'approach': 'Implement AI lead scoring, automate follow-up sequences, optimize marketing campaigns',
            'solutions': selected_tools
        })
    
    # Ensure at least one opportunity
    if not opportunities:
        base_description = 'Establish AI-ready infrastructure and processes to enable future automation and intelligence initiatives.'
        
        # Generate personalized description using LLM
        personalized_description = llm_service.generate_personalized_opportunity_description(
            'process-automation',
            form_data,
            base_description
        )
        
        # Select relevant tools using LLM
        available_workflow_tools = saas_solutions.get("workflow_automation", [])
        selected_tools = llm_service.select_relevant_tools(
            'process-automation',
            form_data,
            available_workflow_tools,
            max_tools=2
        )
        
        # Use hardcoded ROI
        roi = 150000
        
        opportunities.append({
            'title': 'Digital Transformation Foundation',
            'roi': roi,
            'description': personalized_description,
            'impact': 'Improved data quality, streamlined processes, team AI literacy, foundation for advanced implementations',
            'approach': 'Data audit and cleanup, process documentation, team training, pilot project identification',
            'solutions': selected_tools
        })
    
    return opportunities[:3]  # Return top 3 opportunities

def generate_html_assessment_report(assessment_id, data, ai_score, opportunities):
    """Generate an HTML assessment report using the enhanced template"""
    try:
        # Load the enhanced template
        template_path = os.path.join('report_templates', 'enhanced_assessment_report.html')
        if not os.path.exists(template_path):
            return f"<h1>Error: Enhanced assessment template not found</h1>"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Generate comprehensive report data using ReportGenerator
        from report_generator import ReportGenerator
        report_gen = ReportGenerator()
        report_data = report_gen.generate_assessment_report_data(data)
        
        # Helper function to safely parse JSON or string data
        def safe_parse_list(value):
            if isinstance(value, list):
                return value
            elif isinstance(value, str):
                try:
                    # Try to parse as JSON first
                    import json
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return parsed
                except (json.JSONDecodeError, TypeError):
                    pass
                # If it's a string representation of a list, try to parse it
                if value.startswith('[') and value.endswith(']'):
                    # Remove brackets and split by comma
                    content = value[1:-1]
                    items = [item.strip().strip('"\'') for item in content.split(',') if item.strip()]
                    return items
            return []
        
        # Add basic data for template
        report_data.update({
            'assessment_id': assessment_id,
            'ai_score': ai_score,
            'opportunities': opportunities,
            'client_company': data.get('company_name', 'Unknown Company'),
            'primary_contact': f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
            'report_date': datetime.now().strftime('%B %d, %Y'),
            'company_name': data.get('company_name', 'Unknown Company'),
            'industry': data.get('industry', 'Not specified'),
            'company_size': data.get('company_size', 'Not specified'),
            'role': data.get('role', 'Not specified'),
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'website': data.get('website', ''),
            'current_tech': data.get('current_tech', 'Not specified'),
            'ai_experience': data.get('ai_experience', 'Not specified'),
            'budget': data.get('budget', 'Not specified'),
            'timeline': data.get('timeline', 'Not specified'),
            'challenges': safe_parse_list(data.get('challenges', [])),
            'current_tools': safe_parse_list(data.get('current_tools', [])),
            'created_at': data.get('created_at', datetime.now().isoformat()),
            'form_source': data.get('form_source', 'assessment')
        })
        
        # Render template with Jinja2
        from jinja2 import Template
        template = Template(template_content)
        html_content = template.render(**report_data)
        return html_content
        
    except Exception as e:
        return f"<h1>Error generating HTML report: {str(e)}</h1>"

def generate_html_strategy_report(assessment_id, assessment_data, ai_score, opportunities):
    """Generate a comprehensive Strategy Blueprint HTML report"""
    try:
        # Load the strategy blueprint template
        template_path = os.path.join('report_templates', 'strategy_blueprint_report.html')
        
        if not os.path.exists(template_path):
            return f"<h1>Error: Strategy Blueprint template not found</h1>"
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Prepare comprehensive data for the strategy report
        report_data = {
            'assessment_id': assessment_id,
            'client_company': assessment_data.get('company_name', 'Unknown Company'),
            'primary_contact': f"{assessment_data.get('first_name', '')} {assessment_data.get('last_name', '')}".strip(),
            'report_date': datetime.now().strftime('%B %d, %Y'),
            'company_name': assessment_data.get('company_name', 'Unknown Company'),
            'industry': assessment_data.get('industry', 'Not specified'),
            'company_size': assessment_data.get('company_size', 'Not specified'),
            'role': assessment_data.get('role', 'Not specified'),
            'first_name': assessment_data.get('first_name', ''),
            'last_name': assessment_data.get('last_name', ''),
            'email': assessment_data.get('email', ''),
            'phone': assessment_data.get('phone', ''),
            'website': assessment_data.get('website', ''),
            'ai_score': ai_score,
            'opportunities': opportunities,
            'challenges': assessment_data.get('challenges', []),
            'current_tech': assessment_data.get('current_tech', 'Not specified'),
            'ai_experience': assessment_data.get('ai_experience', 'Not specified'),
            'budget': assessment_data.get('budget', 'Not specified'),
            'timeline': assessment_data.get('timeline', 'Not specified'),
            'current_tools': assessment_data.get('current_tools', []),
            'tool_preferences': assessment_data.get('tool_preferences', []),
            'implementation_priority': assessment_data.get('implementation_priority', []),
            'team_availability': assessment_data.get('team_availability', 'Not specified'),
            'change_management_experience': assessment_data.get('change_management_experience', 'Not specified'),
            'data_governance': assessment_data.get('data_governance', []),
            'security_requirements': assessment_data.get('security_requirements', []),
            'compliance_needs': assessment_data.get('compliance_needs', []),
            'integration_requirements': assessment_data.get('integration_requirements', []),
            'success_metrics': assessment_data.get('success_metrics', []),
            'expected_roi': assessment_data.get('expected_roi', 'Not specified'),
            'payback_period': assessment_data.get('payback_period', 'Not specified'),
            'risk_factors': assessment_data.get('risk_factors', []),
            'mitigation_strategies': assessment_data.get('mitigation_strategies', []),
            'implementation_phases': assessment_data.get('implementation_phases', []),
            'resource_requirements': assessment_data.get('resource_requirements', []),
            'training_needs': assessment_data.get('training_needs', []),
            'vendor_criteria': assessment_data.get('vendor_criteria', []),
            'competitors': assessment_data.get('competitors', []),
            'competitive_advantages': assessment_data.get('competitive_advantages', []),
            'market_position': assessment_data.get('market_position', 'Not specified'),
            'vendor_features': assessment_data.get('vendor_features', []),
            'risk_tolerance': assessment_data.get('risk_tolerance', 'Not specified'),
            'risk_concerns': assessment_data.get('risk_concerns', []),
            'org_structure': assessment_data.get('org_structure', 'Not specified'),
            'decision_process': assessment_data.get('decision_process', 'Not specified'),
            'team_size': assessment_data.get('team_size', 'Not specified'),
            'skill_gaps': assessment_data.get('skill_gaps', []),
            'budget_allocation': assessment_data.get('budget_allocation', 'Not specified'),
            'roi_timeline': assessment_data.get('roi_timeline', 'Not specified'),
            'current_kpis': assessment_data.get('current_kpis', []),
            'improvement_goals': assessment_data.get('improvement_goals', []),
            'created_at': assessment_data.get('created_at', datetime.now().isoformat()),
            'form_source': assessment_data.get('form_source', 'assessment'),
            # Additional variables expected by the template
            'strategic_position': assessment_data.get('market_position', 'Emerging').title(),
            'total_roi_min': sum([opp.get('roi', 0) for opp in opportunities]) if opportunities else 50000,
            'competitor_1_name': 'Direct Competitor A',
            'competitor_1_position': 'Market Leader',
            'competitor_1_analysis': 'Strong market presence with established AI capabilities.',
            'competitor_2_name': 'Direct Competitor B',
            'competitor_2_position': 'Challenger',
            'competitor_2_analysis': 'Innovative approach but limited scale.',
            'competitor_3_name': 'Indirect Competitor',
            'competitor_3_position': 'Niche Player',
            'competitor_3_analysis': 'Specialized focus in specific market segments.',
            'strategic_recommendations': 'Focus on rapid AI adoption to gain competitive advantage.',
            'vendors': [
                {'name': 'Vendor A', 'category': 'AI Platform', 'cost_rating': 'medium', 'features_rating': 'high', 'support_rating': 'high', 'integration_rating': 'medium', 'overall_score': 8},
                {'name': 'Vendor B', 'category': 'Analytics', 'cost_rating': 'low', 'features_rating': 'medium', 'support_rating': 'medium', 'integration_rating': 'high', 'overall_score': 7},
                {'name': 'Vendor C', 'category': 'Automation', 'cost_rating': 'high', 'features_rating': 'high', 'support_rating': 'high', 'integration_rating': 'high', 'overall_score': 9}
            ],
            'risks': [
                {'title': 'Data Security Risk', 'level': 'Medium', 'impact': 'High', 'mitigation': 'Implement robust security protocols'},
                {'title': 'Implementation Risk', 'level': 'High', 'impact': 'Medium', 'mitigation': 'Phased rollout approach'},
                {'title': 'Adoption Risk', 'level': 'Medium', 'impact': 'Medium', 'mitigation': 'Comprehensive training program'}
            ],
            'q1_budget': 25000,
            'q2_budget': 35000,
            'q3_budget': 30000,
            'q4_budget': 20000,
            'total_budget': 110000,
            'roi_percentage': 25,
            'kpis': [
                {'metric': 'Efficiency', 'current_value': '75%', 'target_value': '90%'},
                {'metric': 'Cost Savings', 'current_value': '$50K', 'target_value': '$150K'},
                {'metric': 'Customer Satisfaction', 'current_value': '82%', 'target_value': '95%'}
            ]
        }
        
        # Use Jinja2 to render the template
        from jinja2 import Template
        template = Template(template_content)
        html_content = template.render(**report_data)
        
        return html_content
        
    except Exception as e:
        return f"<h1>Error generating Strategy Blueprint report: {str(e)}</h1>"

def generate_assessment_report(assessment_id, data, ai_score, opportunities):
    """Generate clean, professional PDF assessment report"""
    os.makedirs('reports', exist_ok=True)
    filename = f'reports/assessment_{assessment_id}.pdf'
    
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Clean, minimal styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=20,
        alignment=1,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#374151'),
        spaceAfter=30,
        alignment=1,
        fontName='Helvetica'
    )
    
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=12,
        spaceBefore=25,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        fontName='Helvetica'
    )
    
    # Header
    story.append(Paragraph("AI Opportunity Assessment Report", title_style))
    story.append(Paragraph("Strategic Analysis & Implementation Roadmap", subtitle_style))
    
    # Report Overview
    story.append(Paragraph("Report Overview", section_style))
    overview_text = """
    This comprehensive assessment evaluates your organization's AI readiness and identifies 
    high-impact opportunities for artificial intelligence implementation. Based on your 
    specific industry, company size, and current technology landscape, this report provides:
    """
    story.append(Paragraph(overview_text, normal_style))
    
    # Value points - clean list
    value_points = [
        "AI readiness score with detailed breakdown",
        "3-5 prioritized AI opportunities tailored to your business", 
        "High-level ROI estimates for each opportunity",
        "Curated vendor recommendations from our approved portfolio",
        "12-month implementation timeline overview",
        "Immediate next steps to begin your AI journey"
    ]
    
    for point in value_points:
        story.append(Paragraph(point, normal_style))
    
    story.append(Spacer(1, 20))
    
    # Company Profile
    story.append(Paragraph("Company Profile", section_style))
    
    company_info = f"""
    Company: {data.get('company_name', 'N/A')}
    Industry: {data.get('industry', 'N/A')}
    Size: {data.get('company_size', 'N/A')}
    Revenue: {data.get('revenue_range', 'N/A')}
    Primary Goal: {data.get('primary_goal', 'N/A')}
    Contact: {data.get('first_name', '')} {data.get('last_name', '')}
    """
    story.append(Paragraph(company_info, normal_style))
    
    # Add success metrics if provided
    if data.get('success_metrics'):
        story.append(Paragraph("Success Metrics:", normal_style))
        story.append(Paragraph(data.get('success_metrics'), normal_style))
    
    story.append(Spacer(1, 20))
    
    # AI Readiness Assessment
    story.append(Paragraph("AI Readiness Assessment", section_style))
    
    if ai_score >= 80:
        readiness_level = "High Readiness"
        readiness_desc = "Excellent foundation for AI implementation"
        score_color = colors.HexColor('#059669')
    elif ai_score >= 60:
        readiness_level = "Medium Readiness"
        readiness_desc = "Good potential with some preparation needed"
        score_color = colors.HexColor('#d97706')
    else:
        readiness_level = "Developing Readiness"
        readiness_desc = "Foundation building recommended before major AI initiatives"
        score_color = colors.HexColor('#dc2626')
    
    score_style = ParagraphStyle(
        'Score',
        parent=styles['Normal'],
        fontSize=12,
        textColor=score_color,
        fontName='Helvetica-Bold',
        spaceAfter=8
    )
    
    story.append(Paragraph(f"Score: {ai_score}/100", score_style))
    story.append(Paragraph(f"Level: {readiness_level}", normal_style))
    story.append(Paragraph(readiness_desc, normal_style))
    story.append(Spacer(1, 20))
    
    # AI Opportunities
    story.append(Paragraph("Identified AI Opportunities", section_style))
    
    for i, opp in enumerate(opportunities, 1):
        # Opportunity title with subtle background
        opp_title_style = ParagraphStyle(
            'OpportunityTitle',
            parent=styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#1e3a8a'),
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#f1f5f9'),
            borderWidth=1,
            borderColor=colors.HexColor('#cbd5e1'),
            borderPadding=6,
            spaceAfter=10
        )
        
        story.append(Paragraph(f"#{i} {opp['title']}", opp_title_style))
        story.append(Paragraph(opp['description'], normal_style))
        
        roi_style = ParagraphStyle(
            'ROI',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#059669'),
            fontName='Helvetica-Bold',
            spaceAfter=8
        )
        story.append(Paragraph(f"Estimated Annual ROI: ${opp['roi']:,}", roi_style))
        
        # Solutions
        story.append(Paragraph("Recommended Solutions:", normal_style))
        
        for sol in opp['solutions']:
            tool_name = sol['name']
            if sol.get('type') == 'External':
                tool_name = f"{tool_name} *"
            
            solution_text = f"{tool_name} ({sol['type']}) - {sol['cost']}"
            story.append(Paragraph(solution_text, normal_style))
            story.append(Paragraph(sol['description'], normal_style))
        
        story.append(Spacer(1, 15))
    
    # Tool Legend
    legend_style = ParagraphStyle(
        'Legend',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        alignment=1,
        spaceAfter=20
    )
    story.append(Paragraph("Note: * External tool recommendation", legend_style))
    
    # Next Steps
    story.append(Paragraph("Recommended Next Steps", section_style))
    
    next_steps = [
        "Schedule a consultation call to discuss findings in detail",
        "Prioritize opportunities based on your specific business needs", 
        "Develop detailed implementation roadmap for top opportunities",
        "Begin with a pilot project to validate approach and build confidence",
        "Plan team training and change management strategy"
    ]
    
    for step in next_steps:
        story.append(Paragraph(step, normal_style))
    
    # Footer
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        alignment=1,
        fontName='Helvetica'
    )
    story.append(Paragraph("Generated on " + datetime.now().strftime("%B %d, %Y"), footer_style))
    
    doc.build(story)
    return filename

def send_appointment_confirmation(data):
    """Send appointment confirmation email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = data.get('email')
        msg['Subject'] = "AI Consultation Appointment Confirmed"
        
        body = f"""
        Dear {data.get('first_name')},
        
        Your AI consultation appointment has been confirmed for:
        
        Date: {data.get('date')}
        Time: {data.get('time')}
        
        We'll discuss your AI assessment results and develop a strategic implementation plan for your business.
        
        Best regards,
        AI Strategy Pro Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, data.get('email'), text)
        server.quit()
        
    except Exception as e:
        print(f"Email sending failed: {e}")

# Dynamic Form Builder API Endpoints
@app.route('/api/section_configurations')
def get_section_configurations():
    """Get all section configurations"""
    try:
        conn = sqlite3.connect('ai_consultant.db')
        cursor = conn.cursor()
        
        form_flag = request.args.get('form_flag')
        
        query = '''
            SELECT section_name, section_title, step_number, is_required, is_visible, description, form_flag
            FROM section_configurations
        '''
        
        if form_flag:
            query += ' WHERE form_flag = ?'
            query += ' ORDER BY step_number, section_name'
            cursor.execute(query, (form_flag,))
        else:
            query += ' ORDER BY step_number, section_name'
            cursor.execute(query)
        
        rows = cursor.fetchall()
        conn.close()
        
        configurations = []
        for row in rows:
            configurations.append({
                'section_name': row[0],
                'section_title': row[1],
                'step_number': row[2],
                'is_required': bool(row[3]),
                'is_visible': bool(row[4]),
                'description': row[5],
                'form_flag': row[6]
            })
        
        return jsonify({
            'success': True,
            'configurations': configurations
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/field_configurations')
def get_field_configurations():
    """Get all field configurations"""
    try:
        conn = sqlite3.connect('ai_consultant.db')
        cursor = conn.cursor()
        
        form_flag = request.args.get('form_flag')
        
        query = '''
            SELECT fc.field_name, fc.field_label, fc.field_type, fc.section_name, fc.is_required, fc.is_visible, fc.form_flag, fc.step_number, fc.sort_order, sc.step_number as section_step, sc.section_title
            FROM field_configurations fc
            LEFT JOIN section_configurations sc ON fc.section_name = sc.section_name AND fc.form_flag = sc.form_flag
        '''
        
        if form_flag:
            query += ' WHERE fc.form_flag = ?'
            query += ' ORDER BY sc.step_number, fc.step_number, fc.sort_order, fc.field_name'
            cursor.execute(query, (form_flag,))
        else:
            query += ' ORDER BY sc.step_number, fc.step_number, fc.sort_order, fc.field_name'
            cursor.execute(query)
        
        rows = cursor.fetchall()
        conn.close()
        
        configurations = []
        for row in rows:
            configurations.append({
                'field_name': row[0],
                'field_label': row[1],
                'field_type': row[2],
                'section_name': row[3],
                'is_required': bool(row[4]),
                'is_visible': bool(row[5]),
                'form_flag': row[6],
                'step_number': row[7] if row[7] is not None else 1,
                'sort_order': row[8] if row[8] is not None else 0,
                'section_step': row[9] if row[9] is not None else 1,
                'section_title': row[10] if row[10] is not None else 'Unassigned'
            })
        
        return jsonify({
            'success': True,
            'configurations': configurations
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dropdown_options')
def get_dropdown_options():
    """Get all dropdown options"""
    try:
        conn = sqlite3.connect('ai_consultant.db')
        cursor = conn.cursor()
        
        form_flag = request.args.get('form_flag')
        
        query = '''
            SELECT id, field_name, option_value, option_label, sort_order, form_flag
            FROM dropdown_options
        '''
        
        if form_flag:
            query += ' WHERE form_flag = ?'
            query += ' ORDER BY field_name, sort_order'
            cursor.execute(query, (form_flag,))
        else:
            query += ' ORDER BY field_name, sort_order'
            cursor.execute(query)
        
        rows = cursor.fetchall()
        conn.close()
        
        options = []
        for row in rows:
            options.append({
                'id': row[0],
                'field_name': row[1],
                'option_value': row[2],
                'option_label': row[3],
                'sort_order': row[4],
                'form_flag': row[5]
            })
        
        return jsonify({
            'success': True,
            'options': options
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/field_configurations/<field_name>', methods=['PUT'])
def update_field_configuration(field_name):
    """Update a field configuration"""
    try:
        data = request.get_json()
        conn = sqlite3.connect('ai_consultant.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE field_configurations
            SET field_label = ?, field_type = ?, section_name = ?, is_required = ?, is_visible = ?, step_number = ?, sort_order = ?
            WHERE field_name = ?
        ''', (
            data.get('field_label'),
            data.get('field_type'),
            data.get('section_name'),
            data.get('is_required', False),
            data.get('is_visible', True),
            data.get('step_number', 1),
            data.get('sort_order', 0),
            field_name
        ))
        
        # Update section step if provided
        if data.get('section_step') and data.get('section_name'):
            cursor.execute('''
                UPDATE section_configurations
                SET step_number = ?
                WHERE section_name = ? AND form_flag = ?
            ''', (
                data.get('section_step'),
                data.get('section_name'),
                data.get('form_flag', 'A')
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/section_configurations', methods=['POST'])
def add_section_configuration():
    """Add a new section configuration"""
    try:
        data = request.get_json()
        conn = sqlite3.connect('ai_consultant.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO section_configurations (section_name, section_title, step_number, is_required, is_visible, description, form_flag)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('section_name'),
            data.get('section_title'),
            data.get('step_number'),
            data.get('is_required', False),
            data.get('is_visible', True),
            data.get('description'),
            data.get('form_flag')
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/section_configurations/<section_name>', methods=['PUT'])
def update_section_configuration(section_name):
    """Update a section configuration"""
    try:
        data = request.get_json()
        success = db_manager.update_section_configuration(section_name, data)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/section_configurations/<section_name>', methods=['DELETE'])
def delete_section_configuration(section_name):
    """Delete a section configuration"""
    try:
        success = db_manager.delete_section_configuration(section_name)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dropdown_options', methods=['POST'])
def add_dropdown_option():
    """Add a new dropdown option"""
    try:
        data = request.get_json()
        conn = sqlite3.connect('ai_consultant.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO dropdown_options (field_name, option_value, option_label, sort_order, form_flag)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data.get('field_name'),
            data.get('option_value'),
            data.get('option_label'),
            data.get('sort_order', 0),
            data.get('form_flag')
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dropdown_options/<int:option_id>', methods=['PUT'])
def update_dropdown_option(option_id):
    """Update a dropdown option"""
    try:
        data = request.get_json()
        success = db_manager.update_dropdown_option(option_id, data)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dropdown_options/<int:option_id>', methods=['DELETE'])
def delete_dropdown_option(option_id):
    """Delete a dropdown option"""
    try:
        success = db_manager.delete_dropdown_option(option_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)