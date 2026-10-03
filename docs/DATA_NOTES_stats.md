# Thống kê dữ liệu cho khâu CV (sinh tự động bởi `src/inspect_data.py`)

Đọc kèm `docs/DATA_NOTES.md` (phần diễn giải và các quy ước đã chốt).


## 1. Kích thước

| split | cảnh |
|---|---|
| train | 2000 |
| validation | 300 |

### Style

| giá trị | train | validation |
|---|---|---|
| classic | 520 (26.0%) | 80 (26.7%) |
| night | 506 (25.3%) | 77 (25.7%) |
| print | 478 (23.9%) | 71 (23.7%) |
| sketch | 496 (24.8%) | 72 (24.0%) |

### Định dạng file ảnh

| giá trị | train | validation |
|---|---|---|
| jpg | 222 (11.1%) | 103 (34.3%) |
| png | 1778 (88.9%) | 197 (65.7%) |

### Kích thước ảnh (top)

| giá trị | train | validation |
|---|---|---|
| 1152x864 | 507 (25.4%) | 102 (34.0%) |
| 1024x768 | 479 (23.9%) | 35 (11.7%) |
| 1120x840 | 438 (21.9%) | 49 (16.3%) |
| 1024x1024 | 172 (8.6%) | 22 (7.3%) |
| 960x960 | 125 (6.2%) | 10 (3.3%) |
| 1024x896 | 121 (6.0%) | 12 (4.0%) |
| 1136x848 | 25 (1.2%) | 17 (5.7%) |
| 992x992 | 17 (0.8%) | 2 (0.7%) |
| 1136x864 | 9 (0.5%) | 6 (2.0%) |
| 1136x992 | 12 (0.6%) | 3 (1.0%) |
| 1120x848 | 6 (0.3%) | 9 (3.0%) |
| 1104x832 | 12 (0.6%) | 1 (0.3%) |

### Lưới hàng×cột (top)

| giá trị | train | validation |
|---|---|---|
| 7x8 | 132 (6.6%) | 21 (7.0%) |
| 8x7 | 127 (6.3%) | 21 (7.0%) |
| 8x8 | 128 (6.4%) | 20 (6.7%) |
| 6x6 | 123 (6.2%) | 16 (5.3%) |
| 7x6 | 117 (5.8%) | 18 (6.0%) |
| 6x7 | 115 (5.8%) | 19 (6.3%) |
| 8x6 | 119 (6.0%) | 14 (4.7%) |
| 6x8 | 111 (5.5%) | 17 (5.7%) |
| 7x7 | 112 (5.6%) | 10 (3.3%) |
| 8x5 | 120 (6.0%) | 0 (0.0%) |
| 7x5 | 120 (6.0%) | 0 (0.0%) |
| 6x5 | 108 (5.4%) | 0 (0.0%) |
| 5x7 | 107 (5.3%) | 0 (0.0%) |
| 5x8 | 106 (5.3%) | 0 (0.0%) |
| 5x6 | 89 (4.5%) | 0 (0.0%) |

### Số giao lộ mỗi cảnh

| split | min / p5 / p25 / median / p75 / p95 / max |
|---|---|
| train | 21 / 26 / 35 / 41 / 52 / 63 / 72 |
| validation | 30 / 35 / 45 / 53 / 62 / 76 / 80 |

### Số giao lộ khuyết mỗi cảnh

| split | min / p5 / p25 / median / p75 / p95 / max |
|---|---|
| train | 0 / 0 / 0 / 1 / 3 / 4 / 4 |
| validation | 1 / 1 / 2 / 3 / 5 / 6 / 6 |

### Số địa điểm mỗi cảnh

| split | min / p5 / p25 / median / p75 / p95 / max |
|---|---|
| train | 5 / 5 / 6 / 7 / 8 / 9 / 9 |
| validation | 5 / 5 / 6 / 7 / 8 / 9 / 9 |

### Số dòng chú giải mỗi cảnh

| split | min / p5 / p25 / median / p75 / p95 / max |
|---|---|
| train | 11 / 11 / 12 / 13 / 14 / 15 / 17 |
| validation | 11 / 11 / 11 / 12 / 13 / 14 / 15 |

## 2. Khoảng cách d giữa hai giao lộ kề nhau (pixel, trung vị mỗi cảnh)

