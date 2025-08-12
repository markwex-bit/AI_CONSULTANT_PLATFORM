-- Migration: fix_contact_company_field_ordering
-- Description: Fix field ordering for Contact & Company Information section to display fields in logical order
-- Created: 2025-08-12T13:40:16.540302


-- Fix field ordering for Contact & Company Information section
UPDATE field_configurations 
SET sort_order = 1 
WHERE field_name = 'first_name' AND section_name = 'contact_company' AND form_flag = 'A';

UPDATE field_configurations 
SET sort_order = 2 
WHERE field_name = 'last_name' AND section_name = 'contact_company' AND form_flag = 'A';

UPDATE field_configurations 
SET sort_order = 3 
WHERE field_name = 'email' AND section_name = 'contact_company' AND form_flag = 'A';

UPDATE field_configurations 
SET sort_order = 4 
WHERE field_name = 'phone' AND section_name = 'contact_company' AND form_flag = 'A';

UPDATE field_configurations 
SET sort_order = 5 
WHERE field_name = 'company_name' AND section_name = 'contact_company' AND form_flag = 'A';

UPDATE field_configurations 
SET sort_order = 6 
WHERE field_name = 'website' AND section_name = 'contact_company' AND form_flag = 'A';

UPDATE field_configurations 
SET sort_order = 7 
WHERE field_name = 'industry' AND section_name = 'contact_company' AND form_flag = 'A';

UPDATE field_configurations 
SET sort_order = 8 
WHERE field_name = 'role' AND section_name = 'contact_company' AND form_flag = 'A';

UPDATE field_configurations 
SET sort_order = 9 
WHERE field_name = 'company_size' AND section_name = 'contact_company' AND form_flag = 'A';


-- Insert migration record
INSERT OR IGNORE INTO database_migrations (migration_name, description, sql_changes) 
VALUES ('fix_contact_company_field_ordering', 'Fix field ordering for Contact & Company Information section to display fields in logical order', '
-- Fix field ordering for Contact & Company Information section
UPDATE field_configurations 
SET sort_order = 1 
WHERE field_name = ''first_name'' AND section_name = ''contact_company'' AND form_flag = ''A'';

UPDATE field_configurations 
SET sort_order = 2 
WHERE field_name = ''last_name'' AND section_name = ''contact_company'' AND form_flag = ''A'';

UPDATE field_configurations 
SET sort_order = 3 
WHERE field_name = ''email'' AND section_name = ''contact_company'' AND form_flag = ''A'';

UPDATE field_configurations 
SET sort_order = 4 
WHERE field_name = ''phone'' AND section_name = ''contact_company'' AND form_flag = ''A'';

UPDATE field_configurations 
SET sort_order = 5 
WHERE field_name = ''company_name'' AND section_name = ''contact_company'' AND form_flag = ''A'';

UPDATE field_configurations 
SET sort_order = 6 
WHERE field_name = ''website'' AND section_name = ''contact_company'' AND form_flag = ''A'';

UPDATE field_configurations 
SET sort_order = 7 
WHERE field_name = ''industry'' AND section_name = ''contact_company'' AND form_flag = ''A'';

UPDATE field_configurations 
SET sort_order = 8 
WHERE field_name = ''role'' AND section_name = ''contact_company'' AND form_flag = ''A'';

UPDATE field_configurations 
SET sort_order = 9 
WHERE field_name = ''company_size'' AND section_name = ''contact_company'' AND form_flag = ''A'';
');
