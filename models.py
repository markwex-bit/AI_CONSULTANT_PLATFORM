"""Database models and operations (enhanced).

This module defines `DatabaseManager` with full support for the enhanced
assessment form. Arrays are persisted as JSON strings while simple text
fields are stored as plain TEXT, so the Admin View and reports can read
them without stray quotes.
"""

import sqlite3
import json
from contextlib import contextmanager


class DatabaseManager:
    """Database connection and operation manager"""

    def __init__(self, db_path: str = 'ai_consultant.db'):
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    # ---------- Schema ----------
    def init_db(self) -> None:
        """Initialize database tables and ensure new columns exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Base table
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    industry TEXT,
                    company_size TEXT,
                    role TEXT,
                    website TEXT,
                    challenges TEXT,
                    current_tech TEXT,
                    ai_experience TEXT,
                    budget TEXT,
                    timeline TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT,
                    phone TEXT,
                    ai_score INTEGER,
                    opportunities TEXT,
                    report_type TEXT DEFAULT 'assessment',
                    form_source TEXT DEFAULT 'assessment',  -- Tracks which form(s) provided data
                    assessment_completed_at TIMESTAMP,      -- When assessment form was completed
                    strategy_completed_at TIMESTAMP,        -- When strategy form was completed
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                '''
            )

            # Additive columns for enhanced assessment and strategy blueprint
            def add_column(name: str):
                try:
                    cursor.execute(f'ALTER TABLE assessments ADD COLUMN {name}')
                except sqlite3.OperationalError:
                    pass  # already exists

            # Add form tracking columns if they don't exist
            add_column('form_source TEXT DEFAULT "assessment"')
            add_column('assessment_completed_at TIMESTAMP')
            add_column('strategy_completed_at TIMESTAMP')

            # Strategy blueprint related (S_ prefix in views)
            add_column('competitors TEXT')
            add_column('competitive_advantages TEXT')
            add_column('market_position TEXT')
            add_column('vendor_features TEXT')
            add_column('risk_tolerance TEXT')
            add_column('risk_concerns TEXT')
            add_column('org_structure TEXT')
            add_column('decision_process TEXT')
            add_column('team_size TEXT')
            add_column('skill_gaps TEXT')
            add_column('budget_allocation TEXT')
            add_column('roi_timeline TEXT')
            add_column('current_kpis TEXT')
            add_column('improvement_goals TEXT')

            # Enhanced assessment fields (A_ prefix in views)
            add_column('current_tools TEXT')
            add_column('tool_preferences TEXT')
            add_column('implementation_priority TEXT')
            add_column('team_availability TEXT')
            add_column('change_management_experience TEXT')
            add_column('data_governance TEXT')
            add_column('security_requirements TEXT')
            add_column('compliance_needs TEXT')
            add_column('integration_requirements TEXT')
            add_column('success_metrics TEXT')
            add_column('expected_roi TEXT')
            add_column('payback_period TEXT')
            add_column('risk_factors TEXT')
            add_column('mitigation_strategies TEXT')
            add_column('implementation_phases TEXT')
            add_column('resource_requirements TEXT')
            add_column('training_needs TEXT')
            add_column('vendor_criteria TEXT')
            add_column('pilot_project TEXT')
            add_column('scalability_requirements TEXT')
            add_column('maintenance_plan TEXT')

            # Secondary tables
            cursor.execute(
                '''
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
                '''
            )

            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assessment_id INTEGER,
                    stripe_payment_id TEXT,
                    amount INTEGER,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (assessment_id) REFERENCES assessments (id)
                )
                '''
            )

            # Create enhanced views for better data source identification
            self._create_labeled_views(cursor)
            self._create_form_source_views(cursor)

            conn.commit()

    def _create_labeled_views(self, cursor) -> None:
        try:
            cursor.execute('DROP VIEW IF EXISTS assessments_labeled')
            cursor.execute('DROP VIEW IF EXISTS assessment_fields_view')
            cursor.execute('DROP VIEW IF EXISTS strategy_fields_view')
        except Exception:
            pass

        cursor.execute(
            '''
            CREATE VIEW IF NOT EXISTS assessments_labeled AS
            SELECT
              id,
              created_at,
              report_type,
              company_name AS A_company_name,
              industry AS A_industry,
              company_size AS A_company_size,
              role AS A_role,
              challenges AS A_challenges,
              current_tech AS A_current_tech,
              ai_experience AS A_ai_experience,
              budget AS A_budget,
              timeline AS A_timeline,
              first_name AS A_first_name,
              last_name AS A_last_name,
              email AS A_email,
              phone AS A_phone,
              ai_score AS A_ai_score,
              opportunities AS A_opportunities,
              current_tools AS A_current_tools,
              tool_preferences AS A_tool_preferences,
              implementation_priority AS A_implementation_priority,
              team_availability AS A_team_availability,
              change_management_experience AS A_change_management_experience,
              data_governance AS A_data_governance,
              security_requirements AS A_security_requirements,
              compliance_needs AS A_compliance_needs,
              integration_requirements AS A_integration_requirements,
              success_metrics AS A_success_metrics,
              expected_roi AS A_expected_roi,
              payback_period AS A_payback_period,
              risk_factors AS A_risk_factors,
              mitigation_strategies AS A_mitigation_strategies,
              implementation_phases AS A_implementation_phases,
              resource_requirements AS A_resource_requirements,
              training_needs AS A_training_needs,
              vendor_criteria AS A_vendor_criteria,
              pilot_project AS A_pilot_project,
              scalability_requirements AS A_scalability_requirements,
              maintenance_plan AS A_maintenance_plan,
              competitors AS S_competitors,
              competitive_advantages AS S_competitive_advantages,
              market_position AS S_market_position,
              vendor_features AS S_vendor_features,
              risk_tolerance AS S_risk_tolerance,
              risk_concerns AS S_risk_concerns,
              org_structure AS S_org_structure,
              decision_process AS S_decision_process,
              team_size AS S_team_size,
              skill_gaps AS S_skill_gaps,
              budget_allocation AS S_budget_allocation,
              roi_timeline AS S_roi_timeline,
              current_kpis AS S_current_kpis,
              improvement_goals AS S_improvement_goals
            FROM assessments
            '''
        )

        cursor.execute(
            '''
            CREATE VIEW IF NOT EXISTS assessment_fields_view AS
            SELECT
              id,
              created_at,
              report_type,
              company_name AS A_company_name,
              industry AS A_industry,
              company_size AS A_company_size,
              role AS A_role,
              challenges AS A_challenges,
              current_tech AS A_current_tech,
              ai_experience AS A_ai_experience,
              budget AS A_budget,
              timeline AS A_timeline,
              first_name AS A_first_name,
              last_name AS A_last_name,
              email AS A_email,
              phone AS A_phone,
              ai_score AS A_ai_score,
              opportunities AS A_opportunities,
              current_tools AS A_current_tools,
              tool_preferences AS A_tool_preferences,
              implementation_priority AS A_implementation_priority,
              team_availability AS A_team_availability,
              change_management_experience AS A_change_management_experience,
              data_governance AS A_data_governance,
              security_requirements AS A_security_requirements,
              compliance_needs AS A_compliance_needs,
              integration_requirements AS A_integration_requirements,
              success_metrics AS A_success_metrics,
              expected_roi AS A_expected_roi,
              payback_period AS A_payback_period,
              risk_factors AS A_risk_factors,
              mitigation_strategies AS A_mitigation_strategies,
              implementation_phases AS A_implementation_phases,
              resource_requirements AS A_resource_requirements,
              training_needs AS A_training_needs,
              vendor_criteria AS A_vendor_criteria,
              pilot_project AS A_pilot_project,
              scalability_requirements AS A_scalability_requirements,
              maintenance_plan AS A_maintenance_plan
            FROM assessments
            '''
        )

        cursor.execute(
            '''
            CREATE VIEW IF NOT EXISTS strategy_fields_view AS
            SELECT
              id,
              created_at,
              report_type,
              competitors AS S_competitors,
              competitive_advantages AS S_competitive_advantages,
              market_position AS S_market_position,
              vendor_features AS S_vendor_features,
              risk_tolerance AS S_risk_tolerance,
              risk_concerns AS S_risk_concerns,
              org_structure AS S_org_structure,
              decision_process AS S_decision_process,
              team_size AS S_team_size,
              skill_gaps AS S_skill_gaps,
              budget_allocation AS S_budget_allocation,
              roi_timeline AS S_roi_timeline,
              current_kpis AS S_current_kpis,
              improvement_goals AS S_improvement_goals
            FROM assessments
            '''
        )

    def _create_form_source_views(self, cursor) -> None:
        """Create views that clearly identify which form provided which data"""
        try:
            cursor.execute('DROP VIEW IF EXISTS form_data_summary')
            cursor.execute('DROP VIEW IF EXISTS assessment_only_data')
            cursor.execute('DROP VIEW IF EXISTS strategy_only_data')
            cursor.execute('DROP VIEW IF EXISTS complete_data')
        except Exception:
            pass

        # View showing which forms have been completed for each assessment
        cursor.execute(
            '''
            CREATE VIEW IF NOT EXISTS form_data_summary AS
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
            '''
        )

        # View showing only assessment form data
        cursor.execute(
            '''
            CREATE VIEW IF NOT EXISTS assessment_only_data AS
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
            '''
        )

        # View showing only strategy form data
        cursor.execute(
            '''
            CREATE VIEW IF NOT EXISTS strategy_only_data AS
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
            '''
        )

        # View showing complete data (both forms)
        cursor.execute(
            '''
            CREATE VIEW IF NOT EXISTS complete_data AS
            SELECT
                id,
                company_name,
                email,
                form_source,
                assessment_completed_at,
                strategy_completed_at,
                -- Assessment fields
                industry, company_size, role, website, challenges,
                current_tech, ai_experience, budget, timeline,
                first_name, last_name, phone,
                current_tools, tool_preferences, implementation_priority,
                team_availability, change_management_experience, data_governance,
                security_requirements, compliance_needs, integration_requirements,
                success_metrics, expected_roi, payback_period, risk_factors,
                mitigation_strategies, implementation_phases, resource_requirements,
                training_needs, vendor_criteria, pilot_project,
                scalability_requirements, maintenance_plan,
                -- Strategy fields
                competitors, competitive_advantages, market_position,
                vendor_features, risk_tolerance, risk_concerns, org_structure,
                decision_process, team_size, skill_gaps, budget_allocation,
                roi_timeline, current_kpis, improvement_goals
            FROM assessments
            WHERE assessment_completed_at IS NOT NULL AND strategy_completed_at IS NOT NULL
            '''
        )

    # ---------- Writes ----------
    def save_assessment(self, assessment_data: dict, ai_score: int, opportunities: list) -> int:
        """Insert a new assessment with all enhanced fields populated."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Arrays → JSON
            challenges_json = json.dumps(assessment_data.get('challenges', []))
            opportunities_json = json.dumps(opportunities or [])
            current_tools_json = json.dumps(assessment_data.get('current_tools', []))
            tool_preferences_json = json.dumps(assessment_data.get('tool_preferences', []))
            implementation_priority_json = json.dumps(assessment_data.get('implementation_priority', []))
            security_requirements_json = json.dumps(assessment_data.get('security_requirements', []))
            compliance_needs_json = json.dumps(assessment_data.get('compliance_needs', []))
            integration_requirements_json = json.dumps(assessment_data.get('integration_requirements', []))
            success_metrics_json = json.dumps(assessment_data.get('success_metrics', []))
            risk_factors_json = json.dumps(assessment_data.get('risk_factors', []))
            mitigation_strategies_json = json.dumps(assessment_data.get('mitigation_strategies', []))
            implementation_phases_json = json.dumps(assessment_data.get('implementation_phases', []))
            resource_requirements_json = json.dumps(assessment_data.get('resource_requirements', []))
            training_needs_json = json.dumps(assessment_data.get('training_needs', []))
            vendor_criteria_json = json.dumps(assessment_data.get('vendor_criteria', []))

            # Scalars → plain text
            report_type = assessment_data.get('report_type', 'assessment')
            expected_roi_val = assessment_data.get('expected_roi') or ''
            payback_period_val = assessment_data.get('payback_period') or ''
            team_availability_val = assessment_data.get('team_availability') or ''
            change_mgmt_val = assessment_data.get('change_management_experience') or ''
            data_governance_val = assessment_data.get('data_governance') or ''
            pilot_project_val = assessment_data.get('pilot_project') or ''
            scalability_requirements_val = assessment_data.get('scalability_requirements') or ''
            maintenance_plan_val = assessment_data.get('maintenance_plan') or ''
            website_val = assessment_data.get('website') or ''

            cursor.execute(
                '''
                INSERT INTO assessments (
                    company_name, industry, company_size, role, website, challenges,
                    current_tech, ai_experience, budget, timeline,
                    first_name, last_name, email, phone, ai_score, opportunities, report_type,
                    current_tools, tool_preferences, implementation_priority, team_availability,
                    change_management_experience, data_governance, security_requirements,
                    compliance_needs, integration_requirements, success_metrics, expected_roi,
                    payback_period, risk_factors, mitigation_strategies, implementation_phases,
                    resource_requirements, training_needs, vendor_criteria, pilot_project,
                    scalability_requirements, maintenance_plan, form_source, assessment_completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    assessment_data.get('company_name'),
                    assessment_data.get('industry'),
                    assessment_data.get('company_size'),
                    assessment_data.get('role'),
                    website_val,
                    challenges_json,
                    assessment_data.get('current_tech'),
                    assessment_data.get('ai_experience'),
                    assessment_data.get('budget'),
                    assessment_data.get('timeline'),
                    assessment_data.get('first_name'),
                    assessment_data.get('last_name'),
                    assessment_data.get('email'),
                    assessment_data.get('phone'),
                    ai_score,
                    opportunities_json,
                    report_type,
                    current_tools_json,
                    tool_preferences_json,
                    implementation_priority_json,
                    team_availability_val,
                    change_mgmt_val,
                    data_governance_val,
                    security_requirements_json,
                    compliance_needs_json,
                    integration_requirements_json,
                    success_metrics_json,
                    expected_roi_val,
                    payback_period_val,
                    risk_factors_json,
                    mitigation_strategies_json,
                    implementation_phases_json,
                    resource_requirements_json,
                    training_needs_json,
                    vendor_criteria_json,
                    pilot_project_val,
                    scalability_requirements_val,
                    maintenance_plan_val,
                    assessment_data.get('form_source', 'assessment'),
                    assessment_data.get('assessment_completed_at'),
                ),
            )

            conn.commit()
            return cursor.lastrowid

    def update_assessment_fields(self, assessment_id: int, fields: dict, *, ai_score: int | None = None, opportunities: list | None = None) -> bool:
        """Update only provided fields for progressive save. Arrays are JSON-serialized."""
        if not assessment_id:
            raise ValueError('assessment_id is required for update')

        json_array_fields = {
            'challenges', 'current_tools', 'tool_preferences', 'implementation_priority',
            'security_requirements', 'compliance_needs', 'integration_requirements',
            'success_metrics', 'risk_factors', 'mitigation_strategies', 'implementation_phases',
            'resource_requirements', 'training_needs', 'vendor_criteria'
        }

        set_clauses: list[str] = []
        values: list = []

        for key, value in fields.items():
            if key == 'assessment_id':
                continue
            if key in json_array_fields:
                set_clauses.append(f"{key} = ?")
                values.append(json.dumps(value if value is not None else []))
            else:
                set_clauses.append(f"{key} = ?")
                values.append('' if value is None else value)

        if ai_score is not None:
            set_clauses.append('ai_score = ?')
            values.append(ai_score)
        if opportunities is not None:
            set_clauses.append('opportunities = ?')
            values.append(json.dumps(opportunities))

        if not set_clauses:
            return True

        values.append(assessment_id)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE assessments SET {', '.join(set_clauses)} WHERE id = ?", values)
            conn.commit()
            return True

    def update_assessment_strategy(self, assessment_id: int, strategy_data: dict) -> bool:
        """Persist Strategy Blueprint-specific fields and set report_type."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            vendor_features_json = json.dumps(strategy_data.get('vendor_features', []))
            cursor.execute(
                '''
                UPDATE assessments SET
                    competitors = ?,
                    competitive_advantages = ?,
                    market_position = ?,
                    vendor_features = ?,
                    risk_tolerance = ?,
                    risk_concerns = ?,
                    org_structure = ?,
                    decision_process = ?,
                    team_size = ?,
                    skill_gaps = ?,
                    budget_allocation = ?,
                    roi_timeline = ?,
                    current_kpis = ?,
                    improvement_goals = ?,
                    report_type = 'strategy_blueprint',
                    strategy_completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                ''',
                (
                    strategy_data.get('competitors'),
                    strategy_data.get('competitive_advantages'),
                    strategy_data.get('market_position'),
                    vendor_features_json,
                    strategy_data.get('risk_tolerance'),
                    strategy_data.get('risk_concerns'),
                    strategy_data.get('org_structure'),
                    strategy_data.get('decision_process'),
                    strategy_data.get('team_size'),
                    strategy_data.get('skill_gaps'),
                    strategy_data.get('budget_allocation'),
                    strategy_data.get('roi_timeline'),
                    strategy_data.get('current_kpis'),
                    strategy_data.get('improvement_goals'),
                    assessment_id,
                ),
            )
            conn.commit()
            return True

    # ---------- Reads ----------
    def get_assessment_by_email(self, email: str) -> dict | None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM assessments WHERE email = ? ORDER BY created_at DESC LIMIT 1', (email,))
            row = cursor.fetchone()
            if not row:
                return None
            columns = [d[0] for d in cursor.description]
            return dict(zip(columns, row))

    def get_assessments(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT id, company_name, industry, company_size, role,
                       first_name, last_name, email, ai_score, created_at
                FROM assessments
                ORDER BY created_at DESC
                '''
            )
            return cursor.fetchall()

    def get_assessment_by_id(self, assessment_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM assessments WHERE id = ?', (assessment_id,))
            return cursor.fetchone()

    # ---------- Field Configuration Methods ----------
    def initialize_field_configurations(self):
        """Initialize default field configurations if table is empty"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create field_configurations table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS field_configurations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    field_name TEXT UNIQUE NOT NULL,
                    field_label TEXT NOT NULL,
                    field_type TEXT NOT NULL,
                    is_required INTEGER DEFAULT 0,
                    is_visible INTEGER DEFAULT 1,
                    validation_rules TEXT,
                    default_value TEXT,
                    help_text TEXT,
                    step_number INTEGER DEFAULT 1,
                    sort_order INTEGER DEFAULT 0,
                    section_name TEXT,
                    form_flag TEXT DEFAULT 'A'
                )
            ''')
            
            # Create section_configurations table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS section_configurations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    section_name TEXT UNIQUE NOT NULL,
                    section_title TEXT NOT NULL,
                    step_number INTEGER DEFAULT 1,
                    is_required INTEGER DEFAULT 1,
                    is_visible INTEGER DEFAULT 1,
                    description TEXT
                )
            ''')
            
            # Create dropdown_options table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dropdown_options (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    field_name TEXT NOT NULL,
                    option_value TEXT NOT NULL,
                    option_label TEXT NOT NULL,
                    sort_order INTEGER DEFAULT 0,
                    UNIQUE(field_name, option_value)
                )
            ''')
            
            # Add form_flag column if it doesn't exist
            cursor.execute('PRAGMA table_info(field_configurations)')
            columns = [col[1] for col in cursor.fetchall()]
            if 'form_flag' not in columns:
                cursor.execute('ALTER TABLE field_configurations ADD COLUMN form_flag TEXT DEFAULT "A"')
                conn.commit()
                print("Added 'form_flag' column to field_configurations.")
            
            cursor.execute('SELECT COUNT(*) FROM field_configurations')
            if cursor.fetchone()[0] == 0:
                # Initialize sections first
                self._initialize_sections(cursor)
                
                # Default field configurations with sections and form flags
                default_configs = [
                    # Assessment Fields (A)
                    ('company_name', 'Company Name', 'text', 1, 1, 'required', '', 'Enter your company name', 1, 1, 'Contact & Company Information', 'A'),
                    ('first_name', 'First Name', 'text', 1, 1, 'required', '', 'Enter your first name', 1, 2, 'Contact & Company Information', 'A'),
                    ('last_name', 'Last Name', 'text', 1, 1, 'required', '', 'Enter your last name', 1, 3, 'Contact & Company Information', 'A'),
                    ('email', 'Email Address', 'email', 1, 1, 'required|email', '', 'Enter your business email', 1, 4, 'Contact & Company Information', 'A'),
                    ('phone', 'Phone Number', 'tel', 1, 1, 'required', '', 'Enter your phone number', 1, 5, 'Contact & Company Information', 'A'),
                    ('website', 'Website', 'url', 0, 1, 'url', '', 'Enter your company website (optional)', 1, 6, 'Contact & Company Information', 'A'),
                    ('industry', 'Industry', 'select', 1, 1, 'required', '', 'Select your industry', 1, 7, 'Contact & Company Information', 'A'),
                    ('company_size', 'Company Size', 'select', 1, 1, 'required', '', 'Select your company size', 1, 8, 'Contact & Company Information', 'A'),
                    ('role', 'Your Role', 'select', 1, 1, 'required', '', 'Select your role in the company', 1, 9, 'Contact & Company Information', 'A'),
                    ('challenges', 'Key Challenges', 'checkbox', 0, 1, '', '', 'Select your main challenges', 2, 1, 'Business Challenges', 'A'),
                    ('current_tech', 'Current Technology Level', 'select', 1, 1, 'required', '', 'Select your current technology level', 3, 1, 'Technology Foundation', 'A'),
                    ('ai_experience', 'AI Experience', 'select', 1, 1, 'required', '', 'Select your AI experience level', 3, 2, 'Technology Foundation', 'A'),
                    ('deployment_preference', 'Deployment Preference', 'select', 0, 1, '', '', 'Select your deployment preference', 3, 3, 'Technology Foundation', 'A'),
                    ('solution_preference', 'Solution Preference', 'select', 0, 1, '', '', 'Select your solution preference', 3, 4, 'Technology Foundation', 'A'),
                    ('technical_expertise', 'Technical Expertise', 'select', 0, 1, '', '', 'Select your technical expertise level', 3, 5, 'Technology Foundation', 'A'),
                    ('current_tools', 'Current Tools & Software', 'checkbox', 0, 1, '', '', 'Select your current tools', 3, 6, 'Technology Foundation', 'A'),
                    ('tool_preferences', 'Tool Preferences', 'checkbox', 0, 1, '', '', 'Select your tool preferences', 3, 7, 'Technology Foundation', 'A'),
                    ('implementation_priority', 'Implementation Priority', 'checkbox', 0, 1, '', '', 'Select your implementation priorities', 4, 1, 'Implementation Planning', 'A'),
                    ('team_availability', 'Team Availability', 'select', 0, 1, '', '', 'Select team availability', 4, 2, 'Implementation Planning', 'A'),
                    ('change_management_experience', 'Change Management Experience', 'select', 0, 1, '', '', 'Select your change management experience', 4, 3, 'Implementation Planning', 'A'),
                    ('budget', 'Estimated AI Budget', 'select', 1, 1, 'required', '', 'Select your budget range', 4, 4, 'Implementation Planning', 'A'),
                    ('timeline', 'Implementation Timeline', 'select', 1, 1, 'required', '', 'Select your timeline', 4, 5, 'Implementation Planning', 'A'),
                    ('data_governance', 'Data Governance Maturity', 'select', 0, 1, '', '', 'Select your data governance level', 5, 1, 'Security & Compliance', 'A'),
                    ('security_requirements', 'Security Requirements', 'checkbox', 0, 1, '', '', 'Select your security requirements', 5, 2, 'Security & Compliance', 'A'),
                    ('compliance_needs', 'Compliance Needs', 'checkbox', 0, 1, '', '', 'Select your compliance needs', 5, 3, 'Security & Compliance', 'A'),
                    ('integration_requirements', 'Integration Requirements', 'checkbox', 0, 1, '', '', 'Select your integration requirements', 5, 4, 'Security & Compliance', 'A'),
                    ('success_metrics', 'Success Metrics', 'checkbox', 0, 1, '', '', 'Select your success metrics', 6, 1, 'Success Measurement', 'A'),
                    ('expected_roi', 'Expected ROI Range', 'select', 0, 1, '', '', 'Select your expected ROI', 6, 2, 'Success Measurement', 'A'),
                    ('payback_period', 'Expected Payback Period', 'select', 0, 1, '', '', 'Select your payback period', 6, 3, 'Success Measurement', 'A'),
                    
                    # Strategic Blueprint Fields (S)
                    ('competitors', 'Key Competitors', 'textarea', 1, 1, 'required', '', 'List your key competitors', 8, 1, 'Strategic Foundation', 'S'),
                    ('competitive_advantages', 'Competitive Advantages', 'checkbox', 1, 1, 'required', '', 'Select your competitive advantages', 8, 2, 'Strategic Foundation', 'S'),
                    ('market_position', 'Market Position', 'select', 1, 1, 'required', '', 'Select your market position', 8, 3, 'Strategic Foundation', 'S'),
                    ('vendor_features', 'Required Vendor Features', 'checkbox', 1, 1, 'required', '', 'Select required vendor features', 10, 1, 'Vendor Strategy', 'S'),
                    ('risk_tolerance', 'Risk Tolerance', 'select', 1, 1, 'required', '', 'Select your risk tolerance', 11, 1, 'Implementation Strategy', 'S'),
                    ('risk_concerns', 'Risk Concerns', 'checkbox', 1, 1, 'required', '', 'Select your risk concerns', 11, 2, 'Implementation Strategy', 'S'),
                    ('org_structure', 'Organizational Structure', 'select', 1, 1, 'required', '', 'Select your organizational structure', 12, 1, 'Change Management', 'S'),
                    ('decision_process', 'Decision Process', 'select', 1, 1, 'required', '', 'Select your decision process', 12, 2, 'Change Management', 'S'),
                    ('team_size', 'Team Size', 'select', 1, 1, 'required', '', 'Select your team size', 12, 3, 'Change Management', 'S'),
                    ('skill_gaps', 'Skill Gaps', 'checkbox', 1, 1, 'required', '', 'Select your skill gaps', 12, 4, 'Change Management', 'S'),
                    ('budget_allocation', 'Budget Allocation', 'select', 1, 1, 'required', '', 'Select your budget allocation', 11, 3, 'Implementation Strategy', 'S'),
                    ('roi_timeline', 'ROI Timeline', 'select', 1, 1, 'required', '', 'Select your ROI timeline', 11, 4, 'Implementation Strategy', 'S'),
                    ('current_kpis', 'Current KPIs', 'checkbox', 1, 1, 'required', '', 'Select your current KPIs', 6, 15, 'Success Measurement', 'S'),
                    ('improvement_goals', 'Improvement Goals', 'checkbox', 1, 1, 'required', '', 'Select your improvement goals', 6, 16, 'Success Measurement', 'S')
                ]
                
                cursor.executemany(
                    '''
                    INSERT INTO field_configurations 
                    (field_name, field_label, field_type, is_required, is_visible, validation_rules, default_value, help_text, step_number, sort_order, section_name, form_flag)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    default_configs
                )
                
                # Initialize dropdown options
                self._initialize_dropdown_options(cursor)
                
                conn.commit()
            else:
                # Update existing fields with section names and form flags if they don't have them
                self._update_existing_fields_with_sections_and_flags(cursor)
                # Add missing Strategic Blueprint sections
                self._add_missing_strategy_sections(cursor)
                # Add missing Strategic Blueprint fields
                self._add_missing_strategy_fields(cursor)
                # Initialize dropdown options
                self._initialize_dropdown_options(cursor)
                conn.commit()

    def _update_existing_fields_with_sections_and_flags(self, cursor):
        """Update existing fields with their corresponding section names and form flags"""
        # Mapping of field names to section names and form flags
        field_mapping = {
            # Assessment Fields (A)
            'company_name': ('contact_company', 'A'),
            'industry': ('contact_company', 'A'), 
            'company_size': ('contact_company', 'A'),
            'website': ('contact_company', 'A'),
            'first_name': ('contact_company', 'A'),
            'last_name': ('contact_company', 'A'),
            'email': ('contact_company', 'A'),
            'phone': ('contact_company', 'A'),
            'role': ('contact_company', 'A'),
            'biggest_challenge': ('business_challenges', 'A'),
            'challenges': ('business_challenges', 'A'),
            'current_tech': ('technology_foundation', 'A'),
            'ai_experience': ('technology_foundation', 'A'),
            'budget': ('implementation_planning', 'A'),
            'timeline': ('implementation_planning', 'A'),
            'deployment_preference': ('technology_foundation', 'A'),
            'solution_preference': ('technology_foundation', 'A'),
            'technical_expertise': ('technology_foundation', 'A'),
            'security_requirements': ('security_compliance', 'A'),
            'compliance_needs': ('security_compliance', 'A'),
            'success_metrics': ('success_measurement', 'A'),
            'kpis': ('success_measurement', 'A'),
            'maintenance_plan': ('Final Step', 'A'),
            'current_tools': ('technology_foundation', 'A'),
            'tool_preferences': ('technology_foundation', 'A'),
            'implementation_priority': ('implementation_planning', 'A'),
            'team_availability': ('implementation_planning', 'A'),
            'change_management_experience': ('implementation_planning', 'A'),
            'data_governance': ('security_compliance', 'A'),
            'integration_requirements': ('security_compliance', 'A'),
            'expected_roi': ('success_measurement', 'A'),
            'payback_period': ('success_measurement', 'A'),
            'ai_score': ('success_measurement', 'A'),
            'opportunities': ('success_measurement', 'A'),
            
            # Strategic Blueprint Fields (S)
            'strategic_objectives': ('Strategic Foundation', 'S'),
            'business_model': ('Strategic Foundation', 'S'),
            'competitive_advantages': ('Strategic Foundation', 'S'),
            'vendor_preferences': ('Vendor Strategy', 'S'),
            'implementation_approach': ('Implementation Strategy', 'S'),
            'competitors': ('Strategic Foundation', 'S'),
            'market_position': ('Strategic Foundation', 'S'),
            'vendor_features': ('Vendor Strategy', 'S'),
            'risk_tolerance': ('Implementation Strategy', 'S'),
            'risk_concerns': ('Implementation Strategy', 'S'),
            'org_structure': ('Change Management', 'S'),
            'decision_process': ('Change Management', 'S'),
            'team_size': ('Change Management', 'S'),
            'skill_gaps': ('Change Management', 'S'),
            'budget_allocation': ('Implementation Strategy', 'S'),
            'roi_timeline': ('Implementation Strategy', 'S'),
            'current_kpis': ('success_measurement', 'S'),
            'improvement_goals': ('success_measurement', 'S')
        }
        
        # Update existing fields with section names and form flags
        for field_name, (section_name, form_flag) in field_mapping.items():
            cursor.execute(
                'UPDATE field_configurations SET section_name = ?, form_flag = ? WHERE field_name = ?',
                (section_name, form_flag, field_name)
            )
        
        # Set default form_flag for any remaining fields
        cursor.execute('UPDATE field_configurations SET form_flag = "A" WHERE form_flag IS NULL OR form_flag = ""')
        
        print(f"Updated fields with section names and form flags.")

    def _add_missing_strategy_sections(self, cursor):
        """Add missing Strategic Blueprint sections if they don't exist"""
        strategy_sections = [
            ('Strategic Foundation', 'Strategic Foundation', 8, True, True, 'Strategic objectives and business model'),
            ('Technology Architecture', 'Technology Architecture', 9, True, True, 'Technology architecture and integration requirements'),
            ('Vendor Strategy', 'Vendor Strategy', 10, True, True, 'Vendor preferences and evaluation criteria'),
            ('Implementation Strategy', 'Implementation Strategy', 11, True, True, 'Implementation approach and methodology'),
            ('Change Management', 'Change Management', 12, True, True, 'Change management experience and skill gaps')
        ]
        
        for section_name, section_title, step_number, is_required, is_visible, description in strategy_sections:
            # Check if section already exists
            cursor.execute('SELECT COUNT(*) FROM section_configurations WHERE section_name = ?', (section_name,))
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO section_configurations 
                    (section_name, section_title, step_number, is_required, is_visible, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (section_name, section_title, step_number, is_required, is_visible, description))
                print(f"Added missing section: {section_name}")

    def _add_missing_strategy_fields(self, cursor):
        """Add missing Strategic Blueprint fields if they don't exist"""
        strategy_fields = [
            ('competitors', 'Key Competitors', 'textarea', 1, 1, 'required', '', 'List your key competitors', 8, 1, 'Strategic Foundation', 'S'),
            ('competitive_advantages', 'Competitive Advantages', 'checkbox', 1, 1, 'required', '', 'Select your competitive advantages', 8, 2, 'Strategic Foundation', 'S'),
            ('market_position', 'Market Position', 'select', 1, 1, 'required', '', 'Select your market position', 8, 3, 'Strategic Foundation', 'S'),
            ('vendor_features', 'Required Vendor Features', 'checkbox', 1, 1, 'required', '', 'Select required vendor features', 10, 1, 'Vendor Strategy', 'S'),
            ('risk_tolerance', 'Risk Tolerance', 'select', 1, 1, 'required', '', 'Select your risk tolerance', 11, 1, 'Implementation Strategy', 'S'),
            ('risk_concerns', 'Risk Concerns', 'checkbox', 1, 1, 'required', '', 'Select your risk concerns', 11, 2, 'Implementation Strategy', 'S'),
            ('org_structure', 'Organizational Structure', 'select', 1, 1, 'required', '', 'Select your organizational structure', 12, 1, 'Change Management', 'S'),
            ('decision_process', 'Decision Process', 'select', 1, 1, 'required', '', 'Select your decision process', 12, 2, 'Change Management', 'S'),
            ('team_size', 'Team Size', 'select', 1, 1, 'required', '', 'Select your team size', 12, 3, 'Change Management', 'S'),
            ('skill_gaps', 'Skill Gaps', 'checkbox', 1, 1, 'required', '', 'Select your skill gaps', 12, 4, 'Change Management', 'S'),
            ('budget_allocation', 'Budget Allocation', 'select', 1, 1, 'required', '', 'Select your budget allocation', 11, 3, 'Implementation Strategy', 'S'),
            ('roi_timeline', 'ROI Timeline', 'select', 1, 1, 'required', '', 'Select your ROI timeline', 11, 4, 'Implementation Strategy', 'S'),
            ('current_kpis', 'Current KPIs', 'checkbox', 1, 1, 'required', '', 'Select your current KPIs', 6, 15, 'Success Measurement', 'S'),
            ('improvement_goals', 'Improvement Goals', 'checkbox', 1, 1, 'required', '', 'Select your improvement goals', 6, 16, 'Success Measurement', 'S')
        ]
        
        for field_name, field_label, field_type, is_required, is_visible, validation_rules, default_value, help_text, step_number, sort_order, section_name, form_flag in strategy_fields:
            # Check if field already exists
            cursor.execute('SELECT COUNT(*) FROM field_configurations WHERE field_name = ?', (field_name,))
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO field_configurations 
                    (field_name, field_label, field_type, is_required, is_visible, validation_rules, default_value, help_text, step_number, sort_order, section_name, form_flag)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (field_name, field_label, field_type, is_required, is_visible, validation_rules, default_value, help_text, step_number, sort_order, section_name, form_flag))
                print(f"Added missing field: {field_name}")

    def _initialize_sections(self, cursor):
        """Initialize default sections"""
        sections = [
            # Assessment Form Sections (Steps 1-7)
            ('Contact & Company Information', 'Contact & Company Information', 1, True, True, 'Basic company and contact information'),
            ('Business Challenges', 'Business Challenges', 2, True, True, 'Current business challenges and pain points'),
            ('Technology Foundation', 'Technology Foundation', 3, True, True, 'Current technology stack and AI readiness'),
            ('Implementation Planning', 'Implementation Planning', 4, True, True, 'Budget, timeline, and implementation preferences'),
            ('Security & Compliance', 'Security & Compliance', 5, True, True, 'Security requirements and compliance needs'),
            ('Success Measurement', 'Success Measurement', 6, True, True, 'Success metrics and KPIs'),
            ('Final Step', 'Final Step', 7, True, True, 'Final implementation preferences'),
            
            # Strategic Blueprint Form Sections (Steps 8+)
            ('Strategic Foundation', 'Strategic Foundation', 8, True, True, 'Strategic objectives and business model'),
            ('Technology Architecture', 'Technology Architecture', 9, True, True, 'Technology architecture and integration requirements'),
            ('Vendor Strategy', 'Vendor Strategy', 10, True, True, 'Vendor preferences and evaluation criteria'),
            ('Implementation Strategy', 'Implementation Strategy', 11, True, True, 'Implementation approach and methodology'),
            ('Change Management', 'Change Management', 12, True, True, 'Change management experience and skill gaps')
        ]
        
        for section_name, section_title, step_number, is_required, is_visible, description in sections:
            cursor.execute('''
                INSERT OR IGNORE INTO section_configurations 
                (section_name, section_title, step_number, is_required, is_visible, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (section_name, section_title, step_number, is_required, is_visible, description))

    def _initialize_dropdown_options(self, cursor):
        """Initialize default dropdown options"""
        dropdown_options = [
            # Industry options
            ('industry', 'automotive', 'Automotive'),
            ('industry', 'healthcare', 'Healthcare'),
            ('industry', 'manufacturing', 'Manufacturing'),
            ('industry', 'retail', 'Retail'),
            ('industry', 'professional-services', 'Professional Services'),
            ('industry', 'technology', 'Technology'),
            ('industry', 'financial-services', 'Financial Services'),
            ('industry', 'education', 'Education'),
            ('industry', 'other', 'Other'),
            
            # Company size options
            ('company_size', '10-50', '10-50 employees'),
            ('company_size', '51-100', '51-100 employees'),
            ('company_size', '101-250', '101-250 employees'),
            ('company_size', '251-500', '251-500 employees'),
            ('company_size', '500+', '500+ employees'),
            
            # Role options
            ('role', 'ceo-owner', 'CEO/Owner'),
            ('role', 'coo', 'COO'),
            ('role', 'cto', 'CTO'),
            ('role', 'it-director', 'IT Director'),
            ('role', 'operations-manager', 'Operations Manager'),
            ('role', 'business-analyst', 'Business Analyst'),
            ('role', 'project-manager', 'Project Manager'),
            ('role', 'other', 'Other'),
            
            # Current tech options
            ('current_tech', 'basic', 'Basic - Limited technology use'),
            ('current_tech', 'intermediate', 'Intermediate - Some modern tools'),
            ('current_tech', 'advanced', 'Advanced - Modern tech stack'),
            ('current_tech', 'cutting-edge', 'Cutting-edge - Latest technologies'),
            
            # AI experience options
            ('ai_experience', 'none', 'None - No AI experience'),
            ('ai_experience', 'basic', 'Basic - Some AI tools'),
            ('ai_experience', 'intermediate', 'Intermediate - AI implementation'),
            ('ai_experience', 'advanced', 'Advanced - AI strategy'),
            
            # Deployment preference options
            ('deployment_preference', 'cloud', 'Cloud-first - Prefer cloud-based solutions'),
            ('deployment_preference', 'on-premise', 'On-premise - Prefer local deployment'),
            ('deployment_preference', 'hybrid', 'Hybrid - Mix of cloud and on-premise'),
            ('deployment_preference', 'flexible', 'Flexible - Open to best option'),
            
            # Solution preference options
            ('solution_preference', 'saas', 'SaaS - Prefer managed cloud solutions'),
            ('solution_preference', 'open-source', 'Open Source - Prefer customizable solutions'),
            ('solution_preference', 'custom', 'Custom - Prefer tailored development'),
            ('solution_preference', 'hybrid', 'Hybrid - Mix of SaaS and open source'),
            
            # Technical expertise options
            ('technical_expertise', 'limited', 'Limited - Need external support'),
            ('technical_expertise', 'basic', 'Basic - Some technical staff'),
            ('technical_expertise', 'intermediate', 'Intermediate - Skilled IT team'),
            ('technical_expertise', 'advanced', 'Advanced - Strong technical capabilities'),
            
            # Team availability options
            ('team_availability', 'limited', 'Limited - Minimal team availability'),
            ('team_availability', 'moderate', 'Moderate - Some team availability'),
            ('team_availability', 'good', 'Good - Dedicated team time'),
            ('team_availability', 'excellent', 'Excellent - Full team commitment'),
            
            # Change management experience options
            ('change_management_experience', 'none', 'None - No change management experience'),
            ('change_management_experience', 'basic', 'Basic - Some organizational changes'),
            ('change_management_experience', 'intermediate', 'Intermediate - Regular change initiatives'),
            ('change_management_experience', 'advanced', 'Advanced - Extensive change management'),
            
            # Budget options
            ('budget', 'under-10k', 'Under $10,000'),
            ('budget', '10k-25k', '$10,000 - $25,000'),
            ('budget', '25k-50k', '$25,000 - $50,000'),
            ('budget', '50k-100k', '$50,000 - $100,000'),
            ('budget', '100k-250k', '$100,000 - $250,000'),
            ('budget', '250k+', '$250,000+'),
            
            # Timeline options
            ('timeline', 'immediate', 'Immediate - Within 3 months'),
            ('timeline', 'short-term', 'Short-term - 3-6 months'),
            ('timeline', 'medium-term', 'Medium-term - 6-12 months'),
            ('timeline', 'long-term', 'Long-term - 12+ months'),
            
            # Data governance options
            ('data_governance', 'none', 'None - No formal data governance'),
            ('data_governance', 'basic', 'Basic - Some data policies'),
            ('data_governance', 'intermediate', 'Intermediate - Formal data governance'),
            ('data_governance', 'advanced', 'Advanced - Comprehensive data governance'),
            
            # Expected ROI options
            ('expected_roi', 'under-10', 'Under 10%'),
            ('expected_roi', '10-25', '10-25%'),
            ('expected_roi', '25-50', '25-50%'),
            ('expected_roi', '50-100', '50-100%'),
            ('expected_roi', '100+', '100%+'),
            
            # Payback period options
            ('payback_period', 'under-6-months', 'Under 6 months'),
            ('payback_period', '6-12-months', '6-12 months'),
            ('payback_period', '12-24-months', '12-24 months'),
            ('payback_period', '24+months', '24+ months'),
            
            # Strategic Blueprint options
            ('market_position', 'leader', 'Market Leader'),
            ('market_position', 'challenger', 'Market Challenger'),
            ('market_position', 'follower', 'Market Follower'),
            ('market_position', 'niche', 'Niche Player'),
            
            ('risk_tolerance', 'low', 'Low - Conservative approach'),
            ('risk_tolerance', 'moderate', 'Moderate - Balanced approach'),
            ('risk_tolerance', 'high', 'High - Aggressive approach'),
            
            ('org_structure', 'hierarchical', 'Hierarchical'),
            ('org_structure', 'flat', 'Flat'),
            ('org_structure', 'matrix', 'Matrix'),
            ('org_structure', 'agile', 'Agile/Scrum'),
            
            ('decision_process', 'top-down', 'Top-down'),
            ('decision_process', 'consensus', 'Consensus-based'),
            ('decision_process', 'committee', 'Committee-based'),
            ('decision_process', 'agile', 'Agile/Iterative'),
            
            ('team_size', 'small', 'Small - 1-5 people'),
            ('team_size', 'medium', 'Medium - 6-15 people'),
            ('team_size', 'large', 'Large - 16+ people'),
            
            ('budget_allocation', 'technology', 'Technology infrastructure'),
            ('budget_allocation', 'personnel', 'Personnel and training'),
            ('budget_allocation', 'consulting', 'Consulting and services'),
            ('budget_allocation', 'licensing', 'Software licensing'),
            ('budget_allocation', 'other', 'Other'),
            
            ('roi_timeline', 'immediate', 'Immediate - Within 6 months'),
            ('roi_timeline', 'short-term', 'Short-term - 6-12 months'),
            ('roi_timeline', 'medium-term', 'Medium-term - 1-2 years'),
            ('roi_timeline', 'long-term', 'Long-term - 2+ years'),
            
            # Checkbox options for various fields
            ('challenges', 'customer-service', 'Customer service bottleneck'),
            ('challenges', 'data-management', 'Data management issues'),
            ('challenges', 'process-inefficiencies', 'Process inefficiencies'),
            ('challenges', 'manual-tasks', 'Manual/repetitive tasks'),
            ('challenges', 'integration-challenges', 'Integration challenges'),
            ('challenges', 'scalability', 'Scalability issues'),
            ('challenges', 'cost-control', 'Cost control'),
            ('challenges', 'compliance', 'Compliance requirements'),
            
            ('current_tools', 'crm-systems', 'CRM systems'),
            ('current_tools', 'marketing-automation', 'Marketing automation'),
            ('current_tools', 'communication-tools', 'Communication tools'),
            ('current_tools', 'project-management', 'Project management tools'),
            ('current_tools', 'accounting-software', 'Accounting software'),
            ('current_tools', 'hr-systems', 'HR systems'),
            ('current_tools', 'analytics-platforms', 'Analytics platforms'),
            ('current_tools', 'cloud-services', 'Cloud services'),
            
            ('tool_preferences', 'cloud-based', 'Cloud-based solutions'),
            ('tool_preferences', 'integration-capabilities', 'Integration capabilities'),
            ('tool_preferences', 'analytics-platforms', 'Analytics platforms'),
            ('tool_preferences', 'automation-tools', 'Automation tools'),
            ('tool_preferences', 'mobile-friendly', 'Mobile-friendly solutions'),
            ('tool_preferences', 'ai-powered', 'AI-powered features'),
            ('tool_preferences', 'customizable', 'Customizable solutions'),
            ('tool_preferences', 'cost-effective', 'Cost-effective options'),
            
            ('implementation_priority', 'high', 'High priority'),
            ('implementation_priority', 'medium', 'Medium priority'),
            ('implementation_priority', 'low', 'Low priority'),
            ('implementation_priority', 'pilot-project', 'Pilot project'),
            ('implementation_priority', 'full-deployment', 'Full deployment'),
            ('implementation_priority', 'phased-approach', 'Phased approach'),
            
            ('security_requirements', 'encryption', 'Encryption'),
            ('security_requirements', 'compliance-certifications', 'Compliance certifications'),
            ('security_requirements', 'access-controls', 'Access controls'),
            ('security_requirements', 'audit-trails', 'Audit trails'),
            ('security_requirements', 'data-backup', 'Data backup'),
            ('security_requirements', 'disaster-recovery', 'Disaster recovery'),
            ('security_requirements', 'multi-factor-auth', 'Multi-factor authentication'),
            
            ('compliance_needs', 'sox', 'SOX compliance'),
            ('compliance_needs', 'gdpr', 'GDPR compliance'),
            ('compliance_needs', 'hipaa', 'HIPAA compliance'),
            ('compliance_needs', 'industry-specific', 'Industry-specific compliance'),
            ('compliance_needs', 'internal-policies', 'Internal policies'),
            ('compliance_needs', 'audit-requirements', 'Audit requirements'),
            
            ('integration_requirements', 'api-integration', 'API integration'),
            ('integration_requirements', 'database-connectivity', 'Database connectivity'),
            ('integration_requirements', 'third-party-systems', 'Third-party systems'),
            ('integration_requirements', 'legacy-systems', 'Legacy systems'),
            ('integration_requirements', 'cloud-services', 'Cloud services'),
            ('integration_requirements', 'real-time-sync', 'Real-time synchronization'),
            
            ('success_metrics', 'customer-satisfaction', 'Customer satisfaction'),
            ('success_metrics', 'efficiency-improvement', 'Efficiency improvement'),
            ('success_metrics', 'cost-reduction', 'Cost reduction'),
            ('success_metrics', 'revenue-growth', 'Revenue growth'),
            ('success_metrics', 'time-savings', 'Time savings'),
            ('success_metrics', 'error-reduction', 'Error reduction'),
            ('success_metrics', 'productivity-increase', 'Productivity increase'),
            
            ('competitive_advantages', 'innovation-capabilities', 'Innovation capabilities'),
            ('competitive_advantages', 'customer-relationships', 'Customer relationships'),
            ('competitive_advantages', 'operational-efficiency', 'Operational efficiency'),
            ('competitive_advantages', 'technology-stack', 'Technology stack'),
            ('competitive_advantages', 'market-position', 'Market position'),
            ('competitive_advantages', 'brand-reputation', 'Brand reputation'),
            ('competitive_advantages', 'cost-structure', 'Cost structure'),
            
            ('vendor_features', 'scalability', 'Scalability'),
            ('vendor_features', 'customization', 'Customization'),
            ('vendor_features', 'integration-capabilities', 'Integration capabilities'),
            ('vendor_features', 'support-quality', 'Support quality'),
            ('vendor_features', 'pricing-flexibility', 'Pricing flexibility'),
            ('vendor_features', 'security-features', 'Security features'),
            ('vendor_features', 'compliance-certifications', 'Compliance certifications'),
            
            ('risk_concerns', 'data-security', 'Data security'),
            ('risk_concerns', 'vendor-lock-in', 'Vendor lock-in'),
            ('risk_concerns', 'implementation-delays', 'Implementation delays'),
            ('risk_concerns', 'cost-overruns', 'Cost overruns'),
            ('risk_concerns', 'user-adoption', 'User adoption'),
            ('risk_concerns', 'technical-complexity', 'Technical complexity'),
            ('risk_concerns', 'business-disruption', 'Business disruption'),
            
            ('skill_gaps', 'technical-skills', 'Technical skills'),
            ('skill_gaps', 'data-analysis', 'Data analysis'),
            ('skill_gaps', 'change-management', 'Change management'),
            ('skill_gaps', 'project-management', 'Project management'),
            ('skill_gaps', 'ai-literacy', 'AI literacy'),
            ('skill_gaps', 'process-improvement', 'Process improvement'),
            ('skill_gaps', 'vendor-management', 'Vendor management'),
            
            ('current_kpis', 'revenue-growth', 'Revenue growth'),
            ('current_kpis', 'customer-satisfaction', 'Customer satisfaction'),
            ('current_kpis', 'operational-efficiency', 'Operational efficiency'),
            ('current_kpis', 'cost-reduction', 'Cost reduction'),
            ('current_kpis', 'employee-productivity', 'Employee productivity'),
            ('current_kpis', 'market-share', 'Market share'),
            ('current_kpis', 'profit-margins', 'Profit margins'),
            
            ('improvement_goals', 'process-automation', 'Process automation'),
            ('improvement_goals', 'data-analytics', 'Data analytics'),
            ('improvement_goals', 'customer-experience', 'Customer experience'),
            ('improvement_goals', 'operational-efficiency', 'Operational efficiency'),
            ('improvement_goals', 'cost-optimization', 'Cost optimization'),
            ('improvement_goals', 'innovation-capabilities', 'Innovation capabilities'),
            ('improvement_goals', 'competitive-advantage', 'Competitive advantage')
        ]
        
        for field_name, option_value, option_label in dropdown_options:
            cursor.execute('''
                INSERT OR IGNORE INTO dropdown_options 
                (field_name, option_value, option_label)
                VALUES (?, ?, ?)
            ''', (field_name, option_value, option_label))

    def get_field_configurations(self, form_flag=None):
        """Get field configurations, optionally filtered by form flag"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if form_flag:
                cursor.execute('''
                    SELECT * FROM field_configurations 
                    WHERE form_flag = ? 
                    ORDER BY step_number, sort_order
                ''', (form_flag,))
            else:
                cursor.execute('''
                    SELECT * FROM field_configurations 
                    ORDER BY step_number, sort_order
                ''')
            rows = cursor.fetchall()
            columns = [d[0] for d in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def get_section_configurations(self):
        """Get all section configurations"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM section_configurations 
                ORDER BY step_number
            ''')
            rows = cursor.fetchall()
            columns = [d[0] for d in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def get_dropdown_options(self, field_name=None):
        """Get dropdown options, optionally filtered by field name"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if field_name:
                cursor.execute('''
                    SELECT * FROM dropdown_options 
                    WHERE field_name = ? 
                    ORDER BY sort_order, option_label
                ''', (field_name,))
            else:
                cursor.execute('''
                    SELECT * FROM dropdown_options 
                    ORDER BY field_name, sort_order, option_label
                ''')
            rows = cursor.fetchall()
            columns = [d[0] for d in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def get_required_fields(self):
        """Get list of required field names"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT field_name FROM field_configurations 
                WHERE is_required = 1
            ''')
            return [row[0] for row in cursor.fetchall()]

    def update_section_configuration(self, section_name, data):
        """Update a section configuration"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE section_configurations 
                SET section_title = ?, step_number = ?, is_required = ?, is_visible = ?, description = ?
                WHERE section_name = ?
            ''', (
                data.get('section_title'),
                data.get('step_number', 1),
                data.get('is_required', True),
                data.get('is_visible', True),
                data.get('description'),
                section_name
            ))
            conn.commit()
            return True

    def add_dropdown_option(self, field_name, option_value, option_label, sort_order=0):
        """Add a new dropdown option"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO dropdown_options 
                (field_name, option_value, option_label, sort_order)
                VALUES (?, ?, ?, ?)
            ''', (field_name, option_value, option_label, sort_order))
            conn.commit()
            return True

    def update_dropdown_option(self, option_id, data):
        """Update a dropdown option"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build dynamic update query based on provided fields
            update_fields = []
            update_values = []
            
            if 'option_value' in data:
                update_fields.append('option_value = ?')
                update_values.append(data['option_value'])
            
            if 'option_label' in data:
                update_fields.append('option_label = ?')
                update_values.append(data['option_label'])
            
            if 'sort_order' in data:
                update_fields.append('sort_order = ?')
                update_values.append(data['sort_order'])
            
            if not update_fields:
                return False  # No fields to update
            
            update_values.append(option_id)
            
            query = f'''
                UPDATE dropdown_options 
                SET {', '.join(update_fields)}
                WHERE id = ?
            '''
            
            cursor.execute(query, update_values)
            conn.commit()
            return True

    def delete_dropdown_option(self, option_id):
        """Delete a dropdown option"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM dropdown_options WHERE id = ?', (option_id,))
            conn.commit()
            return True

    def update_field_configuration(self, field_name, data):
        """Update a field configuration"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE field_configurations 
                SET field_label = ?, field_type = ?, is_required = ?, is_visible = ?, 
                    validation_rules = ?, default_value = ?, help_text = ?, 
                    step_number = ?, sort_order = ?, section_name = ?, form_flag = ?
                WHERE field_name = ?
            ''', (
                data.get('field_label'),
                data.get('field_type'),
                data.get('is_required', 0),
                data.get('is_visible', 1),
                data.get('validation_rules'),
                data.get('default_value'),
                data.get('help_text'),
                data.get('step_number', 1),
                data.get('sort_order', 0),
                data.get('section_name'),
                data.get('form_flag', 'A'),
                field_name
            ))
            conn.commit()
            return True


# Initialize database manager (used by app)
db_manager = DatabaseManager()
