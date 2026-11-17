"""Tính số liệu QC từ phiếu kiểm và GỢI Ý quyết định Hold / Rework / Release.

    python scripts/qc_report.py [--guideline-gap N] [--data-problem N]

--guideline-gap N : số ca bạn thấy guideline CHƯA có quy tắc (chưa chốt)  -> N > 0 gợi ý HOLD
--data-problem  N : số ảnh hỏng/mờ không dùng được                       -> N > 0 gợi ý HOLD
Đọc: qc_sample.csv, qc_review.csv, và (nếu có) review_stats.json, self_check.json. Ghi submission/qc/qc_report_auto.md.
Phần QC trong REPORT.md (mục 7) do BẠN viết (script không ghi file đó).
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from common import SUB, die, load_taxonomy, read_csv, rel

VALID = ["khong", "bo_sot", "thua", "sai_lop", "sai_vi_tri_kich_thuoc", "sai_thuoc_tinh", "sai_mask"]


def pc(a, b):
    return "n/a" if not b else f"{a}/{b} = {a / b * 100:.1f}%"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--guideline-gap", type=int, default=0)
    ap.add_argument("--data-problem", type=int, default=0)
    ap.add_argument("--sample", type=Path, default=SUB / "qc" / "qc_sample.csv")
    ap.add_argument("--review", type=Path, default=SUB / "qc" / "qc_review.csv")
    ap.add_argument("--stats", type=Path, default=SUB / "qc" / "review_stats.json")
    ap.add_argument("--out", type=Path, default=SUB / "qc" / "qc_report_auto.md")
    ap.add_argument("--profile-label", default="Máy", help="tên nguồn nhãn nền trong bảng trạng thái")
    args = ap.parse_args()
    tax = load_taxonomy()
    r = tax.rules
    qc = SUB / "qc"
    for f in (args.sample, args.review, args.stats):
        if not f.exists():
            die(f"Thiếu {rel(f)}. Cần đủ mẫu QC, phiếu kiểm và số đo bẫy.")
    sample, review = read_csv(args.sample), read_csv(args.review)
    rs = json.loads(args.stats.read_text(encoding="utf-8-sig"))
    sc = json.loads((qc / "self_check.json").read_text(encoding="utf-8-sig")) if (qc / "self_check.json").exists() else None

    imgs = [s["image"] for s in sample]
    n_img, n_obj = len(imgs), sum(int(s["so_doi_tuong"]) for s in sample)
    warns, checked, err_rows = [], set(), []
    for i, row in enumerate(review, 2):
        img, et = (row.get("image") or "").strip(), (row.get("error_type") or "").strip().lower()
        if img not in imgs:
            warns.append(f"Dòng {i}: ảnh '{img}' không nằm trong mẫu (bỏ qua).")
            continue
        if not et:
            continue
        if et not in VALID:
            warns.append(f"Dòng {i}: error_type '{et}' sai (chỉ nhận {', '.join(VALID)}) - bỏ qua.")
            continue
        checked.add(img)
        if et != "khong":
            err_rows.append((img, (row.get("object_id") or "").strip() or f"(dòng {i})", et))
    unchecked = [i for i in imgs if i not in checked]
    if unchecked:
        warns.append(f"{len(unchecked)} ảnh trong mẫu CHƯA kiểm: {', '.join(unchecked[:8])}")
    err_objs, err_imgs = {(i, o) for i, o, _ in err_rows}, {i for i, _, _ in err_rows}
    types = Counter(t for _, _, t in err_rows)
    ex = defaultdict(list)
    for i, _, t in err_rows:
        if i not in ex[t]:
            ex[t].append(i)
    n_err = len(err_rows)
    rate_img = len(err_imgs) / n_img if n_img else None
    top3 = types.most_common(3)
    systematic = bool(top3 and n_err >= 3 and top3[0][1] >= 3 and top3[0][1] / n_err >= 0.5)

    rw, notes = [], []
    if not n_img or unchecked or warns or len(set(imgs)) != n_img:
        rw.append("phiếu QC trống, chưa kiểm đủ, có dòng không hợp lệ hoặc mẫu trùng ảnh")
    if not rs.get("traps") or not rs["traps"].get("n") or rs["traps"].get("rate") is None:
        rw.append("chưa có phép đo bẫy hợp lệ")
    if rate_img is not None and rate_img > r["error_rate_img_max"]:
        rw.append(f"ảnh có lỗi {rate_img * 100:.1f}% > {r['error_rate_img_max'] * 100:.0f}%")
    if systematic:
        rw.append(f"lỗi hệ thống: '{top3[0][0]}' chiếm {top3[0][1]}/{n_err} lỗi")
    if rs and rs.get("traps") and rs["traps"]["rate"] is not None and rs["traps"]["rate"] < r["trap_catch_min"]:
        rw.append(f"bắt bẫy {rs['traps']['rate'] * 100:.0f}% < {r['trap_catch_min'] * 100:.0f}% -> lô duyệt chưa đáng tin")
    if sc and not sc.get("pass"):
        rw.append("độ nhất quán (gán lại mù) dưới ngưỡng")
    if args.guideline_gap > 0 or args.data_problem > 0:
        decision = "HOLD"
        reasons = [f"guideline chưa rõ ({args.guideline_gap} ca) / dữ liệu có vấn đề ({args.data_problem} ảnh) -> giữ lại làm rõ"]
    else:
        decision = "REWORK" if rw else "RELEASE"
        reasons = rw or [f"ảnh lỗi {0 if rate_img is None else rate_img * 100:.1f}% <= {r['error_rate_img_max'] * 100:.0f}%, "
                         "không lỗi hệ thống, bắt bẫy / nhất quán đạt (nếu đã đo)"]
    if unchecked:
        reasons.append("LƯU Ý: còn ảnh mẫu chưa kiểm -> kết luận chưa đáng tin")
    if n_img:
        k_, n_ = len(err_imgs), n_img
        z = 1.96
        ph = k_ / n_
        up = (ph + z * z / (2 * n_) + z * math.sqrt(ph * (1 - ph) / n_ + z * z / (4 * n_ * n_))) / (1 + z * z / n_)
        notes.append(f"{k_} ảnh lỗi trong {n_} ảnh mẫu: cận trên 95% (Wilson) của tỉ lệ ảnh lỗi thật là **{up * 100:.0f}%**. "
                     f"Ngưỡng {r['error_rate_img_max'] * 100:.0f}% không thể được **chứng minh** bằng mẫu nhỏ như vậy: hãy nói rõ giới hạn này trong báo cáo.")

    L = ["# Báo cáo QC tự động (nháp)", "", "> **Gợi ý** do script tính từ phiếu kiểm; không tự xác minh độ đúng của nhãn hay tính độc lập của người kiểm.", "",
         "## Mẫu", f"- {n_img} ảnh ({sum(1 for s in sample if s['la_ca_kho'] == 'yes')} ca khó + "
         f"{sum(1 for s in sample if s['la_ca_kho'] != 'yes')} ngẫu nhiên), {n_obj} đối tượng.", f"- taxonomy {tax.version}", "",
         "## Số đo", "| Chỉ số | Giá trị | Mẫu số |", "|---|---|---|",
         f"| Lỗi **theo đối tượng** | {pc(len(err_objs), n_obj)} | {n_obj} đối tượng trong mẫu |",
         f"| **Ảnh có lỗi** (dùng cho ngưỡng) | {pc(len(err_imgs), n_img)} | {n_img} ảnh trong mẫu |"]
    if rs:
        L.append(f"| {args.profile_label}: accepted / edited / deleted | {pc(rs['accepted'], rs['pre_boxes'])} / {pc(rs['edited'], rs['pre_boxes'])} / {pc(rs['deleted'], rs['pre_boxes'])} | {rs['pre_boxes']} box nguồn |")
        L.append(f"| {args.profile_label}: added | {pc(rs['added'], rs['final_objects'])} | {rs['final_objects']} đối tượng sau duyệt |")
        if rs.get("traps"):
            t = rs["traps"]
            L.append(f"| Bắt lỗi bẫy | {pc(t['caught'], t['n'])} | {t['n']} bẫy |")
    if sc:
        L.append(f"| Nhất quán gán lại mù: IoU TB / cùng lớp | {'n/a' if sc['mean_iou'] is None else '%.3f' % sc['mean_iou']} / "
                 f"{'n/a' if sc['class_agreement'] is None else '%.1f%%' % (sc['class_agreement'] * 100)} | {sc['pairs']} cặp box |")
    L += ["", "## Top 3 loại lỗi"]
    if top3:
        L += ["| Loại lỗi | Số lỗi | Ảnh ví dụ |", "|---|---|---|"] + [f"| {t} | {c} | {', '.join(ex[t][:3])} |" for t, c in top3]
    else:
        L.append("(không ghi nhận lỗi nào)")
    if systematic:
        L.append(f"\n**Lỗi hệ thống**: '{top3[0][0]}' lặp lại -> sửa quy tắc / recipe, không chỉ sửa từng ảnh.")
    if warns:
        L += ["", "## Cảnh báo"] + [f"- {w}" for w in warns]
    if notes:
        L += ["", "## Giới hạn thống kê"] + [f"- {x}" for x in notes]
    L += ["", "## Gợi ý quyết định", f"**{decision}**", ""] + [f"- {x}" for x in reasons]
    L += ["", "Cây quyết định: Hold (guideline chưa rõ / dữ liệu hỏng) -> Rework (> ngưỡng, lỗi lặp, bắt bẫy / nhất quán thấp) -> Release."]
    text = "\n".join(L) + "\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf8")
    print(text)
    print(f"Đã ghi {rel(args.out)}. Hãy tự viết REPORT.md mục 7 dựa trên số liệu này.")


if __name__ == "__main__":
    main()
