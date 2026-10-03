# DATA_NOTES: khảo sát dữ liệu cho khâu CV (ảnh → đồ thị)

Bảng số đầy đủ nằm ở `docs/DATA_NOTES_stats.md`, sinh lại bằng:

```bash
conda run -n courier python src/inspect_data.py --data-root delivery_public --out docs/DATA_NOTES_stats.md --check-images
```

Chỉ khảo sát train (2.000 cảnh) và validation (300 cảnh). Không đọc test.
Phần "quan sát bằng mắt" dựa trên ảnh crop của 8 cảnh train (mỗi style 1 cảnh thường + 1 cảnh hoán đổi) và 40 biểu tượng thời tiết.

---

## 1. Các quy ước đã chốt

### 1.1. Ý nghĩa của `road_look`

`road_look` **luôn có đủ 3 khóa** `normal`, `crowded`, `covered`; không bao giờ rỗng. Mỗi khóa là trạng thái thật của đoạn đường, giá trị là **kiểu vẽ thông thường của trạng thái nào** được dùng để vẽ nó trong ảnh này.

- Cảnh không hoán đổi: `{"normal": "normal", "crowded": "crowded", "covered": "covered"}` (ánh xạ đồng nhất). Train có 85,3% cảnh như vậy, validation 65,3%.
- Ví dụ `train-00044` (classic) có `{"normal": "normal", "crowded": "covered", "covered": "crowded"}`:
  - đường **đông người** được vẽ bằng nét xanh dương, tức kiểu "mái che" thông thường của classic;
  - đường **mái che** được vẽ bằng nét cam, tức kiểu "đông" thông thường;
  - dòng chú giải "Đông người" cũng vẽ swatch xanh dương. **Chú giải luôn đúng với ảnh của chính nó.**
- Có đúng 6 hoán vị (1 đồng nhất + 5 hoán đổi). 5 mẫu hoán đổi có tần suất gần bằng nhau, và không phụ thuộc style.
- `closed` **không bao giờ** tham gia hoán đổi.

"Tỉ lệ ảnh có `road_look` khác rỗng" trong yêu cầu được hiểu là **tỉ lệ khác ánh xạ đồng nhất**: train 14,7%, validation 34,7%.

### 1.2. Lớp look (kiểu vẽ) của EdgePatchNet

```
LOOK_CLASSES = ["none", "normal", "crowded", "covered", "closed"]   # 5 lớp
```

| lớp | nghĩa | train | val |
|---|---|---|---|
| `none` | 2 giao lộ kề nhau đều tồn tại nhưng **không có đoạn nào** | 14,2% | 14,0% |
| `normal` / `crowded` / `covered` | nét vẽ giống kiểu *thông thường* của trạng thái đó (trong style của ảnh) | 37,4 / 20,3 / 21,9% | 29,2 / 23,9 / 24,3% |
| `closed` | đường đóng (nét nhạt + dấu chặn) | 6,2% | 8,6% |

### 1.3. Công thức look = f(status, road_look)

```python
def look_of(status, road_look):
    return road_look[status] if status in ("normal", "crowded", "covered") else "closed"

# chiều ngược lại, dùng ở hậu xử lý: status = bảng_chú_giải[look]
# với bảng_chú_giải = {road_look[k]: k for k in road_look} ∪ {"closed": "closed"}
```

Look của **swatch chú giải**:
- dòng `kind ∈ {normal, crowded, covered}` có look = `road_look[kind]`;
- dòng `closed` có look = `closed`.

Đếm trên toàn bộ swatch, phân bố (kind → look) khớp đúng phân bố `road_look`.

**Quan sát thêm (cả 8 cảnh đã xem):** swatch của dòng `stairs` và `oneway` được vẽ trên nền look của `road_look["normal"]`, cộng thêm bậc thang hoặc mũi tên. Hiện chỉ dùng 4 dòng `normal`/`crowded`/`covered`/`closed` làm mẫu swatch cho đầu look; 2 dòng `stairs`/`oneway` có thể thêm sau, sau khi kiểm chứng trên nhiều cảnh hơn.

### 1.4. Hướng đoạn đường và đường một chiều

