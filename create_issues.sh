#!/bin/bash
# Script to create GitHub issues using GitHub CLI (gh)
# Make sure you have gh installed and authenticated

set -e

echo 'Creating issue 1/6: Migration: ace_remove_powered_by_odoo'
# Extract body content (everything after "## Body" line)
sed -n '/^## Body$/,$p' "issue_templates/issue_01_ace_remove_powered_by_odoo_migration.md" | tail -n +2 | \
gh issue create --title "Migration: ace_remove_powered_by_odoo" --body-file - --label "migration,odoo-19,complexity: low"
sleep 1  # Rate limiting

echo 'Creating issue 2/6: Migration: customer_notes_odoo'
sed -n '/^## Body$/,$p' "issue_templates/issue_02_customer_notes_odoo_migration.md" | tail -n +2 | \
gh issue create --title "Migration: customer_notes_odoo" --body-file - --label "migration,odoo-19,complexity: medium"
sleep 1  # Rate limiting

echo 'Creating issue 3/6: Migration: mail_debrand'
sed -n '/^## Body$/,$p' "issue_templates/issue_03_mail_debrand_migration.md" | tail -n +2 | \
gh issue create --title "Migration: mail_debrand" --body-file - --label "migration,odoo-19,complexity: medium"
sleep 1  # Rate limiting

echo 'Creating issue 4/6: Migration: survey_file_upload_field'
sed -n '/^## Body$/,$p' "issue_templates/issue_04_survey_file_upload_field_migration.md" | tail -n +2 | \
gh issue create --title "Migration: survey_file_upload_field" --body-file - --label "migration,odoo-19,complexity: high"
sleep 1  # Rate limiting

echo 'Creating issue 5/6: Migration: survey_whatsapp'
sed -n '/^## Body$/,$p' "issue_templates/issue_05_survey_whatsapp_migration.md" | tail -n +2 | \
gh issue create --title "Migration: survey_whatsapp" --body-file - --label "migration,odoo-19,complexity: high"
sleep 1  # Rate limiting

echo 'Creating issue 6/6: Migration: whatsapp_calendar'
sed -n '/^## Body$/,$p' "issue_templates/issue_06_whatsapp_calendar_migration.md" | tail -n +2 | \
gh issue create --title "Migration: whatsapp_calendar" --body-file - --label "migration,odoo-19,complexity: medium"
sleep 1  # Rate limiting

echo "All issues created successfully!"