| split | style | min / p5 / p25 / median / p75 / p95 / max |
|---|---|---|
| train | classic | 85.2 / 87.7 / 97.7 / 110 / 127 / 156 / 185 |
| train | night | 85 / 87.9 / 98.3 / 108 / 124 / 148 / 183 |
| train | print | 84.7 / 88.7 / 97.3 / 109 / 130 / 164 / 180 |
| train | sketch | 84.4 / 88.8 / 98.3 / 111 / 129 / 156 / 182 |
| validation | classic | 85.1 / 85.9 / 92 / 97.6 / 104 / 138 / 149 |
| validation | night | 85.6 / 87.2 / 92.6 / 98.4 / 114 / 130 / 146 |
| validation | print | 85.8 / 86.6 / 91.1 / 97.5 / 112 / 126 / 141 |
| validation | sketch | 84.7 / 85.8 / 92.6 / 98.6 / 111 / 130 / 142 |

### d / cạnh ngắn của ảnh

| split | min / p5 / p25 / median / p75 / p95 / max |
|---|---|
| train | 0.0751 / 0.0958 / 0.116 / 0.129 / 0.148 / 0.181 / 0.207 |
| validation | 0.0749 / 0.084 / 0.105 / 0.114 / 0.127 / 0.15 / 0.164 |

### Độ lệch tâm giao lộ khỏi hàng/cột thẳng (theo d, gồm cả ảnh xoay)

| split | min / p5 / p25 / median / p75 / p95 / max |
|---|---|
| train | 0 / 0 / 0.00441 / 0.0166 / 0.0394 / 0.0885 / 0.258 |
| validation | 0 / 0 / 0.00777 / 0.0291 / 0.0685 / 0.15 / 0.342 |

## 3. Suy giảm chất lượng ảnh (degradation)


### Tỉ lệ cảnh bị suy giảm (đếm cờ)

| giá trị | train | validation |
|---|---|---|
| rotated | 724 (52.7%) | 172 (43.4%) |
| blur | 428 (31.1%) | 121 (30.6%) |
| jpeg | 222 (16.2%) | 103 (26.0%) |

(tỉ lệ ở bảng trên là trên tổng số cờ; tỉ lệ trên số cảnh:)

- train: xoay 36.2%, mờ 21.4%, JPEG 11.1%
- validation: xoay 57.3%, mờ 40.3%, JPEG 34.3%

### Suy giảm theo style (style, xoay, mờ, jpeg)

| giá trị | train | validation |
|---|---|---|
| ('classic', '-', '-', '-') | 375 (18.8%) | 23 (7.7%) |
| ('classic', '-', '-', 'jpeg') | 36 (1.8%) | 9 (3.0%) |
| ('classic', '-', 'blur', '-') | 23 (1.1%) | 7 (2.3%) |
| ('classic', '-', 'blur', 'jpeg') | 6 (0.3%) | 2 (0.7%) |
| ('classic', 'rotated', '-', '-') | 64 (3.2%) | 18 (6.0%) |
| ('classic', 'rotated', '-', 'jpeg') | 8 (0.4%) | 15 (5.0%) |
| ('classic', 'rotated', 'blur', '-') | 6 (0.3%) | 3 (1.0%) |
| ('classic', 'rotated', 'blur', 'jpeg') | 2 (0.1%) | 3 (1.0%) |
| ('night', '-', '-', '-') | 343 (17.1%) | 22 (7.3%) |
| ('night', '-', '-', 'jpeg') | 46 (2.3%) | 6 (2.0%) |
| ('night', '-', 'blur', '-') | 38 (1.9%) | 14 (4.7%) |
| ('night', '-', 'blur', 'jpeg') | 4 (0.2%) | 6 (2.0%) |
| ('night', 'rotated', '-', '-') | 63 (3.1%) | 10 (3.3%) |
| ('night', 'rotated', '-', 'jpeg') | 7 (0.3%) | 9 (3.0%) |
| ('night', 'rotated', 'blur', '-') | 5 (0.2%) | 6 (2.0%) |
| ('night', 'rotated', 'blur', 'jpeg') | 0 (0.0%) | 4 (1.3%) |
| ('print', '-', '-', '-') | 132 (6.6%) | 8 (2.7%) |
| ('print', '-', '-', 'jpeg') | 20 (1.0%) | 4 (1.3%) |
| ('print', '-', 'blur', '-') | 217 (10.8%) | 17 (5.7%) |
| ('print', '-', 'blur', 'jpeg') | 33 (1.6%) | 10 (3.3%) |
| ('print', 'rotated', '-', '-') | 24 (1.2%) | 8 (2.7%) |
| ('print', 'rotated', '-', 'jpeg') | 3 (0.1%) | 3 (1.0%) |
| ('print', 'rotated', 'blur', '-') | 44 (2.2%) | 12 (4.0%) |
| ('print', 'rotated', 'blur', 'jpeg') | 5 (0.2%) | 9 (3.0%) |
| ('sketch', '-', '-', '-') | 2 (0.1%) | 0 (0.0%) |
| ('sketch', '-', 'blur', '-') | 1 (0.1%) | 0 (0.0%) |
| ('sketch', 'rotated', '-', '-') | 401 (20.1%) | 28 (9.3%) |
| ('sketch', 'rotated', '-', 'jpeg') | 48 (2.4%) | 16 (5.3%) |
| ('sketch', 'rotated', 'blur', '-') | 40 (2.0%) | 21 (7.0%) |
| ('sketch', 'rotated', 'blur', 'jpeg') | 4 (0.2%) | 7 (2.3%) |

