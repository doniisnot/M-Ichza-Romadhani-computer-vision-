import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Guppy Fish Detector", page_icon="🐟", layout="wide")
st.title("🐟 Guppy Fish Detector")
st.caption("Versi offline sederhana — tanpa API Key, akun Roboflow, atau dataset tambahan.")

st.info(
    "Aplikasi ini menggunakan pemrosesan gambar OpenCV untuk mencari objek berbentuk ikan. "
    "Ini bukan model AI yang dilatih khusus untuk guppy, jadi hasilnya perkiraan dan bisa keliru."
)

uploaded = st.file_uploader("Pilih gambar ikan guppy", type=["jpg", "jpeg", "png", "bmp", "webp"])

def detect_candidates(pil_img):
    rgb = np.array(pil_img.convert("RGB"))
    h, w = rgb.shape[:2]
    # Resize only for processing, preserving the original for output
    scale = min(1.0, 1000 / max(h, w))
    proc = cv2.resize(rgb, (int(w * scale), int(h * scale))) if scale < 1 else rgb.copy()
    ph, pw = proc.shape[:2]
    blurred = cv2.GaussianBlur(proc, (5, 5), 0)
    lab = cv2.cvtColor(blurred, cv2.COLOR_RGB2LAB)
    # Segment areas that differ from the local background using edges and saturation
    hsv = cv2.cvtColor(blurred, cv2.COLOR_RGB2HSV)
    sat = hsv[:, :, 1]
    edges = cv2.Canny(cv2.cvtColor(blurred, cv2.COLOR_RGB2GRAY), 35, 110)
    # Morphological processing joins body/tail edges without requiring a trained dataset
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    edge_regions = cv2.dilate(edges, kernel, iterations=2)
    color_regions = cv2.threshold(sat, 35, 255, cv2.THRESH_BINARY)[1]
    mask = cv2.bitwise_or(edge_regions, color_regions)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8), iterations=1)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []
    image_area = ph * pw
    for c in contours:
        area = cv2.contourArea(c)
        if area < max(180, image_area * 0.001) or area > image_area * 0.35:
            continue
        x, y, bw, bh = cv2.boundingRect(c)
        if bw < 18 or bh < 12:
            continue
        aspect = max(bw, bh) / max(1, min(bw, bh))
        # Prefer elongated, medium-sized regions, a rough visual heuristic only
        if aspect < 1.25:
            continue
        rect_area = bw * bh
        fill = area / max(1, rect_area)
        if fill < 0.12:
            continue
        score = min(0.95, 0.35 + min(aspect, 4.0) * 0.10 + min(fill, 0.8) * 0.20)
        candidates.append((score, x, y, bw, bh))
    candidates.sort(reverse=True)
    # Limit excessive noise and map coordinates to original image
    out = pil_img.convert("RGB").copy()
    draw = ImageDraw.Draw(out)
    boxes = []
    inv = 1 / scale
    for score, x, y, bw, bh in candidates[:30]:
        box = tuple(int(v * inv) for v in (x, y, x + bw, y + bh))
        draw.rectangle(box, outline=(0, 220, 80), width=max(3, out.width // 300))
        label = f"Calon objek {score:.0%}"
        tx, ty = box[0], max(0, box[1] - 24)
        draw.rectangle((tx, ty, tx + 150, ty + 22), fill=(0, 120, 55))
        draw.text((tx + 5, ty + 3), label, fill="white")
        boxes.append({"score": score, "box": box})
    return out, boxes

if uploaded:
    try:
        image = Image.open(uploaded).convert("RGB")
        left, right = st.columns(2)
        with left:
            st.subheader("Gambar asli")
            st.image(image, use_container_width=True)
        with st.spinner("Menganalisis gambar..."):
            result, boxes = detect_candidates(image)
        with right:
            st.subheader("Hasil analisis")
            st.image(result, use_container_width=True)
        if boxes:
            st.success(f"Ditemukan {len(boxes)} kandidat objek berbentuk memanjang.")
            st.write("Kotak hijau adalah perkiraan area objek, bukan kepastian bahwa objek tersebut ikan guppy.")
        else:
            st.warning("Belum ada objek yang cocok dengan aturan sederhana. Coba gambar yang lebih jelas, dengan ikan terlihat utuh dan latar belakang tidak terlalu ramai.")
        st.caption("Catatan: untuk deteksi guppy yang akurat, dibutuhkan model deteksi ikan yang sudah dilatih. Versi ini dibuat agar bisa langsung dicoba tanpa API atau dataset.")
    except Exception as e:
        st.error(f"Gagal membaca gambar: {e}")
else:
    st.markdown("### Cara menggunakan")
    st.write("1. Klik **Browse files**.")
    st.write("2. Pilih gambar guppy dari komputer.")
    st.write("3. Lihat hasil dengan kotak hijau.")
    st.write("Tidak perlu API Key, dataset, akun, atau koneksi internet setelah dependensi terpasang.")
