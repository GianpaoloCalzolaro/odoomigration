#!/usr/bin/env python3
"""
Script to generate GitHub issue templates for migration analysis files.
Since direct GitHub API access is not available, this script creates markdown
templates that can be used to create issues manually or via GitHub CLI.
"""

import os
import re
from pathlib import Path


def extract_module_info(content):
    """Extract key information from migration analysis file."""
    info = {
        'title': '',
        'module_name': '',
        'summary': '',
        'complexity': '',
        'full_content': content
    }
    
    # Extract title (first line with # Migration Issue)
    title_match = re.search(r'# Migration Issue: (.+)', content)
    if title_match:
        info['title'] = title_match.group(1).strip()
    
    # Extract module name
    module_match = re.search(r'\*\*Modulo:\*\* (\w+)', content)
    if module_match:
        info['module_name'] = module_match.group(1)
    
    # Extract complexity level
    complexity_match = re.search(r'Livello di complessità della migrazione: \*\*(.+?)\*\*', content)
    if complexity_match:
        info['complexity'] = complexity_match.group(1)
    
    # Extract summary section (first 1000 chars of SUMMARY section)
    summary_match = re.search(r'## SUMMARY\n\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    if summary_match:
        summary_text = summary_match.group(1).strip()
        # Limit to reasonable length for issue description
        if len(summary_text) > 800:
            summary_text = summary_text[:800] + "...\n\n*[See full analysis in migration_analysis file]*"
        info['summary'] = summary_text
    
    return info


def create_issue_template(migration_file, info):
    """Create a GitHub issue template from migration info."""
    
    # Create labels based on complexity
    labels = ['migration', 'odoo-19']
    if info['complexity']:
        complexity_lower = info['complexity'].lower()
        if 'bassa' in complexity_lower or 'low' in complexity_lower:
            labels.append('complexity: low')
        elif 'media' in complexity_lower or 'medium' in complexity_lower:
            labels.append('complexity: medium')
        elif 'alta' in complexity_lower or 'high' in complexity_lower:
            labels.append('complexity: high')
    
    # Create issue title
    title = f"Migration: {info['module_name'] or info['title']}"
    
    # Create issue body
    body = f"""# Migrazione: {info['title']}

## Complessità
{info['complexity'] or 'Da valutare'}

## Descrizione

{info['summary']}

## File di Analisi
Vedi `migration_analysis/{migration_file}` per l'analisi completa della migrazione.

## Tasks
- [ ] Verificare e aggiornare dipendenze
- [ ] Applicare modifiche richieste al manifest
- [ ] Aggiornare codice Python se necessario
- [ ] Aggiornare template XML/views
- [ ] Testare il modulo migrato
- [ ] Aggiornare documentazione

## Labels
{', '.join(labels)}
"""
    
    return {
        'title': title,
        'body': body,
        'labels': labels,
        'filename': migration_file
    }


def main():
    """Main function to process all migration files and create issue templates."""
    
    # Get the migration_analysis directory
    script_dir = Path(__file__).parent
    migration_dir = script_dir / 'migration_analysis'
    
    if not migration_dir.exists():
        print(f"Error: migration_analysis directory not found at {migration_dir}")
        return
    
    # Find all .md files in migration_analysis
    migration_files = sorted(migration_dir.glob('*.md'))
    
    if not migration_files:
        print("No migration analysis files found!")
        return
    
    print(f"Found {len(migration_files)} migration analysis files\n")
    print("=" * 80)
    
    # Process each migration file
    issues = []
    for md_file in migration_files:
        print(f"\nProcessing: {md_file.name}")
        
        # Read file content
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract information
        info = extract_module_info(content)
        
        # Create issue template
        issue = create_issue_template(md_file.name, info)
        issues.append(issue)
        
        print(f"  Title: {issue['title']}")
        print(f"  Labels: {', '.join(issue['labels'])}")
    
    print("\n" + "=" * 80)
    print(f"\nGenerated {len(issues)} issue templates\n")
    
    # Create output directory for issue templates
    output_dir = script_dir / 'issue_templates'
    output_dir.mkdir(exist_ok=True)
    
    # Write individual issue templates
    for i, issue in enumerate(issues, 1):
        output_file = output_dir / f"issue_{i:02d}_{issue['filename'].replace('.md', '')}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Issue Template\n\n")
            f.write(f"## Title\n```\n{issue['title']}\n```\n\n")
            f.write(f"## Labels\n```\n{', '.join(issue['labels'])}\n```\n\n")
            f.write(f"## Body\n\n{issue['body']}\n")
        
        print(f"Created: {output_file.name}")
    
    # Also create a summary file with all issues
    summary_file = output_dir / 'ALL_ISSUES.md'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("# All Migration Issues\n\n")
        f.write(f"Total issues to create: {len(issues)}\n\n")
        f.write("---\n\n")
        
        for i, issue in enumerate(issues, 1):
            f.write(f"## Issue {i}: {issue['title']}\n\n")
            f.write(f"**Labels:** {', '.join(issue['labels'])}\n\n")
            f.write(f"**Source file:** `migration_analysis/{issue['filename']}`\n\n")
            f.write("### Body\n\n")
            f.write(issue['body'])
            f.write("\n\n---\n\n")
    
    print(f"\nCreated summary file: {summary_file.name}")
    
    # Create a shell script for automated issue creation using gh CLI
    gh_script = script_dir / 'create_issues.sh'
    with open(gh_script, 'w', encoding='utf-8') as f:
        f.write("#!/bin/bash\n")
        f.write("# Script to create GitHub issues using GitHub CLI (gh)\n")
        f.write("# Make sure you have gh installed and authenticated\n\n")
        f.write("set -e\n\n")
        
        for i, issue in enumerate(issues, 1):
            # Escape special characters for shell
            title_escaped = issue['title'].replace('"', '\\"').replace('$', '\\$')
            body_file = f"issue_templates/issue_{i:02d}_{issue['filename'].replace('.md', '')}.md"
            labels_str = ','.join(issue['labels'])
            
            f.write(f"echo 'Creating issue {i}/{len(issues)}: {title_escaped}'\n")
            f.write(f'gh issue create --title "{title_escaped}" ')
            f.write(f'--body-file "{body_file}" ')
            f.write(f'--label "{labels_str}"\n')
            f.write("sleep 1  # Rate limiting\n\n")
        
        f.write('echo "All issues created successfully!"\n')
    
    # Make script executable
    os.chmod(gh_script, 0o755)
    print(f"\nCreated GitHub CLI script: {gh_script.name}")
    
    print("\n" + "=" * 80)
    print("\nNext steps:")
    print("1. Review the generated issue templates in the 'issue_templates/' directory")
    print("2. To create all issues automatically, run: ./create_issues.sh")
    print("3. Or create issues manually using the templates in 'issue_templates/'")
    print("=" * 80)


if __name__ == '__main__':
    main()
