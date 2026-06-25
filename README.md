# GWA Capability Map — Bản đồ Năng lực AI Agent theo Hành vi Lao động (Ngành CS)

> **Không phải nghề nghiệp nào dễ bị AI thay thế, mà là hành vi nào dễ bị thay thế.**

Đồ án phân tích sự bất đồng nhận thức giữa **Chuyên gia kỹ thuật** (đánh giá năng lực
tự động hóa của AI) và **Người lao động ngành CS** (đánh giá nhu cầu giữ quyền quyết
định của con người), trên cùng một đơn vị phân tích: **Generalized Work Activity (GWA)**
— chuẩn phân loại hành vi lao động tổng quát của O\*NET, tái sử dụng được giữa các nghề
và giữa các ngành, thay vì phân tích theo từng Task hay Occupation riêng lẻ.

---

## Tóm tắt 3 Insight chính

### 1. Có một Gradient hành vi thật, không phải ngẫu nhiên
Tương quan giữa Automation Capacity (Expert) và Human Agency (Worker) ở cấp độ từng
rating cá nhân là **r = −0.88** — rất mạnh. Gradient này không phải hiệu ứng gộp nhóm:
nó còn tương quan với độ phức tạp khách quan của công việc (`Domain Expertise
Requirement`: r = −0.55; `Involved Uncertainty`: r = −0.59) — tức hành vi nào AI làm
tốt cũng chính là hành vi được đánh giá ít cần chuyên môn/ít bất định hơn.

### 2. Mức đồng thuận "giao toàn quyền AI" hẹp hơn nhận định ban đầu
Số lượng và ranh giới Tier **không gán tay** — được xác định tự động bằng cách tìm các
khoảng trống (gap) trên Net Score đã sắp xếp vượt quá *(trung bình + 1 độ lệch chuẩn)*
của toàn bộ khoảng trống. Kết quả: đúng **3 Tier**, nhưng **Tier 1 (Tự động hoàn toàn)
chỉ có duy nhất 1 hành vi** — *Documenting/Recording Information* (Net Score = +1.67).
Các hành vi tưởng như "kỹ thuật thuần túy" khác (Working with Computers, Inspecting
Equipment, Monitoring) có Automation Capacity cao nhưng vẫn rơi vào Tier 2 (Copilot),
vì khoảng cách với nhóm Tier 3 chưa đủ lớn theo phân tích thống kê.

| Tier | Số GWA | Net Score | Vai trò Agent đề xuất |
|---|---|---|---|
| 1 — Tự động hoàn toàn | 1 | +1.67 | Autonomous |
| 2 — Agent đề xuất | 6 | +0.61 → +1.37 | Copilot, người duyệt |
| 3 — Agent hỗ trợ | 6 | −0.55 → +0.21 | Trợ lý thông tin, không tự quyết |

### 3. Hành vi sử dụng LLM thực tế khớp xu hướng khảo sát — nhưng chỉ ở mức tổng hợp
Đối chiếu độc lập (không join trực tiếp) giữa Gradient GWA và tần suất dùng LLM thật
(`LLM Usage by Type`, n=1228 worker) cho thấy *Information Access* và *Communication*
được dùng nhiều nhất, *System Design* và *Coding* (theo nghĩa quyết định kiến trúc)
thấp nhất — phù hợp xu hướng với việc *Documenting* đứng đầu và *Guiding/Strategy*
đứng cuối bên Gradient GWA. **Đây là sự phù hợp ở cấp tổng hợp toàn ngành, chưa kiểm
định ở cấp độ cá nhân** (tương quan cá nhân giữa mức dùng LLM và điểm Agency riêng của
từng người chỉ ~0.12–0.14, yếu).

---

## Khuyến nghị Thiết kế AI Agent

Doanh nghiệp **không nên** thiết kế/mua AI Agent theo Chức danh công việc (Occupation)
— một kỹ sư có thể đi qua cả 3 Tier hành vi trong cùng một ngày làm việc. Kiến trúc đề
xuất là **Cơ chế Phân quyền Động theo GWA**: Agent tự chuyển trạng thái tự chủ tùy theo
*loại hành vi* đang thực hiện, không tùy theo *vai trò* của người dùng.

> Đây là khuyến nghị **thận trọng**: phần lớn hành vi lao động ngành CS nên dừng ở
> Tier 2 (Copilot), chỉ một phần rất nhỏ đủ điều kiện tự động hoàn toàn.

---

## Dữ liệu

| File | Mô tả |
|---|---|
| `task_statement_with_metadata.csv` | Task statement + mã O\*NET-SOC + GWA gắn kèm |
| `expert_rated_technological_capability.csv` | Expert rating: Automation Capacity, Domain Expertise, Uncertainty |
| `domain_worker_desires.csv` | Worker rating: Human Agency Scale, lý do giữ quyền |
| `domain_worker_metadata.csv` | Hồ sơ worker: tần suất dùng LLM theo 9 loại hoạt động |

