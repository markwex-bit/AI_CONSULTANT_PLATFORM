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

            # Strategy blueprint related
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

            # Enhanced assessment fields
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

            # Create labeled views to simplify analytics/admin queries
            self._create_labeled_views(cursor)

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
                    scalability_requirements, maintenance_plan
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    report_type = 'strategy_blueprint'
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


# Initialize database manager (used by app)
db_manager = DatabaseManager()
