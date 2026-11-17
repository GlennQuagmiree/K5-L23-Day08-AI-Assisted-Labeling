"""Reconstruct recorded review outputs; --check verifies without writing."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from apply_label_edits import apply_edits
from common import SUB, box_iou, load_coco, xywh_to_xyxy


def read(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def replay(source: Path, edits: Path):
    result, _ = apply_edits(read(source), read(edits))
    result.setdefault('info', {})['description'] = 'Visual re-review; first-pass exports retained separately'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    rework, recheck = SUB/'qc/rework', SUB/'qc/recheck'
    outputs = {
        SUB/'labels/batch_reworked.json': replay(rework/'baseline.coco.json', rework/'edits.json'),
        recheck/'reviewed_blind.coco.json': replay(recheck/'pre_traps.coco.json', recheck/'edits_blind.json'),
    }
    for path, expected in outputs.items():
        if args.check:
            if read(path) != expected:
                raise ValueError(f'Recorded edits do not reproduce {path}')
        else:
            path.write_text(json.dumps(expected, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    final = replay(recheck/'reviewed_blind.coco.json', recheck/'edits_after_grading.json')
    # Trap injection resets review flags. Restore only flags from geometrically matching prior objects.
    prior = load_coco(SUB/'labels/batch_reworked.json')
    names = {im['id']: im['file_name'] for im in final['images']}
    classes = {c['id']: c['name'] for c in final['categories']}
    for a in final['annotations']:
        objects = prior.objects[names[a['image_id']]]
        if any(o.cls == classes[a['category_id']] and box_iou(o.box, xywh_to_xyxy(a['bbox'])) >= .5
               and str(o.attrs.get('can_review', '')).lower() in ('true', '1', 'yes') for o in objects):
            a.setdefault('attributes', {})['can_review'] = True
    for path in [SUB/'labels/batch_rechecked.json', SUB/'labels/qc_fixed.json']:
        if args.check:
            if read(path) != final:
                raise ValueError(f'Recorded edits do not reproduce {path}')
        else:
            path.write_text(json.dumps(final, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    protocol = read(recheck/'protocol.json')
    for path, key in [(recheck/'reviewed_blind.coco.json', 'reviewed_sha256'),
                      (SUB/'release/final_det.coco.json', 'release_sha256'),
                      (recheck/'qc_review.csv', 'qc_review_sha256')]:
        if hashlib.sha256(path.read_bytes()).hexdigest() != protocol[key]:
            raise ValueError(f'Frozen checksum mismatch: {path}')
    print('Recorded edits reproduced; frozen review, QC and release checksums match.')


if __name__ == '__main__':
    main()
