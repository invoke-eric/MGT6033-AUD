import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

def parse_quiz_md(content: str) -> Dict[str, Any]:
    """
    Parse markdown quiz content and convert to structured JSON.
    """
    # Initialize the result structure
    result = {
        "title": "",
        "sections": []
    }
    
    lines = content.split('\n')
    current_section = None
    current_question = None
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        try:
            # Parse main title
            if line.startswith('# ') or line.startswith('**# '):
                title = line.replace('**# ', '').replace('# ', '').replace('**', '').strip()
                result["title"] = title
                i += 1
                continue
                
            # Parse section headers
            if line.startswith('## ') or line.startswith('**## '):
                # Save previous section if exists
                if current_section:
                    if current_question:
                        current_section["questions"].append(current_question)
                        current_question = None
                    result["sections"].append(current_section)
                
                section_title = line.replace('**## ', '').replace('## ', '').replace('**', '').strip()
                current_section = {
                    "title": section_title,
                    "questions": []
                }
                i += 1
                continue
            
            # Parse question numbers with difficulty and type
            question_match = re.match(r'^(\d+)\.\s*\*\*\(([^)]+)\)\*\*\s*(.*)', line)
            if question_match:
                if current_question and current_section:
                    current_section["questions"].append(current_question)
                
                question_number = int(question_match.group(1))
                difficulty_and_type = question_match.group(2)
                question_text = question_match.group(3).strip()
                
                # Check if "Select all that apply" is in the difficulty marker
                is_multiple_select = False
                difficulty = difficulty_and_type
                
                if "Select all that apply" in difficulty_and_type:
                    is_multiple_select = True
                    # Remove "Select all that apply:" from difficulty
                    difficulty = re.sub(r'\s*Select all that apply:\s*', '', difficulty_and_type).strip()
                    # If there's a colon at the end, remove it
                    if difficulty.endswith(':'):
                        difficulty = difficulty[:-1].strip()
                
                # Also check if "Select all that apply:" appears in the question text
                if "Select all that apply:" in question_text:
                    is_multiple_select = True
                    question_text = question_text.replace("Select all that apply:", "").strip()
                
                current_question = {
                    "number": question_number,
                    "difficulty": difficulty,
                    "type": "multiple_select" if is_multiple_select else "single_select",
                    "question": question_text,
                    "options": {}
                }
                i += 1
                continue
            
            # Parse question without difficulty marker (fallback)
            simple_question_match = re.match(r'^(\d+)\.\s*(.*)', line)
            if simple_question_match:
                if current_question and current_section:
                    current_section["questions"].append(current_question)
                
                question_number = int(simple_question_match.group(1))
                question_text = simple_question_match.group(2).strip()
                
                # Check if this line contains difficulty in parentheses
                difficulty = "Unknown"
                if question_text.startswith('**(') and ')**' in question_text:
                    # Format: **(Easy)** Question text
                    difficulty_match = re.match(r'^\*\*\(([^)]+)\)\*\*\s*(.*)', question_text)
                    if difficulty_match:
                        difficulty = difficulty_match.group(1)
                        question_text = difficulty_match.group(2).strip()
                elif question_text.startswith('(') and ')' in question_text:
                    # Format: (Easy) Question text
                    closing_paren = question_text.find(')')
                    difficulty = question_text[1:closing_paren]
                    question_text = question_text[closing_paren + 1:].strip()
                
                # Determine question type
                is_multiple_select = "Select all that apply:" in question_text
                if is_multiple_select:
                    question_text = question_text.replace("Select all that apply:", "").strip()
                
                current_question = {
                    "number": question_number,
                    "difficulty": difficulty,
                    "type": "multiple_select" if is_multiple_select else "single_select",
                    "question": question_text,
                    "options": {}
                }
                i += 1
                continue
                
            # Parse answer options
            option_match = re.match(r'^([A-Z])\.\s*(.*)', line)
            if option_match and current_question:
                option_letter = option_match.group(1)
                option_text = option_match.group(2).strip()
                current_question["options"][option_letter] = option_text
                i += 1
                continue
                
        except Exception as e:
            print(f"Error parsing line {i+1}: '{line}' - {e}")
            
        i += 1
    
    # Don't forget to add the last question and section
    if current_question and current_section:
        current_section["questions"].append(current_question)
    if current_section:
        result["sections"].append(current_section)
    
    return result

