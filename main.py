import subprocess

def main():
    subprocess.run(["uv", "run", "streamlit", "run", "app.py"], check=True)

if __name__ == "__main__":
    main()
