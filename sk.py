import base64
import os
from getpass import getpass
from pathlib import Path

import click as click
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


BACKUP_TARGETS = [
]


class SKManager:

    def __init__(self):
        self._password = None
        self.plain_path = Path(__file__).parent / 'sk.txt'
        self.secret_path = Path(__file__).parent / '.sk'

    def get_password(self) -> str:
        if self._password is None:
            self._password = getpass()
        return self._password

    def _get_encryption_key(self, password):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'42',
            iterations=100000
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def _get_fernet(self):
        return Fernet(self._get_encryption_key(self.get_password()))

    def encrypt(self, text:str) -> bytes:
        return self._get_fernet().encrypt(text.encode())

    def decrypt(self, cipher: bytes) -> str:
        return self._get_fernet().decrypt(cipher).decode()

    def encrypt_file(self, source_path: Path, target_dir: Path):
        with source_path.open() as f:
            text = f.read()
        with target_dir.open('wb') as f:
            f.write(self.encrypt(text))

    def decrypt_file(self, source_path: Path, target_dir: Path):
        with source_path.open('rb') as f:
            cipher = f.read()
        with target_dir.open('w') as f:
            f.write(self.decrypt(cipher))

    def load(self):
        self.decrypt_file(self.secret_path, self.plain_path)

    def save(self):
        self.encrypt_file(self.plain_path, self.secret_path)
        self.plain_path.unlink()

    def backup(self):
        for target in BACKUP_TARGETS:
            target_path = f'{target}/{self.secret_path.name}'
            print(f'Coping to {target_path}')
            stream = os.popen(f"scp '{self.secret_path}' '{target_path}'")
            for line in stream.readlines():
                print(f' > {line.strip()}')
            print()


@click.group()
def cli():
    pass


@cli.command()
def load():
    manager = SKManager()
    manager.load()


@cli.command()
def save():
    manager = SKManager()
    manager.save()


@cli.command()
def backup():
    manager = SKManager()
    manager.backup()


if __name__ == '__main__':
    cli()

    
