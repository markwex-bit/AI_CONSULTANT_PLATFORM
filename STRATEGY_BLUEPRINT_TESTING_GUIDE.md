# Strategy Blueprint Testing Guide

## 🚀 Quick Start Testing

### 1. **Automated Testing**
Run the comprehensive test script:
```bash
python test_strategy_blueprint.py
```

This will test:
- ✅ Database schema
- ✅ Assessment creation
- ✅ Email lookup functionality
- ✅ Strategy upgrade process
- ✅ Payment intent creation
- ✅ Database updates
- ✅ Web interface routes

### 2. **Manual Testing Flow**

#### **Step 1: Start Your Application**
```bash
python app.py
```
Your app should be running at `http://localhost:5000`

#### **Step 2: Create Initial Assessment**
1. Go to `http://localhost:5000/assessment`
2. Fill out the assessment form with test data:
   - Company: "Test Company Inc"
   - Industry: Technology
   - Size: 11-50 employees
   - Role: CEO
   - Challenges: Select "Manual processes" and "Data analysis"
   - Tech Level: Intermediate
   - AI Experience: Exploring
   - Budget: $25,000 - $50,000
   - Timeline: 6 months
   - Contact: Use a test email like `test@example.com`

3. Submit the assessment
4. Note your AI readiness score and opportunities

#### **Step 3: Test Strategy Blueprint Upgrade**
1. Go to `http://localhost:5000/strategy_assessment`
2. Enter the email address you used in Step 2
3. Click "Find My Assessment"
4. **Verify the existing data is displayed correctly:**
   - Company name, industry, size, role
   - AI readiness score
   - Current technology level
   - Challenges and opportunities (as tags)

5. **Fill out the new strategic questions:**
   - **Competitors:** "Competitor A (market leader), Competitor B (niche player)"
   - **Competitive Advantages:** "Strong customer service, innovative technology"
   - **Market Position:** Select "Challenger"
   - **Vendor Features:** Select "Enterprise Support", "API Integration", "Data Security"
   - **Risk Tolerance:** Select "Moderate"
   - **Risk Concerns:** "Data security, employee resistance"
   - **Org Structure:** Select "Hierarchical"
   - **Decision Process:** Select "Consultative"
   - **Team Size:** Select "16-50"
   - **Skill Gaps:** "Data science, AI/ML knowledge"
   - **Budget Allocation:** Select "Balanced"
   - **ROI Timeline:** Select "12 months"
   - **Current KPIs:** "Customer satisfaction (85%), Revenue growth (15%)"
   - **Improvement Goals:** "30% reduction in response time, 25% increase in sales"

6. Click "Generate Strategy Blueprint ($1,500)"

#### **Step 4: Test Payment Flow**
1. You should be redirected to the payment page
2. **Test with Stripe test cards:**
   - **Success:** `4242 4242 4242 4242`
   - **Decline:** `4000 0000 0000 0002`
   - **Expired:** `4000 0000 0000 0069`
   - **Incorrect CVC:** `4000 0000 0000 0127`

3. Use any future expiry date and any 3-digit CVC
4. Test the payment flow

## 🔍 **What to Verify**

### **Database Verification**
Check that the assessment was updated:
```sql
SELECT report_type, competitors, market_position, risk_tolerance 
FROM assessments 
WHERE email = 'test@example.com';
```

Should show:
- `report_type = 'strategy_blueprint'`
- `competitors` field populated
- `market_position` field populated
- `risk_tolerance` field populated

### **UI Verification**
1. **Email Lookup Section:**
   - ✅ Shows when page loads
   - ✅ Validates email input
   - ✅ Shows error for non-existent email
   - ✅ Hides after successful lookup

2. **Existing Data Section:**
   - ✅ Displays all original assessment data
   - ✅ Shows challenges as blue tags
   - ✅ Shows opportunities as orange tags
   - ✅ Data is read-only (not editable)

