import subprocess
import json
import logging
import os
import sys
import glob

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_caller_identity():
    logging.debug("Executing get_caller_identity")
    try:
        command = "aws sts get-caller-identity"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        result.check_returncode()
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing AWS CLI command: {e}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON response: {e}")
        return None

def extract_username(identity):
    logging.debug("Executing extract_username")
    if identity and 'Arn' in identity:
        arn_parts = identity['Arn'].split(':')
        user_part = arn_parts[-1]
        username = user_part.split('/')[-1]
        return username
    return None

def read_tf_file(file_path):
    logging.debug(f"Reading file: {file_path}")
    if not os.path.exists(file_path):
        logging.debug("File does not exist.")
        return []

    with open(file_path, 'r') as file:
        lines = file.readlines()

    return lines

def write_tf_file(file_path, lines):
    logging.debug(f"Writing file: {file_path} with new content.")
    with open(file_path, 'w') as file:
        file.writelines(lines)

def update_owner_in_file(owner, file_path):
    logging.debug(f"Updating owner in file: {file_path} to: {owner}")
    lines = read_tf_file(file_path)
    updated = False
    for i, line in enumerate(lines):
        if 'owner' in line and '=' in line:
            parts = line.split('=', 1)
            key = parts[0].strip()
            current_value = parts[1].strip().strip('"')
            if current_value != owner:
                lines[i] = f'{key} = "{owner}"\n'
                updated = True

    if updated:
        write_tf_file(file_path, lines)
        logging.info(f"Owner updated successfully in {file_path}.")
    else:
        logging.info(f"Owner in {file_path} is already up-to-date or not found.")

def main():
    logging.debug("Starting main function.")
    identity = get_caller_identity()
    owner = extract_username(identity)

    if owner:
        logging.info(f"Owner: {owner}")
        tf_files = [file for file in glob.glob("**/*.tf", recursive=True) if os.path.isfile(file)]
        for file_path in tf_files:
            update_owner_in_file(owner, file_path)
        return 0
    else:
        logging.error("Could not determine the owner.")
        return 1

if __name__ == "__main__":
    logging.debug("Script execution started")
    exit_code = main()
    sys.exit(exit_code)