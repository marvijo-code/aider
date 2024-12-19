import json
import os
from pathlib import Path
import re
from datetime import datetime

def extract_test_names(test_output):
    """Extract test names from test output."""
    if not test_output:
        return []
    
    test_names = []
    for line in test_output.splitlines():
        # Look for both ERROR: and FAIL: lines with full test path
        if line.startswith('ERROR:') or line.startswith('FAIL:'):
            # Keep the full test path including the class name
            test_name = line.split(' ', 1)[1].strip()
            test_names.append(test_name)
    return test_names

def clean_test_output(test_output):
    """Clean up test output by removing #### prefixes and normalizing formatting."""
    if not test_output:
        return ""
    
    # Remove lines starting with ####
    cleaned_lines = []
    for line in test_output.splitlines():
        if line.startswith('####'):
            line = line.replace('####', '').strip()
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def extract_test_output(content):
    """Extract test output from the chat history content."""
    # Look for code blocks with test output
    test_blocks = re.findall(r'```.*?\n(.*?)```', content, re.DOTALL)
    
    # Combine all relevant test output blocks
    test_output = []
    for block in test_blocks:
        # Skip blocks that don't contain error indicators
        if not ('AssertionError' in block or 
                'FAILED' in block or 
                'ERROR:' in block or 
                'FAIL:' in block):
            continue
            
        # Clean up the block and only keep until AssertionError line
        lines = []
        for line in block.strip().splitlines():
            lines.append(line)
            if 'AssertionError:' in line:
                break
                
        if lines:
            test_output.append('\n'.join(lines))
    
    return '\n'.join(test_output)

def parse_test_results(test_output):
    """Parse test output to extract individual test results."""
    test_results = {}
    current_test = None
    current_details = []
    
    for line in test_output.splitlines():
        # Check for test name at the start of a line
        if not line.startswith(' ') and line.strip():  # Line starts with test name
            if current_test:  # Save previous test if exists
                test_results[current_test] = {
                    'status': 'FAILED',
                    'details': '\n'.join(current_details)
                }
            current_test = line.strip()
            current_details = [line]
        elif line.strip():  # Add details for current test
            current_details.append(line)
    
    # Add the last test case
    if current_test:
        test_results[current_test] = {
            'status': 'FAILED',
            'details': '\n'.join(current_details)
        }
    
    return test_results

def get_test_result(directory):
    """Extract test results from chat history file."""
    history_file = os.path.join(directory, '.aider.chat.history.md')
    
    if not os.path.exists(history_file):
        return True, "", {}
        
    with open(history_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Extract test output from code blocks
        test_output = extract_test_output(content)
        
        # Parse test results
        test_results = parse_test_results(test_output)
        
        # Determine if all tests passed
        all_passed = len(test_results) == 0 and not test_output
        
        return all_passed, test_output, test_results

def get_test_summary(folder_path):
    try:
        instructions_file = os.path.join(folder_path, '.docs', 'instructions.md')
        if os.path.exists(instructions_file):
            with open(instructions_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Split into lines and find first non-empty paragraph after header
                paragraphs = content.split('\n\n')
                summary = None
                
                for para in paragraphs:
                    # Skip empty paragraphs and headers
                    if not para.strip() or para.strip().startswith('#'):
                        continue
                    # Found first real paragraph
                    summary = para.strip()
                    break
                
                if summary:
                    print(f"Successfully extracted summary from {instructions_file}")
                    return summary
                return "No summary found"
        else:
            print(f"Warning: Instructions file not found: {instructions_file}")
        return "No instructions found"
    except Exception as e:
        print(f"Error: Failed getting test summary for {folder_path}: {str(e)}")
        return "Error reading instructions"

def generate_report(folder_path):
    try:
        report_file = 'test-report.md'
        processed_dirs = 0
        failed_dirs = 0
        processed_folders = {}

        print(f"Starting report generation for root folder: {folder_path}")
        
        # Verify root folder exists
        if not os.path.exists(folder_path):
            raise ValueError(f"Root folder not found: {folder_path}")
        
        # Walk through the root directory
        for root, dirs, files in os.walk(folder_path):
            if '.aider.chat.history.md' in files:
                processed_dirs += 1
                try:
                    folder_name = os.path.basename(root)
                    passed, test_output, test_results = get_test_result(root)
                    if not passed:  # Only process folders with failed tests
                        summary = get_test_summary(root)
                        processed_folders[folder_name] = (passed, summary, test_output, test_results)
                        failed_dirs += 1
                except Exception as e:
                    print(f"Error: Failed processing directory {folder_name}: {str(e)}")

        if not processed_folders:
            print("No failed tests found.")
            return

        # Write report
        with open(report_file, 'w', encoding='utf-8') as report:
            report.write("# Failed Tests Report\n\n")
            report.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Write statistics
            report.write(f"Directories processed: {processed_dirs}\n")
            report.write(f"Directories with failures: {failed_dirs}\n\n")
            
            # Write failed tests section
            for folder_name, (passed, summary, test_output, test_results) in processed_folders.items():
                report.write(f"## {folder_name}\n")
                if summary:
                    report.write(f"- Summary: {summary}\n\n")
                
                # Show failed test results with details
                for test_name, result in test_results.items():
                    report.write(f"### {test_name}\n")
                    report.write("```\n")
                    report.write(result['details'])
                    report.write("\n```\n\n")
                
                # Add full test output in collapsible section
                if test_output:
                    report.write("<details><summary>Full Test Output</summary>\n\n")
                    report.write("```\n")
                    report.write(clean_test_output(test_output))
                    report.write("\n```\n")
                    report.write("</details>\n\n")

        print(f"\nReport generation completed:")
        print(f"- Processed directories: {processed_dirs}")
        print(f"- Directories with failures: {failed_dirs}")
        
    except Exception as e:
        print(f"Fatal error during report generation: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        import sys
        if len(sys.argv) != 2:
            print("Usage: python generate_report.py <folder_path>")
            sys.exit(1)
        
        folder_path = sys.argv[1]
        generate_report(folder_path)
    except Exception as e:
        print(f"Script execution failed: {str(e)}")
        raise
