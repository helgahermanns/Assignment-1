"""
Main entry point for DTU Optimization Assignment 1.

This script serves as a central dispatcher that can run any part of the assignment.
It provides a menu system to choose which question/part to execute, or can run
specific parts directly via command line arguments.

Usage:
    python main.py                    # Interactive menu
    python main.py --question 1a_iv   # Run Q1a part iv
    python main.py --question 1a_v    # Run Q1a part v  
    python main.py --question 1b_v    # Run Q1b part v
    python main.py --question 1c_v    # Run Q1c part v
    python main.py --question 2b      # Run Q2b
    python main.py --list             # List all available questions
"""

import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

# Import scripts
import scripts.q1a_iv as q1a_iv_script
import scripts.q1a_v as q1a_v_script
import scripts.q1b_v as q1b_v_script
import scripts.q1c_v as q1c_v_script
import scripts.q2b as q2b_script

# Import runner for basic functionality
from runner.runner import Runner


# Available question scripts mapping
AVAILABLE_QUESTIONS = {
    "1a_iv": {
        "name": "Question 1a Part IV - Basic Consumer Flexibility",
        "script": q1a_iv_script,
        "function": "solve_q1_part_iv"
    },
    "1a_v": {
        "name": "Question 1a Part V - Tariff Scenario Analysis", 
        "script": q1a_v_script,
        "function": "solve_q1_part_v"
    },
    "1b_v": {
        "name": "Question 1b Part V - Consumer Type Analysis",
        "script": q1b_v_script, 
        "function": "solve_q1b_part_v"
    },
    "1c_v": {
        "name": "Question 1c Part V - Battery Storage Analysis",
        "script": q1c_v_script,
        "function": "solve_q1c_part_v"
    },
    "2b": {
        "name": "Question 2b - Battery Investment Analysis", 
        "script": q2b_script,
        "function": "solve_q2b"
    }
}


def list_available_questions():
    """Display all available questions that can be run."""
    print("\n" + "=" * 70)
    print("AVAILABLE ASSIGNMENT QUESTIONS")
    print("=" * 70)
    
    for key, info in AVAILABLE_QUESTIONS.items():
        print(f"  {key:<8} - {info['name']}")
    
    print("\nUsage:")
    print("  python main.py --question 1a_iv")
    print("  python main.py                    # Interactive menu")
    print("=" * 70)


def run_question(question_key: str):
    """Run a specific question by key."""
    if question_key not in AVAILABLE_QUESTIONS:
        print(f" Error: Question '{question_key}' not found.")
        print(f"Available questions: {', '.join(AVAILABLE_QUESTIONS.keys())}")
        return False
    
    question_info = AVAILABLE_QUESTIONS[question_key]
    
    print("\n" + "=" * 70)
    print(f"RUNNING: {question_info['name']}")
    print("=" * 70)
    
    try:
        # Get the function from the script module
        script_module = question_info['script']
        function_name = question_info['function']
        
        if hasattr(script_module, function_name):
            solve_function = getattr(script_module, function_name)
            solve_function()
            print(f"\n Successfully completed {question_key}")
            return True
        else:
            print(f" Error: Function '{function_name}' not found in script")
            return False
            
    except Exception as e:
        print(f" Error running {question_key}: {str(e)}")
        print("\nTroubleshooting:")
        print("- Check that Gurobi is installed and licensed")
        print("- Verify data files exist in data/ folders") 
        print("- Ensure required Python packages are installed")
        return False


def interactive_menu():
    """Display interactive menu for question selection."""
    while True:
        print("\n" + "=" * 70)
        print("DTU OPTIMIZATION ASSIGNMENT 1 - INTERACTIVE MENU")
        print("=" * 70)
        
        # Display options
        for i, (key, info) in enumerate(AVAILABLE_QUESTIONS.items(), 1):
            print(f"  {i}. {info['name']}")
        
        print(f"  {len(AVAILABLE_QUESTIONS) + 1}. List all available questions")
        print(f"  {len(AVAILABLE_QUESTIONS) + 2}. Exit")
        
        try:
            choice = input(f"\nSelect option (1-{len(AVAILABLE_QUESTIONS) + 2}): ").strip()
            
            if choice == str(len(AVAILABLE_QUESTIONS) + 2):  # Exit
                print("Goodbye!")
                break
            elif choice == str(len(AVAILABLE_QUESTIONS) + 1):  # List questions
                list_available_questions()
                continue
            else:
                # Convert choice to question key
                choice_num = int(choice)
                if 1 <= choice_num <= len(AVAILABLE_QUESTIONS):
                    question_keys = list(AVAILABLE_QUESTIONS.keys())
                    selected_key = question_keys[choice_num - 1]
                    run_question(selected_key)
                else:
                    print(f"Invalid choice. Please select 1-{len(AVAILABLE_QUESTIONS) + 2}")
                    
        except (ValueError, KeyboardInterrupt):
            print("\n Goodbye!")
            break
        except Exception as e:
            print(f" Error: {e}")


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="DTU Optimization Assignment 1 - Central Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Interactive menu
  python main.py --question 1a_iv  # Run Q1a part iv
  python main.py --question 1a_v   # Run Q1a part v
  python main.py --list            # List available questions
        """
    )
    
    parser.add_argument(
        "--question", "-q",
        type=str,
        help="Question to run (e.g., 1a_iv, 1a_v, 1b_v, 1c_v, 2b)"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true", 
        help="List all available questions"
    )
    
    args = parser.parse_args()
    
    # Handle command line arguments
    if args.list:
        list_available_questions()
    elif args.question:
        run_question(args.question)
    else:
        # No arguments provided - show interactive menu
        interactive_menu()


if __name__ == "__main__":
    main()