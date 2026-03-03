# FA50 GUIDEBOOK

## 프로그램 시작과 기본 흐름
- 모드를 선택합니다. 1vs1, 2vs1, 2vs2, 4vs2, 4vs4
- DCA Setup 모드가 열리면 배치 값을 설정하고 Apply를 누릅니다
- Step 0에서 초기 상태를 설정합니다
- 항공기 Command를 입력하고 Fwd로 step을 진행합니다
- Back으로 이전 step을 확인하고 수정할 수 있습니다
- Play로 전체 전개를 확인합니다

## 화면 조작 안내
- 출력 화면 회전: 마우스 좌클릭 드래그
- 출력 화면 이동: 마우스 우클릭 드래그 또는 방향키
- 출력 화면 확대 축소: 마우스 휠, 키보드 + -, Page Up, Page Down
- Top View와 Plan View 토글은 우측 상단 오버레이에서 선택합니다
- 화면 좌측 상단의 BACK, FWD, +, -, 재생 버튼으로 step과 시점을 제어합니다

## Command 입력 핵심 규칙
- Turn이 S이면 bank는 자동으로 0도로 맞춰집니다
- Pull Up, Pull Down, Level은 한 번에 하나만 선택됩니다
- G MAX를 켜면 현재 속도와 고도 조건의 최대 G가 자동 반영됩니다
- Pitch Hold를 켜면 입력한 pitch를 유지하도록 bank가 계산됩니다
- Level을 켜면 pitch 0도 복귀를 목표로 bank와 g가 자동 보정됩니다

## Step 이동 규칙
- Fwd 1은 새 step을 생성하며 진행합니다
- Fwd 5, Fwd 10은 이미 생성된 step 범위 안에서만 이동합니다
- 예시: 마지막 생성 step이 100이면 step 98에서 Fwd 10을 눌러도 100에서 멈춥니다

## LOS 상세 설명
- LOS 패널은 출력창 좌하단에서 사용합니다
- LOS step 입력칸을 비우면 현재 step 기준으로 LOS가 생성됩니다
- LOS step에 숫자를 입력하면 지정한 step에 LOS가 생성됩니다
- 점 두 개를 연결하면 LOS 선이 만들어집니다

### Step View에서의 LOS
- 현재 선택된 step 기준으로 LOS 선과 라벨이 표시됩니다
- step을 바꾸면 해당 step 기준 LOS 표시가 갱신됩니다
- 현재 step에서 추가한 LOS는 즉시 화면에 반영됩니다

### Overview에서의 LOS
- 누적 궤적을 보면서 LOS가 함께 표시됩니다
- overview 표시 중에도 LOS 추가와 수정이 가능합니다
- playback 중에도 LOS 추가가 가능하며 현재 재생 위치 기준으로 즉시 반영됩니다

## 북마크 기능
- 우측 출력창 좌상단의 노란 별 버튼을 누르면 북마크 입력 팝업이 열립니다
- 현재 step에 대한 메모를 입력하면 북마크가 생성됩니다
- 북마크 목록은 출력창 좌하단에 쌓입니다
- step 번호가 작은 항목이 위에, 큰 항목이 아래에 표시됩니다
- 같은 step에서 다시 별 버튼을 누르면 내용 수정 또는 삭제가 가능합니다

## 저장과 불러오기
- Save 시 step command, DCA 설정, LOS, 북마크가 함께 저장됩니다
- Load 시 저장 당시 상태로 복원됩니다

## 빠른 점검 순서
- Turn, G, bank, pull mode를 한 항공기씩 순서대로 변경하며 확인합니다
- Back 1과 Fwd 1로 의도한 값이 유지되는지 확인합니다
- 마지막으로 Play에서 전체 흐름을 검증합니다
