#!/usr/bin/env python3
"""
Pull the individual acrylic layers out of a "stacking" video.

The video should show the sheets being laid one by one into the same mat,
filmed from above. Three steps:

  1. scan    contact sheet of the whole video (1 frame/s, with timestamps)
  2. frames  extract a time range at 10 fps, straighten every frame to the mat,
             and print a sheet with frame numbers so you can pick one per state
  3. split   given one frame per state (bottom layer first), cut out what each
             new sheet adds and save it as a transparent PNG

  python3 extract_layers.py scan   VIDEO OUT
  python3 extract_layers.py frames VIDEO OUT --start 34 --end 45
  python3 extract_layers.py split  OUT --states 12,25,41,60

Needs ffmpeg, numpy and opencv-python-headless.
"""
import argparse, glob, os, subprocess, json
import numpy as np, cv2

W = 1200  # straightened mat size in px


def run(*a):
    subprocess.run(a, check=True)


def scan(video, out):
    os.makedirs(out, exist_ok=True)
    run("ffmpeg", "-v", "error", "-y", "-i", video, "-vf",
        "fps=1,scale=150:-1,drawtext=text='%{pts\\:hms}':x=3:y=3:fontsize=13:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=12x8",
        "-frames:v", "1", f"{out}/scan.jpg")
    print(f"{out}/scan.jpg")


def order(p):
    s, d = p.sum(1), np.diff(p, axis=1).ravel()
    return np.array([p[s.argmin()], p[d.argmin()], p[s.argmax()], p[d.argmax()]], np.float32)


