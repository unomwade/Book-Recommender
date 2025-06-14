import subprocess
import sys

def run_app():
    """Run the main app."""
    try:
        subprocess.run(["streamlit", "run", "app.py"], check=True)
        print("App script completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error while running app.py: {e}")
        sys.exit(1)

def main():
    """Main entry point for the application."""
    print("Starting main application...")
    run_app()

if __name__ == "__main__":
    main()