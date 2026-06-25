
import pandas as pd
from cleaning import run_cleaning_pipeline

def eda_missing_check(raw_dict: dict):
#Kiểm tra missing value ở các cột quan trọng trước khi cleaning lọc bỏ
    from cleaning import load_data
    raw = load_data()

    print("--- Missing values trước cleaning ---")
    for name, df in raw.items():
        n_missing_cols = df.isna().sum()
        n_missing_cols = n_missing_cols[n_missing_cols > 0]
        if len(n_missing_cols) > 0:
            print(f"[{name}]")
            print(n_missing_cols)
        else:
            print(f"[{name}] Không có missing value")
    print()

#mỗi công việc có bao nhiêu người chấm điểm
def eda_sample_size(data: dict):
    expert_cs, worker_cs = data["expert_cs"], data["worker_cs"]

    n_rater_expert = expert_cs.groupby("Task ID").size()
    n_rater_worker = worker_cs.groupby("Task ID").size()

    print("--- Rater / Task ---")
    print(f"Expert: trung bình {n_rater_expert.mean():.1f} rater/task "
          f"(min={n_rater_expert.min()}, max={n_rater_expert.max()})")
    print(f"Worker: trung bình {n_rater_worker.mean():.1f} rater/task "
          f"(min={n_rater_worker.min()}, max={n_rater_worker.max()})")
    print(">> Nếu Expert chỉ ~2-3 người/task: cần dùng CI khi so sánh giữa các nhóm")

#xem điểm phân bổ như thế nào
def eda_distributions(data: dict):
    expert_cs, worker_cs = data["expert_cs"], data["worker_cs"]

    print("--- Phân phối Automation Capacity Rating (Expert) ---")
    print(expert_cs["Automation Capacity Rating"].describe())
    print("\nSố lượng theo từng mức điểm:")
    print(expert_cs["Automation Capacity Rating"].value_counts().sort_index())

    print("\n--- Phân phối Human Agency Scale Rating (Worker) ---")
    print(worker_cs["Human Agency Scale Rating"].describe())
    print("\n Số lượng theo từng mức điểm:")
    print(worker_cs["Human Agency Scale Rating"].value_counts().sort_index())
    print()

#xem xét mỗi nhóm Hành vi (GWA) có chứa bao nhiêu Task bên trong, và loại bỏ những GWA quá ít task (dưới 3)
def eda_gwa_coverage(data: dict, min_n: int = 3):
    cs_tasks, expert_cs, worker_cs = data["cs_tasks"], data["expert_cs"], data["worker_cs"]

    valid_ids = set(expert_cs["Task ID"]) & set(worker_cs["Task ID"])
    gwa_count = (
        cs_tasks[cs_tasks["Task ID"].isin(valid_ids)]
        .groupby("gwa")["Task ID"].nunique()
        .sort_values(ascending=False)
    )

    print(f"--- Số task theo GWA (tổng {len(gwa_count)} GWA xuất hiện) ---")
    print(gwa_count)

    n_dropped = (gwa_count < min_n).sum()
    print(f"\n>> {n_dropped} GWA có n_task < {min_n}, sẽ bị loại khỏi phân tích chính:")
    print(gwa_count[gwa_count < min_n])
    print()

#xem các biến có tương quan không
def eda_correlation_check(data: dict):
    expert_cs = data["expert_cs"]

    candidate_cols = [
        "Automation Capacity Rating",
        "Human Agency Scale Rating",
        "Domain Expertise Requirement",
        "Involved Uncertainty",
    ]
    available = [c for c in candidate_cols if c in expert_cs.columns]
    missing = [c for c in candidate_cols if c not in expert_cs.columns]
    if missing:
        print(f"[Lưu ý] Các cột không tồn tại trong file Expert, bỏ qua: {missing}")

    print("--- Ma trận tương quan (Expert-level, trước khi group theo GWA) ---")
    print(expert_cs[available].corr().round(2))
    print()



def run_eda():
    data = run_cleaning_pipeline()

    eda_missing_check(data)
    eda_sample_size(data)
    eda_distributions(data)
    eda_gwa_coverage(data)
    eda_correlation_check(data)


if __name__ == "__main__":
    run_eda()
