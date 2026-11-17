"""Apply recorded visual-review edits to COCO without changing first-pass files."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path


def apply_edits(source: dict, edits: dict) -> tuple[dict, list[dict]]:
    result = copy.deepcopy(source)
    images = {im['file_name']: im for im in result['images']}
    categories = {c['name']: c['id'] for c in result['categories']}
    next_id = max((a['id'] for a in result['annotations']), default=0) + 1
    log = []
    for name, actions in edits.items():
        im = images[name]
        for action in actions:
            op = action['operation']
            if op == 'add':
                annotation = {'id': next_id, 'image_id': im['id'],
                              'category_id': categories[action['class']], 'iscrowd': 0,
                              'segmentation': [], 'attributes': {'conf': '', 'can_review': False}}
                next_id += 1
                before = None
                result['annotations'].append(annotation)
            else:
                matches = [a for a in result['annotations'] if a['id'] == action['id'] and a['image_id'] == im['id']]
                if len(matches) != 1:
                    raise ValueError(f"{name}: annotation {action['id']} not unique or absent")
                annotation = matches[0]
                before = copy.deepcopy(annotation)
            if op == 'delete':
                result['annotations'].remove(annotation)
            elif op in ('add', 'update'):
                if 'class' in action:
                    annotation['category_id'] = categories[action['class']]
                if 'box' in action:
                    x1, y1, x2, y2 = action['box']
                    if not (0 <= x1 < x2 <= im['width'] and 0 <= y1 < y2 <= im['height']):
                        raise ValueError(f'{name}: invalid box {action["box"]}')
                    annotation['bbox'] = [x1, y1, x2-x1, y2-y1]
                    annotation['area'] = (x2-x1) * (y2-y1)
                    annotation['segmentation'] = []
                if 'can_review' in action:
                    annotation.setdefault('attributes', {})['can_review'] = action['can_review']
            else:
                raise ValueError(f'Unknown operation: {op}')
            log.append({'image': name, 'operation': op, 'reason': action['reason'],
                        'before': before, 'after': None if op == 'delete' else copy.deepcopy(annotation)})
    return result, log


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--edits', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--log', required=True, type=Path)
    args = parser.parse_args()
    raw = args.source.read_bytes()
    source = json.loads(raw.decode('utf-8-sig'))
    edits = json.loads(args.edits.read_text(encoding='utf-8-sig'))
    result, log = apply_edits(source, edits)
    result.setdefault('info', {})['description'] = 'Visual re-review; first-pass exports retained separately'
    for path, value in [(args.out, result), (args.log, {'source_sha256': hashlib.sha256(raw).hexdigest(), 'changes': log})]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'{len(log)} changes across {len(edits)} images; {len(result["annotations"])} annotations -> {args.out}')


if __name__ == '__main__':
    main()