### Góc xoay (độ, mọi cảnh)

| split | min / p5 / p25 / median / p75 / p95 / max |
|---|---|
| train | -2.5 / -1.51 / 0 / 0 / 0 / 1.43 / 2.48 |
| validation | -2.98 / -2.56 / -0.39 / 0 / 0.3 / 2.37 / 3 |

### Blur (sigma, mọi cảnh)

| split | min / p5 / p25 / median / p75 / p95 / max |
|---|---|
| train | 0 / 0 / 0 / 0 / 0 / 0.76 / 1.1 |
| validation | 0 / 0 / 0 / 0 / 0.7 / 0.99 / 1.09 |

### Chất lượng JPEG (chỉ cảnh có nén)

| split | min / p5 / p25 / median / p75 / p95 / max |
|---|---|
| train | 60 / 61 / 67 / 73 / 80 / 84 / 85 |
| validation | 45 / 46 / 51 / 57 / 66 / 71 / 75 |

## 4. Chú giải hoán đổi (road_look)


### Cảnh có road_look khác ánh xạ đồng nhất

| giá trị | train | validation |
|---|---|---|
| False | 1706 (85.3%) | 196 (65.3%) |
| True | 294 (14.7%) | 104 (34.7%) |

### road_look (mọi mẫu)

| giá trị | train | validation |
|---|---|---|
| {"covered": "covered", "crowded": "crowded", "normal": "normal"} | 1706 (85.3%) | 196 (65.3%) |
| {"covered": "covered", "crowded": "normal", "normal": "crowded"} | 69 (3.5%) | 19 (6.3%) |
| {"covered": "crowded", "crowded": "covered", "normal": "normal"} | 67 (3.4%) | 24 (8.0%) |
| {"covered": "crowded", "crowded": "normal", "normal": "covered"} | 54 (2.7%) | 18 (6.0%) |
| {"covered": "normal", "crowded": "covered", "normal": "crowded"} | 42 (2.1%) | 22 (7.3%) |
| {"covered": "normal", "crowded": "crowded", "normal": "covered"} | 62 (3.1%) | 21 (7.0%) |

### Hoán đổi theo style

| giá trị | train | validation |
|---|---|---|
| ('classic', False) | 439 (21.9%) | 52 (17.3%) |
| ('classic', True) | 81 (4.0%) | 28 (9.3%) |
| ('night', False) | 437 (21.9%) | 55 (18.3%) |
| ('night', True) | 69 (3.5%) | 22 (7.3%) |
| ('print', False) | 404 (20.2%) | 41 (13.7%) |
| ('print', True) | 74 (3.7%) | 30 (10.0%) |
| ('sketch', False) | 426 (21.3%) | 48 (16.0%) |
| ('sketch', True) | 70 (3.5%) | 24 (8.0%) |

### status → look (trên các cạnh thật)

