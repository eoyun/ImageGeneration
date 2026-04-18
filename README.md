# ImageGeneration

## mkImg_hdf5.py

요청한 대로 **과한 구조 변경 없이**, 기본 실행 시 입력 `.dat`를 자동으로 잡도록만 정리했습니다.

### 기본값

- `--outname`: `260218_v1`
- `--dataset`: `DYto2L_1J_MLM`
- `--index`: `0`
- `--lines`: 생략 시 `.dat` 파일 라인 수를 자동 사용

기본 `.dat` 경로:

- `./input/<outname>/<dataset>.dat`
- 즉 기본 실행 시 `./input/260218_v1/DYto2L_1J_MLM.dat`

### 실행 예시

```bash
python3 mkImg_hdf5.py
```

### 직접 `.dat` 지정

```bash
python3 mkImg_hdf5.py --input-dat ./input/260218_v1/WtoLNu_2J_MLM.dat
```