- **Mọi** cạnh trong `scenes.json` có `a < b` theo thứ tự (hàng, cột): `a` là giao lộ **trên** (đoạn dọc) hoặc **trái** (đoạn ngang). Hai giao lộ luôn kề nhau. Kiểm tra trên 144.447 cạnh, không có ngoại lệ.
- `oneway_to` luôn là `a` hoặc `b`. Lớp oneway:
  - `none`;
  - `forward` (`oneway_to == b`, đi được a → b, tức xuống hoặc sang phải);
  - `backward` (`oneway_to == a`).
  forward và backward có tần suất gần bằng nhau ở cả đoạn ngang lẫn đoạn dọc.
- Quy ước patch của EdgePatchNet: `a` nằm bên trái, nên "forward" là mũi tên chỉ sang phải trong patch. Lật ngang patch thì đổi forward ↔ backward.
- Ràng buộc cứng (0 ngoại lệ): cạnh `closed` không bao giờ có `stairs` hay `oneway`; không cạnh nào vừa `stairs` vừa `oneway`.

### 1.5. Lớp cho các task khác

| task | lớp |
|---|---|
| landmark theo giao lộ | 11: `background` + 10 loại (thứ tự như `DE_BAI.md`) |
| có robot | 2. Robot **không bao giờ** đứng trên giao lộ có địa điểm (0/2.300 cảnh), nên hai đầu này loại trừ nhau. |
| heading | 4 (`UP`, `DOWN`, `LEFT`, `RIGHT`), cân bằng |
| legend kind | **18 lớp**: 10 `place:*` + `normal`, `crowded`, `covered`, `closed`, `stairs`, `oneway`, `robot`, **`weather`** |
| weather | **2 lớp `rain` / `dry`** (xem mục 4: khác với yêu cầu ban đầu là 3 lớp) |

---

## 2. Hình học

### 2.1. Ảnh

- 36 kích thước khác nhau, cạnh dài 960–1152 px. Phổ biến nhất: 1152×864, 1024×768, 1120×840. Có cả ảnh vuông 1024×1024 và 960×960.
- PNG ở mode `P` (palette) → bắt buộc `.convert("RGB")`. JPEG ở mode RGB.
- `width`/`height` trong `scenes.json` khớp 100% với file ảnh.
- Phần góc ảnh bị xoay được tô **màu nền của style**, không phải màu đen. Augmentation xoay cũng nên tô bằng màu nền (ví dụ màu của pixel góc ảnh).

### 2.2. Khoảng cách `d` giữa hai giao lộ kề nhau

| | min | median | max |
|---|---|---|---|
| train | 84 | ~110 | 185 |
| validation | 85 | ~98 | 149 |

`d` không phụ thuộc đáng kể vào style. Validation có `d` nhỏ hơn vì lưới lớn hơn. `d` chiếm 0,075–0,21 cạnh ngắn của ảnh.

Hệ quả cho kích thước đầu vào:

| model | đại lượng | giá trị |
|---|---|---|
| LayoutNet | `d` sau resize 1024 (×~0,89) và stride 4 | ≈ 19–41 ô |
| LayoutNet | sigma = 0,08·d | ≈ 1,5–3,3 ô |
| NodePatchNet | patch 1,3·d | 109–240 px, resize về 128 (tỉ lệ 0,53–1,17) |
| EdgePatchNet | dải 1,0·d × 0,5·d | 84–185 × 42–93 px, resize về 64×160 |

### 2.3. Độ lệch tâm giao lộ

Độ lệch so với hàng/cột thẳng, tính cả ảnh bị xoay: trung vị 0,02·d (train) / 0,03·d (val); p95 0,09·d / 0,15·d; max 0,26·d / 0,34·d. Phần lớn là do xoay toàn cục (±3° trên ~8·d → tới ~0,4·d ở mép lưới). → Cần ước lượng và khử góc xoay **trước** khi gom cụm hàng/cột.

### 2.4. Chú giải và thời tiết

- Khối chú giải nằm ở **phải-trên** (~49%), **trái-trên** (~25%) hoặc **trái-dưới** (~26%).
- Biểu tượng thời tiết phần lớn nằm ở phải-trên (~78%).
- Kích thước so với `d`:

| khung | so với d | lưu ý |
|---|---|---|
| swatch | rộng 0,2–0,74·d, cao 0,2–0,67·d | |
| chữ chú giải | rộng 0,3–2,6·d, **cao chỉ 0,05–0,37·d** (p5 ≈ 0,10·d ≈ 9–11 px) | sau resize và stride 4, mask chữ chỉ còn ~2–3 ô chiều cao. Mask nên được nong (dilate) khi tính metric, và crop chữ cần jitter cẩn thận. |
| ô thời tiết | 0,22–1,16·d | |

