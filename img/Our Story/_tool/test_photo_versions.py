"""Regression checks for stale website images after photo-manager saves."""

from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

import gallery_data as G
import save_engine as S


HTML = '''
const COUNTRIES = [{name: "Example", nameEs: "Ejemplo", images: ["Example.jpg","Example2.jpg"]}];
const STATES = [{name: "Example", nameEs: "Ejemplo", filePrefix: "Example", images: ["Example.jpg","Example2.jpg"]}];
const MEXICO_TRIPS = [{name: "Trip 1", nameEs: "Viaje 1", filePrefix: "trip1", images: ["trip1.jpg","trip1_2.jpg"]}];
'''


class PhotoVersionTests(unittest.TestCase):
    def fixture(self, root, folder):
        entry = G.parse_our_story(HTML)[folder][0]
        for base in ('img', 'img_backup'):
            directory = root / base / 'Our Story' / folder
            directory.mkdir(parents=True)
            for i, name in enumerate(entry['images']):
                (directory / name).write_bytes(('photo-%d' % i).encode())
        html = S.refresh_photo_version(str(root), HTML, folder, entry['name'])
        (root / 'our-story.html').write_text(html, encoding='utf-8')
        return entry, html

    def version(self, html, folder):
        entry = G.parse_our_story(html)[folder][0]
        start, end = entry['obj_span']
        return re.search(r'photoVersion: "([a-f0-9]+)"', html[start:end]).group(1)

    def test_reorder_changes_version_even_when_numbered_array_is_unchanged(self):
        for folder in G.GALLERY_BY_FOLDER:
            with self.subTest(folder=folder), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                entry, before = self.fixture(root, folder)
                items = [{'kind': 'existing', 'file': n} for n in reversed(entry['images'])]
                plan = S.compute_plan(tmp, folder, entry, items, {})
                self.assertFalse(plan['arrayChanged'])
                S.apply_plan(tmp, plan, {})
                after = (root / 'our-story.html').read_text(encoding='utf-8')
                self.assertNotEqual(self.version(before, folder), self.version(after, folder))
                for base in ('img', 'img_backup'):
                    directory = root / base / 'Our Story' / folder
                    self.assertEqual((directory / entry['images'][0]).read_bytes(), b'photo-1')
                    self.assertEqual((directory / entry['images'][1]).read_bytes(), b'photo-0')
                self.assertEqual(after, S.refresh_photo_version(tmp, after, folder, entry['name']))

    def test_crop_at_same_filename_changes_version_and_preserves_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry, before = self.fixture(root, 'States')
            items = [{'kind': 'existing', 'file': n} for n in entry['images']]
            items[0]['replace'] = 'crop'
            plan = S.compute_plan(tmp, 'States', entry, items, {'crop': {'bytes': 7}})
            S.apply_plan(tmp, plan, {'crop': (b'cropped', b'')})
            after = (root / 'our-story.html').read_text(encoding='utf-8')
            self.assertNotEqual(self.version(before, 'States'), self.version(after, 'States'))
            self.assertEqual((root / 'img_backup/Our Story/States/Example.jpg').read_bytes(), b'photo-0')

    def test_version_failure_rolls_back_photo_and_original_reordering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry, before = self.fixture(root, 'States')
            items = [{'kind': 'existing', 'file': n} for n in reversed(entry['images'])]
            plan = S.compute_plan(tmp, 'States', entry, items, {})
            with patch.object(S, 'refresh_photo_version', side_effect=OSError('read failed')):
                with self.assertRaises(S.SaveError):
                    S.apply_plan(tmp, plan, {})
            self.assertEqual((root / 'our-story.html').read_text(encoding='utf-8'), before)
            for base in ('img', 'img_backup'):
                self.assertEqual((root / base / 'Our Story/States/Example.jpg').read_bytes(), b'photo-0')


if __name__ == '__main__':
    unittest.main()
