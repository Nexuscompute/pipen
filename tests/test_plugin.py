import pytest

from pipen import plugin, Pipen, Proc

from .helpers import OutputNotGeneratedProc, SimpleProc, pipen  # noqa: F401


class Plugin:
    def __init__(self, name):
        self.name = name

    @plugin.impl
    async def on_complete(self, pipen, succeeded):
        print(f"<<<{self.name}>>>")


@pytest.mark.forked
def test_job_succeeded(pipen, caplog):
    out = pipen.set_starts(OutputNotGeneratedProc).run()
    assert not out


@pytest.mark.forked
def test_plugin_context_only(tmp_path, capsys):
    plugin1 = Plugin("plugin1")
    plugin2 = Plugin("plugin2")
    plugin3 = Plugin("plugin3")
    plugin4 = Plugin("plugin4")

    plugin.register(plugin1, plugin2, plugin3, plugin4)
    plugin.get_plugin("plugin4").disable()

    pipeline = Pipen(
        name="pipeline_plugin_context_only",
        desc="No description",
        loglevel="debug",
        cache=True,
        workdir=tmp_path / ".pipen",
        outdir=tmp_path / "pipeline_plugin_context_only",
        plugins=["plugin1", "plugin2"],
    )
    pipeline.set_starts(SimpleProc).run()
    out = capsys.readouterr().out
    assert "<<<plugin1>>>" in out
    assert "<<<plugin2>>>" in out
    assert "<<<plugin3>>>" not in out
    assert "<<<plugin4>>>" not in out


@pytest.mark.forked
def test_plugin_context_mixed(tmp_path, capsys):
    plugin1 = Plugin("plugin1")
    plugin2 = Plugin("plugin2")
    plugin3 = Plugin("plugin3")
    plugin4 = Plugin("plugin4")

    plugin.register(plugin1, plugin2, plugin3, plugin4)
    plugin.get_plugin("plugin3").disable()
    plugin.get_plugin("plugin4").disable()

    pipeline = Pipen(
        name="pipeline_plugin_context_mixed",
        desc="No description",
        loglevel="debug",
        cache=True,
        workdir=tmp_path / ".pipen",
        outdir=tmp_path / "pipeline_plugin_context_mixed",
        plugins=["+plugin3", plugin.get_plugin("plugin4"), "-plugin2"],
    )
    pipeline.set_starts(SimpleProc).run()
    out = capsys.readouterr().out
    assert "<<<plugin1>>>" in out
    assert "<<<plugin2>>>" not in out
    assert "<<<plugin3>>>" in out
    assert "<<<plugin4>>>" in out


@pytest.mark.forked
def test_jobcmd_hooks(pipen):

    @plugin.register
    class MyJobCmdPlugin:
        @plugin.impl
        def on_jobcmd_init(job):
            return "# on_jobcmd_init from myjobcmdplugin"

        @plugin.impl
        def on_jobcmd_prep(job):
            return "# on_jobcmd_prep from myjobcmdplugin"

        @plugin.impl
        def on_jobcmd_end(job):
            return "# on_jobcmd_end from myjobcmdplugin"

    class MyProc(Proc):
        input = "in:var"
        input_data = [1]
        output = "out:var:{{in.in}}"
        script = "echo {{proc.name}}"

    pipen.set_starts(MyProc).run()
    assert pipen.run()

    wrapper_script = pipen.workdir / "MyProc" / "0" / "job.wrapped.local"
    assert wrapper_script.exists()
    content = wrapper_script.read_text()
    assert "# on_jobcmd_init from myjobcmdplugin" in content
    assert "# on_jobcmd_prep from myjobcmdplugin" in content
    assert "# on_jobcmd_end from myjobcmdplugin" in content
