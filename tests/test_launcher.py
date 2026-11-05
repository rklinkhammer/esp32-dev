import importlib.machinery
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('launcher', str(ROOT / 'esp32'))
spec = importlib.util.spec_from_loader(loader.name, loader)
launcher = importlib.util.module_from_spec(spec)
loader.exec_module(launcher)


class LauncherTests(unittest.TestCase):
    def command(self, *args):
        return launcher.launch(launcher.parser().parse_args(['--dry-run', '--project', str(ROOT), *args]))

    def test_native_arguments_and_identity(self):
        cmd = self.command('idf', '-B', 'build debug', 'build')
        self.assertEqual(cmd[-4:], ['idf.py', '-B', 'build debug', 'build'])
        self.assertIn('--user', cmd)
        self.assertNotIn('--privileged', cmd)
        self.assertIn('IDF_TARGET=esp32s3', cmd)

    def test_smoke_and_target(self):
        cmd = self.command('--target', 'esp32c3', 'smoke')
        self.assertIn('IDF_TARGET=esp32c3', cmd)
        self.assertEqual(cmd[-2:], ['idf.py', 'build'])
        self.assertIn(str(ROOT / 'examples/smoke'), cmd)

    def test_remote_serial(self):
        port = 'rfc2217://host.docker.internal:4000?ign_set_control'
        cmd = self.command('--port', port, 'flash')
        self.assertEqual(cmd[-4:], ['idf.py', '--port', port, 'flash'])
        self.assertNotIn('--device', cmd)

    def test_local_device_group(self):
        cmd = self.command('--port', '/dev/null', 'monitor')
        self.assertEqual(cmd[cmd.index('--device') + 1], '/dev/null:/dev/null')
        self.assertEqual(cmd[cmd.index('--group-add') + 1], str(Path('/dev/null').stat().st_gid))

    def test_missing_device_rejected(self):
        with self.assertRaisesRegex(ValueError, 'character device'):
            self.command('--port', '/dev/esp32-nonexistent', 'flash')

    def test_workspace_containment(self):
        with self.assertRaisesRegex(ValueError, 'inside'):
            self.command('--workspace', '/tmp', 'build')

    def test_pin_and_pull(self):
        cmd = self.command('pull')
        self.assertEqual(cmd[:2], ['docker', 'pull'])
        self.assertRegex(cmd[2], r'^espressif/idf:v6\.1@sha256:[a-f0-9]{64}$')


if __name__ == '__main__':
    unittest.main()
