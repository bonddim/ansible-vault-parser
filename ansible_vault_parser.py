"""
Tools to parse ansible vault
"""
import argparse


def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vault-password-file', dest='vault_password_file', type=str, help='Path to ansible vault password file')
    parser.add_argument('--vault-file', dest='vault_file', type=str, help='Path to ansible vault file')
    args = parser.parse_args()
    return args


def _read_vault(vault_file, vault_password_file):
    from ansible import constants as C
    from ansible.cli import CLI
    from ansible.parsing.dataloader import DataLoader

    password_files = []
    if vault_password_file:
        password_files.append(vault_password_file)

    loader = DataLoader()
    CLI.setup_vault_secrets(
        loader=loader,
        vault_ids=C.DEFAULT_VAULT_IDENTITY_LIST,
        vault_password_files=password_files,
        auto_prompt=False  # disable prompt if no vault password files found
    )

    try:
        return loader.load_from_file(vault_file)
    except Exception:
        return {}


def parse_vault(vault_file, vault_password_file=''):
    '''Parses encrypted ansible vault files

    Uses matched vault password file from:
    - 'vault_password_file' argument (optional)
    - 'vault_password_file' variable in ansible.cfg
    - 'ANSIBLE_VAULT_PASSWORD_FILE' variable in environment

    Parameters:
      :arg vault_file: (str) path to encrypted ansible-vault file
      :kwarg vault_password_file: (str) path to ansible-vault password file
    Returns:
      dict with vault content or empty dict on error
    '''

    try:
        vault_data = _read_vault(vault_file, vault_password_file)

    except ImportError:
        # Run if ansible is installed with python2 backend
        import subprocess
        from ast import literal_eval

        output = subprocess.check_output(['python', __file__, vault_file, vault_password_file])
        vault_data = literal_eval(output.decode('utf-8'))

    return vault_data


if __name__ == "__main__":
    _args = _parse_arguments()
    print(_read_vault(_args.vault_file, _args.vault_password_file))
