from unittest.mock import patch

from acp_adapter.tools import build_tool_start, build_tool_title, extract_locations


def test_build_tool_title_normalizes_wsl_path_on_windows():
    with patch("acp_adapter.tools.os.name", "nt"):
        title = build_tool_title("read_file", {"path": "/mnt/h/workspace/README.md"})
    assert r"H:\workspace\README.md" in title


def test_extract_locations_normalizes_msys_drive_path_on_windows():
    with patch("acp_adapter.tools.os.name", "nt"):
        locations = extract_locations({"path": "/g/Hermes Agent/README.md", "offset": 7})
    assert len(locations) == 1
    assert locations[0].path == r"G:\Hermes Agent\README.md"
    assert locations[0].line == 7


def test_build_tool_start_normalizes_read_file_path_in_title_and_locations():
    with patch("acp_adapter.tools.os.name", "nt"):
        result = build_tool_start(
            "tc-read",
            "read_file",
            {"path": "/mnt/h/project/apps/api/src/app.ts", "offset": 3, "limit": 10},
        )
    assert r"H:\project\apps\api\src\app.ts" in result.title
    assert result.locations[0].path == r"H:\project\apps\api\src\app.ts"
