from src.checkpoint import Checkpoint


def test_new_file_not_processed(tmp_path):
    cp = Checkpoint(str(tmp_path / "checkpoint.json"))
    assert not cp.is_processed("/some/file.md", mtime=1000.0)


def test_mark_and_check(tmp_path):
    cp = Checkpoint(str(tmp_path / "checkpoint.json"))
    cp.mark_processed("/some/file.md", mtime=1000.0)
    assert cp.is_processed("/some/file.md", mtime=1000.0)


def test_modified_file_not_processed(tmp_path):
    cp = Checkpoint(str(tmp_path / "checkpoint.json"))
    cp.mark_processed("/some/file.md", mtime=1000.0)
    assert not cp.is_processed("/some/file.md", mtime=2000.0)


def test_persists_across_instances(tmp_path):
    path = str(tmp_path / "checkpoint.json")
    cp1 = Checkpoint(path)
    cp1.mark_processed("/file.md", mtime=1000.0)
    cp1.save()
    cp2 = Checkpoint(path)
    assert cp2.is_processed("/file.md", mtime=1000.0)