| giá trị | train | validation |
|---|---|---|
| ('closed', 'closed') | 8803 (7.2%) | 2299 (10.0%) |
| ('covered', 'covered') | 26092 (21.5%) | 4499 (19.6%) |
| ('covered', 'crowded') | 1781 (1.5%) | 947 (4.1%) |
| ('covered', 'normal') | 1542 (1.3%) | 870 (3.8%) |
| ('crowded', 'covered') | 1637 (1.3%) | 941 (4.1%) |
| ('crowded', 'crowded') | 23669 (19.5%) | 4350 (18.9%) |
| ('crowded', 'normal') | 1630 (1.3%) | 705 (3.1%) |
| ('normal', 'covered') | 3251 (2.7%) | 1044 (4.5%) |
| ('normal', 'crowded') | 3243 (2.7%) | 1103 (4.8%) |
| ('normal', 'normal') | 49798 (41.0%) | 6243 (27.1%) |

### Dòng chú giải (kind → look của swatch)

| giá trị | train | validation |
|---|---|---|
| ('covered', 'covered') | 1775 (29.6%) | 215 (23.9%) |
| ('covered', 'crowded') | 121 (2.0%) | 42 (4.7%) |
| ('covered', 'normal') | 104 (1.7%) | 43 (4.8%) |
| ('crowded', 'covered') | 109 (1.8%) | 46 (5.1%) |
| ('crowded', 'crowded') | 1768 (29.5%) | 217 (24.1%) |
| ('crowded', 'normal') | 123 (2.0%) | 37 (4.1%) |
| ('normal', 'covered') | 116 (1.9%) | 39 (4.3%) |
| ('normal', 'crowded') | 111 (1.9%) | 41 (4.6%) |
| ('normal', 'normal') | 1773 (29.6%) | 220 (24.4%) |

## 5. Cặp giao lộ kề nhau: có cạnh / không có cạnh / đóng


### Cặp kề nhau (cả hai giao lộ tồn tại)

| giá trị | train | validation |
|---|---|---|
| edge | 121446 (85.8%) | 23001 (86.0%) |
| no_edge | 20039 (14.2%) | 3737 (14.0%) |

### Trạng thái cạnh (status)

| giá trị | train | validation |
|---|---|---|
| normal | 56292 (46.4%) | 8390 (36.5%) |
| crowded | 26936 (22.2%) | 5996 (26.1%) |
| covered | 29415 (24.2%) | 6316 (27.5%) |
| closed | 8803 (7.2%) | 2299 (10.0%) |

## 6. Phân bố lớp cho từng task


### EdgePatchNet / look (gồm none = không có đường)

| giá trị | train | validation |
|---|---|---|
| none | 20039 (14.2%) | 3737 (14.0%) |
| normal | 52970 (37.4%) | 7818 (29.2%) |
| crowded | 28693 (20.3%) | 6400 (23.9%) |
| covered | 30980 (21.9%) | 6484 (24.3%) |
| closed | 8803 (6.2%) | 2299 (8.6%) |

Class weight (train): `none`: inv=1.41, sqrt=1.19, `normal`: inv=0.53, sqrt=0.73, `crowded`: inv=0.99, sqrt=0.99, `covered`: inv=0.91, sqrt=0.96, `closed`: inv=3.21, sqrt=1.79

### EdgePatchNet / stairs (trên cạnh thật)

| giá trị | train | validation |
|---|---|---|
| False | 112022 (92.2%) | 20570 (89.4%) |
| True | 9424 (7.8%) | 2431 (10.6%) |

Class weight (train): `False`: inv=0.54, sqrt=0.74, `True`: inv=6.44, sqrt=2.54

### EdgePatchNet / oneway (forward = đi được a→b)

| giá trị | train | validation |
|---|---|---|
| none | 114862 (94.6%) | 21348 (92.8%) |
| forward | 3225 (2.7%) | 788 (3.4%) |
| backward | 3359 (2.8%) | 865 (3.8%) |

Class weight (train): `none`: inv=0.35, sqrt=0.59, `forward`: inv=12.55, sqrt=3.54, `backward`: inv=12.05, sqrt=3.47

### NodePatchNet / landmark theo giao lộ

| giá trị | train | validation |
|---|---|---|
| background | 72042 (83.8%) | 14200 (87.3%) |
| library | 1422 (1.7%) | 194 (1.2%) |
| dorm | 1385 (1.6%) | 205 (1.3%) |
| sports | 1338 (1.6%) | 246 (1.5%) |
| clinic | 1383 (1.6%) | 195 (1.2%) |
| canteen | 1412 (1.6%) | 221 (1.4%) |
| parking | 1356 (1.6%) | 190 (1.2%) |
| lecture | 1394 (1.6%) | 199 (1.2%) |
| lab | 1408 (1.6%) | 207 (1.3%) |
| office | 1465 (1.7%) | 199 (1.2%) |
| gate | 1336 (1.6%) | 215 (1.3%) |

