"""
Bước 5: STREAMLIT APP
Bản đồ Năng lực AI Agent theo Hành vi Lao động (GWA Capability Map)

Chỉ gọi run_analysis() và vẽ — không tính toán logic ở đây.
Chạy: streamlit run app.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from analysis import run_analysis

st.set_page_config(
    page_title="GWA Capability Map — Ngành CS",
    layout="wide",
)

TIER_COLORS = {
    "Tier 1 — Tự động hoàn toàn": "#1a7a3c",
    "Tier 2 — Agent đề xuất": "#d99a1b",
    "Tier 3 — Agent hỗ trợ": "#c0392b",
}


@st.cache_data
def load_analysis():
    gwa_table, usage_table = run_analysis()
    return gwa_table, usage_table


gwa_df, usage_df = load_analysis()

st.title("Bản đồ Năng lực AI Agent theo Hành vi Lao động (GWA)")
st.caption(
    "Ngành Khoa học Máy tính (O*NET-SOC 15-1xxx) — "
    f"{gwa_df['n_task'].sum()} task, {len(gwa_df)} hành vi lao động tổng quát (GWA)"
)

tab1, tab2, tab3 = st.tabs(
    ["GWA Capability Map", "Reality Check", "Tier-List & Khuyến nghị"]
)


# ============================================================
# TAB 1 — GWA Capability Map (Module 1)
# ============================================================
with tab1:
    st.subheader("Đối chiếu Năng lực AI (Expert) và Nhu cầu giữ quyền (Worker) theo GWA")

    fig = px.scatter(
        gwa_df,
        x="agency_mean",
        y="cap_mean",
        size="n_task",
        color="tier_label",
        error_x="ci95",
        error_y="ci95",
        hover_name="gwa",
        hover_data={"net_score": ":.2f", "n_task": True, "agency_mean": ":.2f", "cap_mean": ":.2f"},
        labels={
            "agency_mean": "Human Agency (Worker muốn giữ quyền)",
            "cap_mean": "Automation Capacity (Expert chấm AI làm được)",
            "tier_label": "Tier",
        },
        color_discrete_map=TIER_COLORS,
        size_max=40,
    )
    fig.update_layout(height=550, legend_title_text="Tier")
    # Đường tham chiếu Cap = Agency, để thấy trực quan vùng nào Cap > Agency (nên giao AI)
    fig.add_shape(
        type="line", x0=1, y0=1, x1=5, y1=5,
        line=dict(color="gray", dash="dot", width=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Kích thước điểm = số task hỗ trợ (n_task). Thanh lỗi = khoảng tin cậy 95% của Net Score. "
        "Đường chấm chéo: Cap = Agency — điểm nằm dưới đường này có Automation Capacity > Human Agency."
    )


# ============================================================
# TAB 2 — Parallel Delegation Reality Check (Module 2)
# ============================================================
with tab2:
    st.subheader("Đối chiếu Xu hướng Song song: Lý thuyết khảo sát vs Hành vi thực tế")
    st.caption(
        "Hai biểu đồ độc lập, KHÔNG join trực tiếp GWA ↔ LLM Usage Type "
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Gradient GWA (khảo sát Expert + Worker)**")
        fig_gwa = px.bar(
            gwa_df.sort_values("net_score", ascending=True),
            x="net_score",
            y="gwa",
            orientation="h",
            color="tier_label",
            color_discrete_map=TIER_COLORS,
            labels={"net_score": "Net Score (Cap − Agency)", "gwa": ""},
        )
        fig_gwa.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_gwa, use_container_width=True)

    with col2:
        st.markdown(f"**Tần suất dùng LLM thực tế** (n={usage_df['n_worker'].iloc[0]} worker)")
        fig_usage = px.bar(
            usage_df.sort_values("avg_frequency", ascending=True),
            x="avg_frequency",
            y="usage_type",
            orientation="h",
            labels={"avg_frequency": "Tần suất TB (0=Never .. 3=Daily)", "usage_type": ""},
        )
        fig_usage.update_traces(marker_color="#4a6fa5")
        fig_usage.update_layout(height=500)
        st.plotly_chart(fig_usage, use_container_width=True)

    st.info(
        "Quan sát: Information Access/Communication/Edit được dùng tần suất cao nhất, "
        "Decision/System Design thấp nhất — xu hướng tổng thể phù hợp với việc Documenting "
        "đứng đầu và Guiding/Strategy đứng cuối bên Gradient GWA. "
        "Đây là phù hợp ở mức xu hướng tổng hợp, **chưa kiểm định ở cấp độ cá nhân**."
    )


# ============================================================
# TAB 3 — AI Architecture Tier-List (Module 3)
# ============================================================
with tab3:
    st.subheader("Khung Khuyến nghị Phân quyền AI Agent theo Tier")

    st.warning(
        "**Lưu ý phương pháp luận:** Tier được chia bằng 2 khoảng trống lớn nhất trên Net Score "
        "đã sắp xếp (gap detection), không gán tay theo ngưỡng cố định. Cả 2 khoảng trống lớn nhất "
        "đều nằm ở nửa trên của dải, dẫn đến Tier 1 chỉ có 1 GWA — đây là kết quả khách quan của "
        "thuật toán trên dữ liệu hiện có (n mẫu mỏng ở một số GWA: 6–14 task/nhóm), không phải lựa "
        "chọn chủ quan. Ranh giới Tier 2/Tier 3 cũng cần được đọc cùng với CI 95% (cột bên dưới), "
        "vì khoảng tin cậy giữa các GWA liền kề có thể chồng lấn."
    )

    display_cols = {
        "gwa": "Hành vi (GWA)",
        "n_task": "n_task",
        "cap_mean": "Automation Capacity",
        "agency_mean": "Human Agency",
        "net_score": "Net Score",
        "ci95": "± CI 95%",
        "tier_label": "Tier",
    }
    table = gwa_df[list(display_cols.keys())].rename(columns=display_cols)
    table = table.round(2)

    def highlight_tier(row):
        color = TIER_COLORS.get(row["Tier"], "white")
        return [f"background-color: {color}33"] * len(row)

    st.dataframe(
        table.style.apply(highlight_tier, axis=1),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")
    st.markdown("### Khuyến nghị Thiết kế AI Agent")
    st.markdown(
        """
Doanh nghiệp **không nên** thiết kế AI Agent theo Chức danh công việc (Occupation) — một kỹ
sư có thể đi qua cả 3 Tier hành vi trong cùng một ngày làm việc.

Kiến trúc đề xuất — **Cơ chế Phân quyền Động theo GWA**:

- **Tier 1 (Autonomous):** chỉ áp dụng rõ ràng cho hành vi *Documenting/Recording Information*.
  Mức đồng thuận giao toàn quyền tuyệt đối trong ngành CS hẹp hơn nhận định ban đầu.
- **Tier 2 (Copilot — đề xuất, người duyệt):** mặc định cho phần lớn quy trình kỹ thuật
  (Working with Computers, Inspecting, Monitoring, Thinking Creatively...) — AI có năng lực
  cao nhưng chưa đủ tách biệt để giao toàn quyền.
- **Tier 3 (Trợ lý thông tin — không tự quyết):** các bước thẩm định, chiến lược, lãnh đạo
  (Judging Qualities, Developing Strategies, Guiding Subordinates).

→ Đây là khuyến nghị **thận trọng**: phần lớn hành vi lao động ngành CS nên dừng ở Tier 2,
chỉ một phần rất nhỏ đủ điều kiện tự động hoàn toàn.
"""
    )