- **Thứ tự dòng chú giải cố định** (100% cảnh):
  `[weather] > place:* … > normal > crowded > covered > closed > stairs > oneway > robot`.
  Dòng `weather` có mặt ở 38,5% (train) / 43,7% (val) cảnh. Khối địa điểm chỉ liệt kê các loại có trên bản đồ (100%). Thứ tự này dùng được làm **phương án dự phòng** trong hậu xử lý khi CropClsNet không chắc.
- Chữ chú giải: mỗi kind không phải địa điểm có **2 cách viết**, chọn ngẫu nhiên, không phụ thuộc style. Ví dụ `closed`: "Đường đóng" / "Cấm đi / đang sửa"; `normal`: "Đường thường" / "Lối đi thường". Dòng `weather` có 5 cách viết: "Thời tiết", "Thời tiết: mưa", "… nắng", "… nhiều mây", "… nắng nhẹ".

---

## 3. Cách vẽ theo style (quan sát bằng mắt)

| | classic | night | print | sketch |
|---|---|---|---|---|
| nền | trắng xanh nhạt | xanh đen | trắng ngà (giấy) | be (giấy vẽ tay) |
| giao lộ | vòng tròn trắng | ô vuông nhỏ sáng | chấm đen | vòng tròn trắng viền nâu |
| `normal` | xám xanh nhạt | xám đá | nét đơn đen mảnh | nâu xám |
| `crowded` | cam | hồng | **nét đứt** đen đậm | đỏ |
| `covered` | xanh dương | xanh ngọc (cyan) | **nét đôi** | xanh lá |
| `closed` | nét nhạt + **X đỏ** | nét tối + **thanh chắn đỏ-trắng** | nét xám + **X đen** | nét nhạt + **X đỏ nâu** |
| bậc thang | vạch ngang đậm cắt qua đường | vạch vàng | vạch đen | vạch nâu đen |
| một chiều | 2 chevron trên nền đường | 2 chevron trắng | 2 chevron | 2 chevron |
| địa điểm | thẻ chữ viết tắt (TV, KTX…) | vòng tròn trắng có biểu tượng hình | **nhãn tên đầy đủ** ("Bãi xe") | huy hiệu tròn màu có viết tắt |
| robot | ghim tròn "R" + mũi chỉ hướng | tròn vàng "R" + mũi | tròn đen "R" + mũi | tròn cam "R" + mũi |

Ghi chú:
- Bậc thang và mũi tên một chiều được vẽ **đè lên** nét của trạng thái đường. Look và stairs/oneway là các đầu độc lập.
- `none` = **không có nét nào** giữa hai giao lộ. Đây là trường hợp khác với `closed`, vốn vẫn có nét nhạt kèm dấu chặn ở giữa đoạn. Trong lưới còn có các chỗ khuyết giao lộ ("hồ nước", vòng tròn xanh nhạt). Cặp kề nhau mà một đầu không tồn tại thì không được đưa vào EdgePatchNet.
- Màu của `normal` / `crowded` / `covered` trong ảnh hoán đổi lấy đúng từ bảng màu của style. Model chỉ cần học 3 kiểu vẽ mỗi style, rồi tra chú giải để ra trạng thái thật.

---

## 4. Thời tiết: 4 loại biểu tượng, nhãn 2 lớp

Biểu tượng thực tế có **4 loại**: mây mưa, mây, mặt trời, mặt trời + mây.

| nhãn `weather` | biểu tượng |
|---|---|
| `rain` | mây mưa |
| `dry` | mây, mặt trời, hoặc mặt trời + mây |

`scenes.json` chỉ có `rain` (39%) / `dry` (61%), và chiến thuật robot cũng chỉ cần mưa hay không. → **Đầu weather của CropClsNet dùng 2 lớp `rain`/`dry`**, không phải 3 lớp. Không có nhãn đầy đủ cho nắng / mây, chỉ có chữ chú giải ở ~18% cảnh.

---

## 5. Suy giảm chất lượng ảnh (degradation)

| | train | validation |
|---|---|---|
| bị xoay | 36,2% (±2,5°) | **57,3% (±3,0°)** |
| bị mờ | 21,4% (sigma ≤ 1,1) | **40,3%** (sigma ≤ 1,1, p75 = 0,7) |
| nén JPEG | 11,1% (quality 60–85) | **34,3% (quality 45–75, trung vị 57)** |