def convert_quiz_to_json(input_file: str, output_file: Optional[str] = None) -> None:
    """
    Convert a markdown quiz file to JSON format.
    
    Args:
        input_file: Path to the input markdown file
        output_file: Path to the output JSON file (optional)
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    if not input_path.suffix.lower() in ['.md', '.txt']:
        print(f"Warning: Input file doesn't have .md or .txt extension")
    
    # Read the markdown content
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the content
    try:
        parsed_data = parse_quiz_md(content)
    except Exception as e:
        print(f"Error parsing quiz content: {e}")
        return
    
    # Determine output file path
    if output_file is None:
        output_file = input_path.with_suffix('.json')
    
    # Write JSON output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(parsed_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully converted {input_file} to {output_file}")
    
    # Print summary statistics
    total_questions = sum(len(s['questions']) for s in parsed_data['sections'])
    difficulty_counts = {}
    type_counts = {"single_select": 0, "multiple_select": 0}
    
    for section in parsed_data['sections']:
        for question in section['questions']:
            difficulty = question.get('difficulty', 'Unknown')
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
            type_counts[question['type']] += 1
    
    print(f"Found {len(parsed_data['sections'])} sections with {total_questions} total questions")
    print(f"Question types: {type_counts['single_select']} single-select, {type_counts['multiple_select']} multiple-select")
    print(f"Difficulty distribution: {dict(difficulty_counts)}")

def batch_convert_quiz(input_directory: str, output_directory: Optional[str] = None) -> None:
    """
    Convert all markdown quiz files in a directory to JSON format.
    
    Args:
        input_directory: Directory containing markdown files
        output_directory: Directory for output JSON files (optional)
    """
    input_path = Path(input_directory)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory not found: {input_directory}")
    
    if output_directory:
        output_path = Path(output_directory)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = input_path
    
    # Find all markdown files
    md_files = list(input_path.glob('*.md')) + list(input_path.glob('*.txt'))
    
    if not md_files:
        print(f"No markdown files found in {input_directory}")
        return
    
    print(f"Found {len(md_files)} markdown files to convert")
    
    for md_file in md_files:
        try:
            output_file = output_path / f"{md_file.stem}.json"
            convert_quiz_to_json(str(md_file), str(output_file))
            print()  # Add spacing between files
        except Exception as e:
            print(f"Error converting {md_file}: {e}")

def validate_quiz_structure(data: Dict[str, Any]) -> List[str]:
    """
    Validate the structure of parsed quiz data and return any issues found.
    """
    issues = []
    
    if not data.get('title'):
        issues.append("Missing quiz title")
    
    if not data.get('sections'):
        issues.append("No sections found")
        return issues
    
    for section_idx, section in enumerate(data['sections']):
        if not section.get('title'):
            issues.append(f"Section {section_idx + 1} missing title")
        
        if not section.get('questions'):
            issues.append(f"Section '{section.get('title', 'Unknown')}' has no questions")
            continue
        
        for question in section['questions']:
            if not question.get('question'):
                issues.append(f"Question {question.get('number', 'Unknown')} missing question text")
            
            if not question.get('options'):
                issues.append(f"Question {question.get('number', 'Unknown')} missing options")
            elif len(question['options']) < 2:
                issues.append(f"Question {question.get('number', 'Unknown')} has fewer than 2 options")
    
    return issues

def main():
    """
    Main function to handle command line arguments and execute conversion.
    """
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python quiz_to_json.py <input_file.md> [output_file.json]")
        print("  python quiz_to_json.py --batch <input_directory> [output_directory]")
        print("  python quiz_to_json.py --validate <input_file.md>")
        print("\nExamples:")
        print("  python quiz_to_json.py quiz.md")
        print("  python quiz_to_json.py quiz.md converted_quiz.json")
        print("  python quiz_to_json.py --batch ./quiz_files ./json_files")
        print("  python quiz_to_json.py --validate quiz.md")
        return
    
    if sys.argv[1] == '--batch':
        if len(sys.argv) < 3:
            print("Error: --batch requires input directory")
            return
        
        input_dir = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else None
        batch_convert_quiz(input_dir, output_dir)
        
    elif sys.argv[1] == '--validate':
        if len(sys.argv) < 3:
            print("Error: --validate requires input file")
            return
        
        input_file = sys.argv[2]
        input_path = Path(input_file)
        
        if not input_path.exists():
            print(f"Error: Input file not found: {input_file}")
            return
        
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            parsed_data = parse_quiz_md(content)
            issues = validate_quiz_structure(parsed_data)
            
            if issues:
                print(f"Validation issues found in {input_file}:")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print(f"✓ {input_file} is valid")
                
        except Exception as e:
            print(f"Error parsing {input_file}: {e}")
            
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        convert_quiz_to_json(input_file, output_file)

if __name__ == "__main__":
    main()