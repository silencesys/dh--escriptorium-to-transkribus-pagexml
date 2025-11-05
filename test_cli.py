import io
import os
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout

import convert_pagexml


SAMPLE_XML = '<?xml version="1.0"?>\n<PcGts xmlns="http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15">\n</PcGts>'


class TestCLI(unittest.TestCase):

    def test_welcome_message_shown_when_no_args(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            convert_pagexml.main([])
        out = buf.getvalue()
        self.assertIn('PAGE XML Converter', out)
        self.assertIn('Usage examples:', out)

    def test_single_file_auto_output(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            in_file = td_path / 'page1.xml'
            in_file.write_text(SAMPLE_XML, encoding='utf-8')

            # auto output via -o
            convert_pagexml.main(['-f', str(in_file), '-o'])

            out_file = td_path / 'page1_transkribus.xml'
            self.assertTrue(out_file.exists(), 'Auto-generated output file should exist')
            content = out_file.read_text(encoding='utf-8')
            self.assertIn('2013-07-15', content)

    def test_single_file_explicit_output_dir_creation(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            in_file = td_path / 'page2.xml'
            in_file.write_text(SAMPLE_XML, encoding='utf-8')

            out_dir = td_path / 'outdir'
            self.assertFalse(out_dir.exists())

            buf = io.StringIO()
            with redirect_stdout(buf):
                convert_pagexml.main(['-f', str(in_file), '-o', str(out_dir), '-v'])
            out = buf.getvalue()

            self.assertTrue(out_dir.exists(), 'Output directory should be created')
            out_file = out_dir / 'page2_transkribus.xml'
            self.assertTrue(out_file.exists(), 'Output file should be created inside output directory')
            self.assertTrue('Created output directory' in out or 'Using existing output directory' in out or 'no-extension heuristic' in out)

    def test_single_file_explicit_output_file(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            in_file = td_path / 'page3.xml'
            in_file.write_text(SAMPLE_XML, encoding='utf-8')

            explicit = td_path / 'myout.xml'
            convert_pagexml.main(['-f', str(in_file), '-o', str(explicit)])

            self.assertTrue(explicit.exists(), 'Explicit output file should be created')
            self.assertIn('2013-07-15', explicit.read_text(encoding='utf-8'))

    def test_directory_conversion_with_output_dir(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            input_dir = td_path / 'indir'
            input_dir.mkdir()
            for i in range(3):
                f = input_dir / f'p{i+1}.xml'
                f.write_text(SAMPLE_XML, encoding='utf-8')

            out_dir = td_path / 'outbatch'
            convert_pagexml.main(['-d', str(input_dir), '-o', str(out_dir)])

            self.assertTrue(out_dir.exists())
            files = list(out_dir.glob('*_transkribus.xml'))
            self.assertEqual(len(files), 3)
            for f in files:
                self.assertIn('2013-07-15', f.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