**Suy giảm phụ thuộc mạnh vào style** (train):
- `sketch`: 99,4% bị xoay, chỉ 9% bị mờ;
- `print`: 62,6% bị mờ;
- `classic` và `night`: phần lớn ảnh sạch.

Validation trộn đều hơn, ví dụ có `classic` vừa xoay vừa JPEG. Nếu chỉ dùng ảnh gốc, model có thể học nhầm tương quan "xoay ⇒ sketch" hoặc "mờ ⇒ print".

→ **Augmentation phải áp đều cho mọi style.** Mức mặc định (`--aug-strength medium`) phải bao phủ validation:
- xoay ±3,5° với p ≈ 0,6, tô màu nền;
- Gaussian blur sigma 0–1,2 với p ≈ 0,45;
- JPEG quality 40–90 với p ≈ 0,4;
- độ sáng/tương phản ±15%;
- nhiễu Gauss nhẹ.

Mức `strong` nới rộng thêm: xoay ±5°, blur 1,5, JPEG 30.

---

## 6. Lưới, giao lộ và địa điểm

| | train | validation |
|---|---|---|
| hàng / cột | 5–9 (TB 6,7 / 6,6) | 6–9 (TB 7,7 / 7,5) |
| giao lộ mỗi cảnh | 21–72 | 30–80 |
| giao lộ khuyết | 0–4 | 1–6 |
| cặp kề nhau (cả hai giao lộ tồn tại) | 141.485 | 26.738 |
| … trong đó không có cạnh (`none`) | 14,2% | 14,0% |
| … trong đó cạnh `closed` | 6,2% | 8,6% |

- Validation không có lưới 5 hàng hoặc 5 cột. Train có 5–9 nên vẫn bao phủ.
- Mỗi cảnh có 5–9 địa điểm; mỗi loại xuất hiện tối đa 2 lần. Trường hợp 2 bản: 26% (train) / 47,5% (val) theo loại.
- Hai địa điểm không bao giờ nằm chung một giao lộ.

---

## 7. Phân bố lớp và class weight (từ train)

| task | lớp hiếm | weight `inverse` | weight `sqrt_inverse` |
|---|---|---|---|
| look | `closed` 6,2% | 3,21 | 1,79 |
| stairs | `True` 7,8% | 6,44 | 2,54 |
| oneway | `forward` / `backward` ~2,7% mỗi lớp | ~12,3 | ~3,5 |
| landmark | `background` 83,8%; mỗi loại ~1,6% | background 0,11; mỗi loại ~5,6 | background 0,33; mỗi loại ~2,4 |
| có robot | `True` 2,3% | 21,5 | 4,6 |
| heading | cân bằng | ~1 | ~1 |
| legend kind | gần cân bằng (`weather` hiếm nhất, 3%) | ≤ 1,9 | – |
| weather | `rain` 39% | 1,28 | 1,13 |

Đề xuất mặc định: `--class-weights sqrt_inverse` cho landmark, robot, stairs và oneway; `none` cho heading, legend và weather. Toàn bộ số liệu nằm trong `DATA_NOTES_stats.md` §6.

---

## 8. Khác biệt so với mô tả nhiệm vụ (cần xác nhận)

1. **Weather 2 lớp thay vì 3.** Nhãn chỉ có `rain`/`dry`, trong khi biểu tượng có 4 loại.
2. **Legend có thêm kind `weather`.** Tổng là 18 lớp kind.
3. **`road_look` không bao giờ rỗng.** "Hoán đổi" được định nghĩa là khác ánh xạ đồng nhất.
4. **Suy giảm ảnh gắn với style** (sketch gần như luôn xoay, print đa số bị mờ). Augmentation cần áp đều.
5. **Thứ tự dòng chú giải cố định.** Có thể dùng làm phương án dự phòng khi đọc chú giải.
6. **`src/evaluate_pipeline.py` chưa tồn tại** trong repo. Bước 7 cần script này: chạy chiến thuật trên `predicted_scenes_*.json` và so với `labels.json`. Sẽ viết khi tới bước đó, dựa trên `src/evaluate_oracle.py`.
7. **Môi trường:** env `courier` hiện chỉ có Python 3.11 và Pillow 12; cần cài torch, timm, smp… ở bước 2. GPU Quadro RTX 8000 (48 GB) là **máy dùng chung**; lúc khảo sát, các tiến trình khác chiếm ~45 GB, chỉ còn ~3 GB. Batch mặc định ở mục 8 của nhiệm vụ (layout 8×1024², edge 512…) có thể không vừa nếu GPU vẫn bận như vậy.
