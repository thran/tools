from sk import SKManager


def test_password(mocker):
    getpass = mocker.patch('sk.getpass', return_value='pass')

    manager = SKManager()
    assert manager.get_password() == 'pass'
    assert manager.get_password() == 'pass'
    getpass.assert_called_once()


def test_key():
    manager = SKManager()
    for password in ['pass', 'er23ns', 'ads*%$@3d']:
        assert manager._get_encryption_key(password) == manager._get_encryption_key(password)


def test_coding(mocker):
    mocker.patch('sk.getpass', return_value='pass')

    manager = SKManager()
    text = 'text'
    c = manager.encrypt(text)
    assert type(c) is bytes
    assert manager.decrypt(c) == text


def test_file_coding(mocker, tmpdir):
    mocker.patch('sk.getpass', return_value='pass')
    text = 'dadadjas\n\ndasdasd\n'
    with (tmpdir / 'file.txt').open('w') as f:
        f.write(text)

    manager = SKManager()
    manager.encrypt_file(tmpdir / 'file.txt', tmpdir / '.file')
    assert (tmpdir / '.file').exists()
    manager.decrypt_file(tmpdir / '.file', tmpdir / 'file2.txt')
    assert (tmpdir / 'file2.txt').open().read() == text
