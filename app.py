"""
GWA Capability Map: Bản đồ Năng lực AI Agent theo Hành vi Lao động
Chạy: streamlit run app.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from analysis import run_analysis

st.set_page_config(
    page_title="GWA Capability Map",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Màu sắc học thuật: xanh navy, teal, amber trung tính, đỏ gạch ──
TIER_COLORS = {
    "Tier 1 — Tự động hoàn toàn": "#2A6049",
    "Tier 2 — Agent đề xuất":     "#7A5C1E",
    "Tier 3 — Agent hỗ trợ":      "#8B2E2E",
}
TIER_BG = {
    "Tier 1 — Tự động hoàn toàn": "#EBF5F0",
    "Tier 2 — Agent đề xuất":     "#FBF4E6",
    "Tier 3 — Agent hỗ trợ":      "#F9EAEA",
}
C_BLUE   = "#1C3A5E"
C_MUTED  = "#5A5A5A"
C_LINE   = "#D0CCC4"
C_BG     = "#FAFAF8"
C_ACCENT = "#2A6049"

CHART_BASE = dict(
    font=dict(family="Georgia, Times New Roman, serif", size=12, color="#2C2C2C"),
    paper_bgcolor="white",
    plot_bgcolor="#FAFAF8",
    margin=dict(t=36, b=36, l=16, r=16),
)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;0,700;1,400&family=Source+Sans+3:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Source Sans 3', sans-serif;
    background-color: {C_BG};
    color: #2C2C2C;
}}
.block-container {{ padding-top: 2.2rem; max-width: 1160px; }}

/* Tiêu đề app */
.app-header {{
    border-bottom: 2px solid {C_ACCENT};
    padding-bottom: 0.9rem;
    margin-bottom: 1.6rem;
}}
.app-title {{
    font-family: 'Lora', serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: {C_BLUE};
    line-height: 1.25;
    margin: 0;
}}
.app-subtitle {{
    font-size: 0.95rem;
    color: {C_MUTED};
    margin-top: 0.3rem;
}}

/* KPI card */
.kpi-row {{ display: flex; gap: 1rem; margin-bottom: 1.6rem; }}
.kpi {{
    flex: 1;
    background: white;
    border: 1px solid {C_LINE};
    border-top: 3px solid {C_ACCENT};
    border-radius: 4px;
    padding: 0.85rem 1rem;
}}
.kpi-num {{
    font-family: 'Lora', serif;
    font-size: 1.55rem;
    font-weight: 700;
    color: {C_BLUE};
    line-height: 1;
}}
.kpi-lbl {{
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {C_MUTED};
    margin-top: 0.3rem;
}}

/* Section label trên mỗi tab */
.section-label {{
    font-family: 'Lora', serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: {C_BLUE};
    margin: 0 0 0.25rem 0;
}}
.section-note {{
    font-size: 0.88rem;
    color: {C_MUTED};
    border-left: 3px solid {C_LINE};
    padding-left: 0.75rem;
    margin-bottom: 1.2rem;
    line-height: 1.55;
}}

/* Tab styling */
div[data-baseweb="tab-list"] {{ gap: 0; border-bottom: 1px solid {C_LINE}; }}
button[data-baseweb="tab"] {{
    font-family: 'Source Sans 3', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    border-radius: 0;
    padding: 0.5rem 1.2rem;
    color: {C_MUTED};
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {C_BLUE};
    border-bottom: 2px solid {C_BLUE};
}}

/* Methodological note */
.method-note {{
    background: #F0F4F8;
    border-left: 3px solid {C_BLUE};
    padding: 0.75rem 1rem;
    border-radius: 0 4px 4px 0;
    font-size: 0.88rem;
    color: #2C2C2C;
    line-height: 1.6;
    margin-bottom: 1.2rem;
}}

/* Recommendation box */
.rec-box {{
    background: white;
    border: 1px solid {C_LINE};
    border-radius: 4px;
    padding: 1.2rem 1.4rem;
    line-height: 1.7;
    font-size: 0.95rem;
}}
.rec-tier {{
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
    padding: 0.55rem 0;
    border-bottom: 1px solid {C_LINE};
}}
.rec-tier:last-child {{ border-bottom: none; }}
.tier-badge {{
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    padding: 0.2rem 0.55rem;
    border-radius: 3px;
    white-space: nowrap;
    margin-top: 0.15rem;
}}
.t1 {{ background: #EBF5F0; color: #2A6049; }}
.t2 {{ background: #FBF4E6; color: #7A5C1E; }}
.t3 {{ background: #F9EAEA; color: #8B2E2E; }}
.rec-text {{ font-size: 0.9rem; color: #2C2C2C; }}

/* Observation box */
.obs-box {{
    background: #F7F5F0;
    border: 1px solid {C_LINE};
    border-radius: 4px;
    padding: 0.75rem 1rem;
    font-size: 0.88rem;
    color: #2C2C2C;
    margin-top: 0.8rem;
    line-height: 1.6;
}}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load():
    return run_analysis()

gwa_df, usage_df = load()
n_tiers = gwa_df["tier"].nunique()
n_tasks  = int(gwa_df["n_task"].sum())

# ── Header ──
st.markdown(f"""
<div class="app-header">
  <p class="app-title">Bản đồ Năng lực AI Agent theo Hành vi Lao động (GWA)</p>
  <p class="app-subtitle">
    Ngành Khoa học Máy tính · O*NET-SOC 15-1xxx ·
    Đối chiếu Automation Capacity (Expert) và Human Agency (Worker)
    trên {len(gwa_df)} Generalized Work Activities
  </p>
