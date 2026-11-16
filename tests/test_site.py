import importlib.util, json, tempfile, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('builder',Path(__file__).resolve().parents[1]/'scripts/build_site.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class SiteTests(unittest.TestCase):
 def release(self):return {'tag_name':'v1','html_url':builder.GITHUB+'/releases/tag/v1','assets':[{'name':'pkg-example.tar.catz','browser_download_url':builder.GITHUB+'/releases/download/v1/pkg-example.tar.catz','size':512,'digest':'sha256:abc'}]}
 def test_stable_only(self):
  release=self.release();draft={**release,'draft':True};preview={**release,'prerelease':True}
  result=builder.catalog([draft,preview,release]);self.assertEqual(len(result['releases']),1);self.assertEqual(len(result['packages']),1);self.assertFalse(result['remote_pkg_client_ready'])
 def test_foreign_asset_rejected(self):
  release=self.release();release['assets'][0]['browser_download_url']='https://example.com/unsigned'
  with self.assertRaises(ValueError):builder.catalog([release])
 def test_pages_and_catalogs(self):
  with tempfile.TemporaryDirectory() as directory:
   out=Path(directory)/'dist';builder.build([],out)
   for name in ['pkg','ports','cdn']:
    page=(out/name/'index.html').read_text();self.assertIn('No artifacts have been published',page);self.assertNotIn('A Unix',page);self.assertNotIn('{{',page);self.assertEqual(json.loads((out/name/'index.json').read_text())['artifacts'],[])
   self.assertIn('A Unix',(out/'index.html').read_text());self.assertNotIn('Native packages.',(out/'index.html').read_text())
 def test_escape_release_data(self):
  release=self.release();release['assets'][0]['name']='pkg-<script>alert(1)</script>'
  with tempfile.TemporaryDirectory() as directory:
   out=Path(directory)/'dist';builder.build([release],out);page=(out/'pkg/index.html').read_text();self.assertNotIn('<script>',page);self.assertIn('&lt;script&gt;',page)
if __name__=='__main__':unittest.main()
