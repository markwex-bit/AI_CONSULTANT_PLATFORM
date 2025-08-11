# Data Source Identification System

## Overview
This document explains how to identify which data comes from which form in the AI Consultant Platform. The system uses multiple approaches to clearly track data sources.

## Database Schema Approach

### 1. Form Source Tracking Fields
The `assessments` table includes these tracking fields:

```sql
form_source TEXT DEFAULT 'assessment'           -- Tracks which form(s) provided data
assessment_completed_at TIMESTAMP               -- When assessment form was completed  
strategy_completed_at TIMESTAMP                 -- When strategy form was completed
```

### 2. Field Naming Convention
Fields are organized by form source:

**Assessment Report Fields (A_ prefix in views):**
- Basic info: `company_name`, `industry`, `company_size`, `role`, `website`
- Contact: `first_name`, `last_name`, `email`, `phone`
- Business: `challenges`, `current_tech`, `ai_experience`, `budget`, `timeline`
- Enhanced: `current_tools`, `tool_preferences`, `implementation_priority`, etc.

**Strategy Blueprint Fields (S_ prefix in views):**
- Competitive: `competitors`, `competitive_advantages`, `market_position`
- Vendor: `vendor_features`, `risk_tolerance`, `risk_concerns`
- Organizational: `org_structure`, `decision_process`, `team_size`, `skill_gaps`
- Financial: `budget_allocation`, `roi_timeline`, `current_kpis`, `improvement_goals`

## Database Views for Data Source Identification

### 1. `form_data_summary` View
Shows completion status for each assessment:

```sql
SELECT * FROM form_data_summary;
```

**Completion Status Values:**
- `'Complete (Both Forms)'` - Both assessment and strategy forms completed
- `'Assessment Only'` - Only assessment form completed
- `'Strategy Only'` - Only strategy form completed  
- `'Incomplete'` - Neither form completed

### 2. `assessment_only_data` View
Shows only data from the Assessment Report form:

```sql
SELECT * FROM assessment_only_data;
```

### 3. `strategy_only_data` View  
Shows only data from the Strategy Blueprint form:

```sql
SELECT * FROM strategy_only_data;
```

### 4. `complete_data` View
Shows all data when both forms are completed:

```sql
SELECT * FROM complete_data;
```

### 5. `assessments_labeled` View
Shows all data with A_ and S_ prefixes to identify form source:

```sql
SELECT * FROM assessments_labeled;
```

## Usage Examples

### Check Which Forms Are Completed
```sql
SELECT 
    company_name,
    email,
    completion_status,
    assessment_completed_at,
    strategy_completed_at
FROM form_data_summary
ORDER BY created_at DESC;
```

### Get Only Assessment Form Data
```sql
SELECT 
    company_name,
    industry,
    challenges,
    current_tech,
    ai_experience
FROM assessment_only_data
WHERE assessment_completed_at IS NOT NULL;
```

### Get Only Strategy Form Data
```sql
SELECT 
    company_name,
    competitors,
    competitive_advantages,
    market_position
FROM strategy_only_data
WHERE strategy_completed_at IS NOT NULL;
```

### Get Complete Client Data (Both Forms)
```sql
SELECT 
    company_name,
    email,
    -- Assessment fields
    industry,
    challenges,
    current_tech,
    -- Strategy fields  
    competitors,
    competitive_advantages,
    market_position
FROM complete_data;
```

## Admin Interface Integration

### Form Source Display
The admin interface shows:
- **Form Source**: Which form(s) provided data
- **Completion Status**: Visual indicator of form completion
- **Completion Dates**: When each form was completed

### Data Organization
- Assessment fields are grouped together
- Strategy fields are grouped together
- Clear visual separation between form sources

## API Endpoints

### Get Form Summary
```http
GET /api/form_summary
```

Returns completion status for all assessments.

### Get Assessment-Only Data
```http
GET /api/assessment_data
```

Returns only assessment form data.

### Get Strategy-Only Data  
```http
GET /api/strategy_data
```

Returns only strategy form data.

## Best Practices

### 1. Always Check Form Source
Before using data, verify which form provided it:
```python
if assessment.get('assessment_completed_at'):
    # Use assessment form data
    pass

if assessment.get('strategy_completed_at'):
    # Use strategy form data  
    pass
```

### 2. Use Appropriate Views
- Use `assessment_only_data` for assessment-specific operations
- Use `strategy_only_data` for strategy-specific operations
- Use `complete_data` when you need all available data

### 3. Handle Missing Data Gracefully
```python
# Check if data exists before using it
if assessment.get('competitors'):
    # Strategy form was completed
    competitors = json.loads(assessment['competitors'])
else:
    # Strategy form not completed yet
    competitors = []
```

### 4. Update Form Source Tracking
When forms are completed, update the tracking fields:
```python
# When assessment form is completed
db_manager.update_assessment_fields(
    assessment_id, 
    {'assessment_completed_at': datetime.now()}
)

# When strategy form is completed  
db_manager.update_assessment_strategy(
    assessment_id,
    strategy_data,
    strategy_completed_at=datetime.now()
)
```

## Troubleshooting

### Common Issues

1. **Missing Form Source Data**
   - Check if `form_source` field is populated
   - Verify completion timestamps are set

2. **Incomplete Data**
   - Use `form_data_summary` to identify incomplete assessments
   - Check which forms still need to be completed

3. **Data Source Confusion**
   - Use the labeled views (A_ and S_ prefixes)
   - Check completion status before using data

### Debug Queries

```sql
-- Check for assessments with missing form source
SELECT id, company_name, form_source 
FROM assessments 
WHERE form_source IS NULL;

-- Check completion status distribution
SELECT completion_status, COUNT(*) 
FROM form_data_summary 
GROUP BY completion_status;

-- Find assessments with partial data
SELECT id, company_name, 
       assessment_completed_at IS NOT NULL as has_assessment,
       strategy_completed_at IS NOT NULL as has_strategy
FROM assessments;
```

## Migration Notes

When adding new fields:
1. Add to appropriate form group (Assessment or Strategy)
2. Update relevant database views
3. Add to form source tracking if needed
4. Update documentation

This system ensures clear data lineage and makes it easy to identify which form provided which data for any assessment.