</div>
""", unsafe_allow_html=True)

# ── KPI row ──
k1, k2, k3, k4 = st.columns(4)
for col, num, lbl in [
    (k1, n_tasks,          "Task phân tích"),
    (k2, len(gwa_df),      "Hành vi (GWA)"),
    (k3, n_tiers,          "Tier phân quyền"),
    (k4, usage_df["n_worker"].iloc[0], "Worker khảo sát"),
]:
    col.markdown(
        f'<div class="kpi"><div class="kpi-num">{num}</div>'
        f'<div class="kpi-lbl">{lbl}</div></div>',
        unsafe_allow_html=True,
    )

tab1, tab2, tab3 = st.tabs([
    "Capability Map",
    "Reality Check",
    "Tier-List và Khuyến nghị",
])


# ════════════════════════════════════════════════════
# TAB 1 — GWA Capability Map
# ════════════════════════════════════════════════════
with tab1:
    st.markdown('<p class="section-label">Vị trí của từng GWA theo hai chiều đánh giá</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-note">'
        'Trục ngang: mức độ Worker muốn giữ quyền quyết định (Human Agency, thang 1–5). '
        'Trục dọc: năng lực AI theo đánh giá của Expert (Automation Capacity, thang 1–5). '
        'Kích thước điểm tỉ lệ với số task hỗ trợ. Thanh sai số thể hiện khoảng tin cậy 95%.'
        '</p>',
        unsafe_allow_html=True,
    )

    fig = px.scatter(
        gwa_df,
        x="agency_mean", y="cap_mean",
        size="n_task", color="tier_label",
        error_x="ci95", error_y="ci95",
        hover_name="gwa",
        hover_data={
            "net_score":    ":.2f",
            "n_task":       True,
            "agency_mean":  ":.2f",
            "cap_mean":     ":.2f",
            "tier_label":   False,
        },
        labels={
            "agency_mean": "Human Agency",
            "cap_mean":    "Automation Capacity",
            "tier_label":  "Phân nhóm",
        },
        color_discrete_map=TIER_COLORS,
        size_max=36,
    )
    fig.add_shape(
        type="line", x0=1.5, y0=1.5, x1=5, y1=5,
        line=dict(color="#AAAAAA", dash="dot", width=1),
    )
    fig.add_annotation(
        x=4.6, y=4.7, text="Cap = Agency",
        showarrow=False,
        font=dict(size=10, color="#AAAAAA"),
        textangle=-40,
    )
    fig.update_traces(
        marker=dict(line=dict(width=1.2, color="white")),
        error_x=dict(thickness=1, color="#CCCCCC"),
        error_y=dict(thickness=1, color="#CCCCCC"),
    )
    fig.update_layout(
        **CHART_BASE,
        height=520,
        xaxis=dict(title="Human Agency (thang 1–5)", gridcolor="#EBEBEB", range=[1.8, 3.8]),
        yaxis=dict(title="Automation Capacity (thang 1–5)", gridcolor="#EBEBEB", range=[2.0, 4.7]),
        legend=dict(
            title="Phân nhóm Tier",
            orientation="h",
            yanchor="bottom", y=1.01,
            xanchor="left", x=0,
            font=dict(size=11),
        ),
    )
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════
# TAB 2 — Reality Check
# ════════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-label">Đối chiếu xu hướng khảo sát và hành vi sử dụng LLM thực tế</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-note">'
        'Hai biểu đồ được xây từ hai nguồn độc lập và không được join trực tiếp — '
        'vì GWA và loại hoạt động LLM là hai hệ phân loại khác nhau. '
        'Người đọc tự quan sát sự tương đồng xu hướng tổng thể.'
        '</p>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("**Net Score theo GWA** — dữ liệu khảo sát Expert và Worker")
        fig_gwa = px.bar(
            gwa_df.sort_values("net_score", ascending=True),
            x="net_score", y="gwa",
            orientation="h",
            color="tier_label",
            color_discrete_map=TIER_COLORS,
            labels={"net_score": "Net Score (Automation Capacity − Human Agency)", "gwa": ""},
        )
        fig_gwa.update_traces(marker_line_width=0)
        fig_gwa.update_layout(
            **CHART_BASE,
            height=480,
            showlegend=False,
            xaxis=dict(gridcolor="#EBEBEB", zeroline=True, zerolinecolor="#AAAAAA", zerolinewidth=1),
            yaxis=dict(gridcolor="white", tickfont=dict(size=11)),
        )
        st.plotly_chart(fig_gwa, use_container_width=True)

    with col2:
        st.markdown(f"**Tần suất dùng LLM theo loại hoạt động** — n = {usage_df['n_worker'].iloc[0]} worker")
        fig_usage = px.bar(
            usage_df.sort_values("avg_frequency", ascending=True),
            x="avg_frequency", y="usage_type",
            orientation="h",
            labels={"avg_frequency": "Tần suất trung bình (0 = Không dùng, 3 = Hàng ngày)", "usage_type": ""},
        )
        fig_usage.update_traces(marker_color="#4A6FA5", marker_line_width=0)
        fig_usage.update_layout(
            **CHART_BASE,
            height=480,
            xaxis=dict(gridcolor="#EBEBEB", range=[0, 2.4]),
            yaxis=dict(gridcolor="white", tickfont=dict(size=11)),
        )
        st.plotly_chart(fig_usage, use_container_width=True)

    st.markdown(
        '<div class="obs-box">'
        '<strong>Nhận xét:</strong> Các hoạt động Information Access, Communication và Edit có tần suất LLM cao nhất, '
        'trong khi System Design và Decision có tần suất thấp nhất — phù hợp xu hướng tổng thể với '
        'việc Documenting đứng đầu và Guiding/Strategy đứng cuối trong Gradient GWA. '
        'Đây là sự phù hợp ở mức tổng hợp toàn ngành; chưa được kiểm định ở cấp độ cá nhân '
        '(tương quan cá nhân r ≈ 0,12–0,14).'
        '</div>',
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════
# TAB 3 — Tier-List và Khuyến nghị
# ════════════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-label">Phân nhóm 13 GWA theo mức độ phân quyền AI</p>', unsafe_allow_html=True)

    st.markdown(
        '<div class="method-note">'
        '<strong>Lưu ý phương pháp luận.</strong> '
        'Số lượng Tier và ranh giới phân nhóm được xác định tự động bằng phương pháp phát hiện '
        'khoảng trống (gap detection) dựa trên z-score: một khoảng trống được coi là ranh giới '
        'Tier thực sự nếu vượt quá (mean + 1 độ lệch chuẩn) của toàn bộ phân phối khoảng trống. '
        'Với dữ liệu hiện tại, hai khoảng trống đáng kể (gap = 0,300 và gap = 0,403) đều nằm ở '
        'nửa trên của dải Net Score, dẫn đến Tier 1 chỉ có một GWA — kết quả khách quan của thuật toán, '
        'không phải lựa chọn chủ quan. Khoảng tin cậy 95% giữa các GWA liền kề ở vùng Tier 2/Tier 3 '
        'có thể chồng lấn do cỡ mẫu mỏng (6–14 task/nhóm); ranh giới này nên được đọc như '
        'định hướng thiết kế, không phải ngưỡng thống kê tuyệt đối.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Bảng dữ liệu
    display_cols = {
        "gwa":          "Hành vi (GWA)",
        "n_task":       "n",
        "cap_mean":     "Automation Capacity",
        "agency_mean":  "Human Agency",
        "net_score":    "Net Score",
        "ci95":         "CI 95%",
        "tier_label":   "Phân nhóm",
    }
    table = gwa_df[list(display_cols.keys())].rename(columns=display_cols).round(2)

    def style_tier(row):
        bg = TIER_BG.get(row["Phân nhóm"], "white")
        return [f"background-color: {bg}; color: #2C2C2C"] * len(row)

    st.dataframe(
        table.style.apply(style_tier, axis=1),
        use_container_width=True,
        hide_index=True,
        height=460,
        column_config={
            "Hành vi (GWA)":       st.column_config.TextColumn(width="large"),
            "n":                   st.column_config.NumberColumn(width="small"),
            "Automation Capacity": st.column_config.NumberColumn(format="%.2f"),
            "Human Agency":        st.column_config.NumberColumn(format="%.2f"),
            "Net Score":           st.column_config.NumberColumn(format="%.2f"),
            "CI 95%":              st.column_config.NumberColumn(format="±%.2f"),
            "Phân nhóm":           st.column_config.TextColumn(width="medium"),
        },
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-label">Khuyến nghị thiết kế AI Agent</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-note">'
        'Kiến trúc AI Agent nên được thiết kế theo cơ chế phân quyền động dựa trên GWA, '
        'không theo chức danh công việc. Một kỹ sư có thể đi qua cả ba nhóm hành vi trong cùng một ngày làm việc.'
        '</p>',
        unsafe_allow_html=True,
    )

    st.markdown("""