Class weight (train): `background`: inv=0.11, sqrt=0.33, `library`: inv=5.49, sqrt=2.34, `dorm`: inv=5.64, sqrt=2.38, `sports`: inv=5.84, sqrt=2.42, `clinic`: inv=5.65, sqrt=2.38, `canteen`: inv=5.53, sqrt=2.35, `parking`: inv=5.76, sqrt=2.40, `lecture`: inv=5.60, sqrt=2.37, `lab`: inv=5.55, sqrt=2.36, `office`: inv=5.33, sqrt=2.31, `gate`: inv=5.85, sqrt=2.42

### NodePatchNet / có robot

| giá trị | train | validation |
|---|---|---|
| False | 83941 (97.7%) | 15971 (98.2%) |
| True | 2000 (2.3%) | 300 (1.8%) |

Class weight (train): `False`: inv=0.51, sqrt=0.72, `True`: inv=21.49, sqrt=4.64

### NodePatchNet / heading (trên giao lộ có robot)

| giá trị | train | validation |
|---|---|---|
| UP | 504 (25.2%) | 69 (23.0%) |
| DOWN | 492 (24.6%) | 79 (26.3%) |
| LEFT | 503 (25.1%) | 76 (25.3%) |
| RIGHT | 501 (25.1%) | 76 (25.3%) |

Class weight (train): `UP`: inv=0.99, sqrt=1.00, `DOWN`: inv=1.02, sqrt=1.01, `LEFT`: inv=0.99, sqrt=1.00, `RIGHT`: inv=1.00, sqrt=1.00

### CropClsNet / legend kind

| giá trị | train | validation |
|---|---|---|
| closed | 2000 (7.8%) | 300 (8.3%) |
| covered | 2000 (7.8%) | 300 (8.3%) |
| crowded | 2000 (7.8%) | 300 (8.3%) |
| normal | 2000 (7.8%) | 300 (8.3%) |
| oneway | 2000 (7.8%) | 300 (8.3%) |
| place:canteen | 1109 (4.3%) | 152 (4.2%) |
| place:clinic | 1094 (4.2%) | 136 (3.7%) |
| place:dorm | 1103 (4.3%) | 138 (3.8%) |
| place:gate | 1067 (4.1%) | 142 (3.9%) |
| place:lab | 1114 (4.3%) | 138 (3.8%) |
| place:lecture | 1108 (4.3%) | 133 (3.7%) |
| place:library | 1141 (4.4%) | 132 (3.6%) |
| place:office | 1137 (4.4%) | 140 (3.9%) |
| place:parking | 1085 (4.2%) | 132 (3.6%) |
| place:sports | 1067 (4.1%) | 161 (4.4%) |
| robot | 2000 (7.8%) | 300 (8.3%) |
| stairs | 2000 (7.8%) | 300 (8.3%) |
| weather | 771 (3.0%) | 131 (3.6%) |

Class weight (train): `closed`: inv=0.72, sqrt=0.85, `covered`: inv=0.72, sqrt=0.85, `crowded`: inv=0.72, sqrt=0.85, `normal`: inv=0.72, sqrt=0.85, `oneway`: inv=0.72, sqrt=0.85, `place:canteen`: inv=1.29, sqrt=1.14, `place:clinic`: inv=1.31, sqrt=1.14, `place:dorm`: inv=1.30, sqrt=1.14, `place:gate`: inv=1.34, sqrt=1.16, `place:lab`: inv=1.29, sqrt=1.13, `place:lecture`: inv=1.29, sqrt=1.14, `place:library`: inv=1.26, sqrt=1.12, `place:office`: inv=1.26, sqrt=1.12, `place:parking`: inv=1.32, sqrt=1.15, `place:sports`: inv=1.34, sqrt=1.16, `robot`: inv=0.72, sqrt=0.85, `stairs`: inv=0.72, sqrt=0.85, `weather`: inv=1.86, sqrt=1.36

### CropClsNet / weather

| giá trị | train | validation |
|---|---|---|
| dry | 1221 (61.0%) | 188 (62.7%) |
| rain | 779 (39.0%) | 112 (37.3%) |

