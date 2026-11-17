from __future__ import annotations

import copy
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from apply_label_edits import apply_edits


class RecordedEditsTest(unittest.TestCase):
    def setUp(self):
        self.source = {'images': [{'id': 1, 'file_name': 'one.jpg', 'width': 100, 'height': 100}],
                       'categories': [{'id': 1, 'name': 'person'}, {'id': 2, 'name': 'car'}],
                       'annotations': [{'id': 7, 'image_id': 1, 'category_id': 1, 'bbox': [10, 10, 30, 40],
                                        'attributes': {'conf': '0.8', 'can_review': True}, 'segmentation': []}]}

    def test_update_retains_source_and_confidence(self):
        before = copy.deepcopy(self.source)
        result, log = apply_edits(self.source, {'one.jpg': [
            {'operation': 'update', 'id': 7, 'class': 'car', 'box': [12, 15, 45, 65], 'reason': 'review'}]})
        self.assertEqual(before, self.source)
        self.assertEqual(result['annotations'][0]['attributes'], before['annotations'][0]['attributes'])
        self.assertEqual(result['annotations'][0]['bbox'], [12, 15, 33, 50])
        self.assertEqual(log[0]['before'], before['annotations'][0])

    def test_add_and_delete_do_not_reuse_ids(self):
        result, _ = apply_edits(self.source, {'one.jpg': [
            {'operation': 'delete', 'id': 7, 'reason': 'false positive'},
            {'operation': 'add', 'class': 'person', 'box': [20, 20, 50, 80], 'reason': 'missing'}]})
        self.assertEqual([a['id'] for a in result['annotations']], [8])
        self.assertEqual(result['annotations'][0]['attributes']['conf'], '')

    def test_invalid_target_and_geometry_are_rejected(self):
        for action in [dict(operation='delete', id=99, reason='invalid'),
                       dict(operation='update', id=7, box=[0, 0, 101, 20], reason='outside')]:
            with self.assertRaises(ValueError):
                apply_edits(self.source, {'one.jpg': [action]})


class QCGateTest(unittest.TestCase):
    def test_incomplete_qc_cannot_release(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            with (p/'sample.csv').open('w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows([['image','la_ca_kho','so_doi_tuong'], ['one.jpg','no',1]])
            (p/'review.csv').write_text('image,object_id,error_type,reviewer,note\none.jpg,,,,\n', encoding='utf-8')
            stats = {'accepted': 1, 'pre_boxes': 1, 'edited': 0, 'deleted': 0, 'added': 0, 'final_objects': 1,
                     'traps': {'n': 12, 'caught': 12, 'rate': 1}}
            (p/'stats.json').write_text(json.dumps(stats), encoding='utf-8')
            proc = subprocess.run([sys.executable, str(ROOT/'scripts/qc_report.py'),
                                   '--sample', str(p/'sample.csv'), '--review', str(p/'review.csv'),
                                   '--stats', str(p/'stats.json'), '--out', str(p/'out.md')],
                                  cwd=ROOT, capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn('**REWORK**', (p/'out.md').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
