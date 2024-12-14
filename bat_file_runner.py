import subprocess
import os

def run_bat_file(file_path):
    """
    Runs a .bat file and prints its output.

    Args:
        file_path (str): Path to the .bat file.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return
    
    if not file_path.endswith('.bat'):
        print(f"Error: The file '{file_path}' is not a .bat file.")
        return
    
    try:
        # Run the .bat file
        result = subprocess.run(file_path, shell=True, text=True, capture_output=True)
        
        # Print output and errors
        print("Output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Example usage
    bat_file_path = input("Enter the path to the .bat file: ").strip()
    run_bat_file(bat_file_path)
