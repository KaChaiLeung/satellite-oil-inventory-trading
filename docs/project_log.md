# Project Log

## 2025-08-07

**Phase 1 – AOI Definition & Script Scaffolding**

- Defined centre point at (35.93572, -96.74041) – Cushing, OK
- Decided on ±0.05° buffer – bounding box:
  - lat 35.88572 : 35.98572
  - lon -96.79041 : -96.69041
- Saved as "scripts/config.py:AOI_BBOX"
- Created stub scripts: download_sentinel.py, crop_and_stack.py, prepare_labels.py, utils.py

**Phase 1 – Data Acquisition & Preprocessing**

- Downloading data using Microsoft Planetary Computer
- Defined start date, end date, and day_delta in "scripts/config.py"
  - Start: 2017-01-01 (For surface reflectance)
  - End: 2025-08-06
  - Delta: ±1 day