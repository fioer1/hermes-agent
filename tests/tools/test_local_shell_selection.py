from unittest.mock import patch

from tools.environments.local import _find_bash


def test_find_bash_prefers_git_bash_over_windows_wsl_launcher(monkeypatch):
    monkeypatch.setattr("tools.environments.local._IS_WINDOWS", True)

    def fake_isfile(path: str) -> bool:
        return path == r"C:\Program Files\Git\bin\bash.exe"

    with patch("tools.environments.local.os.path.isfile", side_effect=fake_isfile), \
         patch("tools.environments.local.shutil.which", return_value=r"C:\Windows\System32\bash.exe"):
        assert _find_bash() == r"C:\Program Files\Git\bin\bash.exe"


def test_find_bash_uses_non_wsl_bash_from_path_when_git_bash_not_in_default_location(monkeypatch):
    monkeypatch.setattr("tools.environments.local._IS_WINDOWS", True)

    with patch("tools.environments.local.os.path.isfile", return_value=False), \
         patch("tools.environments.local.shutil.which", return_value=r"D:\PortableGit\bin\bash.exe"):
        assert _find_bash() == r"D:\PortableGit\bin\bash.exe"
