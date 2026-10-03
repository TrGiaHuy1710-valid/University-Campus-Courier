# Tổng quan dữ liệu: Phenikaa Campus Courier v2

Tài liệu này giải thích dữ liệu trông như thế nào, mỗi trường có ý nghĩa gì, và các con số thống kê nói lên điều gì cho cách giải. Mọi số liệu dưới đây được sinh bởi `data_stats.py` và lưu đầy đủ trong `stats.json`.

## 0. Cách chạy

```bash
python3 src/data_overview/data_stats.py      # in thống kê, ghi src/data_overview/stats.json
python3 src/data_overview/show_samples.py    # vẽ chú thích lên ảnh, lưu vào src/data_overview/samples/
python3 src/data_overview/show_samples.py --split validation --index 0 5 12
```

Mỗi ảnh trong `samples/` gồm bản gốc (bên trái) và bản có chú thích từ `scenes.json` (bên phải):
- chấm tím: tâm giao lộ;
- màu đường cho biết trạng thái **thật**: xám = thường, cam = đông, xanh = mái che, đỏ = đóng;
- `S` = bậc thang; vạch hồng = chiều đi được của đường một chiều;
- khung xanh lá và vàng: mẫu ký hiệu và chữ của chú giải;
- khung tím: biểu tượng thời tiết.

---

## 1. Bài toán trong một câu

Mỗi dòng dữ liệu gồm **ảnh bản đồ**, **câu yêu cầu tiếng Việt** và **robot_id (0–9)**. Cần dự đoán **bước đi đầu tiên** của robot: `0=UP, 1=DOWN, 2=LEFT, 3=RIGHT`. Đây là hướng tuyệt đối trên ảnh, không phải trái/phải theo hướng mặt robot.

```
ảnh ──► đồ thị lưới (đường, trạng thái, địa điểm, robot, thời tiết) ─┐
                                                                      ├─► chiến thuật robot_id ─► hướng đi
câu ──► (goal, via, tham chiếu, gấp?, dễ vỡ?) ────────────────────────┘
```

## 2. Các file và cách chúng liên kết

| split | dòng | cảnh | có nhãn | có `scenes.json` |
|---|---|---|---|---|
| train | 20.000 | 2.000 | có | có |
| validation | 3.000 | 300 | có | có |
| test | 12.000 | 1.200 | **không** | **không** |

- **`observations.json`**: danh sách dòng `{id, robot_id, image, mission}`. **Mỗi cảnh có đúng 10 dòng liên tiếp** (robot 0 → 9), dùng chung ảnh và câu. Vì vậy dòng `i` thuộc cảnh `i // 10` và là robot `i % 10`.
- **`labels.json`**: danh sách số nguyên, cùng thứ tự với `observations.json`.
- **`scenes.json`**: chú thích "đáp án" của từng cảnh, xếp theo thứ tự cảnh. Đây là file quan trọng nhất để học, vì nó cho biết ảnh vẽ cái gì và câu nói gì:
  - `grid`, `nodes[].rc` (hàng, cột) và `nodes[].xy` (pixel tâm giao lộ);
  - `edges[]`: `a`, `b`, `status` (normal/crowded/covered/closed), `stairs`, `oneway_to`;
  - `landmarks[]`: `type` và `rc`;
  - `robot`: `rc` và `heading`;
  - `weather`: rain/dry;
  - `mission`: `goal`, `via`, `goal_ref`, `via_ref`, `urgent`, `fragile`;
  - `legend[]`: khung pixel của mẫu ký hiệu và chữ chú giải;
  - `weather_box`: khung biểu tượng thời tiết;
  - `road_look`: chú giải có bị hoán đổi hay không;
  - `degradation`: độ xoay, độ mờ, chất lượng JPEG;
  - `style`: kiểu vẽ.
- **Test chỉ có ảnh và câu.** Hệ thống phải tự đọc ảnh và câu để dựng lại thông tin như `scenes.json`.

> Luật thi cấm dùng nội dung test (đọc câu, xem ảnh) để viết luật hoặc huấn luyện. Vì thế `data_stats.py` chỉ thống kê **cấu trúc** của test (số dòng, định dạng và kích thước ảnh), không đọc câu yêu cầu của test.

## 3. Ảnh

| | train | validation | test |
|---|---|---|---|
| PNG / JPEG | 1.778 / 222 | 197 / 103 | 814 / 386 |
| số kích thước khác nhau | 36 | 26 | 37 |
| kích thước phổ biến | 1152×864, 1024×768, 1120×840 | 1152×864, 1120×840 | 1152×864, 1120×840 |
| bị xoay | 36,2% (±2,5°) | 57,3% (±3,0°) | – |
| bị mờ | 21,4% | 40,3% | – |
| nén JPEG (chất lượng) | 11,1% (60–85, trung vị 73) | 34,3% (45–75, trung vị 57) | – |

