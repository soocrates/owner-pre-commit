import os
import re

def scan_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.tf') or file.endswith('.tfvars'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                    updated_content = check_and_replace_file(content)
                    if updated_content != content:
                        with open(file_path, 'w') as f:
                            f.write(updated_content)
    print("All files processed and updated where necessary.")

def check_and_replace_file(content):
    resource_pattern = re.compile(r'resource\s+"aws_[^"]+"\s+"[^"]+"\s+\{(?:[^{}]|\{[^{}]*\})*tags\s*=\s*\{[^}]*\}', re.DOTALL)
    module_pattern = re.compile(r'module\s+"[^"]+"\s+\{(?:[^{}]|\{[^{}]*\})*tags\s*=\s*\{[^}]*\}', re.DOTALL)
    provider_pattern = re.compile(r'provider\s+"aws"\s+\{(?:[^{}]|\{[^{}]*\})*default_tags\s*\{(?:[^{}]|\{[^{}]*\})*\}\s*\}', re.DOTALL)
    owner_key_pattern = re.compile(r'owner\s*=\s*["\'][^"\']*["\']')

    provider_match = provider_pattern.search(content)
    updated_content = content

    for pattern in [resource_pattern, module_pattern]:
        for match in pattern.finditer(content):
            tags_block = match.group(0)
            if 'tags' in tags_block and owner_key_pattern.search(tags_block):
                if not (provider_match and provider_match.start() < match.start() < provider_match.end()):
                    updated_tags_block = owner_key_pattern.sub('owner = var.owner', tags_block)
                    updated_content = updated_content.replace(tags_block, updated_tags_block)

    return updated_content

if __name__ == "__main__":
    project_directory = os.path.dirname(os.path.abspath(__file__))
    scan_files(project_directory)
