# 빌드 방법

스크립트는 제작 환경의 경로(`/tmp/claude-0/...`, `/mnt/user-data/...`)를 그대로 쓰고 있습니다. 직접 실행하려면 각 파일 위쪽의 경로를 자기 환경에 맞게 고치세요.

## 준비물

- 일본판 원본 게임 폴더 (BLJM60307, ISO를 푼 것)
- 유럽판 원본과 유럽판 한글패치 결과 폴더 (텍스처 이식용)
- 유럽판 한글패치 번역 데이터
  - `src.json`: 영어 원문 키 목록
  - `ko_full.json`: 번역
  - 저장소에 없음
- Python 3, numpy, Pillow, scipy
- Go 1.22 이상 (패처)
- 글꼴: `NotoSerifKR[wght].ttf`, `NanumGothic-ExtraBold.ttf`

## 구성

```
tools/
├─ text/       build_ini.py  유럽판 번역을 일본판 키로 옮겨 INI 생성
│              finalize_text.py  일본판 글꼴 폭 기준 줄바꿈, 개별 수정
│              widths.py, wrap.py, jpcmp.py  폭 계산·줄바꿈·INI 읽기
│              fix_missing.py  일본판 전용 문구 번역, 넘어가기 문구
├─ font/       jp_font.py  fonts_JP.g1n에 한글 추가 (hangul.py, g1n.py 사용)
├─ texture/    transplant.py  유럽판 한글 텍스처 38장 이식
│              fix_tex.py  일본판 배치 텍스처 3장 다시 그리기
│              fix_light00.py  일본판 전용 그림 글자 묶음 Light00
│              restyle.py, build_ui.py, cpkg.py, g1t.py  공통 모듈
├─ ui/         luac51.py  Lua 5.1(빅엔디언, float) 바이트코드 읽기
│              scan_scale.py, fix_subscale.py  자막 배율 0.8 → 0.9
├─ patcher/
│  ├─ mkpatch/ 차분 데이터 생성기
│  └─ apply/   패처 (ISO·폴더·UDF)
└─ diag/       ISO 진단 도구
```

## 순서

1. **텍스트**
   1. `build_ini.py`: UIStrings·Scenario·SubTitle는 유럽판 번역을 키 대응으로 옮깁니다. 동영상 자막은 `fmv_ko.json`(일본어 원문 번역)을 씁니다.
   2. `finalize_text.py`: 줄 길이를 넘는 문장을 다시 나눕니다.
   3. `fix_missing.py`: 일본판 전용 문구를 채웁니다.
2. **글꼴:** `jp_font.py`로 `fonts_JP_ko.g1n`을 만들고 `TrojanMusou/Fonts/fonts_JP.g1n` 자리에 넣습니다.
3. **텍스처**
   ```
   python3 transplant.py <일본판 PS3/> <유럽판 원본 PS3/> <유럽판 한글 PS3/> <결과 PS3/>
   python3 fix_tex.py        # 결과 폴더의 묶음 파일을 고쳐 씀
   python3 fix_light00.py    # CommonMasterPackage.cpkg의 Light00
   ```
   `CommonMasterPackage.cpkg`는 일본판과 유럽판 원본이 같으므로, 유럽판 한글패치 결과에서 시작합니다.
4. **자막 배율:** `fix_subscale.py`로 `UI/Scenes/*/*_JPN.lpkg` 4개를 고칩니다.
5. **차분과 패처**
   ```
   cd tools/patcher/mkpatch && go build -o mkpatch .
   ./mkpatch <일본판 원본 루트> <결과 루트> list.txt patch.bin
   cp patch.bin ../apply/ && : > ../apply/patch_upd.bin
   cd ../apply
   GOOS=windows GOARCH=amd64 go build -trimpath \
     -ldflags "-s -w -X main.titleID=BLJM60307 -X main.version=1.0 -X 'main.gameName=TROY無双'" \
     -o TroyMusouKOR_Patcher.exe .
   ```
   `list.txt`에는 바뀐 파일 107개의 경로를 적습니다. 구성은 다음과 같습니다.
   - INI 99개
   - 글꼴 1개
   - 묶음 파일 3개
   - 장면 파일 4개

## 검증

- **시험용 ISO:** `genisoimage -udf -J`로 원본 파일을 담은 UDF 브리지 ISO를 만들고, UDF 2.50 메타데이터 파티션 형식으로 바꾼 것도 준비합니다.
- **ISO 시험:** 두 ISO 모두에 적용한 뒤 7-Zip으로 UDF·ISO9660을 각각 풀어 결과 폴더와 바이트 단위로 비교합니다.
- **폴더 시험:** 게임 폴더 적용·되돌리기 결과를 원본·결과와 비교합니다.
- **실기 확인:** 마지막으로 RPCS3에서 화면을 확인합니다.
