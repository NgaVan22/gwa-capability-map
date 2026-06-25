import pandas as pd
import ast

DATA_DIR = "data"  

# Mã SOC chuẩn BLS cho "Computer Occupations" (15-1xxx)
CS_SOC_PREFIX = "15-1"

FREQ_MAP = {"Never": 0, "Monthly": 1, "Weekly": 2, "Daily": 3}


# ---------- BƯỚC 1: LOAD ----------

def load_data(data_dir: str = DATA_DIR) -> dict:
    """Đọc 4 file CSV thô."""
    raw = {
        "tasks": pd.read_csv(f"{data_dir}/task_statement_with_metadata.csv"),
        "expert": pd.read_csv(f"{data_dir}/expert_rated_technological_capability.csv"),
        "worker": pd.read_csv(f"{data_dir}/domain_worker_desires.csv"),
        "meta": pd.read_csv(f"{data_dir}/domain_worker_metadata.csv"),
    }
    return raw


# ---------- BƯỚC 2: CLEANING ----------
#chuyển cột skill từ string sang list và lấy GWA đầu tiên
def parse_skill_list(skill_str):
    if pd.isna(skill_str):
        return None
    try:
        lst = ast.literal_eval(skill_str)
        return lst[0] if lst else None
    except (ValueError, SyntaxError):
        return skill_str  # nếu không parse được, giữ nguyên string gốc

#lọc đúng SOC 15-1, parse GWA và loại duplicate Task ID
def clean_tasks(tasks: pd.DataFrame) -> pd.DataFrame:
    df = tasks.copy()

    # Lọc theo mã SOC chuẩn, không dùng list tên tay (dễ sai/sót)
    df["O*NET-SOC Code"] = df["O*NET-SOC Code"].astype(str)
    df = df[df["O*NET-SOC Code"].str.startswith(CS_SOC_PREFIX)]

    # Parse GWA chính
    df["gwa"] = df["Skill (O*NET Work Activity)"].apply(parse_skill_list)

    # Loại các dòng không parse được GWA (nếu có)
    n_before = len(df)
    df = df.dropna(subset=["gwa"])
    n_after = len(df)
    if n_before != n_after:
        print(f"[clean_tasks] Loại {n_before - n_after} dòng không parse được GWA")

    cols = ["Task ID", "Task", "Occupation (O*NET-SOC Title)", "O*NET-SOC Code", "gwa"]
    df = df[cols].drop_duplicates(subset="Task ID")
    return df

#Giữ rating Expert hợp lệ (1-5), thuộc đúng phạm vi Task ID đã lọc trong expert
def clean_expert(expert: pd.DataFrame, valid_task_ids: set) -> pd.DataFrame:
    df = expert.copy()
    df = df[df["Task ID"].isin(valid_task_ids)]

    # Kiểm tra missing & range hợp lệ (thang 1-5)
    df = df.dropna(subset=["Automation Capacity Rating", "Human Agency Scale Rating"])
    df = df[df["Automation Capacity Rating"].between(1, 5)]
    df = df[df["Human Agency Scale Rating"].between(1, 5)]
    return df

#Giữ rating Worker hợp lệ (1-5), thuộc đúng phạm vi Task ID đã lọc trong worker
def clean_worker(worker: pd.DataFrame, valid_task_ids: set) -> pd.DataFrame:
    df = worker.copy()
    df = df[df["Task ID"].isin(valid_task_ids)]
    df = df.dropna(subset=["Human Agency Scale Rating"])
    df = df[df["Human Agency Scale Rating"].between(1, 5)]
    return df

#Chuyển LLM Usage by Type thành só 0-3
def clean_meta(meta: pd.DataFrame) -> pd.DataFrame:
    df = meta.copy()
    usage_cols = [c for c in df.columns if c.startswith("LLM Usage by Type")]
    for c in usage_cols:
        df[c] = df[c].map(FREQ_MAP)
    return df


def run_cleaning_pipeline(data_dir: str = DATA_DIR) -> dict:
    raw = load_data(data_dir)

    cs_tasks = clean_tasks(raw["tasks"])
    valid_ids = set(cs_tasks["Task ID"])

    expert_cs = clean_expert(raw["expert"], valid_ids)
    worker_cs = clean_worker(raw["worker"], valid_ids)
    meta_clean = clean_meta(raw["meta"])

    return {
        "cs_tasks": cs_tasks,
        "expert_cs": expert_cs,
        "worker_cs": worker_cs,
        "meta": meta_clean,
    }


if __name__ == "__main__":
    data = run_cleaning_pipeline()
    print("=== Kết quả Cleaning ===")
    print(f"CS tasks (sau lọc SOC 15-1): {len(data['cs_tasks'])} task")
    print(f"  Số nghề: {data['cs_tasks']['Occupation (O*NET-SOC Title)'].nunique()}")
    print(f"Expert ratings hợp lệ: {len(data['expert_cs'])} dòng, "
          f"{data['expert_cs']['Task ID'].nunique()} task có Expert rating")
    print(f"Worker ratings hợp lệ: {len(data['worker_cs'])} dòng, "
          f"{data['worker_cs']['Task ID'].nunique()} task có Worker rating")

    common = set(data['expert_cs']['Task ID']) & set(data['worker_cs']['Task ID'])
    print(f"Task có ĐỦ cả Expert + Worker: {len(common)}")
