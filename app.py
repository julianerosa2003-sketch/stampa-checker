import streamlit as st
import numpy as np
from PIL import Image
from scipy import ndimage
from io import BytesIO
import base64
import os

# ── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stampa Checker",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS customizado ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Reset geral */
    .block-container { padding: 1rem 2rem !important; max-width: 1200px; }
    header[data-testid="stHeader"] { background: transparent; }
    .stApp { background: #f0f4f8; }

    /* Esconder menu e footer padrão */
    #MainMenu, footer, .stDeployButton { display: none !important; }

    /* Header customizado */
    .app-header {
        background: linear-gradient(135deg, #1a365d 0%, #2d5a87 100%);
        padding: 1rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .app-header h1 {
        color: white;
        font-size: 1.6rem;
        margin: 0;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .app-header .subtitle {
        color: #a0c4e8;
        font-size: 0.85rem;
        margin: 0;
    }

    /* Cards */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    .card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #1a365d;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Métricas */
    .metric-row {
        display: flex;
        align-items: center;
        padding: 0.6rem 0;
        border-bottom: 1px solid #f0f4f8;
    }
    .metric-row:last-child { border-bottom: none; }
    .metric-icon {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        margin-right: 0.75rem;
        flex-shrink: 0;
    }
    .metric-icon.blue { background: #e8f0fe; color: #1a73e8; }
    .metric-icon.green { background: #e6f4ea; color: #34a853; }
    .metric-icon.orange { background: #fef3e2; color: #f9a825; }
    .metric-icon.red { background: #fce8e6; color: #ea4335; }
    .metric-icon.purple { background: #f3e8fd; color: #9334e6; }
    .metric-label {
        font-size: 0.75rem;
        color: #5f6368;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 1rem;
        font-weight: 700;
        color: #1a365d;
    }

    /* Veredito */
    .verdict {
        padding: 1rem 1.2rem;
        border-radius: 10px;
        margin-top: 0.5rem;
        text-align: center;
    }
    .verdict.approved {
        background: linear-gradient(135deg, #e6f4ea 0%, #ceead6 100%);
        border: 1px solid #34a853;
    }
    .verdict.warning {
        background: linear-gradient(135deg, #fef3e2 0%, #fde7c0 100%);
        border: 1px solid #f9a825;
    }
    .verdict.rejected {
        background: linear-gradient(135deg, #fce8e6 0%, #f8d0cc 100%);
        border: 1px solid #ea4335;
    }
    .verdict-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    .verdict-text {
        font-size: 1.1rem;
        font-weight: 800;
    }

    /* Notas gauge */
    .score-bar {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.4rem 0;
    }
    .score-bar-label {
        font-size: 0.8rem;
        color: #5f6368;
        min-width: 130px;
    }
    .score-bar-track {
        flex: 1;
        height: 8px;
        background: #e8eaed;
        border-radius: 4px;
        overflow: hidden;
    }
    .score-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s;
    }
    .score-bar-value {
        font-size: 0.85rem;
        font-weight: 700;
        min-width: 35px;
        text-align: right;
    }

    /* Sugestões */
    .suggestion {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 0.75rem;
        background: #f8fafc;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 3px solid #1a73e8;
    }
    .suggestion-icon {
        font-size: 1.2rem;
        margin-top: 2px;
    }
    .suggestion-text {
        font-size: 0.85rem;
        color: #3c4043;
        line-height: 1.4;
    }
    .suggestion-text strong {
        color: #1a365d;
    }

    /* Tabela de impressão */
    .print-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
    }
    .print-table th {
        background: #f0f4f8;
        padding: 0.6rem 0.8rem;
        text-align: left;
        font-weight: 600;
        color: #5f6368;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .print-table td {
        padding: 0.6rem 0.8rem;
        border-bottom: 1px solid #f0f4f8;
        color: #3c4043;
    }

    /* Upload area override */
    [data-testid="stFileUploader"] {
        background: white;
        border-radius: 12px;
        padding: 1rem;
    }
    [data-testid="stFileUploader"] section {
        padding: 1.5rem;
        border: 2px dashed #cbd5e1 !important;
        border-radius: 10px;
        background: #f8fafc;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: #1a73e8 !important;
        background: #e8f0fe;
    }

    /* Streamlit elements override */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: white;
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
    }

    /* Esconder label do file uploader */
    [data-testid="stFileUploader"] label { display: none !important; }

    /* Image container */
    .img-preview {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        text-align: center;
    }

    /* Detalhes técnicos */
    .tech-detail {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background: #f0f4f8;
        padding: 0.3rem 0.7rem;
        border-radius: 6px;
        font-size: 0.78rem;
        color: #5f6368;
        margin: 0.2rem;
    }

    div[data-testid="stMetric"] {
        background: white;
        padding: 0.8rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ── Constantes ──────────────────────────────────────────────────────────────
STAMP_SIZES = {
    "Pequena (15×20 cm)": (15, 20),
    "Média (25×30 cm)": (25, 30),
    "Grande (30×40 cm)": (30, 40),
    "Extra Grande (40×50 cm)": (40, 50),
}

MIN_PX_ESTAMPA = 2500
IDEAL_PX_ESTAMPA = 3500


# ── Funções de análise ──────────────────────────────────────────────────────
def analyze_technical(img: Image.Image, file_size: int) -> dict:
    arr = np.array(img)
    gray = np.array(img.convert("L")).astype(float)
    lap = ndimage.laplace(gray)
    w, h = img.size

    result = {
        "width": w, "height": h, "total_px": w * h,
        "file_size": file_size, "format": img.format or "PNG",
        "mode": img.mode, "bits": len(img.getbands()) * 8,
        "dpi_meta": img.info.get("dpi", None),
        "icc": img.info.get("icc_profile", None) is not None,
    }

    if img.mode == "RGBA":
        alpha = arr[:, :, 3]
        total = alpha.size
        result["has_transparency"] = True
        result["pct_transparent"] = (alpha == 0).sum() / total * 100
        result["pct_semi"] = (((alpha > 0) & (alpha < 255)).sum()) / total * 100
        result["pct_opaque"] = (alpha == 255).sum() / total * 100
        alpha_dx = np.abs(np.diff(alpha.astype(float), axis=1))
        result["aa_smooth"] = int(((alpha_dx > 0) & (alpha_dx < 128)).sum())
        result["aa_hard"] = int((alpha_dx >= 128).sum())
        result["aa_ratio"] = result["aa_smooth"] / (result["aa_hard"] + 1)
    else:
        result["has_transparency"] = False

    mask = arr[:, :, 3] > 128 if img.mode == "RGBA" else np.ones(arr.shape[:2], bool)
    rgb = arr[:, :, :3][mask]
    result["unique_colors"] = len(np.unique(rgb, axis=0)) if len(rgb) > 0 else 0

    if len(rgb) > 0:
        lum = 0.299 * rgb[:, 0].astype(float) + 0.587 * rgb[:, 1].astype(float) + 0.114 * rgb[:, 2].astype(float)
        result["lum_min"] = float(lum.min())
        result["lum_max"] = float(lum.max())
        result["lum_mean"] = float(lum.mean())
        result["lum_std"] = float(lum.std())
        result["contrast_range"] = float(lum.max() - lum.min())

    result["laplacian_var"] = float(lap.var())
    result["edge_mean"] = float(np.abs(lap).mean())
    result["grad_h"] = float(np.abs(np.diff(gray, axis=1)).mean())
    result["grad_v"] = float(np.abs(np.diff(gray, axis=0)).mean())
    result["strong_edges_pct"] = (np.abs(lap) > 50).sum() / lap.size * 100

    result["print_sizes"] = {}
    for ppi in [300, 200, 150]:
        result["print_sizes"][ppi] = (round((w / ppi) * 2.54, 1), round((h / ppi) * 2.54, 1))

    return result


def analyze_quality(img: Image.Image, tech: dict) -> dict:
    w, h = tech["width"], tech["height"]
    menor_lado = min(w, h)
    quality = {"scores": {}, "verdict": "", "issues": [], "recommendations": []}

    # ── Nota técnica ──
    score_tech = 0.0
    if menor_lado >= IDEAL_PX_ESTAMPA: score_tech += 4.0
    elif menor_lado >= MIN_PX_ESTAMPA: score_tech += 3.0
    elif menor_lado >= 1500: score_tech += 2.0
    elif menor_lado >= 800: score_tech += 1.0
    else: quality["issues"].append(f"Resolução muito baixa ({w}×{h} px). Mínimo: {MIN_PX_ESTAMPA} px no menor lado.")

    if tech.get("has_transparency"): score_tech += 1.0
    else:
        quality["issues"].append("Sem transparência — fundo branco será impresso.")
        quality["recommendations"].append("Remover fundo e exportar como PNG com transparência.")

    if tech.get("icc"): score_tech += 1.0
    else: quality["recommendations"].append("Incorporar perfil ICC (sRGB ou CMYK).")

    uc = tech.get("unique_colors", 0)
    if uc >= 30000: score_tech += 2.0
    elif uc >= 10000: score_tech += 1.5
    elif uc >= 5000: score_tech += 1.0
    elif uc >= 1000: score_tech += 0.5

    if tech.get("has_transparency"):
        if tech.get("aa_hard", 0) == 0: score_tech += 1.0
        elif tech.get("aa_ratio", 0) > 3: score_tech += 0.7
        else:
            score_tech += 0.3
            quality["issues"].append("Anti-aliasing fraco nas bordas.")

    lap_var = tech.get("laplacian_var", 0)
    if lap_var > 2000: score_tech += 1.0
    elif lap_var > 500: score_tech += 0.7
    elif lap_var > 100:
        score_tech += 0.5
        if menor_lado > 2000 and lap_var < 500:
            quality["issues"].append("Possível upscale por IA: resolução alta mas nitidez baixa.")
            quality["recommendations"].append("Aplicar sharpening leve (Unsharp Mask).")
    else:
        score_tech += 0.2
        quality["issues"].append("Nitidez muito baixa.")

    quality["scores"]["technical"] = round(min(score_tech, 10.0), 1)

    # ── Nota visual ──
    score_visual = 5.0
    contrast = tech.get("lum_std", 0)
    if contrast > 60: score_visual += 2.0
    elif contrast > 40: score_visual += 1.5
    elif contrast > 20: score_visual += 1.0
    elif contrast > 10:
        score_visual += 0.5
        quality["issues"].append(f"Contraste baixo ({contrast:.1f}). Pode se perder na impressão.")
        quality["recommendations"].append("Aumentar contraste ou escurecer cores.")
    else:
        quality["issues"].append("Contraste muito baixo.")
        quality["recommendations"].append("Revisar cores: aumentar saturação.")

    lum_range = tech.get("contrast_range", 0)
    if lum_range > 200: score_visual += 1.5
    elif lum_range > 150: score_visual += 1.0
    elif lum_range > 100: score_visual += 0.5

    if uc >= 50000: score_visual += 1.0
    elif uc >= 10000: score_visual += 0.5

    quality["scores"]["visual"] = round(min(score_visual, 10.0), 1)

    # ── Nota impressão ──
    score_print = 0.0
    ps = tech["print_sizes"][300]
    if ps[0] >= 25 and ps[1] >= 30: score_print += 4.0
    elif ps[0] >= 20 and ps[1] >= 25: score_print += 3.0
    elif ps[0] >= 15 and ps[1] >= 20: score_print += 2.0
    elif ps[0] >= 10 and ps[1] >= 10: score_print += 1.0
    else: quality["issues"].append(f"A 300 PPI imprime apenas {ps[0]}×{ps[1]} cm — insuficiente.")

    if tech.get("has_transparency"): score_print += 2.0
    if tech.get("icc"): score_print += 1.5
    if tech.get("format") in ("PNG", "TIFF"): score_print += 1.0
    elif tech.get("format") == "JPEG":
        score_print += 0.3
        quality["issues"].append("JPEG: compressão com perda. Prefira PNG ou TIFF.")

    if contrast > 30: score_print += 1.5
    elif contrast > 15: score_print += 0.5

    quality["scores"]["print"] = round(min(score_print, 10.0), 1)

    # Veredito
    scores = quality["scores"]
    avg = (scores["technical"] + scores["visual"] + scores["print"]) / 3
    if avg >= 7.5 and min(scores.values()) >= 6.0:
        quality["verdict"] = "PRONTO PARA IMPRESSÃO"
        quality["verdict_class"] = "approved"
        quality["verdict_icon"] = "✅"
    elif avg >= 5.0 and min(scores.values()) >= 4.0:
        quality["verdict"] = "APROVADO COM RESSALVAS"
        quality["verdict_class"] = "warning"
        quality["verdict_icon"] = "⚠️"
    else:
        quality["verdict"] = "NECESSITA DE CORREÇÕES"
        quality["verdict_class"] = "rejected"
        quality["verdict_icon"] = "❌"

    if menor_lado < MIN_PX_ESTAMPA:
        quality["recommendations"].insert(0,
            f"Obter arquivo com mínimo {MIN_PX_ESTAMPA} px no menor lado. "
            "Se feito no Canva, recrie num canvas de 3500×4000 px ou maior."
        )

    if not quality["recommendations"]:
        quality["recommendations"].append("Nenhuma correção crítica. Imagem pronta para uso.")

    return quality


def get_resolution_label(w, h):
    menor = min(w, h)
    if menor >= IDEAL_PX_ESTAMPA: return "Excelente", "green"
    elif menor >= MIN_PX_ESTAMPA: return "Boa", "green"
    elif menor >= 1500: return "Regular", "orange"
    elif menor >= 800: return "Baixa", "orange"
    else: return "Insuficiente", "red"


def get_sharpness_label(lap_var):
    if lap_var > 2000: return "Excelente"
    elif lap_var > 500: return "Boa"
    elif lap_var > 100: return "Regular"
    else: return "Baixa"


def get_dpi_effective(w, h):
    """Calcula DPI efetivo para estampa 25x30cm."""
    dpi_w = w / (25 / 2.54)
    dpi_h = h / (30 / 2.54)
    return round(min(dpi_w, dpi_h))


def score_color(score):
    if score >= 7: return "#34a853"
    elif score >= 5: return "#f9a825"
    else: return "#ea4335"


def render_score_bar(label, score, max_score=10):
    pct = (score / max_score) * 100
    color = score_color(score)
    return f"""
    <div class="score-bar">
        <span class="score-bar-label">{label}</span>
        <div class="score-bar-track">
            <div class="score-bar-fill" style="width:{pct}%; background:{color};"></div>
        </div>
        <span class="score-bar-value" style="color:{color};">{score}</span>
    </div>
    """


def render_metric(icon, icon_class, label, value):
    return f"""
    <div class="metric-row">
        <div class="metric-icon {icon_class}">{icon}</div>
        <div>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    </div>
    """


def render_suggestion(icon, title, text):
    return f"""
    <div class="suggestion">
        <span class="suggestion-icon">{icon}</span>
        <div class="suggestion-text"><strong>{title}</strong><br>{text}</div>
    </div>
    """


# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div>
        <h1>🔍 STAMPA CHECKER</h1>
        <p class="subtitle">Análise de qualidade para estampas</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Upload ──────────────────────────────────────────────────────────────────
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False

col_upload, col_spacer = st.columns([1, 2])

with col_upload:
    st.markdown("""
    <div class="card">
        <div class="card-title">📤 Upload da Estampa</div>
        <p style="font-size:0.85rem; color:#5f6368; margin-bottom:0.5rem;">
            Arraste ou selecione a imagem para análise.<br>
            Suporta PNG, JPG, TIFF, BMP, WEBP.
        </p>
    </div>
    """, unsafe_allow_html=True)

uploaded = st.file_uploader(
    "upload",
    type=["png", "jpg", "jpeg", "tiff", "tif", "bmp", "webp"],
    label_visibility="collapsed",
)

# ── Análise ─────────────────────────────────────────────────────────────────
if uploaded is not None:
    file_bytes = uploaded.getvalue()
    file_size = len(file_bytes)

    try:
        img = Image.open(BytesIO(file_bytes))
    except Exception as e:
        st.error(f"Erro ao abrir a imagem: {e}")
        st.stop()

    with st.spinner("Analisando imagem..."):
        tech = analyze_technical(img, file_size)
        quality = analyze_quality(img, tech)

    dpi_eff = get_dpi_effective(tech["width"], tech["height"])
    res_label, res_color_name = get_resolution_label(tech["width"], tech["height"])
    sharp_label = get_sharpness_label(tech["laplacian_var"])

    # ── Layout principal ────────────────────────────────────────────────
    col_preview, col_metrics = st.columns([3, 2])

    # Preview da imagem
    with col_preview:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">🖼️ Preview — {uploaded.name}</div>', unsafe_allow_html=True)
        st.image(img, use_container_width=True)

        # Tags de info rápida
        tags_html = f"""
        <div style="margin-top:0.8rem;">
            <span class="tech-detail">📐 {tech['width']}×{tech['height']} px</span>
            <span class="tech-detail">📁 {tech['format']}</span>
            <span class="tech-detail">💾 {tech['file_size']/1024:.0f} KB</span>
            <span class="tech-detail">🎨 {tech['mode']} ({tech['bits']}bits)</span>
            <span class="tech-detail">🔢 {tech['unique_colors']:,} cores</span>
        """
        if tech.get("has_transparency"):
            tags_html += '<span class="tech-detail">✅ Transparência</span>'
        else:
            tags_html += '<span class="tech-detail">❌ Sem transparência</span>'
        if tech.get("icc"):
            tags_html += '<span class="tech-detail">✅ ICC</span>'
        else:
            tags_html += '<span class="tech-detail">⚠️ Sem ICC</span>'
        tags_html += "</div>"
        st.markdown(tags_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Métricas e veredito
    with col_metrics:
        # Card de métricas
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📊 Análise</div>', unsafe_allow_html=True)

        dpi_icon_class = "green" if dpi_eff >= 300 else ("orange" if dpi_eff >= 150 else "red")
        dpi_label = "Excelente" if dpi_eff >= 300 else ("Boa" if dpi_eff >= 200 else ("Mínima" if dpi_eff >= 150 else "Insuficiente"))

        metrics_html = ""
        metrics_html += render_metric("📐", dpi_icon_class, "RESOLUÇÃO EFETIVA (DPI P/ 25×30CM)", f"{dpi_eff} DPI ({dpi_label})")
        metrics_html += render_metric("🎨", "blue" if tech["unique_colors"] >= 10000 else "orange", "QUALIDADE DE PX", f"{res_label} ({tech['width']}×{tech['height']})")

        contrast_val = tech.get("lum_std", 0)
        contrast_label = "Alto" if contrast_val > 40 else ("Médio" if contrast_val > 20 else "Baixo")
        contrast_class = "green" if contrast_val > 40 else ("orange" if contrast_val > 20 else "red")
        metrics_html += render_metric("🔲", contrast_class, "CONTRASTE", f"{contrast_label} ({contrast_val:.1f})")

        metrics_html += render_metric("✨", "purple", "NITIDEZ", f"{sharp_label}")

        ps300 = tech["print_sizes"][300]
        print_class = "green" if ps300[0] >= 25 else ("orange" if ps300[0] >= 15 else "red")
        metrics_html += render_metric("🖨️", print_class, "IMPRESSÃO A 300 DPI", f"{ps300[0]}×{ps300[1]} cm")

        st.markdown(metrics_html, unsafe_allow_html=True)

        # Veredito
        st.markdown(f"""
        <div class="verdict {quality['verdict_class']}">
            <div class="verdict-label">VEREDITO</div>
            <div class="verdict-text">{quality['verdict_icon']} {quality['verdict']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Linha 2: Notas + Sugestões ──────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col_scores, col_suggestions = st.columns([1, 1])

    with col_scores:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📈 Notas</div>', unsafe_allow_html=True)
        scores = quality["scores"]
        bars = ""
        bars += render_score_bar("Qualidade Técnica", scores["technical"])
        bars += render_score_bar("Qualidade Visual", scores["visual"])
        bars += render_score_bar("Prep. Impressão", scores["print"])
        st.markdown(bars, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Tabela de impressão
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🖨️ Tamanhos de Impressão</div>', unsafe_allow_html=True)
        table_rows = ""
        for ppi in [300, 200, 150]:
            ps = tech["print_sizes"][ppi]
            quality_label = "Ótima" if ppi == 300 else ("Boa" if ppi == 200 else "Mínima")
            ok = "✅" if ps[0] >= 20 or ps[1] >= 20 else "❌"
            table_rows += f"<tr><td>{ppi} PPI</td><td>{quality_label}</td><td>{ps[0]} × {ps[1]} cm</td><td>{ok}</td></tr>"

        st.markdown(f"""
        <table class="print-table">
            <thead><tr><th>PPI</th><th>Qualidade</th><th>Tamanho</th><th>Viável</th></tr></thead>
            <tbody>{table_rows}</tbody>
        </table>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_suggestions:
        # Problemas
        if quality["issues"]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">⚠️ Problemas Encontrados</div>', unsafe_allow_html=True)
            for issue in quality["issues"]:
                st.markdown(render_suggestion("⚠️", "", issue), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Recomendações
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">💡 Sugestões de Melhoria</div>', unsafe_allow_html=True)

        suggestion_icons = ["🔧", "🎨", "📐", "🖨️", "✨", "📁"]
        for i, rec in enumerate(quality["recommendations"]):
            icon = suggestion_icons[i % len(suggestion_icons)]
            # Extrair primeira frase como título
            parts = rec.split(".", 1)
            title = parts[0] + "."
            detail = parts[1].strip() if len(parts) > 1 else ""
            st.markdown(render_suggestion(icon, title, detail), unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Compatibilidade com estampas
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">👕 Compatibilidade com Estampas</div>', unsafe_allow_html=True)
        compat_rows = ""
        for name, (tw, th) in STAMP_SIZES.items():
            checks = []
            for ppi in [300, 200, 150]:
                ps = tech["print_sizes"][ppi]
                checks.append("✅" if ps[0] >= tw and ps[1] >= th else "❌")
            compat_rows += f"<tr><td>{name}</td><td>{checks[0]}</td><td>{checks[1]}</td><td>{checks[2]}</td></tr>"

        st.markdown(f"""
        <table class="print-table">
            <thead><tr><th>Tamanho</th><th>300 PPI</th><th>200 PPI</th><th>150 PPI</th></tr></thead>
            <tbody>{compat_rows}</tbody>
        </table>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # ── Estado vazio ────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex; gap:1.5rem; margin-top:1rem;">
        <div class="card" style="flex:1; text-align:center; padding:2rem;">
            <div style="font-size:2.5rem; margin-bottom:0.5rem;">📐</div>
            <div style="font-weight:700; color:#1a365d; margin-bottom:0.3rem;"> Análise Técnica</div>
            <div style="font-size:0.85rem; color:#5f6368;">
                Resolução, formato, transparência, cores, nitidez,
                detecção de upscale e tamanhos de impressão.
            </div>
        </div>
        <div class="card" style="flex:1; text-align:center; padding:2rem;">
            <div style="font-size:2.5rem; margin-bottom:0.5rem;">🎨</div>
            <div style="font-weight:700; color:#1a365d; margin-bottom:0.3rem;"> Qualidade e Veredito</div>
            <div style="font-size:0.85rem; color:#5f6368;">
                Notas de 0 a 10, veredito automático, problemas
                encontrados e sugestões de melhoria.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center; padding:2rem 0 1rem; color:#9ca3af; font-size:0.75rem;">
    Stampa Checker v1.0 — HallDevs
</div>
""", unsafe_allow_html=True)


