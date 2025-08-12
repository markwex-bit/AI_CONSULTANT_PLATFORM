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

            # Create Dynamic Form Builder tables
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS section_configurations (
                    section_name TEXT PRIMARY KEY,
                    section_title TEXT NOT NULL,
                    step_number INTEGER NOT NULL,
                    is_required BOOLEAN DEFAULT FALSE,
                    is_visible BOOLEAN DEFAULT TRUE,
                    description TEXT,
                    form_flag TEXT NOT NULL CHECK (form_flag IN ('A', 'S'))
                )
                '''
            )

            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS field_configurations (
                    field_name TEXT PRIMARY KEY,
                    field_label TEXT NOT NULL,
                    field_type TEXT NOT NULL CHECK (field_type IN ('text', 'email', 'select', 'checkbox', 'textarea', 'number')),
                    section_name TEXT,
                    is_required BOOLEAN DEFAULT FALSE,
                    is_visible BOOLEAN DEFAULT TRUE,
                    form_flag TEXT NOT NULL CHECK (form_flag IN ('A', 'S')),
                    FOREIGN KEY (section_name) REFERENCES section_configurations (section_name)
                )
                '''
            )

            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS dropdown_options (
                    option_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    field_name TEXT NOT NULL,
                    option_value TEXT NOT NULL,
                    option_label TEXT NOT NULL,
                    sort_order INTEGER DEFAULT 0,
                    form_flag TEXT NOT NULL CHECK (form_flag IN ('A', 'S')),
                    FOREIGN KEY (field_name) REFERENCES field_configurations (field_name)
                )
                '''
            )

            # Add missing columns to existing Dynamic Form Builder tables
            def add_column_to_table(table_name: str, column_name: str, column_definition: str):
                try:
                    cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}')
                except sqlite3.OperationalError:
                    pass  # column already exists

            # Add form_flag column to existing tables if they exist
            add_column_to_table('section_configurations', 'form_flag', 'TEXT NOT NULL DEFAULT "A" CHECK (form_flag IN ("A", "S"))')
            add_column_to_table('field_configurations', 'form_flag', 'TEXT NOT NULL DEFAULT "A" CHECK (form_flag IN ("A", "S"))')
            add_column_to_table('dropdown_options', 'form_flag', 'TEXT NOT NULL DEFAULT "A" CHECK (form_flag IN ("A", "S"))')

            # Initialize default data for Dynamic Form Builder
            self._initialize_dynamic_form_data(cursor)

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
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

    def _initialize_dynamic_form_data(self, cursor):
        """Initialize default data for Dynamic Form Builder"""
        
        # Update existing records to have proper form_flag values
        cursor.execute('UPDATE section_configurations SET form_flag = "A" WHERE form_flag IS NULL OR form_flag = ""')
        cursor.execute('UPDATE field_configurations SET form_flag = "A" WHERE form_flag IS NULL OR form_flag = ""')
        cursor.execute('UPDATE dropdown_options SET form_flag = "A" WHERE form_flag IS NULL OR form_flag = ""')
        
        # Initialize section configurations
        section_configs = [
            # Assessment Form Sections
            ('contact_company', 'Contact & Company Information', 1, True, True, 'Basic company and contact information', 'A'),
            ('business_challenges', 'Business Challenges & Goals', 2, True, True, 'Current challenges and AI goals', 'A'),
            ('current_technology', 'Current Technology Stack', 3, True, True, 'Existing technology infrastructure', 'A'),
            ('ai_experience', 'AI Experience & Readiness', 4, True, True, 'Team AI experience and readiness assessment', 'A'),
            ('budget_timeline', 'Budget & Timeline', 5, True, True, 'Budget constraints and implementation timeline', 'A'),
            ('team_availability', 'Team & Resources', 6, True, True, 'Team availability and resource assessment', 'A'),
            ('implementation_plan', 'Implementation Planning', 7, True, True, 'Implementation strategy and planning', 'A'),
            
            # Strategic Blueprint Sections
            ('competitive_analysis', 'Competitive Analysis', 1, True, True, 'Market position and competitive landscape', 'S'),
            ('risk_assessment', 'Risk Assessment & Tolerance', 2, True, True, 'Risk factors and organizational tolerance', 'S'),
            ('organizational_structure', 'Organizational Structure', 3, True, True, 'Decision-making and team structure', 'S'),
            ('budget_allocation', 'Budget & ROI Planning', 4, True, True, 'Budget allocation and ROI expectations', 'S'),
            ('performance_metrics', 'Performance Metrics & KPIs', 5, True, True, 'Current KPIs and improvement goals', 'S')
        ]
        
        for section in section_configs:
            cursor.execute('''
                INSERT OR REPLACE INTO section_configurations 
                (section_name, section_title, step_number, is_required, is_visible, description, form_flag)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', section)
        
        # Initialize field configurations
        field_configs = [
            # Assessment Form Fields
            ('company_name', 'Company Name', 'text', 'contact_company', True, True, 'A'),
            ('industry', 'Industry', 'select', 'contact_company', True, True, 'A'),
            ('company_size', 'Company Size', 'select', 'contact_company', True, True, 'A'),
            ('role', 'Your Role', 'select', 'contact_company', True, True, 'A'),
            ('first_name', 'First Name', 'text', 'contact_company', True, True, 'A'),
            ('last_name', 'Last Name', 'text', 'contact_company', True, True, 'A'),
            ('email', 'Email Address', 'email', 'contact_company', True, True, 'A'),
            ('phone', 'Phone Number', 'text', 'contact_company', False, True, 'A'),
            ('challenges', 'Current Challenges', 'checkbox', 'business_challenges', True, True, 'A'),
            ('current_tech', 'Current Technology Stack', 'checkbox', 'current_technology', True, True, 'A'),
            ('ai_experience', 'AI Experience Level', 'select', 'ai_experience', True, True, 'A'),
            ('current_tools', 'Current AI Tools', 'checkbox', 'current_technology', False, True, 'A'),
            ('budget', 'Budget Range', 'select', 'budget_timeline', True, True, 'A'),
            ('timeline', 'Implementation Timeline', 'select', 'budget_timeline', True, True, 'A'),
            ('team_availability', 'Team Availability', 'select', 'team_availability', True, True, 'A'),
            ('change_management_experience', 'Change Management Experience', 'select', 'team_availability', False, True, 'A'),
            ('data_governance', 'Data Governance Maturity', 'select', 'current_technology', False, True, 'A'),
            ('security_requirements', 'Security Requirements', 'checkbox', 'current_technology', False, True, 'A'),
            ('compliance_needs', 'Compliance Needs', 'checkbox', 'current_technology', False, True, 'A'),
            ('integration_requirements', 'Integration Requirements', 'checkbox', 'current_technology', False, True, 'A'),
            ('success_metrics', 'Success Metrics', 'checkbox', 'implementation_plan', False, True, 'A'),
            ('expected_roi', 'Expected ROI', 'select', 'budget_timeline', False, True, 'A'),
            ('payback_period', 'Payback Period', 'select', 'budget_timeline', False, True, 'A'),
            ('risk_factors', 'Risk Factors', 'checkbox', 'implementation_plan', False, True, 'A'),
            ('mitigation_strategies', 'Mitigation Strategies', 'checkbox', 'implementation_plan', False, True, 'A'),
            ('implementation_phases', 'Implementation Phases', 'checkbox', 'implementation_plan', False, True, 'A'),
            ('resource_requirements', 'Resource Requirements', 'checkbox', 'implementation_plan', False, True, 'A'),
            ('training_needs', 'Training Needs', 'checkbox', 'implementation_plan', False, True, 'A'),
            ('vendor_criteria', 'Vendor Criteria', 'checkbox', 'implementation_plan', False, True, 'A'),
            ('pilot_project', 'Pilot Project', 'select', 'implementation_plan', False, True, 'A'),
            ('scalability_requirements', 'Scalability Requirements', 'checkbox', 'implementation_plan', False, True, 'A'),
            ('maintenance_plan', 'Maintenance Plan', 'select', 'implementation_plan', False, True, 'A'),
            
            # Strategic Blueprint Fields
            ('competitors', 'Key Competitors', 'textarea', 'competitive_analysis', True, True, 'S'),
            ('competitive_advantages', 'Competitive Advantages', 'textarea', 'competitive_analysis', True, True, 'S'),
            ('market_position', 'Market Position', 'select', 'competitive_analysis', True, True, 'S'),
            ('vendor_features', 'Vendor Features', 'checkbox', 'competitive_analysis', False, True, 'S'),
            ('risk_tolerance', 'Risk Tolerance', 'select', 'risk_assessment', True, True, 'S'),
            ('risk_concerns', 'Risk Concerns', 'checkbox', 'risk_assessment', False, True, 'S'),
            ('org_structure', 'Organizational Structure', 'select', 'organizational_structure', True, True, 'S'),
            ('decision_process', 'Decision Process', 'select', 'organizational_structure', True, True, 'S'),
            ('team_size', 'Team Size', 'select', 'organizational_structure', True, True, 'S'),
            ('skill_gaps', 'Skill Gaps', 'checkbox', 'organizational_structure', False, True, 'S'),
            ('budget_allocation', 'Budget Allocation', 'select', 'budget_allocation', True, True, 'S'),
            ('roi_timeline', 'ROI Timeline', 'select', 'budget_allocation', True, True, 'S'),
            ('current_kpis', 'Current KPIs', 'checkbox', 'performance_metrics', False, True, 'S'),
            ('improvement_goals', 'Improvement Goals', 'checkbox', 'performance_metrics', True, True, 'S')
        ]
        
        for field in field_configs:
            cursor.execute('''
                INSERT OR REPLACE INTO field_configurations 
                (field_name, field_label, field_type, section_name, is_required, is_visible, form_flag)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', field)
        
        # Initialize dropdown options
        dropdown_options = [
            # Industry options
            ('industry', 'technology', 'Technology', 1, 'A'),
            ('industry', 'healthcare', 'Healthcare', 2, 'A'),
            ('industry', 'finance', 'Finance', 3, 'A'),
            ('industry', 'manufacturing', 'Manufacturing', 4, 'A'),
            ('industry', 'retail', 'Retail', 5, 'A'),
            ('industry', 'education', 'Education', 6, 'A'),
            ('industry', 'consulting', 'Consulting', 7, 'A'),
            ('industry', 'other', 'Other', 8, 'A'),
            
            # Company size options
            ('company_size', '1-10', '1-10 employees', 1, 'A'),
            ('company_size', '11-50', '11-50 employees', 2, 'A'),
            ('company_size', '51-200', '51-200 employees', 3, 'A'),
            ('company_size', '201-1000', '201-1000 employees', 4, 'A'),
            ('company_size', '1000+', '1000+ employees', 5, 'A'),
            
            # Role options
            ('role', 'executive', 'C-Level Executive', 1, 'A'),
            ('role', 'director', 'Director/VP', 2, 'A'),
            ('role', 'manager', 'Manager', 3, 'A'),
            ('role', 'individual', 'Individual Contributor', 4, 'A'),
            ('role', 'consultant', 'Consultant', 5, 'A'),
            
            # AI Experience options
            ('ai_experience', 'none', 'No experience', 1, 'A'),
            ('ai_experience', 'basic', 'Basic understanding', 2, 'A'),
            ('ai_experience', 'intermediate', 'Some implementation', 3, 'A'),
            ('ai_experience', 'advanced', 'Advanced implementation', 4, 'A'),
            ('ai_experience', 'expert', 'Expert level', 5, 'A'),
            
            # Budget options
            ('budget', 'under_10k', 'Under $10,000', 1, 'A'),
            ('budget', '10k_50k', '$10,000 - $50,000', 2, 'A'),
            ('budget', '50k_100k', '$50,000 - $100,000', 3, 'A'),
            ('budget', '100k_500k', '$100,000 - $500,000', 4, 'A'),
            ('budget', '500k_plus', '$500,000+', 5, 'A'),
            
            # Timeline options
            ('timeline', 'immediate', 'Immediate (0-3 months)', 1, 'A'),
            ('timeline', 'short_term', 'Short term (3-6 months)', 2, 'A'),
            ('timeline', 'medium_term', 'Medium term (6-12 months)', 3, 'A'),
            ('timeline', 'long_term', 'Long term (1+ years)', 4, 'A'),
            
            # Team availability options
            ('team_availability', 'full_time', 'Full-time dedicated team', 1, 'A'),
            ('team_availability', 'part_time', 'Part-time availability', 2, 'A'),
            ('team_availability', 'limited', 'Limited availability', 3, 'A'),
            ('team_availability', 'external', 'External resources needed', 4, 'A'),
            
            # Change management experience options
            ('change_management_experience', 'none', 'No experience', 1, 'A'),
            ('change_management_experience', 'basic', 'Basic experience', 2, 'A'),
            ('change_management_experience', 'moderate', 'Moderate experience', 3, 'A'),
            ('change_management_experience', 'extensive', 'Extensive experience', 4, 'A'),
            
            # Data governance options
            ('data_governance', 'none', 'No formal governance', 1, 'A'),
            ('data_governance', 'basic', 'Basic policies', 2, 'A'),
            ('data_governance', 'moderate', 'Moderate governance', 3, 'A'),
            ('data_governance', 'advanced', 'Advanced governance', 4, 'A'),
            
            # Expected ROI options
            ('expected_roi', 'under_20', 'Under 20%', 1, 'A'),
            ('expected_roi', '20_50', '20-50%', 2, 'A'),
            ('expected_roi', '50_100', '50-100%', 3, 'A'),
            ('expected_roi', '100_plus', '100%+', 4, 'A'),
            
            # Payback period options
            ('payback_period', 'under_6', 'Under 6 months', 1, 'A'),
            ('payback_period', '6_12', '6-12 months', 2, 'A'),
            ('payback_period', '12_24', '12-24 months', 3, 'A'),
            ('payback_period', '24_plus', '24+ months', 4, 'A'),
            
            # Pilot project options
            ('pilot_project', 'yes', 'Yes, we want to start with a pilot', 1, 'A'),
            ('pilot_project', 'no', 'No, we want full implementation', 2, 'A'),
            ('pilot_project', 'maybe', 'Maybe, depending on recommendations', 3, 'A'),
            
            # Maintenance plan options
            ('maintenance_plan', 'internal', 'Internal team', 1, 'A'),
            ('maintenance_plan', 'external', 'External vendor', 2, 'A'),
            ('maintenance_plan', 'hybrid', 'Hybrid approach', 3, 'A'),
            ('maintenance_plan', 'undecided', 'Not decided yet', 4, 'A'),
            
            # Strategic Blueprint options
            ('market_position', 'leader', 'Market Leader', 1, 'S'),
            ('market_position', 'challenger', 'Market Challenger', 2, 'S'),
            ('market_position', 'follower', 'Market Follower', 3, 'S'),
            ('market_position', 'niche', 'Niche Player', 4, 'S'),
            
            ('risk_tolerance', 'low', 'Low Risk Tolerance', 1, 'S'),
            ('risk_tolerance', 'moderate', 'Moderate Risk Tolerance', 2, 'S'),
            ('risk_tolerance', 'high', 'High Risk Tolerance', 3, 'S'),
            
            ('org_structure', 'centralized', 'Centralized', 1, 'S'),
            ('org_structure', 'decentralized', 'Decentralized', 2, 'S'),
            ('org_structure', 'matrix', 'Matrix', 3, 'S'),
            ('org_structure', 'hybrid', 'Hybrid', 4, 'S'),
            
            ('decision_process', 'autocratic', 'Autocratic', 1, 'S'),
            ('decision_process', 'consensus', 'Consensus-based', 2, 'S'),
            ('decision_process', 'committee', 'Committee-based', 3, 'S'),
            ('decision_process', 'democratic', 'Democratic', 4, 'S'),
            
            ('team_size', 'small', 'Small (1-5 people)', 1, 'S'),
            ('team_size', 'medium', 'Medium (6-15 people)', 2, 'S'),
            ('team_size', 'large', 'Large (16+ people)', 3, 'S'),
            
            ('budget_allocation', 'conservative', 'Conservative (10-20% of revenue)', 1, 'S'),
            ('budget_allocation', 'moderate', 'Moderate (20-30% of revenue)', 2, 'S'),
            ('budget_allocation', 'aggressive', 'Aggressive (30%+ of revenue)', 3, 'S'),
            
            ('roi_timeline', 'short', 'Short term (6-12 months)', 1, 'S'),
            ('roi_timeline', 'medium', 'Medium term (1-2 years)', 2, 'S'),
            ('roi_timeline', 'long', 'Long term (2+ years)', 3, 'S')
        ]
        
        for option in dropdown_options:
            cursor.execute('''
                INSERT OR REPLACE INTO dropdown_options 
                (field_name, option_value, option_label, sort_order, form_flag)
                VALUES (?, ?, ?, ?, ?)
            ''', option)

    # ---------- Dynamic Form Builder CRUD Methods ----------
    def update_section_configuration(self, section_name: str, data: dict) -> bool:
        """Update a section configuration"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            set_clauses = []
            values = []
            
            if 'section_title' in data:
                set_clauses.append('section_title = ?')
                values.append(data['section_title'])
            
            if 'step_number' in data:
                set_clauses.append('step_number = ?')
                values.append(data['step_number'])
            
            if 'is_required' in data:
                set_clauses.append('is_required = ?')
                values.append(data['is_required'])
            
            if 'is_visible' in data:
                set_clauses.append('is_visible = ?')
                values.append(data['is_visible'])
            
            if 'description' in data:
                set_clauses.append('description = ?')
                values.append(data['description'])
            
            if not set_clauses:
                return True
            
            values.append(section_name)
            
            cursor.execute(f'''
                UPDATE section_configurations 
                SET {', '.join(set_clauses)}
                WHERE section_name = ?
            ''', values)
            
            conn.commit()
            return True

    def delete_section_configuration(self, section_name: str) -> bool:
        """Delete a section configuration and update related fields"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # First, update all fields that reference this section to have NULL section_name
            cursor.execute('''
                UPDATE field_configurations 
                SET section_name = NULL 
                WHERE section_name = ?
            ''', (section_name,))
            
            # Then delete the section
            cursor.execute('''
                DELETE FROM section_configurations 
                WHERE section_name = ?
            ''', (section_name,))
            
            conn.commit()
            return True

    def update_dropdown_option(self, option_id: int, data: dict) -> bool:
        """Update a dropdown option"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            set_clauses = []
            values = []
            
            if 'field_name' in data:
                set_clauses.append('field_name = ?')
                values.append(data['field_name'])
            
            if 'option_value' in data:
                set_clauses.append('option_value = ?')
                values.append(data['option_value'])
            
            if 'option_label' in data:
                set_clauses.append('option_label = ?')
                values.append(data['option_label'])
            
            if 'sort_order' in data:
                set_clauses.append('sort_order = ?')
                values.append(data['sort_order'])
            
            if not set_clauses:
                return True
            
            values.append(option_id)
            
            cursor.execute(f'''
                UPDATE dropdown_options 
                SET {', '.join(set_clauses)}
                WHERE option_id = ?
            ''', values)
            
            conn.commit()
            return True

    def delete_dropdown_option(self, option_id: int) -> bool:
        """Delete a dropdown option"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM dropdown_options 
                WHERE option_id = ?
            ''', (option_id,))
            
            conn.commit()
            return True


# Initialize database manager (used by app)
db_manager = DatabaseManager()