- Có **4 kiểu vẽ** (`classic`, `night`, `print`, `sketch`), mỗi kiểu chiếm khoảng 25%. Mỗi kiểu có bảng màu, cách vẽ địa điểm, phông chữ và vị trí chú giải riêng. Ngay cả câu chữ trong chú giải cũng khác nhau, ví dụ "Đường thường" / "Lối đi thường", "Đường đóng" / "Cấm đi / đang sửa".
- PNG lưu dạng palette, nên phải đọc bằng `Image.open(p).convert("RGB")`.
- **Ảnh validation xấu hơn train rất nhiều:** xoay nhiều hơn, mờ nhiều hơn, JPEG nén mạnh hơn. Test nhiều JPEG như validation (32%). Mô hình CV phải được augment (xoay, mờ, nén JPEG) mạnh hơn mức của train.

### Chú giải bị hoán đổi (`road_look`)

| | train | validation |
|---|---|---|
| cảnh có hoán đổi | **14,7%** | **34,7%** |

`road_look = {"crowded": "covered"}` nghĩa là trong ảnh này, đường đông được vẽ giống kiểu "mái che" thông thường. Có 5 kiểu hoán đổi (hoán vị của normal/crowded/covered), xuất hiện với tần suất gần bằng nhau. Riêng đường đóng không bao giờ bị hoán đổi.

→ **Không thể học "màu cam = đông"**. Phải so kiểu nét của từng đoạn đường với mẫu ký hiệu trong chú giải của **chính ảnh đó**.

## 4. Lưới đường

| | train | validation |
|---|---|---|
| số hàng | 5–9 (TB 6,7) | 6–9 (TB 7,7) |
| số cột | 5–9 (TB 6,6) | 6–9 (TB 7,5) |
| giao lộ bị thiếu mỗi cảnh | 0–4 (TB 1,5) | 1–6 (TB 3,2) |
| số đoạn đường mỗi cảnh | 22–116 (TB 61) | 36–133 (TB 77) |
| tỉ lệ đoạn có so với lưới đầy | ~80% | ~77% |

Tỉ lệ trạng thái đoạn đường:

| trạng thái | train | validation |
|---|---|---|
| normal (thường) | 46,4% | 36,5% |
| covered (mái che) | 24,2% | 27,5% |
| crowded (đông) | 22,2% | 26,1% |
| closed (đóng) | 7,2% | 10,0% |
| có bậc thang | 7,8% | 10,6% |
| một chiều | 5,4% | 7,2% |

Bản đồ validation **lớn hơn và nhiều "chướng ngại" hơn** (đóng, bậc thang, một chiều). Chỉ cần đọc sai một đoạn trên đường đi là có thể sai hướng của nhiều robot cùng lúc.

## 5. Địa điểm

- Mỗi cảnh có 5–9 địa điểm (trung bình 7), thuộc 10 loại; tần suất các loại gần như đều nhau.
- **Địa điểm trùng loại rất phổ biến:** 85,5% cảnh train và **100% cảnh validation** có ít nhất một loại xuất hiện 2 lần.
- Địa điểm đích bị trùng trên bản đồ: **26,4%** ở train và **49,3%** ở validation. Lúc đó phải xác định đúng bản nào, bằng tham chiếu trong câu, hoặc theo chiến thuật nếu câu không chỉ rõ.

| ký hiệu | loại | | ký hiệu | loại |
|---|---|---|---|---|
| TV | library | | XE | parking |
| KTX | dorm | | GĐ | lecture |
| TT | sports | | TN | lab |
| YT | clinic | | HC | office |
| CA | canteen | | CT | gate |

## 6. Robot và thời tiết

- Hướng mũi robot phân bố đều 4 hướng, mỗi hướng khoảng 25%.
- Trời mưa: 39% ở train và 37% ở validation. Mưa ảnh hưởng tới robot 3 (Mây Mưa) và robot 4 (Sơn Dương).

## 7. Câu yêu cầu (mission)

| | train | validation |
|---|---|---|
| độ dài (từ) | 6–50, trung vị 22 | 7–60, trung vị **34** |
| câu **không dấu** | 12,1% | **24,7%** |
| có từ phủ định (không/đừng/chưa…) | 39,4% | **80,7%** |
| có điểm ghé (via) | 31,5% | **50,3%** |
| có tham chiếu cho goal | 12% (240) | **39% (116)** |
| có tham chiếu cho via | 4% (85) | **18% (55)** |
| gấp (urgent) | 39,0% | 38,3% |
| dễ vỡ (fragile) | 40,1% | 36,7% |

- Các loại tham chiếu: `north/south/east/west` (bản nằm xa nhất về phía đó) và `near/far` (gần hoặc xa một địa điểm mốc hơn). Tần suất các loại khá đều.
- Ví dụ một câu khó trong validation, có đủ phủ định, gây nhiễu và không dấu:
  > *"Robot oi, khong can ghe day phong hoc. Bep truong o cang tin man tren dang cho hop giay. Dung nham voi phong lab nhe. Do khong vo duoc dau. Dang can gap lam."*
  > → goal = canteen (bản phía **bắc**), via = không có, urgent = **có**, fragile = **không**
