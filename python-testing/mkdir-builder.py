import os

def create_directories(dir_list):
    for dir_name in dir_list:
        try:
            os.makedirs(dir_name, exist_ok=True)
            print(f"Directory '{dir_name}' created successfully.")
        except OSError as error:
            print(f"Creation of the directory '{dir_name}' failed: {error}")

def main():
    directories = ["configs", "playbooks", "reports", "templates", "vars"]
    create_directories(directories)

if __name__ == "__main__":
    main()