**Phạm vi:** lọc theo mã `O*NET-SOC Code` bắt đầu bằng `15-1` (Computer Occupations
theo chuẩn BLS — loại nhóm `15-2x` Mathematical Science Occupations) → **21 nghề CS,
144 task có đủ cả Expert + Worker rating, gộp về 13 GWA** đạt ngưỡng mẫu tối thiểu
(n≥3 task/nhóm).

---

## Phương pháp

```
Net Score (GWA) = mean(Automation Capacity Rating) − mean(Human Agency Scale Rating)
```

Tier được chia bằng **gap detection tự động**: tính khoảng trống giữa các Net Score
liền kề (đã sắp xếp giảm dần), một khoảng trống được coi là ranh giới Tier thật nếu
vượt quá `mean(gap) + 1×std(gap)`. Số lượng Tier = số khoảng trống đáng kể + 1 — không
gán cứng số Tier hay ngưỡng điểm cắt bằng tay.

---

## Cấu trúc Project

```
.
├── data/                     # 4 file CSV gốc
├── cleaning.py               # Bước 1+2: Load & Clean (lọc SOC 15-1, parse GWA, encode)
├── eda.py                    # Bước 3: Khám phá dữ liệu (missing, distribution, correlation)
├── analysis.py                # Bước 4: Tính Net Score theo GWA, gap detection chia Tier
├── app.py                     # Bước 5: Streamlit — 3 module trực quan hóa
└── requirements.txt
```

Chạy theo đúng pipeline:
```bash
python cleaning.py    # kiểm tra số liệu sau lọc/clean
python eda.py          # khám phá: missing, phân phối, tương quan
python analysis.py    # bảng Net Score + Tier + LLM Usage
streamlit run app.py  # mở app tương tác
```

---

## App Streamlit — 3 Module

**1. GWA Capability Map** — Scatter Automation Capacity vs Human Agency, màu theo
Tier, kích thước điểm theo số task hỗ trợ, error bar = CI 95%.

**2. Reality Check** — 2 biểu đồ độc lập đặt cạnh nhau (Gradient GWA | Tần suất dùng
LLM thực tế), không join trực tiếp để tránh suy diễn vượt dữ liệu.

**3. Tier-List & Khuyến nghị** — Bảng đầy đủ 13 GWA kèm CI 95%, và khung khuyến nghị
thiết kế Agent theo 3 Tier.

---

## Hạn chế đã biết

- **Mẫu Expert mỏng:** trung bình 2.5 rater/task (min 2, max 4) → CI 95% khá rộng ở
  một số GWA (đặc biệt nhóm Tier 3, n=6–8 task/nhóm). Ranh giới Tier 2/Tier 3 cần đọc
  cùng cột CI, không chỉ nhìn Net Score trung bình.
- **6 GWA bị loại** vì n<3 task, trong đó có *Making Decisions and Solving Problems*
  (n=2) — đáng tiếc vì liên quan trực tiếp đề tài nhưng không đủ tin cậy thống kê.
- **272/1500 worker thiếu dữ liệu `LLM Usage by Type`** (thiếu cả block, không phải
  ngẫu nhiên từng câu) — đã loại khi tính bảng Reality Check; có thể tạo độ lệch nhẹ
  nếu nhóm thiếu dữ liệu có đặc điểm dùng LLM khác biệt với nhóm còn lại.
- **GWA Extraction đơn giản hóa:** mỗi task có thể gắn nhiều GWA, nhưng pipeline hiện
  tại chỉ lấy GWA đầu tiên trong danh sách làm nhãn chính.
- Đối chiếu Gradient GWA và LLM Usage Type (Module 2) là **2 hệ phân loại độc lập**,
  không có cầu nối dữ liệu trực tiếp — kết luận chỉ ở mức xu hướng tổng thể.

---

## Hướng mở rộng

- Áp khung GWA này sang ngành khác để kiểm tra tính tổng quát hóa.
- Hồi quy đa biến `Net Score ~ Domain Expertise + Involved Uncertainty` (lưu ý đa
  cộng tuyến giữa 2 biến này, r=0.54 — cần kiểm tra VIF trước khi đưa cùng vào model).
- Thử nghiệm trọng số theo toàn bộ danh sách GWA của mỗi task, thay vì chỉ lấy GWA đầu.

---

## Nguồn dữ liệu & Công nghệ

- O\*NET-SOC Code, Generalized Work Activity: [O\*NET Online](https://www.onetonline.org/)
- Python, pandas, Streamlit, Plotly
