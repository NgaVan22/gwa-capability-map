"""
Bước 4: ANALYSIS
Tính Net Score theo GWA, chia Tier bằng gap detection, và tính bảng LLM Usage thực tế.
Output của file này là input trực tiếp cho app.py (Streamlit).
"""

import pandas as pd
from cleaning import run_cleaning_pipeline

MIN_N_TASK = 3 #GWA ít hơn 3 thì bị loại
N_TIERS = 3 #số lượng phân tầng


# ---------- TÍNH NET SCORE THEO GWA ----------
#Join Expert + Worker qua Task ID -> gắn GWA -> group theo GWA ->tính Cap mean, Agency mean, Net Score, std, CI 95%.
def build_gwa_table(data: dict, min_n: int = MIN_N_TASK) -> pd.DataFrame:
    cs_tasks, expert_cs, worker_cs = data["cs_tasks"], data["expert_cs"], data["worker_cs"]

    expert_agg = (
        expert_cs.groupby("Task ID")
        .agg(cap=("Automation Capacity Rating", "mean"))
        .reset_index()
    )
    worker_agg = (
        worker_cs.groupby("Task ID")
        .agg(agency=("Human Agency Scale Rating", "mean"))
        .reset_index()
    )

    # Chỉ giữ task có ĐỦ cả Expert và Worker (inner join hai lần)
    merged = (
        cs_tasks[["Task ID", "gwa"]]
        .merge(expert_agg, on="Task ID", how="inner")
        .merge(worker_agg, on="Task ID", how="inner")
    )

    gwa = (
        merged.groupby("gwa")
        .agg(
            n_task=("Task ID", "size"),
            cap_mean=("cap", "mean"),
            cap_std=("cap", "std"),
            agency_mean=("agency", "mean"),
            agency_std=("agency", "std"),
        )
        .reset_index()
    )

    gwa = gwa[gwa["n_task"] >= min_n].copy()
    gwa["net_score"] = gwa["cap_mean"] - gwa["agency_mean"]

    # SE gộp từ 2 nguồn sai số (Cap và Agency), dùng cho CI 95% của Net Score
    gwa["cap_std"] = gwa["cap_std"].fillna(0)
    gwa["agency_std"] = gwa["agency_std"].fillna(0)
    combined_var = (gwa["cap_std"] ** 2 + gwa["agency_std"] ** 2) / gwa["n_task"]
    gwa["net_se"] = combined_var ** 0.5
    gwa["ci95"] = 1.96 * gwa["net_se"]

    return gwa.sort_values("net_score", ascending=False).reset_index(drop=True)


# ---------- CHIA TIER BẰNG GAP DETECTION ----------
#    Chia Tier dựa trên (n_tiers - 1) khoảng trống lớn nhất giữa các Net Score
#liền kề (đã sort giảm dần) — tránh ngưỡng số cố định dễ lỗi thời khi đổi mẫu.
def assign_tiers_by_gap(gwa_df: pd.DataFrame, n_tiers: int = N_TIERS) -> pd.DataFrame:
    df = gwa_df.sort_values("net_score", ascending=False).reset_index(drop=True)

    # Khoảng cách giữa điểm i và điểm i+1
    gaps = (df["net_score"] - df["net_score"].shift(-1)).abs()
    gaps = gaps.iloc[:-1]  # bỏ NaN ở dòng cuối

    cut_after_indices = gaps.nlargest(n_tiers - 1).index.tolist()
    cut_after_indices.sort()

    tier_labels = []
    current_tier = 1
    for i in range(len(df)):
        tier_labels.append(current_tier)
        if i in cut_after_indices:
            current_tier += 1

    df["tier"] = tier_labels

    tier_names = {
        1: "Tier 1 — Tự động hoàn toàn",
        2: "Tier 2 — Agent đề xuất",
        3: "Tier 3 — Agent hỗ trợ",
    }
    df["tier_label"] = df["tier"].map(tier_names)

    # In ra khoảng trống đã dùng để cắt
    print("--- Gap detection: khoảng trống dùng để cắt Tier ---")
    for idx in cut_after_indices:
        print(
            f"  Cắt sau '{df.loc[idx, 'gwa']}' (Net={df.loc[idx, 'net_score']:.2f}) "
            f"-> '{df.loc[idx + 1, 'gwa']}' (Net={df.loc[idx + 1, 'net_score']:.2f}), "
            f"gap={gaps[idx]:.3f}"
        )
    print()

    return df


# ---------- BẢNG LLM USAGE THỰC TẾ ----------
#Tính tần suất dùng LLM trung bình theo 9 loại hoạt động. 
# Loại các dòng thiếu dữ liệu (272 worker không trả lời block này, đã thấy ở EDA)
#để không tính trung bình sai trên giá trị NaN.
def build_llm_usage_table(data: dict) -> pd.DataFrame:
    meta = data["meta"]
    usage_cols = [c for c in meta.columns if c.startswith("LLM Usage by Type")]

    meta_valid = meta.dropna(subset=usage_cols)
    n_dropped = len(meta) - len(meta_valid)
    print(f"[build_llm_usage_table] Loại {n_dropped} worker thiếu dữ liệu LLM Usage "
          f"(còn lại {len(meta_valid)}/{len(meta)})\n")

    usage_avg = meta_valid[usage_cols].mean().sort_values(ascending=False) #điểm trung bình tần suất dùng AI
    usage_avg.index = [c.replace("LLM Usage by Type - ", "") for c in usage_avg.index]

    result = usage_avg.reset_index()
    result.columns = ["usage_type", "avg_frequency"]
    result["n_worker"] = len(meta_valid)
    return result


# ---------- CHẠY TOÀN BỘ ANALYSIS ----------

def run_analysis():
    data = run_cleaning_pipeline()

    gwa_table = build_gwa_table(data)
    gwa_table = assign_tiers_by_gap(gwa_table)
    usage_table = build_llm_usage_table(data)

    return gwa_table, usage_table


if __name__ == "__main__":
    gwa_table, usage_table = run_analysis()

    print("=== Bảng Net Score theo GWA (đã chia Tier) ===")
    cols = ["gwa", "n_task", "cap_mean", "agency_mean", "net_score", "ci95", "tier_label"]
    print(gwa_table[cols].round(2).to_string(index=False))

    print("\n=== Bảng LLM Usage by Type (Reality Check) ===")
    print(usage_table.round(2).to_string(index=False))
