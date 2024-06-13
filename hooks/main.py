import subprocess
import json
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

TFVARS_FILE = "script.tfvars"

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

def read_tfvars(file_path):
    logging.debug(f"Reading TFVars file: {file_path}")
    if not os.path.exists(file_path):
        logging.debug("TFVars file does not exist.")
        return {}

    with open(file_path, 'r') as file:
        lines = file.readlines()

    tfvars = {}
    for line in lines:
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value is value.strip().strip('"')
            tfvars[key] = value

    logging.debug(f"Current TFVars: {tfvars}")
    return tfvars

def write_tfvars(file_path, tfvars):
    logging.debug(f"Writing TFVars file: {file_path} with values: {tfvars}")
    with open(file_path, 'w') as file:
        for key, value in tfvars.items():
            file.write(f'{key} = "{value}"\n')
    logging.debug(f"Updated TFVars file: {file_path}")

def update_owner_in_tfvars(owner):
    logging.debug(f"Updating owner in TFVars to: {owner}")
    tfvars = read_tfvars(TFVARS_FILE)
    previous_owner = tfvars.get('owner', '')
    tfvars['owner'] = owner
    write_tfvars(TFVARS_FILE, tfvars)
    return previous_owner != owner

def main():
    logging.debug("Starting main function.")
    identity = get_caller_identity()
    owner = extract_username(identity)

    if owner:
        logging.info(f"Owner: {owner}")
        if update_owner_in_tfvars(owner):
            logging.info("Owner updated successfully.")
            return 0
        else:
            logging.info("Owner was already up-to-date.")
            return 0
    else:
        logging.error("Could not determine the owner.")
        return 1

if __name__ == "__main__":
    logging.debug("Script execution started")
    sys.exit(main())
