import importlib.util
import ipaddress
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('privacy_scan',ROOT/'privacy_scan.py')
privacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(privacy)


class PrivacyChecks(unittest.TestCase):
    def scan(self,text):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'example.txt').write_text(text)
            return privacy.scan(root)

    def test_generator_version_is_not_a_network_address(self):
        version='.'.join(('155','0','0','0'))
        self.assertEqual(self.scan('Creator: HeadlessChrome/'+version),[])

    def test_address_in_metadata_is_still_detected(self):
        address=str(ipaddress.IPv4Address(2130706433))
        self.assertTrue(any(r['kind']=='literal-ip-address' for r in self.scan('Server: '+address)))

    def test_example_contact_does_not_hide_personal_contact(self):
        self.assertEqual(self.scan('contact@example.invalid'),[])
        address='person'+'@'+'private-domain'+'.test'
        self.assertTrue(any(r['kind']=='non-example-email' for r in self.scan(address)))


if __name__=='__main__':unittest.main()
