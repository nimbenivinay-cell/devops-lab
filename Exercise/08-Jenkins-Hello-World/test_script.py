import os
import unittest
import subprocess

class HelloWorldScriptTestCase(unittest.TestCase):
    def test_sh_file_content(self):
        sh_path = os.path.join(os.path.dirname(__file__), "hello-world.sh")
        self.assertTrue(os.path.exists(sh_path), "hello-world.sh must exist")
        with open(sh_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("#!/bin/bash", content)
        self.assertIn('echo "Hello, Jenkins!"', content)

    def test_ps1_execution(self):
        ps1_path = os.path.join(os.path.dirname(__file__), "hello-world.ps1")
        self.assertTrue(os.path.exists(ps1_path), "hello-world.ps1 must exist")
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps1_path],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "Hello, Jenkins!")

if __name__ == '__main__':
    unittest.main()
