import runpy


def test_module_entrypoint_invokes_cli_main(monkeypatch):
    called = {"value": False}

    def fake_main() -> None:
        called["value"] = True

    monkeypatch.setattr("triage_toolkit.cli.main", fake_main)

    runpy.run_module("triage_toolkit.__main__", run_name="__main__")

    assert called["value"] is True