- Đề nói rõ validation và test có **cách diễn đạt không có trong train**. Mô hình NLP chỉ học thuộc từ khóa của train sẽ không đủ.

## 8. Nhãn và mức độ bất đồng giữa các robot

Hướng đi tuyệt đối gần như đều 25% cho mỗi lớp, ở mọi robot. Vì vậy đoán theo lớp phổ biến nhất chỉ được khoảng 25%, đúng như baseline của starter.

Thú vị hơn là bước đi so với **hướng mũi robot** (train):

| robot | thẳng | rẽ phải | rẽ trái | quay đầu | giống robot 0 |
|---|---|---|---|---|---|
| 0 Tia Chớp | 25,8 | 21,3 | 22,9 | 30,0 | 100 |
| 1 Yên Tĩnh | 17,5 | 21,5 | 24,8 | 36,2 | 69,0 |
| 2 Mái Hiên | 18,2 | 20,9 | 23,9 | 37,0 | 84,7 |
| 3 Mây Mưa | 19,2 | 21,4 | 23,9 | 35,5 | 79,2 |
| 4 Sơn Dương | 20,8 | 21,4 | 23,6 | 34,2 | 70,0 |
| 5 Thẳng Tắp | 34,8 | 30,4 | 30,7 | **4,2** | 69,5 |
| 6 Hỏa Tốc | 18,0 | 20,8 | 24,9 | 36,4 | 77,8 |
| 7 Nâng Niu | 25,8 | 25,8 | 27,1 | 21,4 | 84,5 |
| 8 Lề Phải | 29,7 | **35,7** | **18,6** | 16,0 | 74,3 |
| 9 Tham Lam | 26,6 | 22,8 | 25,8 | 24,9 | 55,2 |

Bảng này đã gợi ý chiến thuật của từng robot ngay từ nhãn:
- **Robot 5** gần như không bao giờ quay đầu (4,2%), vì nó rất ghét đổi hướng.
- **Robot 8** rẽ phải nhiều gấp đôi rẽ trái, đúng với tên "Lề Phải".
- **Robot 9** khác robot 0 nhiều nhất (chỉ giống 55%), vì nó chỉ nhìn một bước.

Số hướng khác nhau mà 10 robot chọn trong cùng một cảnh:

| | 1 hướng (cả 10 đồng ý) | 2 | 3 | 4 |
|---|---|---|---|---|
| train | 10,8% | 71,8% | 16,9% | 0,4% |
| validation | **3,0%** | 72,3% | 22,0% | 2,7% |

Ở validation, các robot bất đồng nhiều hơn hẳn. Mức "giống robot 0" của robot 1 giảm từ 69% xuống 36%, của robot 4 từ 70% xuống 43%. Một mô hình gần như đoán chung cho mọi robot sẽ tụt điểm mạnh trên validation và test.

## 9. Train và validation khác nhau thế nào? (tóm tắt)

| khía cạnh | validation so với train |
|---|---|
| bản đồ | lớn hơn (~7,6 hàng/cột so với 6,7), nhiều giao lộ thiếu hơn |
| đường | nhiều đoạn đóng, bậc thang, một chiều hơn |
| ảnh | xoay, mờ, nén JPEG nhiều hơn; chú giải hoán đổi 35% (train 15%) |
| địa điểm | 100% cảnh có địa điểm trùng; 49% đích bị trùng |
| câu | dài hơn ~50%, gấp đôi tỉ lệ không dấu, 81% có phủ định, 50% có via |
| nhãn | robot bất đồng nhiều hơn |

Đề cho biết test giống validation (profile "hard"). Vì vậy **luôn đo trên validation**, không tin điểm train.

## 10. Ý nghĩa cho cách giải

1. **Khâu chiến thuật đã xong:** `policy_params.json` đạt 100% trên train và validation khi dùng `scenes.json`. Phần còn lại của điểm phụ thuộc hoàn toàn vào việc đọc ảnh và đọc câu.
2. **NLP:** đầu ra là một bộ trường cố định. Cần xử lý câu không dấu, phủ định, thứ tự "ghé… trước", tham chiếu không gian và địa điểm gây nhiễu.
3. **CV:** phải đọc chú giải của từng ảnh (do có hoán đổi) và chịu được xoay, mờ, JPEG. Độ chính xác từng đoạn đường cần rất cao, vì mỗi bản đồ có khoảng 60–130 đoạn.
4. **Ưu tiên kiểm tra:** sai một trường trong câu (ví dụ goal) làm sai cả 10 robot; sai một đoạn đường thường chỉ làm sai vài robot.