Class weight (train): `dry`: inv=0.82, sqrt=0.90, `rain`: inv=1.28, sqrt=1.13

### Look theo style (gồm none)

| giá trị | train | validation |
|---|---|---|
| ('classic', 'closed') | 2307 (1.6%) | 610 (2.3%) |
| ('classic', 'covered') | 7847 (5.5%) | 1803 (6.7%) |
| ('classic', 'crowded') | 7512 (5.3%) | 1629 (6.1%) |
| ('classic', 'none') | 5123 (3.6%) | 996 (3.7%) |
| ('classic', 'normal') | 13654 (9.7%) | 2201 (8.2%) |
| ('night', 'closed') | 2241 (1.6%) | 586 (2.2%) |
| ('night', 'covered') | 7886 (5.6%) | 1475 (5.5%) |
| ('night', 'crowded') | 7411 (5.2%) | 1667 (6.2%) |
| ('night', 'none') | 5148 (3.6%) | 847 (3.2%) |
| ('night', 'normal') | 13694 (9.7%) | 2018 (7.5%) |
| ('print', 'closed') | 2100 (1.5%) | 538 (2.0%) |
| ('print', 'covered') | 7557 (5.3%) | 1659 (6.2%) |
| ('print', 'crowded') | 6758 (4.8%) | 1610 (6.0%) |
| ('print', 'none') | 4924 (3.5%) | 966 (3.6%) |
| ('print', 'normal') | 12593 (8.9%) | 1722 (6.4%) |
| ('sketch', 'closed') | 2155 (1.5%) | 565 (2.1%) |
| ('sketch', 'covered') | 7690 (5.4%) | 1547 (5.8%) |
| ('sketch', 'crowded') | 7012 (5.0%) | 1494 (5.6%) |
| ('sketch', 'none') | 4844 (3.4%) | 928 (3.5%) |
| ('sketch', 'normal') | 13029 (9.2%) | 1877 (7.0%) |

### Oneway theo hướng đoạn

| giá trị | train | validation |
|---|---|---|
| ('horizontal', 'backward') | 1681 (1.4%) | 450 (2.0%) |
| ('horizontal', 'forward') | 1615 (1.3%) | 405 (1.8%) |
| ('horizontal', 'none') | 57373 (47.2%) | 10657 (46.3%) |
| ('vertical', 'backward') | 1678 (1.4%) | 415 (1.8%) |
| ('vertical', 'forward') | 1610 (1.3%) | 383 (1.7%) |
| ('vertical', 'none') | 57489 (47.3%) | 10691 (46.5%) |

### Số bản của một loại địa điểm trên cùng bản đồ

| giá trị | train | validation |
|---|---|---|
| 1 | 8151 (73.9%) | 737 (52.5%) |
| 2 | 2874 (26.1%) | 667 (47.5%) |

## 7. Chú giải và thời tiết: vị trí, kích thước


### Vị trí khối chú giải (style, ngang, dọc)

| giá trị | train | validation |
|---|---|---|
| ('classic', 'left', 'bottom') | 145 (7.2%) | 14 (4.7%) |
| ('classic', 'left', 'top') | 131 (6.5%) | 27 (9.0%) |
| ('classic', 'right', 'top') | 244 (12.2%) | 39 (13.0%) |
| ('night', 'left', 'bottom') | 109 (5.5%) | 27 (9.0%) |
| ('night', 'left', 'top') | 130 (6.5%) | 17 (5.7%) |
| ('night', 'right', 'top') | 267 (13.3%) | 33 (11.0%) |
| ('print', 'left', 'bottom') | 137 (6.8%) | 22 (7.3%) |
| ('print', 'left', 'top') | 120 (6.0%) | 11 (3.7%) |
| ('print', 'right', 'top') | 221 (11.1%) | 38 (12.7%) |
| ('sketch', 'left', 'bottom') | 129 (6.5%) | 14 (4.7%) |
| ('sketch', 'left', 'top') | 119 (6.0%) | 18 (6.0%) |
| ('sketch', 'right', 'top') | 248 (12.4%) | 40 (13.3%) |

### Vị trí biểu tượng thời tiết

