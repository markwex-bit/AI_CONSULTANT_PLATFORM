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
                         'training_needs', 'vendor_criteria']:
                # Parse JSON arrays
                assessment[column] = json.loads(row[i]) if row[i] else []
            else:
                # Regular text fields
                assessment[column] = row[i]
        
        conn.close()
        return jsonify({'success': True, 'assessment': assessment})
        
    except Exception as e:
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

        # Generate HTML report
        report_html = generate_html_assessment_report(assessment_id, assessment_data, ai_score, opportunities)
        
        # Save the HTML report
        company_name = assessment.get('company_name', 'Unknown').replace(' ', '_').replace('/', '_')
        report_type = assessment.get('report_type', 'assessment')
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
        
        # Save to database using context manager
        with sqlite3.connect('ai_consultant.db') as conn:
            cursor = conn.cursor()
            
            challenges_json = json.dumps(data.get('challenges', []))
            opportunities_json = json.dumps(opportunities)
            
            cursor.execute('''
                INSERT INTO assessments (
                    company_name, industry, company_size, role, challenges,
                    current_tech, ai_experience, budget, timeline,
                    first_name, last_name, email, phone, ai_score, opportunities
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('company_name'), data.get('industry'), data.get('company_size'),
                data.get('role'), challenges_json, data.get('current_tech'),
                data.get('ai_experience'), data.get('budget'), data.get('timeline'),
                data.get('first_name'), data.get('last_name'), data.get('email'),
                data.get('phone'), ai_score, opportunities_json
            ))
            
            assessment_id = cursor.lastrowid
        
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
    try:
        conn = sqlite3.connect('ai_consultant.db')
        cursor = conn.cursor()
        
        sample_assessments = [
            ('Tech Innovations Inc', 'technology', '101-250', 'ceo', 
             '["manual-processes", "data-analysis"]', 'advanced', 'implementing', 
             'over-100k', 'immediate', 'Jane', 'Doe', 'jane@techinnovations.com', 
             '555-0123', 92, '[]'),
            ('Metro Healthcare', 'healthcare', '251-500', 'it-director',
             '["customer-service", "document-processing"]', 'intermediate', 'piloting',
             '50k-100k', '3-months', 'Dr. Robert', 'Johnson', 'robert@metrohealthcare.com',
             '555-0456', 78, '[]'),
            ('AutoParts Plus', 'automotive', '51-100', 'ops-manager',
             '["manual-processes", "competitive-pressure"]', 'basic', 'exploring',
             '25k-50k', '6-months', 'Maria', 'Garcia', 'maria@autopartsplus.com',
             '555-0789', 65, '[]')
        ]
        
        for sample in sample_assessments:
            cursor.execute('''
                INSERT INTO assessments (
                    company_name, industry, company_size, role, challenges,
                    current_tech, ai_experience, budget, timeline,
                    first_name, last_name, email, phone, ai_score, opportunities
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample)
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
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
    """Generate an HTML assessment report"""
    try:
        # Create a professional HTML report
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Strategy Assessment Report - {data.get('company_name', 'Company')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #4f46e5;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #1f2937;
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            color: #6b7280;
            margin: 10px 0 0 0;
            font-size: 1.1em;
        }}
        .score-section {{
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }}
        .score {{
            font-size: 4em;
            font-weight: bold;
            margin: 0;
        }}
        .score-label {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .section {{
            margin-bottom: 30px;
            padding: 25px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            background: #fafafa;
        }}
        .section h2 {{
            color: #1f2937;
            border-bottom: 2px solid #4f46e5;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .opportunity-card {{
            background: white;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        .opportunity-title {{
            color: #1f2937;
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .opportunity-description {{
            color: #6b7280;
            margin-bottom: 15px;
        }}
        .roi {{
            color: #059669;
            font-weight: bold;
            font-size: 1.1em;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .info-item {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #4f46e5;
        }}
        .info-label {{
            font-weight: bold;
            color: #374151;
            margin-bottom: 5px;
        }}
        .info-value {{
            color: #6b7280;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            color: #6b7280;
        }}
        @media print {{
            body {{ background: white; }}
            .container {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Strategy Assessment Report</h1>
            <p>Generated for {data.get('company_name', 'Company')} on {datetime.now().strftime('%B %d, %Y')}</p>
        </div>
        
        <div class="score-section">
            <div class="score">{ai_score}%</div>
            <div class="score-label">AI Readiness Score</div>
        </div>
        
        <div class="section">
            <h2>Company Information</h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Company Name</div>
                    <div class="info-value">{data.get('company_name', 'Not specified')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Industry</div>
                    <div class="info-value">{data.get('industry', 'Not specified')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Company Size</div>
                    <div class="info-value">{data.get('company_size', 'Not specified')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Primary Contact</div>
                    <div class="info-value">{data.get('first_name', '')} {data.get('last_name', '')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Role</div>
                    <div class="info-value">{data.get('role', 'Not specified')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Email</div>
                    <div class="info-value">{data.get('email', 'Not provided')}</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Current Technology Assessment</h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Current Tech Level</div>
                    <div class="info-value">{data.get('current_tech', 'Not specified')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">AI Experience</div>
                    <div class="info-value">{data.get('ai_experience', 'Not specified')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Budget Range</div>
                    <div class="info-value">{data.get('budget', 'Not specified')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Timeline</div>
                    <div class="info-value">{data.get('timeline', 'Not specified')}</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Business Challenges</h2>
            <div class="info-item">
                <div class="info-value">
                    {', '.join(data.get('challenges', [])) if data.get('challenges') else 'No challenges specified'}
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>AI Opportunities</h2>
            {''.join([f'''
            <div class="opportunity-card">
                <div class="opportunity-title">{opp.get('title', 'Opportunity')}</div>
                <div class="opportunity-description">{opp.get('description', 'No description available')}</div>
                <div class="roi">Estimated ROI: ${opp.get('roi', 0):,}</div>
            </div>
            ''' for opp in opportunities]) if opportunities else '<p>No opportunities identified</p>'}
        </div>
        
        <div class="footer">
            <p>Report ID: {assessment_id} | Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>This report was generated by the AI Strategy Consultant Platform</p>
        </div>
    </div>
</body>
</html>
        """
        return html_content
    except Exception as e:
        return f"<html><body><h1>Error generating report</h1><p>{str(e)}</p></body></html>"

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
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)