<div class="rec-box">
  <div class="rec-tier">
    <span class="tier-badge t1">Tier 1 — Autonomous</span>
    <span class="rec-text">
      Áp dụng cho hành vi <em>Documenting / Recording Information</em> (Net Score = +1,67).
      Đây là GWA duy nhất có khoảng cách đủ xa để giao toàn quyền cho AI Agent mà không cần
      giám sát trực tiếp của con người. Mức đồng thuận tự động hóa tuyệt đối trong ngành CS
      hẹp hơn nhiều so với nhận định ban đầu.
    </span>
  </div>
  <div class="rec-tier">
    <span class="tier-badge t2">Tier 2 — Copilot</span>
    <span class="rec-text">
      Mặc định cho phần lớn quy trình kỹ thuật: Working with Computers, Inspecting Equipment,
      Monitoring Processes, Thinking Creatively, và các GWA tương tự (Net Score = +0,61 đến +1,37).
      AI đóng vai trò đề xuất và hỗ trợ; kỹ sư giữ quyền phê duyệt cuối cùng.
    </span>
  </div>
  <div class="rec-tier">
    <span class="tier-badge t3">Tier 3 — Advisory</span>
    <span class="rec-text">
      Dành cho các hành vi mang tính thẩm định, chiến lược và lãnh đạo: Judging Qualities,
      Developing Strategies, Guiding Subordinates (Net Score = −0,55 đến +0,21).
      AI chỉ cung cấp thông tin và phân tích; con người đưa ra toàn bộ quyết định.
    </span>
  </div>
</div>
""", unsafe_allow_html=True)