| giá trị | train | validation |
|---|---|---|
| ('classic', 'left', 'bottom') | 62 (3.1%) | 5 (1.7%) |
| ('classic', 'left', 'top') | 64 (3.2%) | 13 (4.3%) |
| ('classic', 'right', 'top') | 394 (19.7%) | 62 (20.7%) |
| ('night', 'left', 'bottom') | 43 (2.1%) | 9 (3.0%) |
| ('night', 'left', 'top') | 54 (2.7%) | 7 (2.3%) |
| ('night', 'right', 'top') | 409 (20.4%) | 61 (20.3%) |
| ('print', 'left', 'bottom') | 50 (2.5%) | 9 (3.0%) |
| ('print', 'left', 'top') | 50 (2.5%) | 6 (2.0%) |
| ('print', 'right', 'top') | 378 (18.9%) | 56 (18.7%) |
| ('sketch', 'left', 'bottom') | 51 (2.5%) | 3 (1.0%) |
| ('sketch', 'left', 'top') | 52 (2.6%) | 6 (2.0%) |
| ('sketch', 'right', 'top') | 393 (19.6%) | 63 (21.0%) |

### Thứ tự dòng chú giải (place* = khối địa điểm liên tiếp)

| giá trị | train | validation |
|---|---|---|
| place* > normal > crowded > covered > closed > stairs > oneway > robot | 1229 (61.5%) | 169 (56.3%) |
| weather > place* > normal > crowded > covered > closed > stairs > oneway > robot | 771 (38.5%) | 131 (43.7%) |

### Swatch rộng / d

| split | min / p5 / p25 / median / p75 / p95 / max |
|---|---|
| train | 0.2 / 0.309 / 0.415 / 0.496 / 0.564 / 0.633 / 0.732 |
| validation | 0.294 / 0.395 / 0.5 / 0.595 / 0.651 / 0.703 / 0.738 |

### Swatch cao / d

| split | min / p5 / p25 / median / p75 / p95 / max |
|---|---|
| train | 0.2 / 0.277 / 0.345 / 0.406 / 0.457 / 0.519 / 0.634 |
| validation | 0.28 / 0.342 / 0.412 / 0.48 / 0.522 / 0.576 / 0.665 |

### Label rộng / d

| split | min / p5 / p25 / median / p75 / p95 / max |
|---|---|
| train | 0.275 / 0.519 / 0.774 / 1 / 1.29 / 1.79 / 2.58 |
| validation | 0.393 / 0.607 / 0.916 / 1.18 / 1.51 / 2.03 / 2.6 |

### Label cao / d

| split | min / p5 / p25 / median / p75 / p95 / max |
|---|---|
| train | 0.0453 / 0.0997 / 0.13 / 0.155 / 0.18 / 0.217 / 0.309 |
| validation | 0.0672 / 0.126 / 0.159 / 0.184 / 0.213 / 0.267 / 0.37 |

### Weather box cạnh / d

| split | min / p5 / p25 / median / p75 / p95 / max |
|---|---|
| train | 0.216 / 0.309 / 0.42 / 0.526 / 0.659 / 0.819 / 1.16 |
| validation | 0.287 / 0.362 / 0.485 / 0.591 / 0.739 / 0.906 / 1.09 |

## 8. Chữ trong chú giải theo kind (train + validation)

| kind | các cách viết (số lần) |
|---|---|
| `closed` | Cấm đi / đang sửa (1161); Đường đóng (1139) |
| `covered` | Có mái che (1153); Lối có mái che (1147) |
| `crowded` | Đông người (1165); Đường đông người (1135) |
| `normal` | Lối đi thường (1161); Đường thường (1139) |
| `oneway` | Một chiều (theo mũi tên) (1164); Đường một chiều (1136) |
| `place:canteen` | Căn tin (1261) |
| `place:clinic` | Trạm y tế (1230) |
| `place:dorm` | Ký túc xá (1241) |
| `place:gate` | Cổng trường (1209) |
| `place:lab` | Phòng thí nghiệm (1252) |
| `place:lecture` | Giảng đường (1241) |
| `place:library` | Thư viện (1273) |
| `place:office` | Phòng hành chính (1277) |
| `place:parking` | Bãi xe (1217) |
| `place:sports` | Nhà thể thao (1228) |
| `robot` | Robot (mũi = hướng mặt) (1155); Robot và hướng đang quay (1145) |
| `stairs` | Cầu thang bộ (1151); Bậc thang (1149) |
| `weather` | Thời tiết (548); Thời tiết: mưa (135); Thời tiết: nắng (111); Thời tiết: nhiều mây (54); Thời tiết: nắng nhẹ (54) |
