from app.infrastructure.filesystem import WorkspaceManager


def test_workspace_isolation(tmp_path):
    first = WorkspaceManager(tmp_path).create("one")
    second = WorkspaceManager(tmp_path).create("two")
    assert first.root != second.root
    assert first.output.is_dir()