def window_quad(img):
    """Corners of the opening in the white mat (the art window). Hands can cover the mat's
    outer edge, but the opening itself stays visible."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mat = ((hsv[:, :, 2] > 160) & (hsv[:, :, 1] < 60)).astype(np.uint8) * 255
    mat = cv2.morphologyEx(mat, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    cs, hier = cv2.findContours(mat, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hier is None:
        return None, 0
    H, Wd = img.shape[:2]
    best = None
    for i, c in enumerate(cs):
        if hier[0][i][3] < 0:          # want holes (contours with a parent)
            continue
        area = cv2.contourArea(c)
        if area < H * Wd * .06:
            continue
        hull = cv2.convexHull(c)
        q = None
        for eps in np.linspace(.01, .08, 30):
            a = cv2.approxPolyDP(hull, eps * cv2.arcLength(hull, True), True)
            if len(a) == 4:
                q = a
                break
        if q is None:
            continue
        # a real window is nearly square and nearly fills its hull
        rect = cv2.minAreaRect(q)
        ratio = min(rect[1]) / max(rect[1]) if max(rect[1]) else 0
        if ratio < .8:
            continue
        if best is None or area > best[1]:
            best = (order(q.reshape(4, 2).astype(np.float32)), area)
    return best if best else (None, 0)


def frames(video, out, start, end):
    raw, warped = f"{out}/raw", f"{out}/warped"
    for d in (raw, warped):
        os.makedirs(d, exist_ok=True)
        for f in glob.glob(f"{d}/*"):
            os.remove(f)
    run("ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(end - start), "-i", video,
        "-vf", "fps=10", "-q:v", "2", f"{raw}/%03d.jpg")
    M0 = W * .06   # keep a strip of mat around the window
    dst = np.float32([[M0, M0], [W - M0, M0], [W - M0, W - M0], [M0, W - M0]])
    stats = {}
    for f in sorted(glob.glob(f"{raw}/*.jpg")):
        n = int(os.path.basename(f)[:3])
        img = cv2.imread(f)
        q, area = window_quad(img)
        if q is None:
            continue
        w = cv2.warpPerspective(img, cv2.getPerspectiveTransform(q, dst), (W, W), flags=cv2.INTER_CUBIC)
        g = cv2.cvtColor(w, cv2.COLOR_BGR2GRAY)
        inner = g[int(W * .1):-int(W * .1), int(W * .1):-int(W * .1)]
        stats[n] = dict(sharp=float(cv2.Laplacian(inner, cv2.CV_64F).var()),
                        bright=float((inner > 80).mean()))
        cv2.imwrite(f"{warped}/{n:03d}.jpg", w, [cv2.IMWRITE_JPEG_QUALITY, 93])
    json.dump(stats, open(f"{out}/stats.json", "w"), indent=1)
    # contact sheet with frame number, coverage and sharpness
    tiles = []
    for n, s in stats.items():
        t = cv2.resize(cv2.imread(f"{warped}/{n:03d}.jpg"), (160, 160))
        cv2.putText(t, f"{n} {s['bright']*100:.0f}% {s['sharp']:.0f}", (4, 14), cv2.FONT_HERSHEY_SIMPLEX, .42, (0, 255, 255), 1)
        tiles.append(t)
    cols = 12
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    sheet = np.vstack([np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)])
    cv2.imwrite(f"{out}/frames.jpg", sheet)
    print(f"{out}/frames.jpg  ({len(stats)} usable frames)")


def align(src, ref, box):
    """Fine-align src to ref with a homography, matching only the mat/window border (the artwork changes between states)."""
    x, y, w, h = box
    band = np.zeros((W, W), np.uint8)
    cv2.rectangle(band, (x - 40, y - 40), (x + w + 40, y + h + 40), 255, -1)
    cv2.rectangle(band, (x + 20, y + 20), (x + w - 20, y + h - 20), 0, -1)
    k = 2
    prep = lambda im: cv2.GaussianBlur(cv2.resize(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), (W // k, W // k)), (0, 0), 2).astype(np.float32)
    s, r, mk = prep(src), prep(ref), cv2.resize(band, (W // k, W // k))
    H = np.eye(2, 3, dtype=np.float32)
    try:
        _, H = cv2.findTransformECC(r, s, H, cv2.MOTION_EUCLIDEAN,
                                    (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 400, 1e-7), mk, 5)
    except cv2.error:
        return src
    H[:, 2] *= k
    if abs(H[0, 2]) > 25 or abs(H[1, 2]) > 25:   # implausible jump: keep the window-based warp
        return src
    return cv2.warpAffine(src, H, (W, W), flags=cv2.INTER_CUBIC + cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)


def split(out, states, size=1000, lift=28):
    lay = f"{out}/layers"
    os.makedirs(lay, exist_ok=True)
    for f in glob.glob(f"{lay}/*"):
        os.remove(f)
    imgs = [cv2.imread(f"{out}/warped/{n:03d}.jpg") for n in states]
    ref = imgs[-1]
    M0 = int(W * .06)
    box = (M0, M0, W - 2 * M0, W - 2 * M0)
    # the window-based warp is already accurate; no extra alignment
    pad = 6
    crop = lambda im: cv2.resize(im[M0 + pad:W - M0 - pad, M0 + pad:W - M0 - pad], (size, size), interpolation=cv2.INTER_CUBIC)
    imgs = [crop(i) for i in imgs]
    gray = lambda im: cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), (0, 0), 3).astype(np.float32)
    # levels: video blacks are often lifted; stretch so the bare acrylic reads as black
    lo, hi = np.percentile(imgs[-1], 3), np.percentile(imgs[-1], 99.7)
    imgs = [np.clip((im.astype(np.float32) - lo) * (255 / max(1, hi - lo)), 0, 255).astype(np.uint8) for im in imgs]
    final = imgs[-1]
    bg = np.percentile(gray(final), 8)
    # covered[k] = area scratched once the first k+1 sheets are stacked (solid regions, cumulative)
    covered, acc = [], np.zeros((size, size), np.uint8)
    for im in imgs:
        mk = (gray(im) > bg + lift).astype(np.uint8) * 255
        mk = cv2.morphologyEx(mk, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))
        mk = cv2.morphologyEx(mk, cv2.MORPH_OPEN, np.ones((15, 15), np.uint8))
        acc = cv2.bitwise_or(acc, mk)
        covered.append(acc.copy())
    # each pixel belongs to the first sheet that covers it; anything left goes to the top sheet
    art = covered[-1] > 0                       # scratched anywhere in the finished piece
    label = np.full((size, size), len(imgs) - 1, np.uint8)
    for k in range(len(imgs) - 1, -1, -1):
        label[(covered[k] > 0) & art] = k
    label[~art] = 0                             # bare black belongs to the back panel
    # bare black connected to the outside belongs to the back panel; enclosed dark (pupils, nose) stays
    b = size // 40
    dark = (gray(final) < bg + lift).astype(np.uint8)
    dark[:b], dark[-b:], dark[:, :b], dark[:, -b:] = 1, 1, 1, 1   # the window edge counts as outside
    n, lab, stt, _ = cv2.connectedComponentsWithStats(dark)
    outside = lab == lab[0, 0]
    label[outside] = 0
    label[:b], label[-b:], label[:, :b], label[:, -b:] = 0, 0, 0, 0
    label = cv2.medianBlur(label, 21)
    # a dark patch on a clear sheet is just untouched acrylic: hand it back to the black sheet
    g = gray(final)
    for k in range(1, len(imgs)):
        n, lab, stt, _ = cv2.connectedComponentsWithStats((label == k).astype(np.uint8))
        for j in range(1, n):
            comp = lab == j
            if stt[j, cv2.CC_STAT_AREA] < 800 or np.median(g[comp]) < bg + lift * 1.3:
                label[comp] = 0
    meta = []
    for k in range(len(imgs)):
        region = (label == k).astype(np.uint8)
        if k < len(imgs) - 1:   # tuck each sheet slightly under the next one so no seams show
            grown = cv2.dilate(region, np.ones((13, 13), np.uint8))
            # grow only under higher sheets (they cover it); never over bare black or lower sheets
            region = region | (grown & (label > k)).astype(np.uint8) if k else region
        a = cv2.GaussianBlur(region.astype(np.float32) * 255, (0, 0), 3)
        if k == 0:  # bottom sheet is black acrylic: keep it opaque
            img = (final * (a[..., None] / 255) + 6 * (1 - a[..., None] / 255)).astype(np.uint8)
            cv2.imwrite(f"{lay}/1.jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])
            meta.append("1.jpg")
        else:
            cv2.imwrite(f"{lay}/{k + 1}.png", np.dstack([final, a.clip(0, 255).astype(np.uint8)]))
            meta.append(f"{k + 1}.png")
    cv2.imwrite(f"{lay}/full.jpg", imgs[-1], [cv2.IMWRITE_JPEG_QUALITY, 90])
    ii = np.indices((size, size))
    chk = np.dstack([(((ii[0] // 40) + (ii[1] // 40)) % 2 * 40 + 60).astype(np.uint8)] * 3)
    tiles = []
    for f in meta + ["full.jpg"]:
        im = cv2.imread(f"{lay}/{f}", cv2.IMREAD_UNCHANGED)
        if im.shape[2] == 4:
            al = im[:, :, 3:4] / 255
            im = (im[:, :, :3] * al + chk * (1 - al)).astype(np.uint8)
        tiles.append(cv2.resize(im, (320, 320)))
    cv2.imwrite(f"{out}/layers.jpg", np.hstack(tiles))
    json.dump(dict(states=states, layers=meta), open(f"{lay}/layers.json", "w"))
    print(f"{out}/layers.jpg", meta)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["scan", "frames", "split"])
    ap.add_argument("a")
    ap.add_argument("b", nargs="?")
    ap.add_argument("--start", type=float)
    ap.add_argument("--end", type=float)
    ap.add_argument("--states")
    ap.add_argument("--lift", type=float, default=28, help="how much brighter than bare black counts as scratched")
    o = ap.parse_args()
    if o.cmd == "scan":
        scan(o.a, o.b)
    elif o.cmd == "frames":
        frames(o.a, o.b, o.start, o.end)
    else:
        split(o.a, [int(x) for x in o.states.split(",")], lift=o.lift)