3. **New Questions Section:**
   - ✅ All form fields are present
   - ✅ Required fields are marked
   - ✅ Checkboxes work correctly
   - ✅ Form validation works

4. **Payment Page:**
   - ✅ Shows product summary
   - ✅ Displays $1,500 price
   - ✅ Stripe card element loads
   - ✅ Payment processing works

## 🐛 **Common Issues & Solutions**

### **Issue: "No assessment found" error**
**Solution:** 
- Check that the email matches exactly
- Verify the assessment was created successfully
- Check database connection

### **Issue: Database columns missing**
**Solution:**
```bash
python -c "from models import DatabaseManager; db = DatabaseManager(); db.init_db()"
```

### **Issue: Payment page not loading**
**Solution:**
- Check Stripe keys are configured
- Verify the route exists in app.py
- Check for JavaScript errors in browser console

### **Issue: Form submission fails**
**Solution:**
- Check browser console for JavaScript errors
- Verify all required fields are filled
- Check server logs for Python errors

## 📊 **Test Data Examples**

### **Sample Assessment Data**
```json
{
  "company_name": "Tech Innovations Inc",
  "industry": "technology",
  "company_size": "11-50",
  "role": "ceo",
  "challenges": ["manual-processes", "data-analysis"],
  "current_tech": "intermediate",
  "ai_experience": "exploring",
  "budget": "25k-50k",
  "timeline": "6-months",
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane@techinnovations.com",
  "phone": "555-123-4567"
}
```

### **Sample Strategy Data**
```json
{
  "competitors": "Competitor A (market leader), Competitor B (niche player), Competitor C (startup)",
  "competitive_advantages": "Strong customer service, innovative technology stack, agile development process",
  "market_position": "challenger",
  "vendor_features": ["enterprise-support", "api-integration", "data-security"],
  "risk_tolerance": "moderate",
  "risk_concerns": "Data security, employee resistance to change, integration complexity",
  "org_structure": "hierarchical",
  "decision_process": "consultative",
  "team_size": "16-50",
  "skill_gaps": "Data science expertise, AI/ML knowledge, system integration skills",
  "budget_allocation": "balanced",
  "roi_timeline": "12-months",
  "current_kpis": "Customer satisfaction (85%), Revenue growth (15%), Operational efficiency (70%)",
  "improvement_goals": "30% reduction in response time, 25% increase in sales, 40% improvement in efficiency"
}
```

## 🎯 **Success Criteria**

Your Strategy Blueprint implementation is working correctly if:

1. ✅ **Email lookup** finds existing assessments
2. ✅ **Existing data** displays as read-only summary
3. ✅ **New questions** collect strategic information
4. ✅ **Database** stores all strategy data
5. ✅ **Payment flow** processes $1,500 transactions
6. ✅ **Report type** updates to 'strategy_blueprint'
7. ✅ **User experience** is smooth and professional

## 🚨 **Security Testing**

1. **Test with invalid email addresses**
2. **Test with non-existent assessment IDs**
3. **Verify payment amount is correct ($1,500)**
4. **Check that sensitive data isn't exposed in URLs**
5. **Test form validation and sanitization**

## 📝 **Testing Checklist**

- [ ] Database schema updated correctly
- [ ] Email lookup functionality works
- [ ] Existing data displays properly
- [ ] New form fields collect data correctly
- [ ] Form validation works
- [ ] Database updates with strategy data
- [ ] Payment intent creation works
- [ ] Payment page loads correctly
- [ ] Stripe integration functions
- [ ] Report type updates correctly
- [ ] Error handling works properly
- [ ] UI is responsive and professional

## 🔧 **Troubleshooting Commands**

```bash
# Check database schema
sqlite3 ai_consultant.db ".schema assessments"

# View test data
sqlite3 ai_consultant.db "SELECT * FROM assessments WHERE email LIKE '%test%';"

# Check Flask app is running
curl http://localhost:5000/

# Test API endpoint
curl -X POST http://localhost:5000/api/lookup_assessment \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```







