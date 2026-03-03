# CHANGELOG_FA50.md

## Update Notes
- v0.6.02 | 2026-03-03 13:37 KST | Created new version file `fa50_0.6.02.py` from `0.6.01` and bumped internal `APP_VERSION` to `0.6.02` for next release cycle.
- v0.6.02 | 2026-03-03 13:37 KST | `fa50_0.6.01.py` 기반으로 `fa50_0.6.02.py` 새 버전 파일을 생성하고 내부 `APP_VERSION`을 `0.6.02`로 상향.
- v0.6.01 | 2026-03-03 13:31 KST | Version bump for release packaging and update-chain test (`0.6.00 -> 0.6.01`); no behavior logic change.
- v0.6.01 | 2026-03-03 13:31 KST | 릴리즈 패키징 및 업데이트 체인 테스트(`0.6.00 -> 0.6.01`)를 위한 버전 증가, 동작 로직 변경 없음.
- v0.6.00 | 2026-03-03 13:27 KST | Added GitHub-based auto-update flow: app checks `version.json` on startup, prompts user when newer version exists, downloads release asset, verifies SHA256, and (EXE mode) applies update via helper script then restarts.
- v0.6.00 | 2026-03-03 13:27 KST | GitHub 기반 자동업데이트를 추가: 시작 시 `version.json`을 확인하고 최신 버전이 있으면 팝업 안내 후 다운로드, SHA256 검증, EXE 실행 모드에서는 헬퍼 스크립트로 교체/재시작하도록 구현.
- v0.5.99 | 2026-03-03 02:25 KST | Fixed Straight-turn pull behavior: when `Turn=S`, `Pull Up/Pull Down` can now stay checked and drive pitch change by G while bank is still auto-forced to 0.
- v0.5.99 | 2026-03-03 02:25 KST | `Turn=S`일 때 Pull 모드가 강제로 해제되던 문제를 수정하여 `Pull Up/Pull Down` 체크를 유지하고 G 기반 pitch 변화가 가능하도록 했으며, bank는 계속 0으로 자동 고정.
- v0.5.98 | 2026-03-03 02:21 KST | Removed visible `Applied G` field from Command UI, tightened Initial/Current State and Offset label-value spacing, and compacted left panel/input widths to reduce overall UI footprint with screenshot validation.
- v0.5.98 | 2026-03-03 02:21 KST | Command UI에서 표시용 `Applied G` 항목을 제거하고 Initial/Current State 및 Offset 라벨-입력칸 간격을 축소했으며, 좌측 패널/입력칸 폭을 추가로 줄여 전체 UI 점유를 축소(스크린샷 검증).
- v0.5.97 | 2026-03-03 02:16 KST | Initial/Current State fields changed to vertical order (Altitude > HDG > Airspeed > Mach) to reduce panel width; global `HOLD SPEED` moved below AIRCRAFT #1; `Offset from #1/#3` remains Step-0-only while Step>0 shows #2~#8 in #1-like current-state UI.
- v0.5.97 | 2026-03-03 02:16 KST | Initial/Current State를 세로 순서(Altitude > HDG > Airspeed > Mach)로 변경해 폭을 줄이고, 전역 `HOLD SPEED`를 AIRCRAFT #1 아래로 이동했으며, `Offset from #1/#3`는 Step 0에서만 표시되고 Step>0에서는 #2~#8도 #1과 같은 현재상태 UI로 표시되도록 유지.
- v0.5.96 | 2026-03-03 02:13 KST | Moved `Applied G` label from Pitch row to G row so it sits next to G controls.
- v0.5.96 | 2026-03-03 02:13 KST | `Applied G` 라벨을 Pitch 줄에서 G 줄 옆으로 이동.
- v0.5.95 | 2026-03-03 02:11 KST | Moved global `HOLD SPEED` next to AIRCRAFT #1 header and made `Offset from #1/#3` panels visible only at Step 0; from Step > 0, #2~#8 now show the same current-state style as #1.
- v0.5.95 | 2026-03-03 02:11 KST | 전역 `HOLD SPEED`를 AIRCRAFT #1 헤더 옆으로 이동하고 `Offset from #1/#3` 블록을 Step 0에서만 표시되도록 변경했으며, Step > 0에서는 #2~#8도 #1과 동일한 현재상태 UI로 보이도록 수정.
- v0.5.94 | 2026-03-03 02:06 KST | Command layout adjusted again: `Bank` moved to the row directly below `G` as requested.
- v0.5.94 | 2026-03-03 02:06 KST | 요청에 맞춰 Command 배치를 재조정하여 `Bank`를 `G` 바로 아래 줄로 이동.
- v0.5.93 | 2026-03-03 02:03 KST | Re-aligned Command row so `Power` and `Bank` are on the same line, and separated `MAX G` onto the G line to reduce visual confusion with Bank.
- v0.5.93 | 2026-03-03 02:03 KST | Command 영역에서 `Power`와 `Bank`를 같은 줄로 정렬하고 `MAX G`를 G 줄로 분리해 Bank와의 혼동을 줄이도록 재배치.
- v0.5.92 | 2026-03-03 02:00 KST | Repositioned `MAX G` between `G` and `Bank`, added concise hover help for MAX G / Pitch Hold / Pull Up / Pull Down / Level, and compacted input widths plus left panel minimum width with screenshot validation.
- v0.5.92 | 2026-03-03 02:00 KST | `MAX G`를 `G`와 `Bank` 사이로 이동하고 MAX G / Pitch Hold / Pull Up / Pull Down / Level 툴팁 설명을 추가했으며, 입력칸과 좌측 패널 폭을 컴팩트하게 축소하고 스크린샷으로 검증.
- v0.5.91 | 2026-03-03 01:57 KST | Removed empty-state bookmark text so no placeholder message is shown when there are zero bookmarks.
- v0.5.91 | 2026-03-03 01:57 KST | 북마크가 없을 때 표시되던 안내 문구를 제거해 빈 상태에서 텍스트가 나타나지 않도록 수정.
- v0.5.90 | 2026-03-03 01:55 KST | Fixed bookmark clipping by forcing immediate overlay relayout on add/edit/delete and scaling bookmark panel height by item count above brand stamp.
- v0.5.90 | 2026-03-03 01:55 KST | 북마크 추가/편집/삭제 직후 오버레이 재배치를 강제하고, 브랜드 문구 위 기준으로 항목 수에 따라 패널 높이를 자동 확장해 잘림 문제를 수정.
- v0.5.89 | 2026-03-03 01:48 KST | Bookmark stack now auto-grows upward from above the bottom-right brand stamp based on item count, while keeping step-ascending re-sort so earlier steps stay on top.
- v0.5.89 | 2026-03-03 01:48 KST | 북마크 스택이 우하단 브랜드 문구 위를 기준으로 항목 수만큼 위로 자동 확장되도록 조정했고, step 오름차순 재정렬로 빠른 step이 항상 위에 오도록 유지.
- v0.5.88 | 2026-03-03 01:44 KST | Bookmark UI simplified: removed header/panel boxing, moved star button next to top-center STEP label, and changed each bookmark row to per-step card with right-side edit pen and X delete actions.
- v0.5.88 | 2026-03-03 01:44 KST | 북마크 UI를 단순화해 헤더/박스 배경을 제거하고 별 버튼을 중앙 상단 STEP 라벨 옆으로 이동했으며, 각 북마크 우측에 펜 편집과 X 삭제 버튼을 추가.
- v0.5.87 | 2026-03-03 01:41 KST | Moved bookmark panel to bottom-right and redesigned bookmarks as per-step card buttons sorted by step; click a card to jump, with selected-card highlight and delete by selection.
- v0.5.87 | 2026-03-03 01:41 KST | 북마크 패널을 우하단으로 이동하고 step별 카드 버튼 UI로 개편했으며, step 오름차순 정렬과 클릭 이동, 선택 하이라이트, 선택 삭제를 적용.
- v0.5.86 | 2026-03-03 01:34 KST | Bookmark UI redesigned with clickable one-line rows per step, step jump in Step View, camera-state snapshot/restore per bookmark, CSV persistence for camera fields, and bookmark delete action.
- v0.5.86 | 2026-03-03 01:34 KST | 북마크 UI를 줄 단위 클릭 리스트로 개편하고 클릭 시 Step View 해당 step 이동, 북마크별 카메라 저장/복원, CSV 카메라 필드 저장/로드, 북마크 삭제 기능을 추가.
- v0.5.85 | 2026-03-03 01:28 KST | Added in-view bookmark mode (yellow star + step note stack at lower-left), enforced `Turn=S -> bank 0` across normal and infeasible paths, capped `Fwd 5/10` to already-created steps, and switched GUIDE dialog to `FA50_GUIDEBOOK.md`.
- v0.5.85 | 2026-03-03 01:28 KST | 출력창 북마크 모드(노란 별 버튼 + 좌하단 step 메모 스택) 추가, 정상/예외 경로 모두에서 `Turn=S -> bank 0` 강제, `Fwd 5/10`을 이미 생성된 step 범위로 제한, GUIDE 창 기본 문서를 `FA50_GUIDEBOOK.md`로 전환.
- v0.5.83 | 2026-03-03 01:06 KST | Fixed BA/RA coupling after individual-drag toggle by separating BA/RA spin sync targets; removed top drag-help labels; reduced DCA base font size to prevent clipping.
- v0.5.83 | 2026-03-03 01:06 KST | 개별 드래그 후 BA 이동 시 RA 연동 이동이 생기지 않도록 BA/RA 동기화 대상을 분리하고, 상단 드래그 안내 문구를 제거했으며 DCA 기본 폰트를 축소해 잘림을 완화.
- v0.5.82 | 2026-03-03 01:01 KST | In DCA preview individual-drag mode, BA/RA position controls are now locked (disabled) to prevent anchor-conflict disappearance; left panel font reduced one more step to avoid clipping.
- v0.5.82 | 2026-03-03 01:01 KST | DCA 미리보기 개별 드래그 모드에서 BA/RA Position 입력을 잠가(비활성화) 앵커 충돌로 항공기가 사라지는 문제를 방지하고, 좌측 폰트를 한 단계 더 축소해 UI 잘림을 완화.
- v0.5.81 | 2026-03-03 00:59 KST | DCA Setup layout tuned to 1:1 left/right split, left-panel font reduced by 2 steps, and preview drag now syncs BA/RA distance fields back to left controls in real time.
- v0.5.81 | 2026-03-03 00:59 KST | DCA Setup 좌/우 비율을 1:1로 조정하고 좌측 폰트를 2단계 축소했으며, 우측 미리보기 드래그 시 BA/RA 거리값이 좌측 입력값에 실시간 동기화되도록 수정.
- v0.5.80 | 2026-03-03 00:52 KST | Fixed false Back/Fwd prompt on legacy CSV reload by (1) preventing stale G range clipping during `set_command`, and (2) normalizing bank dirty-compare to integer UI resolution with Qt-style half-up rounding.
- v0.5.80 | 2026-03-03 00:52 KST | 구버전 CSV 로드 후 Back/Fwd 오검출 수정: (1) `set_command` 시 이전 step G range 잔재로 인한 silent 클리핑 제거, (2) bank 변경 비교를 현재 UI 정수 분해능(0.5 올림) 기준으로 정규화.
- v0.5.79 | 2026-03-03 00:45 KST | Fixed Back/Fwd false prompt noise by tracking user-authored pitch/bank intent (`pitch_user_set`, `bank_user_set`) and comparing `pitch_deg` only in true pitch-command modes.
- v0.5.79 | 2026-03-03 00:45 KST | Back/Fwd 오검출 보정: 사용자 입력 의도(`pitch_user_set`, `bank_user_set`)를 명시적으로 추적하고, `pitch_deg`는 실제 pitch command 모드에서만 변경 비교하도록 수정.
- v0.5.78 | 2026-03-03 00:34 KST | Fixed Back/Fwd false-change source by preventing non-MAX mode from auto-clipping `g_cmd`; dynamic max now only hard-applies when MAX is checked.
- v0.5.78 | 2026-03-03 00:34 KST | Back/Fwd 오검출 원인 보정: MAX 미체크 상태에서는 `g_cmd` 자동 클리핑을 금지하고, MAX 체크 시에만 동적 최대값을 강제 적용.
- v0.5.77 | 2026-03-02 23:51 KST | Added scenario save/load support for per-mode enabled aircraft list via META `enabled_ids`.
- v0.5.77 | 2026-03-02 23:51 KST | 시나리오 저장/불러오기에 모드 내 활성 항공기 목록(`enabled_ids`) 저장/복원 지원 추가.
- v0.5.76 | 2026-03-02 23:48 KST | Fixed false “changed aircraft” prompts after Back/Fwd by excluding auto-derived command fields (G MAX-derived g_cmd, display pitch, pitch-hold-derived bank) from dirty detection.
- v0.5.76 | 2026-03-02 23:48 KST | Back/Fwd 후 변경 프롬프트 오검출 수정: 자동유도 필드(G MAX의 g_cmd, 표시용 pitch, pitch hold 유도 bank)를 변경 비교에서 제외.
- v0.5.75 | 2026-03-02 23:19 KST | Fixed Pitch Hold semantics to preserve user-entered pitch setpoint (not 0 deg) and keep real-time bank auto-solve from G.
- v0.5.75 | 2026-03-02 23:19 KST | Pitch Hold가 0도 고정이 아니라 사용자 입력 pitch setpoint를 유지하고, G 기반 bank 자동계산이 실시간 유지되도록 보정.
- v0.5.74 | 2026-03-02 23:17 KST | Added per-step G MAX re-evaluation on step advance and new Pitch Hold mode (hold pitch angle, auto-solve bank from G).
- v0.5.74 | 2026-03-02 23:17 KST | step 진행 시 G MAX 재계산 반영 기능과 Pitch Hold 모드(피치각 고정, G 기반 bank 자동계산)를 추가.
- v0.5.73 | 2026-03-02 23:06 KST | Added G MAX checkbox (auto-set to PS max G) and fixed Pull-Up manual pitch input being overwritten by auto preview.
- v0.5.73 | 2026-03-02 23:06 KST | G MAX 체크박스(PS 최대 G 자동 적용) 추가 및 Pull-Up 수동 pitch 입력이 자동 미리보기로 덮이는 문제 수정.
- v0.5.72 | 2026-03-02 23:01 KST | Added dynamic Command-G max (PS-based by current condition) and Pull-Up pitch/bank bidirectional auto-coupling with Level->Pull Up auto-switch on intent.
- v0.5.72 | 2026-03-02 23:01 KST | 현재 조건 기반 PS 최대 G를 Command G에 동적 적용하고, Pull Up에서 pitch/bank 양방향 자동연동 + 의도 입력 시 Level->Pull Up 자동전환을 추가.
- v0.5.71 | 2026-03-02 22:46 KST | Removed LEVEL-mode 4G hard cap; LEVEL G is now constrained by PS-feasible limit (CAS/ALT/POWER based) up to 9G.
- v0.5.71 | 2026-03-02 22:46 KST | LEVEL 상태의 4G 고정 제한을 제거하고, CAS/ALT/POWER 기반 PS 가용 G(최대 9G)로 제한되도록 수정.
- v0.5.69 | 2026-03-02 22:36 KST | Added 2 more zoom-out steps on panel detach (11 -> 13 total).
- v0.5.69 | 2026-03-02 22:36 KST | 패널 분리 시 축소를 2회 추가(총 13회) 적용.
- v0.5.68 | 2026-03-02 22:35 KST | Added 3 more zoom-out steps on panel detach (8 -> 11 total).
- v0.5.68 | 2026-03-02 22:35 KST | 패널 분리 시 축소 단계를 3회 추가(총 11회) 적용.
- v0.5.67 | 2026-03-02 22:33 KST | Camera step counts updated: non-detached startup zoom-in changed to x3; detached panel click now applies W then zoom-out x8.
- v0.5.67 | 2026-03-02 22:33 KST | 카메라 배율 단계 조정: 미분리 시작 확대 3회로 변경, 패널 분리 클릭 시 W 정렬 후 축소 8회 적용.
- v0.5.66 | 2026-03-02 22:30 KST | Simplified startup camera rules: non-detached uses Top+N then fixed zoom-in x5; panel detach click now immediately applies compass W effect.
- v0.5.66 | 2026-03-02 22:30 KST | 시작 카메라 규칙 단순화: 미분리 시 Top+N 후 고정 확대 5회, 패널 분리 클릭 시 즉시 나침반 W 효과 적용.
- v0.5.65 | 2026-03-02 22:28 KST | DCA startup framing now targets yellow mission HEIGHT line; normal mode keeps N at 12 with vertical fit, detached-panel mode rotates to N at 3 with horizontal fit (both with one-step zoom-out margin).
- v0.5.65 | 2026-03-02 22:28 KST | DCA 시작 프레이밍 기준을 노란 HEIGHT 선으로 변경: 미분리는 N 12시+상하 맞춤, 패널 분리는 N 3시+좌우 맞춤(둘 다 1단계 축소 여유 적용).
- v0.5.64 | 2026-03-02 22:23 KST | For DCA startup view, top camera now fits mission-area top/bottom to screen top/bottom (north-up retained).
- v0.5.64 | 2026-03-02 22:23 KST | DCA 시작 화면에서 mission area 상/하단이 화면 상/하단에 맞도록 top 카메라 거리를 조정(북쪽 12시 정렬 유지).
- v0.5.63 | 2026-03-02 22:21 KST | Startup 3D view now auto-frames to clean Top+North-up (12 o'clock N) with full battlefield footprint visibility.
- v0.5.63 | 2026-03-02 22:21 KST | 실행 직후 3D 화면이 Top View + 북쪽 12시 정렬로 자동 설정되고, 전장 전체가 보이도록 자동 프레이밍 적용.
- v0.5.62 | 2026-03-02 22:17 KST | In Plan View, YZ is now shown instead of XZ (XY/XZ hidden, YZ visible).
- v0.5.62 | 2026-03-02 22:17 KST | Plan View에서 XZ 대신 YZ가 보이도록 변경(XY/XZ 숨김, YZ 표시).
- v0.5.61 | 2026-03-02 22:15 KST | Plan View switched back to XZ two-way views (0/180), and YZ vertical plane is now snapped to XY lattice for cleaner checkerboard intersection.
- v0.5.61 | 2026-03-02 22:15 KST | Plan View를 XZ 2방향(0/180)으로 복원하고, YZ 수직 평면을 XY 격자 간격에 스냅해 교차가 더 깔끔하게 맞도록 조정.
- v0.5.60 | 2026-03-02 22:13 KST | Removed XZ grid entirely; kept only YZ vertical grid on x=0 axis, and restored plan view to YZ-only two-way side views.
- v0.5.60 | 2026-03-02 22:13 KST | XZ 그리드를 완전 제거하고 x=0 축의 YZ 수직 그리드만 유지, plan view도 YZ 2방향만 보이도록 복원.
- v0.5.59 | 2026-03-02 22:11 KST | Plan View now uses only XZ side projections (azimuth 0/180), while vertical grid visibility is limited to Y-axis plane (YZ) outside plan mode.
- v0.5.59 | 2026-03-02 22:11 KST | Plan View를 XZ 투영 2방향(azimuth 0/180)으로 변경하고, 일반 수직 그리드는 Y축 평면(YZ)만 보이도록 조정.
- v0.5.58 | 2026-03-02 22:07 KST | Plan View now supports only Y-axis side views (left/right: 90/270 deg), and plan grid visibility is limited to YZ only.
- v0.5.58 | 2026-03-02 22:07 KST | Plan View를 Y축 좌/우(90/270도) 2방향으로만 동작하도록 제한하고, Plan 모드 그리드는 YZ만 보이도록 수정.
- v0.5.57 | 2026-03-02 22:12 KST | In DCA setup mode, all rendered grids are now constrained to mission-area footprint only (including vertical columns).
- v0.5.57 | 2026-03-02 22:12 KST | DCA setup ????? ??? ?? mission area ????? ?????(?? ?? ??) ??.
- v0.5.55 | 2026-03-02 22:08 KST | Restored DCA vertical grid planes (XZ/YZ) to legacy x/y-axis-aligned style from v0.5.53 while keeping mission-area-only XY grid.
- v0.5.55 | 2026-03-02 22:08 KST | DCA ??? ??(XZ/YZ)? 0.5.53? x/y? ?? ???? ????, XY? mission area ??? ??.
- v0.5.54 | 2026-03-02 22:02 KST | DCA setup grid generation is now constrained to mission-area footprint (XY and vertical columns) instead of full-world planes.
- v0.5.54 | 2026-03-02 22:02 KST | DCA setup ? ??? ?? ??? ?? mission area ??(XY ? ?? ??)??? ????? ??.
- v0.5.53 | 2026-03-02 21:54 KST | DCA preview CAP-split state and BA heading overrides are now propagated to actual start state (runtime DCA + placement), with CAP split markers rendered in output view.
- v0.5.53 | 2026-03-02 21:54 KST | DCA ????? CAP ?? ??/BA ?? ?????? ?? ?? ??(??? DCA/??)? ????, ???? CAP ?? ??? ????? ??.
- v0.5.52 | 2026-03-02 19:20 KST | CAP-split placement updated: 2vs2 uses #1->left CAP FRONT and #2->right CAP REAR; for 2vs2/4vs2/4vs4 non-#1 squads auto-position at CAP REAR with 180deg heading.
- v0.5.52 | 2026-03-02 19:20 KST | CAP ?? ??? ??? 2vs2? #1 ?? CAP FRONT, #2 ?? CAP REAR? ???? 2vs2/4vs2/4vs4?? #1 ?? ?? CAP REAR + 180? ??? ?? ??.
- v0.5.51 | 2026-03-02 19:12 KST | CAP-split now auto-sets non-#1 BA squad heading to 180deg (CAP rear-facing default).
- v0.5.51 | 2026-03-02 19:12 KST | CAP ??(??) ? #1 ??? ??? BA ??? ?? ??? 180?? ?? ????? ??.
- v0.5.50 | 2026-03-02 19:15 KST | Replaced top text rotation control with on-preview squad rotate icon; reinforced CAP-split squad drag behavior so grouped movement always applies.
- v0.5.50 | 2026-03-02 19:15 KST | ?? ??? ?? ??? ???? ? ?? ?? ????? ????, CAP ?? ? ?? ?? ??? ?? ????? ??.
- v0.5.49 | 2026-03-02 19:13 KST | BA drag grouping updated: #1/#2 and #3/#4 now move together by grabbing either member; aircraft pick priority is now above CAP lines/points.
- v0.5.49 | 2026-03-02 19:13 KST | BA ???? #1/#2, #3/#4 ?? ???? ????, CAP ?/????? ??? ?? ????? ??.
- v0.5.48 | 2026-03-02 19:05 KST | Added CAP-split squad control rules, squad 180? flip control, and aircraft arrow symbols in DCA preview.
- v0.5.48 | 2026-03-02 19:05 KST | DCA ?????? CAP ?? ?? ?? ??, ?? 180? ?? ??, ??? ??? ??? ??.
- v0.5.47 | 2026-03-02 18:57 KST | CAP pair now spawns at quarter points (10nm from each side when width=40), #3 is anchored to right CAP FRONT, and CAP C.F-C.R side lines are draggable for lateral slide.
- v0.5.47 | 2026-03-02 18:57 KST | CAP ?? 1/4 ??(? 40?? ?? ???? 10nm)?? ???? #3? ?? CAP FRONT? ?????? CAP ?? C.F-C.R ? ??? ????? ??.
- v0.5.46 | 2026-03-02 18:50 KST | CAP add now initializes at left/right one-third points; BA #1/#2 follow left CAP and #3/#4 follow right CAP lateral movement.
- v0.5.46 | 2026-03-02 18:50 KST | CAP ?? ?? ??? ?/? 1/3?? ???? BA #1/#2? ?? CAP, #3/#4? ?? CAP ?? ??? ????? ??.
- v0.5.45 | 2026-03-02 18:46 KST | CAP add now duplicates the whole center CAP pair (C.F+C.R) into left/right separated pairs with per-side dashed connectors.
- v0.5.45 | 2026-03-02 18:46 KST | CAP ?? ? ?? C.F/C.R ? ?? ?? ??? 2??? ????, ?? ?? ?? ??? ????? ??.
- v0.5.44 | 2026-03-02 18:42 KST | Added DCA preview pan (right-drag + arrow keys) and moved CAP add control to preview bottom-right with symmetric CAP pair behavior.
- v0.5.44 | 2026-03-02 18:42 KST | DCA ????? ??? ???/??? ? ??? ???? CAP ?? ??? ?????? ??, CAP ? ?? ??? ??.
- v0.5.43 | 2026-03-02 18:38 KST | Added BA cone expansion (#2 in 2vs2, #3 in 4vs2) and CAP 2-point symmetric slide logic in DCA preview.
- v0.5.43 | 2026-03-02 18:38 KST | DCA ?????? BA ? ??(2vs2:#2, 4vs2:#3)? CAP 2??? ?? ???? ??? ??.
- v0.5.42 | 2026-03-02 18:32 KST | Simplified preview helper texts and fixed main guide box at top for cleaner UI.
- v0.5.42 | 2026-03-02 18:32 KST | ???? ?? ??? ????? ?? ?? ??? ?? ???? ??? UI? ??.
- v0.5.40 | 2026-03-02 18:29 KST | Added clear C.F-to-C.R distance visualization in DCA preview (dashed connector + centered nm label).
- v0.5.40 | 2026-03-02 18:29 KST | DCA ?????? C.F-C.R ?? ???? ?? ?? ???? ?? nm ??? ??.
- v0.5.39 | 2026-03-02 18:22 KST | Decoupled CAP FRONT and BA #1 movement after init-default; B.E drag is vertical-only; DCA preview now supports mouse-wheel zoom.
- v0.5.39 | 2026-03-02 18:22 KST | CAP FRONT와 BA #1 연동을 기본값 이후 해제하고, B.E는 수직 이동만 허용하며, DCA 미리보기 마우스휠 줌을 추가.
- v0.5.38 | 2026-03-02 18:12 KST | DCA preview now supports C.F/C.R/B.E point drag; mission-area view keeps fixed feel but auto-falls back to minimal zoom-out only when clipping would occur.
- v0.5.38 | 2026-03-02 18:12 KST | DCA 미리보기에서 C.F/C.R/B.E 포인트 드래그를 지원하고, mission area는 평소 고정 뷰를 유지하되 클리핑 시에만 최소 줌아웃으로 보정하도록 수정.
- v0.5.37 | 2026-03-02 18:08 KST | DCA preview resize no longer auto-zooms; mission lower-corner drag no longer collapses height; added BA #1 +-60deg / 40nm cone overlay.
- v0.5.37 | 2026-03-02 18:08 KST | DCA ???? ???? ? ?? ???? ???? ?? ?? ?? ???? ????? BA #1 ?60?/40nm ? ????? ??.
- v0.5.36 | 2026-03-02 17:58 KST | DCA setup preview now supports mouse drag for HMRL/INNER DEZ/OUTER DEZ/COMMIT and corner-resize mission area with live nm feedback.
- v0.5.36 | 2026-03-02 17:58 KST | DCA setup 미리보기에서 HMRL/INNER DEZ/OUTER DEZ/COMMIT 라인 드래그와 mission area 코너 리사이즈, 실시간 nm 피드백을 지원하도록 수정.
- v0.5.35 | 2026-03-02 17:49 KST | DCA setup dialog now opens in full-window (maximized) mode.
- v0.5.35 | 2026-03-02 17:49 KST | DCA setup 창을 전체 창(최대화) 모드로 열리도록 수정.
- v0.5.34 | 2026-03-02 17:42 KST | Removed all auto popup-close hooks; popup handling is fully manual again.
- v0.5.34 | 2026-03-02 17:42 KST | 자동 팝업 닫기 훅을 전부 제거하고 수동 팝업 처리로 복귀.
- v0.5.33 | 2026-03-02 17:35 KST | Overview/play arrows now use per-step segment shafts (p0��p1), improving #4 continuity vs #1/#2/#3.
- v0.5.33 | 2026-03-02 17:35 KST | overview/play ȭ��ǥ�� step ����(p0��p1) shaft ������� ������ #4 ���Ӽ� ������ ����.
- v0.5.32 | 2026-03-02 17:35 KST | Separated arrow/trail Z layers more aggressively in overview/play for shaft visibility stability.
- v0.5.32 | 2026-03-02 17:35 KST | overview/play���� ȭ��ǥ/��� Z ���̾� �и��� ��ȭ�� shaft ���ü� ����ȭ.
- v0.5.31 | 2026-03-02 17:30 KST | Auto-probe camera now frames #1~#4 BA arrows so all are visible in overview/play PNG.
- v0.5.31 | 2026-03-02 17:30 KST | �ڵ� ĸó ī�޶� #1~#4 �������� �����̹��� overview/play PNG���� ��� ���̵��� ����.
- v0.5.30 | 2026-03-02 17:28 KST | DCA setup dialogs now auto-click Apply via QDialog hook; panel-detach Yes remains blocked.
- v0.5.30 | 2026-03-02 17:28 KST | DCA setup ���̾�α׿��� QDialog ������ Apply �ڵ� Ŭ��, �гκи� Yes�� ��� ����.
- v0.5.29 | 2026-03-02 17:28 KST | Popup auto-confirm prioritizes Apply and excludes panel-detach affirmative button.
- v0.5.29 | 2026-03-02 17:28 KST | �˾� �ڵ�Ȯ�� �� Apply �켱, �гκи� Ȯ�� ��ư�� ����.
- v0.5.25 | 2026-03-02 17:17 KST | Auto probe now always writes failure logs (even startup failures) and includes a one-click runner batch file.
- v0.5.25 | 2026-03-02 17:17 KST | �ڵ� ������ ���� �� �����ص� �α׸� �ݵ�� ���⵵�� �����߰�, ��Ŭ�� ���� ��ġ������ �߰�.
- v0.5.24 | 2026-03-02 17:14 KST | Auto visual probe now saves into `visual_probes` folder and opens PNG/TXT automatically after capture.
- v0.5.24 | 2026-03-02 17:14 KST | �ڵ� �ð����� ����� `visual_probes` ������ �����ϰ�, ĸó �� PNG/TXT�� �ڵ����� ������ ����.
- v0.5.23 | 2026-03-02 17:11 KST | Added auto visual-probe mode: 4vs2 + fwd5 + top view captures overview/play PNG and a probe log in one run.
- v0.5.23 | 2026-03-02 17:11 KST | �ڵ� �ð����� ��� �߰�: 4vs2 + fwd5 + top view �������� overview/play PNG�� �α׸� �� ���� ����.
- v0.5.22 | 2026-03-02 16:58 KST | Step-arrow rendering is now forced to top layer (`additive` + high depth) to prevent shaft disappearance in Overview/Play.
- v0.5.22 | 2026-03-02 16:58 KST | Overview/Play���� shaft ���� ������ ���� step ȭ��ǥ�� ���� ���̾�(`additive` + ���� depth)�� ���� ������.
- v0.5.21 | 2026-03-02 16:41 KST | Overview/Play step arrows now render from per-step heading (not p0->p1 distance), preventing skipped shaft appearance on later aircraft.
- v0.5.21 | 2026-03-02 16:41 KST | Overview/Play ȭ��ǥ�� step �̵��Ÿ� ����� �ƴ� step�� heading ������� �������� �Ĺ� ��ü shaft ����(�� ĭ �ǳʶ�) ������ ����.
- v0.5.06 | 2026-03-02 15:04 KST | During playback, LOS creation is enabled via the lower-left LOS panel (relation map), not right-click authoring.
- v0.5.06 | 2026-03-02 15:04 KST | ��� �� LOS �߰��� ��Ŭ���� �ƴ϶� ���ϴ� LOS �г�(�����)���� �����ϵ��� ����.
- v0.5.03 | 2026-03-02 14:48 KST | Resolved Level/Pull Up priority conflict: Level check stays Level, but later user bank edit in turn auto-switches to Pull Up.
- v0.5.03 | 2026-03-02 14:48 KST | Level/Pull Up �켱���� �浹 �ذ�: Level üũ�� �����ǰ�, ���� ��ȸ �� bank ���� ���� �� Pull Up���� �ڵ� ��ȯ.
- v0.5.02 | 2026-03-02 14:43 KST | Level selection now overrides Pull Up and immediately applies level-assist bank/G correction.
- v0.5.02 | 2026-03-02 14:43 KST | Pull Up ���¿����� Level üũ �� Level �켱 ���� �� �ڵ� ����(bank/G) ������ �����ϵ��� ����.
- v0.5.01 | 2026-03-02 14:37 KST | Turn + G + user bank input now keeps bank and auto-switches to Pull Up.
- v0.5.01 | 2026-03-02 14:37 KST | ��ȸ+G+����� ��ũ �Է� �� ��ũ�� �����ϰ� Pull Up�� �ڵ� üũ�ϵ��� ����.

---

## v0.5.83
- Date/Time (KST): 2026-03-03 01:06
- Request Summary (EN): Prevent RA from shifting when BA is moved after toggling individual-aircraft drag; remove top drag-help text; verify and tune UI clipping by checking actual rendered result.
- 요청 요약 (KO): 개별 이동 on/off 이후 BA 이동 시 RA가 같이 움직이지 않도록 수정하고, 상단 드래그 안내 문구를 제거하며 실제 렌더 결과를 확인해 UI 잘림을 보정.

### Changed Files
- `fa50_0.5.83.py` (new version from `fa50_0.5.82.py`)
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Split BA/RA back-sync targets:
   - `_sync_position_spins_from_preview(target='both')` added with target filtering (`ba` / `ra` / `both`).
   - BA drag paths now sync BA only, not RA:
     - aircraft drag uses `target=group`
     - CAP pair operations use `target='ba'`
2. Removed top drag-help labels:
   - removed extra helper labels in preview header row.
   - kept only a compact `개별 이동` checkbox.
3. Reduced DCA base font size:
   - dialog stylesheet changed from 16/17pt class to 14/15pt class to reduce clipping risk.

### 코드/로직 변경 사항 (KO)
1. BA/RA 역동기화 대상을 분리:
   - `_sync_position_spins_from_preview(target='both')`로 확장하고 `ba/ra/both` 타깃 동기화 지원.
   - BA 드래그 경로에서는 RA를 건드리지 않도록 변경:
     - 항공기 드래그: `target=group`
     - CAP pair 동작: `target='ba'`
2. 상단 드래그 안내 문구 제거:
   - 미리보기 상단 보조 문구 라벨 제거.
   - `개별 이동` 체크박스만 간결하게 유지.
3. DCA 기본 폰트 축소:
   - 다이얼로그 스타일 폰트를 16/17pt -> 14/15pt로 낮춰 UI 잘림 완화.

### Validation (EN)
1. Syntax validation: `python -m py_compile fa50_0.5.83.py` passed.
2. Behavior check (automated):
   - individual drag ON -> move BA member
   - individual drag OFF -> move BA group
   - verified RA anchor spin and RA lead point remain unchanged (`delta = 0`).
3. Render check:
   - offscreen DCA dialog screenshot captured and reviewed after font/layout updates.

### 검증 내용 (KO)
1. 문법 검증: `python -m py_compile fa50_0.5.83.py` 통과.
2. 동작 검증(자동):
   - 개별 드래그 ON 후 BA 이동
   - 개별 드래그 OFF 후 BA 그룹 이동
   - RA 거리 스핀/리드 포인트 변화 없음(`delta = 0`) 확인.
3. 렌더 검증:
   - 오프스크린 DCA 다이얼로그 스크린샷을 생성/확인해 폰트 및 레이아웃 보정 결과 점검.

## v0.5.82
- Date/Time (KST): 2026-03-03 01:01
- Request Summary (EN): Lock BA/RA position controls during individual-aircraft drag and reduce left-panel font further because UI text is clipped.
- 요청 요약 (KO): 개별 항공기 이동 시 BA/RA Position을 잠그고, 좌측 UI 글씨가 잘리는 문제를 완화하기 위해 폰트를 추가 축소.

### Changed Files
- `fa50_0.5.82.py` (new version from `fa50_0.5.81.py`)
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Added position-lock behavior for individual drag mode:
   - New helper: `_set_position_controls_locked(locked)`.
   - Locks (disables) `BA/RA distance + heading` controls when individual drag is enabled:
     - `ba_from_asset_nm`, `ba_heading_deg`, `ra_from_asset_nm`, `ra_heading_deg`
2. Updated individual-drag toggle flow:
   - `_on_individual_drag_toggled()` now applies the lock state immediately.
   - Initial lock state applied on dialog startup.
3. Prevented auto back-sync while locked:
   - `_sync_position_spins_from_preview()` now returns early in individual-drag mode.
4. Left font reduced one more step:
   - `_shrink_widget_font(left_wrap, steps=3)` (previously 2).

### 코드/로직 변경 사항 (KO)
1. 개별 드래그 모드 Position 잠금 로직 추가:
   - `_set_position_controls_locked(locked)` 헬퍼 추가.
   - 개별 드래그 활성 시 `BA/RA 거리 + 헤딩` 입력을 비활성화:
     - `ba_from_asset_nm`, `ba_heading_deg`, `ra_from_asset_nm`, `ra_heading_deg`
2. 개별 드래그 토글 동작 보강:
   - `_on_individual_drag_toggled()`에서 잠금 상태를 즉시 반영.
   - 다이얼로그 초기 진입 시에도 잠금 상태를 명시 적용.
3. 잠금 중 자동 역동기화 차단:
   - `_sync_position_spins_from_preview()`가 개별 드래그 모드에서는 즉시 반환하도록 수정.
4. 좌측 폰트 추가 축소:
   - `_shrink_widget_font(left_wrap, steps=3)`로 변경(기존 2).

### Validation (EN)
1. Syntax validation: `python -m py_compile fa50_0.5.82.py` passed.

### 검증 내용 (KO)
1. 문법 검증: `python -m py_compile fa50_0.5.82.py` 통과.

## v0.5.81
- Date/Time (KST): 2026-03-03 00:59
- Request Summary (EN): DCA setup UI refinement: make left/right panes 1:1, reduce left font size by two steps, and ensure preview edits propagate all corresponding left-side values.
- 요청 요약 (KO): DCA setup UI 조정: 좌/우 창 비율 1:1, 좌측 폰트 2단계 축소, 우측 미리보기 수정값이 좌측 값들에 실시간 반영되도록 개선.

### Changed Files
- `fa50_0.5.81.py` (new version from `fa50_0.5.80.py`)
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. DCA setup split ratio updated to 1:1:
   - left scroll and right preview both set with equal stretch.
   - left minimum width reduced to avoid left-dominant layout lock.
2. Left panel font reduced by two steps:
   - added `_shrink_widget_font(left_wrap, steps=2)` and applied to left-side controls only.
3. Preview -> left real-time synchronization improved:
   - added `_sync_position_spins_from_preview()` to recompute and write BA/RA distance fields (`ba_from_asset_nm`, `ra_from_asset_nm`) from current preview geometry.
   - called after aircraft drag, CAP pair slide drag (line/point), and CAP pair toggle alignment so left values stay consistent with preview state.

### 코드/로직 변경 사항 (KO)
1. DCA setup 좌/우 비율 1:1 적용:
   - 좌측 스크롤과 우측 미리보기 stretch를 동일하게 설정.
   - 좌측 최소 폭을 낮춰 좌측 과점유 레이아웃 고정 해제.
2. 좌측 패널 폰트 2단계 축소:
   - `_shrink_widget_font(left_wrap, steps=2)` 추가 및 좌측 컨트롤에만 적용.
3. 미리보기 -> 좌측 실시간 동기화 보강:
   - `_sync_position_spins_from_preview()`를 추가해 현재 미리보기 형상 기준으로 BA/RA 거리(`ba_from_asset_nm`, `ra_from_asset_nm`)를 좌측 스핀박스에 반영.
   - 항공기 드래그, CAP pair 슬라이드(line/point), CAP pair 토글 정렬 시 동기화 호출.

### Validation (EN)
1. Syntax validation: `python -m py_compile fa50_0.5.81.py` passed.

### 검증 내용 (KO)
1. 문법 검증: `python -m py_compile fa50_0.5.81.py` 통과.

## v0.5.80
- Date/Time (KST): 2026-03-03 00:52
- Request Summary (EN): Reproduce with `OACM NO SW.csv` (`Back` to step 0, then repeated `Fwd`) and remove recurring false “Apply changed aircraft” popup.
- 요청 요약 (KO): `OACM NO SW.csv` 로드 후 `Back`으로 step0 이동, `Fwd` 반복 시 재발하는 “Apply changed aircraft” 오검출 팝업 제거.

### Changed Files
- `fa50_0.5.80.py` (new version from `fa50_0.5.79.py`)
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Fixed stale G-range clipping while restoring commands:
   - In `AircraftControls.set_command()`, reset `g_cmd` range to `[0.5, 9.0]` before applying saved `g_cmd`.
   - This prevents prior-step dynamic max range from silently clipping loaded values (e.g., 6.0 -> 4.0).
2. Fixed bank dirty-detection normalization for legacy CSV precision:
   - In `_cmd_values_equal()`, bank comparison now uses integer UI resolution with half-up rounding (`floor(x+0.5)`).
   - Prevents false dirty on values like `33.6` vs spinner `34`, `78.5` vs spinner `79`.

### 코드/로직 변경 사항 (KO)
1. 명령 복원 시 이전 G 범위 잔재로 인한 silent 클리핑 수정:
   - `AircraftControls.set_command()`에서 저장값 적용 전에 `g_cmd` 범위를 `[0.5, 9.0]`으로 초기화.
   - 이전 step의 동적 max range 때문에 저장 G가 자동으로 깎이는 문제(예: 6.0 -> 4.0) 제거.
2. 구버전 CSV 소수 bank 값 비교 정규화:
   - `_cmd_values_equal()`에서 bank 비교를 현재 UI 정수 분해능 + half-up 반올림(`floor(x+0.5)`)으로 수행.
   - `33.6` vs `34`, `78.5` vs `79` 같은 오검출 제거.

### Validation (EN)
1. Loaded `OACM NO SW.csv`.
2. Executed user path exactly: `Back` to step 0, then checked 10 consecutive `Fwd` attempts.
3. Result: no dirty aircraft detected on each attempt (`changed=[]` for step 0..9), so false prompt condition did not occur.

### 검증 내용 (KO)
1. `OACM NO SW.csv` 로드.
2. 사용자 재현 시나리오 그대로 수행: step0으로 `Back` 후 `Fwd` 10회 연속 검사.
3. 결과: 매 회차 `changed=[]`(step 0~9)로 오검출 조건 미발생.

## v0.5.79
- Date/Time (KST): 2026-03-03 00:45
- Request Summary (EN): Run random maneuver generation + repeated Back/Fwd validation and fix false “Apply changed aircraft” prompt that appears without user edits.
- 요청 요약 (KO): 랜덤 기동 생성 후 Back/Fwd 반복 검증을 수행하고, 사용자 수정이 없는데도 뜨는 “Apply changed aircraft” 오검출을 수정.

### Changed Files
- `fa50_0.5.79.py` (new version from `fa50_0.5.78.py`)
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Added command-intent flags to command payload:
   - `pitch_user_set`
   - `bank_user_set`
2. Updated `AircraftControls.read_command()` to include those intent flags.
3. Updated `AircraftControls.set_command()` to restore intent flags from command data, preventing display-only pitch from being reclassified as user input on Back.
4. Updated `MainWindow._cmd_values_equal()`:
   - `pitch_deg` is compared for dirty detection only when:
     - `pitch_hold` is enabled, or
     - pull mode is UP/DOWN and at least one side indicates explicit user pitch intent.
5. Extended default command schema and CSV scenario save/load to persist:
   - `pitch_user_set`
   - `bank_user_set`

### 코드/로직 변경 사항 (KO)
1. 명령 데이터에 사용자 입력 의도 플래그 추가:
   - `pitch_user_set`
   - `bank_user_set`
2. `AircraftControls.read_command()`가 위 플래그를 함께 저장하도록 수정.
3. `AircraftControls.set_command()`에서 플래그를 복원해, Back 시 표시용 pitch가 사용자 입력으로 재분류되는 문제를 제거.
4. `MainWindow._cmd_values_equal()` 변경:
   - dirty 판정에서 `pitch_deg` 비교는 다음 경우에만 수행:
     - `pitch_hold` 활성화
     - 또는 pull mode가 UP/DOWN이면서 명시적 사용자 pitch 입력 의도가 있을 때
5. 기본 명령 스키마와 CSV save/load에 아래 항목 영속화:
   - `pitch_user_set`
   - `bank_user_set`

### Validation (EN)
1. Runtime automation executed with Qt offscreen (`PYQTGRAPH_QT_LIB=PySide6`).
2. Random UI command generation -> step advance scenario creation.
3. Repeated `Back 1 -> changed-check -> Fwd 1` cycle for 20 iterations.
4. Result: `failures = 0` (no false dirty detection / no false prompt condition).

### 검증 내용 (KO)
1. Qt 오프스크린(`PYQTGRAPH_QT_LIB=PySide6`) 환경에서 런타임 자동 검증 수행.
2. UI에 랜덤 명령을 주입해 step을 생성.
3. `Back 1 -> 변경감지 검사 -> Fwd 1` 사이클을 20회 반복.
4. 결과: `failures = 0` (오검출 없음, false prompt 조건 미발생).

## v0.5.01
- Date/Time (KST): 2026-03-02 14:37
- Request Summary (EN): If user commands turn and G, then manually edits bank, treat as climb/descent turn intent: keep bank value and auto-check Pull Up.
- ��û ��� (KO): ����ڰ� ��ȸ�� G�� ���� �� ��ũ�� ���� �����ϸ� ���/���� ��ȸ �ǵ��� ������ ��ũ���� �����ϰ� Pull Up�� �ڵ� üũ.

### Changed Files
- `fa50_0.5.01.py` (new version from `fa50_0.5.00.py`)
- `fa50_0.5.01_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Updated `MainWindow._enforce_level_and_pull_logic()`.
2. Added `user_bank_turn_intent` condition:
   - turn is not straight (`turn != "S"`)
   - user explicitly edited bank (`has_user_bank_input()`)
   - commanded G is above 1.0 (`g_cmd > 1.0`)
   - bank is non-zero (`abs(bank_cmd) > 0`)
3. When condition is met:
   - force `level_hold` OFF
   - auto-set pull mode to `UP`
   - keep user-entered bank (no auto overwrite by level-assist path)
4. Existing straight-flight behavior remains unchanged (straight still auto-zeroes bank).

### �ڵ�/���� ���� ���� (KO)
1. `MainWindow._enforce_level_and_pull_logic()`�� ������.
2. `user_bank_turn_intent` ������ �߰���:
   - ������ �ƴ� ��ȸ ���� (`turn != "S"`)
   - ����ڰ� ��ũ�� ���� ������ (`has_user_bank_input()`)
   - G ����� 1.0 �ʰ� (`g_cmd > 1.0`)
   - ��ũ�� 0�� �ƴ� (`abs(bank_cmd) > 0`)
3. �� ���� ���� ��:
   - `level_hold` �ڵ� ����
   - pull mode�� `UP`���� �ڵ� ����
   - ����ڰ� �Է��� ��ũ���� ����(���� ���� ������ ����� ����)
4. ���� ���� ������ ������(���������� bank �ڵ� 0).

### Verification (EN)
- Validation report: `fa50_0.5.01_validation_report.txt`
- Total cases executed: 23 (>= required 20)
- Results:
  - PASS: `T1_user_bank_intent_auto_pullup`
  - PASS: `T2_zero_bank_no_forced_pullup`
  - PASS: `T3_straight_bank_zero`
  - PASS: `T4_23_random_runtime_20cases`
- Summary: Passed 4, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.01_validation_report.txt`
- �� ���� ���̽�: 23ȸ (�䱸 �ּ� 20ȸ ����)
- ���:
  - ���: `T1_user_bank_intent_auto_pullup`
  - ���: `T2_zero_bank_no_forced_pullup`
  - ���: `T3_straight_bank_zero`
  - ���: `T4_23_random_runtime_20cases`
- ���: 4 ���, 0 ����

### Remaining Risks / Notes (EN)
- `has_user_bank_input()` is session/UI-state based; behavior depends on whether bank was touched by user in current edit flow.

### ���� ����ũ / ���� (KO)
- `has_user_bank_input()`�� UI ���� ���� ����̹Ƿ�, ���� ���� �帧���� ����ڰ� ��ũ�� ���� �ǵ�ȴ����� ���� ������ �޶��� �� ����.

---

## v0.5.02
- Date/Time (KST): 2026-03-02 14:43
- Request Summary (EN): Even when Pull Up is currently selected, if user checks Level, Level must be selected and level correction (bank or G) must be applied.
- ��û ��� (KO): Pull Up�� ���õ� ���¿����� ����ڰ� Level�� üũ�ϸ� Level�� �켱 ���õǰ�, Level ����(bank �Ǵ� G ����)�� ����Ǿ�� ��.

### Changed Files
- `fa50_0.5.02.py` (new version from `fa50_0.5.01.py`)
- `fa50_0.5.02_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Updated `MainWindow._enforce_level_and_pull_logic()`.
2. Changed priority of the user-bank-intent branch by adding `and (not level_on)` to `user_bank_turn_intent`.
3. Resulting behavior:
   - If Level is ON, Level-assist path is applied first (Pull mode becomes NONE, level correction logic runs).
   - The auto Pull Up conversion is now only applied when Level is OFF.

### �ڵ�/���� ���� ���� (KO)
1. `MainWindow._enforce_level_and_pull_logic()`�� ������.
2. `user_bank_turn_intent` ���ǿ� `and (not level_on)`�� �߰��� �켱������ ������.
3. ���� ���:
   - Level�� ON�̸� Level ���� ������ �켱 �����(Pull mode�� NONE���� ����, level ���� ����).
   - �ڵ� Pull Up ��ȯ�� Level�� OFF�� ���� �����.

### Verification (EN)
- Validation report: `fa50_0.5.02_validation_report.txt`
- Total cases executed: 24 (>= required 20)
- Results:
  - PASS: `T1_level_overrides_pullup`
  - PASS: `T2_intent_pullup_when_not_level`
  - PASS: `T3_straight_bank_zero`
  - PASS: `T4_random_21_cases_runtime`
- Summary: Passed 4, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.02_validation_report.txt`
- �� ���� ���̽�: 24ȸ (�䱸 �ּ� 20ȸ ����)
- ���:
  - ���: `T1_level_overrides_pullup`
  - ���: `T2_intent_pullup_when_not_level`
  - ���: `T3_straight_bank_zero`
  - ���: `T4_random_21_cases_runtime`
- ���: 4 ���, 0 ����

### Remaining Risks / Notes (EN)
- `has_user_bank_input()` remains UI-session-state based; intent detection still depends on whether bank was explicitly touched by user.

### ���� ����ũ / ���� (KO)
- `has_user_bank_input()`�� UI ���� ���� ����̹Ƿ�, ��ũ�� ����ڰ� ���� �ǵ�ȴ��� ���ο� ���� �ǵ� �Ǵ� ����� �޶��� �� ����.
---
## v0.5.03
- Date/Time (KST): 2026-03-02 14:48
- Request Summary (EN): Fix conflict so both behaviors work: (1) Pull Up -> Level check must keep Level, and (2) while Level is ON, user bank edit in turn should auto-switch to Pull Up for climb/descent turn intent.
- ?? ?? (KO): ? ??? ?? ??? ?? ??: (1) Pull Up ???? Level ?? ? Level ??, (2) Level ????? ?? ? ???? bank? ?? ???? ??/?? ?? ??? Pull Up ?? ??.
### Changed Files
- 
a50_0.5.03.py (new version from 
a50_0.5.02.py)
- 
a50_0.5.03_validation_report.txt
- CHANGELOG_FA50.md (this file)
### Code/Logic Changes (EN)
1. Updated AircraftControl._on_level_toggled():
   - when Level is explicitly checked, reset manual-bank intent flag (_bank_user_set = False).
   - effect: immediate Level selection is not auto-overridden by stale prior bank intent.
2. Updated MainWindow._enforce_level_and_pull_logic():
   - removed nd (not level_on) from user_bank_turn_intent.
   - effect: if user later edits bank while turning with G>1, intent is re-armed and auto-switches to Pull Up (Level OFF).
3. Net behavior:
   - Level click priority works.
   - Later manual bank edit priority also works.
### ??/?? ?? ?? (KO)
1. AircraftControl._on_level_toggled() ??:
   - ???? Level? ????? ???? ?? bank ?? ???(_bank_user_set)? ???.
   - ??: ?? bank ?? ?? ??? Level ??? ?? ?? ???? ?? ??.
2. MainWindow._enforce_level_and_pull_logic() ??:
   - user_bank_turn_intent?? nd (not level_on) ?? ??.
   - ??: ?? ???? ?? ???? bank? ?? ?? ???? ??? ?????? Pull Up ?? ??(Level OFF).
3. ?? ??:
   - Level ?? ?? ?? ??.
   - ?? ?? bank ?? ?? ??? ?? ??.
### Verification (EN)
- Validation report: 
a50_0.5.03_validation_report.txt
- Total cases executed: 25 (>= required 20)
- Results:
  - PASS: T1_pullup_to_level_priority
  - PASS: T2_level_then_user_bank_to_pullup
  - PASS: T3_straight_bank_zero
  - PASS: T4_random_22_runtime
- Summary: Passed 4, Failed 0
### ?? (KO)
- ?? ???: 
a50_0.5.03_validation_report.txt
- ? ?? ???: 25? (?? ?? 20? ??)
- ??:
  - ??: T1_pullup_to_level_priority
  - ??: T2_level_then_user_bank_to_pullup
  - ??: T3_straight_bank_zero
  - ??: T4_random_22_runtime
- ??: 4 ??, 0 ??
### Remaining Risks / Notes (EN)
- Manual intent still depends on UI-state semantics (_bank_user_set) and is triggered by explicit user bank edits.
### ?? ??? / ?? (KO)
- ?? ?? ??? UI ?? ???(_bank_user_set) ????, bank ?? ?? ???? ?? ????.

---

## v0.5.06
- Date/Time (KST): 2026-03-02 15:04
- Request Summary (EN): During playback, LOS lines should be created via the lower-left LOS panel (relation map), not by right-click authoring.
- ��û ��� (KO): ��� �� LOS ������ ��Ŭ���� �ƴ϶� ���ϴ� LOS �г�(�����)�� �߰��ǵ��� ����.

### Changed Files
- `fa50_0.5.06.py` (new version from `fa50_0.5.05.py`)
- `fa50_0.5.06_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Updated `MainWindow._map_mode_enabled()` to always return `True`.
2. Effect:
   - LOS relation-map panel remains enabled during playback.
   - `_on_relation_map_pair_drawn(...)` now accepts pair creation during playback.
3. Playback LOS origin behavior:
   - In playback-time Step View, relation-map creation is stored as `origin="overview"`, so it is rendered immediately in realtime playback context.
4. Right-click authoring is not used for this playback-time LOS workflow.

### �ڵ�/���� ���� ���� (KO)
1. `MainWindow._map_mode_enabled()`�� �׻� `True`�� ��ȯ�ϵ��� ����.
2. ȿ��:
   - ��� �߿��� LOS ����� �г� �Է��� Ȱ��ȭ��.
   - `_on_relation_map_pair_drawn(...)` ��η� ��� �� LOS ������ ��������.
3. ��� �� LOS origin ����:
   - ��� �� Step View������ ����� ���� ��ũ�� `origin="overview"`�� ����Ǿ� �ǽð� ���ؽ�Ʈ���� ��� ��������.
4. ��� �� LOS ���� ��ũ�÷ο�� ��Ŭ���� �ƴ϶� LOS �г� ��θ� ���.

### Verification (EN)
- Validation report: `fa50_0.5.06_validation_report.txt`
- Total cases executed: 24 (>= required 20)
- Results:
  - PASS: `T1_map_enabled_during_playback`
  - PASS: `T2_relation_map_draw_playback`
  - PASS: `T3_right_click_not_used_playback`
  - PASS: `T4_relation_map_repeat_21`
- Summary: Passed 4, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.06_validation_report.txt`
- �� ���� ���̽�: 24ȸ (�䱸 �ּ� 20ȸ ����)
- ���:
  - ���: `T1_map_enabled_during_playback`
  - ���: `T2_relation_map_draw_playback`
  - ���: `T3_right_click_not_used_playback`
  - ���: `T4_relation_map_repeat_21`
- ���: 4 ���, 0 ����

### Remaining Risks / Notes (EN)
- Existing historical sections in `CHANGELOG_FA50.md` contain prior encoding corruption from earlier edits; current v0.5.06 entry is appended in UTF-8.

### ���� ����ũ / ���� (KO)
- `CHANGELOG_FA50.md`�� ���� �Ϻ� �������� ���� ���� �� �߻��� ���ڵ� ������ ���� ����. �̹� v0.5.06 ��Ʈ���� UTF-8�� �߰���.

---

## v0.5.07
- Date/Time (KST): 2026-03-02 15:20
- Request Summary (EN): DCA-time RA placement logic was changed to use asset forward-axis anchoring for LAB/ECHELON, and RA position controls are disabled after DCA setup.
- ��û ��� (KO): DCA ���� �� RA ��ġ ������ ���� ������ ���� LAB/ECHELON ��ġ�� �����ϰ�, ���� ���� RA ��ġ UI �Է��� ��Ȱ��ȭ.

### Changed Files
- `fa50_0.5.07.py` (new version from `fa50_0.5.06.py`)
- `fa50_0.5.07_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Added RA UI lock state and apply function:
   - `self.dca_ra_ui_locked`
   - `_apply_dca_ra_ui_lock()`
2. Added RA shape parser for current setup:
   - `_current_ra_shape_from_setup()`
3. Updated DCA RA layout application:
   - RA center anchored on asset forward axis.
   - `LAB`: lead RA left by half spacing, wing RA right by half spacing.
   - `ECHELON`: lead RA left-forward 45 deg by half spacing, wing RA right-aft by half spacing.
   - Removed conflicting prior half-distance offset behavior for these two shapes.
4. DCA apply/load and clear flows now toggle RA lock state and apply UI lock consistently.
5. UI refresh/input-enable path now reapplies DCA RA lock so controls remain disabled while DCA context is active.

### �ڵ�/���� ���� ���� (KO)
1. DCA ���� RA UI ��� ���� �� ���� �Լ� �߰�:
   - `self.dca_ra_ui_locked`
   - `_apply_dca_ra_ui_lock()`
2. ���� �¾����� RA ���� ���� �Ǻ� �Լ� �߰�:
   - `_current_ra_shape_from_setup()`
3. DCA RA ��ġ ���� ����:
   - RA �߽��� ���� ������ �������� ����.
   - `LAB`: ���� RA�� ���� 1/2, �� RA�� ���� 1/2�� �̵�.
   - `ECHELON`: ���� RA�� ������ 45�� ���� 1/2, �� RA�� ���Ĺ� 1/2�� �̵�.
   - �ش� �������� ���� �浹 ���� half-distance ������ ���� ����.
4. DCA ����/�ҷ�����/���� �帧���� RA ��� ���¸� �ϰ��ǰ� ����.
5. UI ����/�Է� Ȱ��ȭ ��ƾ������ ��� ������ ��ȣ���Ͽ� DCA Ȱ�� �� RA ��ġ �Է��� ��Ȱ�� ����.

### Verification (EN)
- Validation report: `fa50_0.5.07_validation_report.txt`
- Simple validation policy: 3 runs only
- Results:
  - PASS: `V1_2vs2_lab`
  - PASS: `V2_4vs2_echelon`
  - PASS: `V3_dca_ra_ui_lock`
- Summary: Passed 3, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.07_validation_report.txt`
- �ܼ� ���� ��å: 3ȸ�� ����
- ���:
  - ���: `V1_2vs2_lab`
  - ���: `V2_4vs2_echelon`
  - ���: `V3_dca_ra_ui_lock`
- ���: 3 ���, 0 ����

---

## v0.5.08
- Date/Time (KST): 2026-03-02 15:30
- Request Summary (EN): Fixed DCA RA-shape ambiguity so 2vs2/4vs2 LAB and ECHELON no longer leave RA lead (#3/#5) on the asset center extension line.
- ��û ��� (KO): DCA RA ���� �Ǻ� ��ȣ�� �������� 2vs2/4vs2�� LAB/ECHELON���� RA ����(#3/#5)�� ���� �߽� ���弱�� ���� ������ ����.

### Changed Files
- `fa50_0.5.08.py` (new version from `fa50_0.5.07.py`)
- `fa50_0.5.08_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Added `_infer_two_ship_ra_shape_from_controls(mode_key, ra_ids)`.
   - Infers `LAB/ECHELON/RANGE` from current RA wing relative bearing (nearest of 90/135/180).
2. Updated `_apply_dca_ba_ra_layout_via_be(...)`.
   - Keeps setup-key parse, but now applies control-state inference as fallback/override to avoid stale setup-key mismatch.
   - Ensures LAB/ECHELON branch is selected consistently when intended.

### �ڵ�/���� ���� ���� (KO)
1. `_infer_two_ship_ra_shape_from_controls(mode_key, ra_ids)` �߰�.
   - RA �� ��� bearing�� �������� `LAB/ECHELON/RANGE`(90/135/180 �ֱ���) �Ǻ�.
2. `_apply_dca_ba_ra_layout_via_be(...)` ����.
   - setup ���ڿ� �Ǻ��� �����ϵ�, ��� ��� �Ǻ��� ���� ����.
   - LAB/ECHELON �ǵ� �� �бⰡ ���������� ���õǵ��� ����.

### Verification (EN)
- Validation report: `fa50_0.5.08_validation_report.txt`
- Simple validation policy: 3 runs only
- Results:
  - PASS: `V1_py_compile_fa50_0.5.08`
  - PASS: `V2_shape_inference_hook_present`
  - PASS: `V3_shape_classifier_smoke`
- Summary: Passed 3, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.08_validation_report.txt`
- �ܼ� ���� ��å: 3ȸ�� ����
- ���:
  - ���: `V1_py_compile_fa50_0.5.08`
  - ���: `V2_shape_inference_hook_present`
  - ���: `V3_shape_classifier_smoke`
- ���: 3 ���, 0 ����

---

## v0.5.09
- Date/Time (KST): 2026-03-02 15:34
- Request Summary (EN): Further hardened DCA RA shape resolution for 2vs2/4vs2 to prevent RA lead (#3/#5) from remaining on asset forward-axis in LAB/ECHELON cases.
- ��û ��� (KO): 2vs2/4vs2 DCA RA ���� �Ǻ��� �߰� �����Ͽ� LAB/ECHELON���� RA ����(#3/#5)�� ���� �����࿡ ���� ������ ����.

### Changed Files
- `fa50_0.5.09.py` (new version from `fa50_0.5.08.py`)
- `fa50_0.5.09_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. `_current_ra_shape_from_setup()` hardened for `4vs2`:
   - Broad token priority: if setup text contains `ECHELON` or `LAB`, classify immediately.
   - Keeps exact `+ RA ...` parse as secondary.
2. `_infer_two_ship_ra_shape_from_controls()` improved:
   - LAB now accepts mirrored bearings `90/270`.
   - ECHELON now accepts mirrored bearings `135/225`.
   - RANGE accepts `180/0`.
3. In `_apply_dca_ba_ra_layout_via_be(...)`:
   - setup-derived `LAB/ECHELON` is now preserved (not overridden by fallback inference).
   - fallback inference applies only when setup result is not LAB/ECHELON.

### �ڵ�/���� ���� ���� (KO)
1. `4vs2`�� `_current_ra_shape_from_setup()` ����:
   - setup ���ڿ��� `ECHELON`/`LAB` ��ū�� ������ �켱 �з�.
   - ���� `+ RA ...` ��Ȯ �Ľ��� ������ ����.
2. `_infer_two_ship_ra_shape_from_controls()` ����:
   - LAB: `90/270` ��� ���.
   - ECHELON: `135/225` ��� ���.
   - RANGE: `180/0` ���.
3. `_apply_dca_ba_ra_layout_via_be(...)`����:
   - setup���� �̹� `LAB/ECHELON`�̸� fallback �߷����� ����� �ʵ��� ����.
   - setup�� ��ȣ�� ���� fallback �߷� ����.

### Verification (EN)
- Validation report: `fa50_0.5.09_validation_report.txt`
- Simple validation policy: 3 runs only
- Results:
  - PASS: `V1_py_compile_fa50_0.5.09`
  - PASS: `V2_ra_shape_guard_present`
  - PASS: `V3_shape_classifier_mirrored_smoke`
- Summary: Passed 3, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.09_validation_report.txt`
- �ܼ� ���� ��å: 3ȸ�� ����
- ���:
  - ���: `V1_py_compile_fa50_0.5.09`
  - ���: `V2_ra_shape_guard_present`
  - ���: `V3_shape_classifier_mirrored_smoke`
- ���: 3 ���, 0 ����

### Note (EN)
- Full GUI runtime reproduction could not be executed in this shell because `PyQt6` is not installed in the current environment.

### ���� (KO)
- ���� �� ȯ�濡 `PyQt6`�� ���� GUI ��Ÿ�� ���� �׽�Ʈ�� ���� �������� ����.

---

## v0.5.10
- Date/Time (KST): 2026-03-02 15:41
- Request Summary (EN): Added camera zoom controls via on-screen +/- buttons and keyboard shortcuts (+/-), including PageUp/PageDown.
- ��û ��� (KO): ī�޶� Ȯ��/��Ҹ� ȭ�� +/- ��ư�� Ű���� ����Ű(+/-), PageUp/PageDown���� ���� �����ϰ� �߰�.

### Changed Files
- `fa50_0.5.10.py` (new version from `fa50_0.5.09.py`)
- `fa50_0.5.10_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Added overlay zoom buttons on view:
   - `self.btn_view_zoom_in` (`+`)
   - `self.btn_view_zoom_out` (`-`)
2. Added unified zoom handler:
   - `_adjust_view_zoom(scale)` updates camera distance with clamped range (`500` to `300000`).
3. Connected zoom UI and shortcuts:
   - Button click: `+/-`
   - Keyboard: `+`, `=`, `Num+`, `-`, `_`, `Num-`, `PgUp`, `PgDown`
4. Updated overlay layout row to place zoom buttons next to `FWD/BACK`.
5. Added zoom tooltips in `_sync_play_button_icon()`.

### �ڵ�/���� ���� ���� (KO)
1. �� �������̿� �� ��ư �߰�:
   - `self.btn_view_zoom_in` (`+`)
   - `self.btn_view_zoom_out` (`-`)
2. ���� �� ó�� �Լ� �߰�:
   - `_adjust_view_zoom(scale)`���� ī�޶� distance�� `500~300000` ������ ������ ����.
3. UI/Ű���� ����:
   - ��ư Ŭ��: `+/-`
   - Ű����: `+`, `=`, `Num+`, `-`, `_`, `Num-`, `PgUp`, `PgDown`
4. �������� 1��(`FWD/BACK`)�� �� ��ư ��ġ �ݿ�.
5. `_sync_play_button_icon()`�� �� ��ư ���� �߰�.

### Verification (EN)
- Validation report: `fa50_0.5.10_validation_report.txt`
- Simple validation policy: 3 runs only
- Results:
  - PASS: `V1_py_compile_fa50_0.5.10`
  - PASS: `V2_zoom_bindings_present`
  - PASS: `V3_keyboard_zoom_shortcuts_present`
- Summary: Passed 3, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.10_validation_report.txt`
- �ܼ� ���� ��å: 3ȸ�� ����
- ���:
  - ���: `V1_py_compile_fa50_0.5.10`
  - ���: `V2_zoom_bindings_present`
  - ���: `V3_keyboard_zoom_shortcuts_present`
- ���: 3 ���, 0 ����

---

## v0.5.11
- Date/Time (KST): 2026-03-02 15:47
- Request Summary (EN): DCA Setup preview now reflects RA LAB/ECHELON placement logic the same way as runtime DCA application.
- ��û ��� (KO): DCA Setup �̸����⿡�� RA LAB/ECHELON ������ ���� DCA ���� ������ �����ϰ� ���̵��� ����.

### Changed Files
- `fa50_0.5.11.py` (new version from `fa50_0.5.10.py`)
- `fa50_0.5.11_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Added `ra_shape_preview` parameter to `DcaSetupDialog`.
2. In preview geometry builder, added runtime-consistent two-ship RA branch:
   - `LAB`: lead left half-span, wing right half-span.
   - `ECHELON`: lead left-forward, wing right-aft (normalized diagonal vectors).
3. Applied the preview RA-shape branch when:
   - RA has at least 2 aircraft,
   - shape is LAB/ECHELON,
   - preview drag override is not active (`_drag_changed == False`).
4. `MainWindow` now passes `ra_shape_preview=str(self._current_ra_shape_from_setup())` when opening DCA setup dialog.

### �ڵ�/���� ���� ���� (KO)
1. `DcaSetupDialog`�� `ra_shape_preview` ���� �߰�.
2. ������ ���� ��꿡 ���� ��Ÿ�Ӱ� ������ RA 2�� ���� �б� �߰�:
   - `LAB`: ���� ���� half-span, �� ���� half-span.
   - `ECHELON`: ���� ������, �� ���Ĺ�(����ȭ �밢 ����).
3. ������ ���� �б� ���� ����:
   - RA�� 2�� �̻�,
   - ������ LAB/ECHELON,
   - �巡�� ���� ���� ���°� �ƴ� ��(`_drag_changed == False`).
4. `MainWindow`���� DCA ���̾�α� ���� �� `ra_shape_preview=str(self._current_ra_shape_from_setup())` �����ϵ��� ����.

### Verification (EN)
- Validation report: `fa50_0.5.11_validation_report.txt`
- Simple validation policy: 3 runs only
- Results:
  - PASS: `V1_py_compile_fa50_0.5.11`
  - PASS: `V2_preview_ra_shape_wiring`
  - PASS: `V3_main_to_dialog_shape_pass`
- Summary: Passed 3, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.11_validation_report.txt`
- �ܼ� ���� ��å: 3ȸ�� ����
- ���:
  - ���: `V1_py_compile_fa50_0.5.11`
  - ���: `V2_preview_ra_shape_wiring`
  - ���: `V3_main_to_dialog_shape_pass`
- ���: 3 ���, 0 ����

---

## v0.5.12
- Date/Time (KST): 2026-03-02 15:51
- Request Summary (EN): Fixed DCA preview drag behavior and introduced mode control so default drag moves BA/RA as groups, while per-aircraft drag and metric overlays are only enabled from a dedicated tab with explicit activation.
- ��û ��� (KO): DCA �̸����� �巡�� ������ �����ϰ�, �⺻�� BA/RA �׷� �̵����� �����ϸ� ���� �ǿ��� ��ư�� ���� ���� ���� �װ��� �̵� �� ����/�Ÿ� ǥ�ð� �������� ����.

### Changed Files
- `fa50_0.5.12.py` (new version from `fa50_0.5.11.py`)
- `fa50_0.5.12_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Added preview mode UI in DCA dialog:
   - `Group Move` tab: default group-drag mode.
   - `Individual Adjust` tab with explicit toggle button (`���� �װ��� ��ġ���� ON/OFF`).
2. Added mode helpers:
   - `_on_preview_mode_tab_changed(...)`
   - `_on_individual_drag_toggled(...)`
   - `_is_individual_drag_enabled()`
3. Updated drag logic in `_apply_drag_position_nm(...)`:
   - Default mode: moving any aircraft in BA/RA translates the whole corresponding group together.
   - Individual mode (tab + toggle ON): preserves per-aircraft drag behavior.
4. Updated metric overlay rendering:
   - distance/bearing metric boxes are drawn only when individual mode is enabled.

### �ڵ�/���� ���� ���� (KO)
1. DCA ���̾�α� �̸����� ��� UI �߰�:
   - `Group Move` ��: �⺻ �׷� �̵�.
   - `Individual Adjust` �� + ����� Ȱ��ȭ ��ư(`���� �װ��� ��ġ���� ON/OFF`).
2. ��� ���� �Լ� �߰�:
   - `_on_preview_mode_tab_changed(...)`
   - `_on_individual_drag_toggled(...)`
   - `_is_individual_drag_enabled()`
3. `_apply_drag_position_nm(...)` �巡�� ���� ����:
   - �⺻ ���: BA/RA �Ҽ� �װ��� ��� ���� �巡���ص� �ش� �׷� ��ü�� ���� �̵�.
   - ���� ���(�� + ON): ���� ���� �װ��� �̵� ���� ���.
4. �Ÿ�/���� ��Ʈ�� �ڽ� ǥ�� ���� ����:
   - ���� ��� Ȱ�� �ÿ��� ǥ��.

### Verification (EN)
- Validation report: `fa50_0.5.12_validation_report.txt`
- Simple validation policy: 3 runs only
- Results:
  - PASS: `V1_py_compile_fa50_0.5.12`
  - PASS: `V2_preview_mode_tab_and_button`
  - PASS: `V3_drag_mode_logic_gate`
- Summary: Passed 3, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.12_validation_report.txt`
- �ܼ� ���� ��å: 3ȸ�� ����
- ���:
  - ���: `V1_py_compile_fa50_0.5.12`
  - ���: `V2_preview_mode_tab_and_button`
  - ���: `V3_drag_mode_logic_gate`
- ���: 3 ���, 0 ����

---

## v0.5.13
- Date/Time (KST): 2026-03-02 15:56
- Request Summary (EN): Replaced preview individual-move tab UI with a checkbox prompt, and fixed DCA apply so RA/BA positions adjusted in preview are reflected in real setup placement.
- ��û ��� (KO): �̸����� ���� �̵� �� UI�� üũ�ڽ� ������� �����ϰ�, �̸����⿡�� ������ RA/BA ��ġ�� ���� DCA ��ġ���� �ݿ��ǵ��� ����.

### Changed Files
- `fa50_0.5.13.py` (new version from `fa50_0.5.12.py`)
- `fa50_0.5.13_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. DCA preview control UI changed:
   - Removed tab-based `Group Move / Individual Adjust` control.
   - Added checkbox prompt: `�װ��⸦ ���� �����ϱ��?` + help text.
   - Individual drag is now enabled only by this checkbox.
2. Drag behavior kept as requested:
   - Default (checkbox OFF): BA moves as BA group, RA moves as RA group.
   - Checkbox ON: per-aircraft independent drag enabled.
   - Distance/bearing metric boxes shown only when checkbox ON.
3. Applied-preview position persistence fix:
   - Added `respect_member_offsets` option in `_apply_dca_ba_ra_layout_via_be(...)`.
   - In DCA dialog apply path, when preview drag changed (`_drag_changed=True`), call now passes `respect_member_offsets=True`.
   - Effect: RA moved in preview is no longer reset to original runtime default location on actual setup apply.

### �ڵ�/���� ���� ���� (KO)
1. DCA �̸����� ���� UI ����:
   - `Group Move / Individual Adjust` �� ����.
   - `�װ��⸦ ���� �����ϱ��?` ���� + üũ�ڽ� ������� ��ü.
   - ���� �巡�״� �ش� üũ�ڽ� ON�� ���� Ȱ��ȭ.
2. ��û�� �巡�� ���� ����:
   - �⺻(üũ OFF): BA�� BA����, RA�� RA���� �׷� �̵�.
   - üũ ON: �װ��� ���� �̵� ����.
   - �Ÿ�/���� ��Ʈ�� �ڽ��� üũ ON�� ���� ǥ��.
3. �̸�����-������ �ݿ� ���� ����:
   - `_apply_dca_ba_ra_layout_via_be(...)`�� `respect_member_offsets` �ɼ� �߰�.
   - DCA ���̾�α� ���� �� `_drag_changed=True`�̸� `respect_member_offsets=True`�� ȣ��.
   - ȿ��: �̸����⿡�� �̵��� RA ��ġ�� ���� ���� ��ġ���� �ݿ��ǰ� �ʱ� ��ġ�� �ǵ��ư��� ����.

### Verification (EN)
- Validation report: `fa50_0.5.13_validation_report.txt`
- Simple validation policy: 3 runs only
- Results:
  - PASS: `V1_py_compile_fa50_0.5.13`
  - PASS: `V2_preview_checkbox_mode`
  - PASS: `V3_preview_to_apply_offset_bridge`
- Summary: Passed 3, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.13_validation_report.txt`
- �ܼ� ���� ��å: 3ȸ�� ����
- ���:
  - ���: `V1_py_compile_fa50_0.5.13`
  - ���: `V2_preview_checkbox_mode`
  - ���: `V3_preview_to_apply_offset_bridge`
- ���: 3 ���, 0 ����

---

## v0.5.14
- Date/Time (KST): 2026-03-02 15:59
- Request Summary (EN): Fixed DCA preview group-drag so RA #5/#6 ordering no longer flips while moving the RA group.
- ��û ��� (KO): DCA �̸����⿡�� RA �׷� �̵� �� #5/#6 ��ġ�� ���� �ڹٲ�� ������ ����.

### Changed Files
- `fa50_0.5.14.py` (new version from `fa50_0.5.13.py`)
- `fa50_0.5.14_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Updated preview group-drag branch in `_apply_drag_position_nm(...)`.
2. Previous behavior:
   - only lead offset was shifted during group drag.
   - could cause shape re-materialization mismatch and visual #5/#6 swap.
3. New behavior:
   - computes current positions for all members in dragged group (BA or RA),
   - applies one common translation delta to each member,
   - writes back all member offsets relative to group base.
4. Effect:
   - preserves left/right ordering and spacing while dragging group.

### �ڵ�/���� ���� ���� (KO)
1. `_apply_drag_position_nm(...)`�� �׷� �巡�� �б� ����.
2. ���� ����:
   - �׷� �̵� �� ���� �����¸� �̵�.
   - ���� ���� �籸�� �������� #5/#6 �ð��� �ڹٲ� ����.
3. ���� ����:
   - �巡�׵� �׷�(BA/RA)�� ���� ǥ�� ��ǥ�� ��� ����,
   - ���� delta�� ���� �����̵�,
   - �׷� ���� �������� �� ��ü���� �ٽ� ���.
4. ȿ��:
   - �׷� �̵� �� ��/�� ������ ������ ������.

### Verification (EN)
- Validation report: `fa50_0.5.14_validation_report.txt`
- Simple validation policy: 3 runs only
- Results:
  - PASS: `V1_py_compile_fa50_0.5.14`
  - PASS: `V2_group_drag_translate_all_members`
  - PASS: `V3_left_right_preserve_logic_present`
- Summary: Passed 3, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.14_validation_report.txt`
- �ܼ� ���� ��å: 3ȸ�� ����
- ���:
  - ���: `V1_py_compile_fa50_0.5.14`
  - ���: `V2_group_drag_translate_all_members`
  - ���: `V3_left_right_preserve_logic_present`
- ���: 3 ���, 0 ����

---

## v0.5.15
- Date/Time (KST): 2026-03-02 16:05
- Request Summary (EN): Fixed DCA preview so battlefield framing stays fixed while dragging aircraft; the battlefield no longer shifts/disappears during preview movement.
- ��û ��� (KO): DCA �̸����⿡�� �װ��� �巡�� �� ���� �����̹��� �����ǵ��� �����Ͽ� ������ �����̰ų� ������� ������ �ذ�.

### Changed Files
- `fa50_0.5.15.py` (new version from `fa50_0.5.14.py`)
- `fa50_0.5.15_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Updated preview auto-fit bounds in `_update_preview()`.
2. Removed BA/RA draggable aircraft points from map framing bounds.
3. Kept static DCA geometry (mission, BE/ASSET, CAP/HMRL/DEZ/COMMIT/RA line/radius) as framing basis.
4. Effect:
   - dragging aircraft no longer recenters/rescales the whole preview battlefield.
   - battlefield remains visually fixed while aircraft move.

### �ڵ�/���� ���� ���� (KO)
1. `_update_preview()`�� �̸����� �ڵ� �����̹� ��� ��� ����.
2. �巡�׵Ǵ� BA/RA �װ��� ��ǥ�� �����̹� ��迡�� ����.
3. ���� ���� ������ ���� DCA ���(�̼� ����, BE/ASSET, CAP/HMRL/DEZ/COMMIT/RA ����/�ݰ�)�� ����.
4. ȿ��:
   - �װ��� �̵� �� �̸����� ��ü�� ���߽�/�罺���ϵ��� ����.
   - ������ �����ǰ� �װ��⸸ ������ ����.

### Verification (EN)
- Validation report: `fa50_0.5.15_validation_report.txt`
- Simple validation policy: 3 runs only
- Results:
  - PASS: `V1_py_compile_fa50_0.5.15`
  - PASS: `V2_fixed_battlefield_bounds_comment`
  - PASS: `V3_bounds_excludes_dragged_aircraft`
- Summary: Passed 3, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.15_validation_report.txt`
- �ܼ� ���� ��å: 3ȸ�� ����
- ���:
  - ���: `V1_py_compile_fa50_0.5.15`
  - ���: `V2_fixed_battlefield_bounds_comment`
  - ���: `V3_bounds_excludes_dragged_aircraft`
- ���: 3 ���, 0 ����

---

## v0.5.16
- Date/Time (KST): 2026-03-02 16:07
- Request Summary (EN): Fixed preview group-drag offset semantics so dragging #5 no longer sends #6 away/disappears.
- ��û ��� (KO): �̸����� �׷� �巡�� ������ ������ �����Ͽ� #5 �̵� �� #6�� �ָ� ���ư� ������� ������ �ذ�.

### Changed Files
- `fa50_0.5.16.py` (new version from `fa50_0.5.15.py`)
- `fa50_0.5.16_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Updated default group-drag branch in `_apply_drag_position_nm(...)`.
2. Root cause:
   - non-lead member offsets were being rewritten as base-relative during group move,
   - but dialog geometry expects non-lead offsets to be lead-relative.
3. Fix:
   - compute translated positions for all members,
   - write lead offset as base-relative,
   - write each non-lead offset as lead-relative (`member - moved_lead`).
4. Effect:
   - RA wing (#6) remains in correct relative position while moving RA lead (#5),
   - no disappearing/fly-away behavior.

### �ڵ�/���� ���� ���� (KO)
1. `_apply_drag_position_nm(...)`�� �⺻ �׷� �巡�� �б� ����.
2. ����:
   - �׷� �̵� �� �񸮵� ��� �������� base �������� ����,
   - �׷��� ���̾�α� ���� ����� �񸮵� �������� lead �������� �ؼ�.
3. ����:
   - �׷� ��� ���� �̵� ��ǥ ���,
   - ����� base ���� ���������� ����,
   - �񸮵�� �̵��� ���� ���� ��� ������(`member - moved_lead`)���� ����.
4. ȿ��:
   - #5 �̵� �� #6 ��� ��ġ ����,
   - ������ų� Ƣ�� ���� ����.

### Verification (EN)
- Validation report: `fa50_0.5.16_validation_report.txt`
- Simple validation policy: 3 runs only
- Results:
  - PASS: `V1_py_compile_fa50_0.5.16`
  - PASS: `V2_group_drag_offset_semantics`
  - PASS: `V3_ra_wing_disappear_guard`
- Summary: Passed 3, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.16_validation_report.txt`
- �ܼ� ���� ��å: 3ȸ�� ����
- ���:
  - ���: `V1_py_compile_fa50_0.5.16`
  - ���: `V2_group_drag_offset_semantics`
  - ���: `V3_ra_wing_disappear_guard`
- ���: 3 ���, 0 ����

---

## v0.5.17
- Date/Time (KST): 2026-03-02 16:17
- Request Summary (EN): Hardened arrow shaft rendering for overview/play by drawing shaft/wing as explicit line segments to prevent intermittent missing-shaft behavior on some aircraft/steps.
- ��û ��� (KO): overview/play���� �Ϻ� ��ü/������ shaft ���� ������ ���� ���� ȭ��ǥ�� ���������� �ƴ� shaft/wing ���� ���׸�Ʈ�� �׸����� ����.

### Changed Files
- `fa50_0.5.17.py` (new version from `fa50_0.5.16.py`)
- `fa50_0.5.17_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Updated `_draw_arrow_dashed(...)`:
   - replaced polyline build (`_add_step_arrow_poly`) with explicit segment draws:
     - shaft: `tail -> apex`
     - wing(s): `apex -> wing_l/wing_r`
2. Updated `_draw_arrow_solid(...)` similarly to explicit segment-based rendering.
3. Reason:
   - explicit per-segment rendering is more robust against intermittent shaft-drop artifacts in overview/play pipelines.

### �ڵ�/���� ���� ���� (KO)
1. `_draw_arrow_dashed(...)` ����:
   - ��������(`_add_step_arrow_poly`) ��� ���׸�Ʈ ���� ���������� ����:
     - shaft: `tail -> apex`
     - wing: `apex -> wing_l/wing_r`
2. `_draw_arrow_solid(...)`�� �����ϰ� ���׸�Ʈ ������ ������� ����.
3. ����:
   - overview/play ������ ��ο��� ������ shaft ���� ��Ƽ��Ʈ�� ����.

### Verification (EN)
- Validation report: `fa50_0.5.17_validation_report.txt`
- Simple validation policy: 3 runs only
- Results:
  - PASS: `V1_py_compile_fa50_0.5.17`
  - PASS: `V2_shaft_draw_as_explicit_segment`
  - PASS: `V3_no_polyline_shaft_path`
- Summary: Passed 3, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.17_validation_report.txt`
- �ܼ� ���� ��å: 3ȸ�� ����
- ���:
  - ���: `V1_py_compile_fa50_0.5.17`
  - ���: `V2_shaft_draw_as_explicit_segment`
  - ���: `V3_no_polyline_shaft_path`
- ���: 3 ���, 0 ����

### Note (EN)
- Full visual confirmation in real GUI is still required on your side; this environment supports code/runtime checks but not human-vision UI inspection.

### ���� (KO)
- ���� �ð� Ȯ���� ����� ȭ�鿡�� �ʿ���. �� ȯ���� �ڵ�/��Ÿ�� ������ �����ϳ� ��� ������ ���� UI�� ���� ������ �Ұ�.

---

## v0.5.18
- Date/Time (KST): 2026-03-02 16:35
- Request Summary (EN): Added an overview/play arrow Z-lift to prevent shaft visibility loss caused by depth conflict with path/line rendering.
- ��û ��� (KO): overview/play���� ��μ����� ���� �浹�� shaft�� ���� ���̴� ������ ���̱� ���� ȭ��ǥ ������ Z �������� �߰�.

### Changed Files
- `fa50_0.5.18.py` (new version from `fa50_0.5.17.py`)
- `fa50_0.5.18_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. In `refresh_ui()` overview/play branch, introduced `z_lift_ft = 12.0` for arrow rendering points.
2. Applied Z-lift to:
   - historical arrow starts (`st_pt`) and their `next_pt`
   - current arrow start (`cur_pt_over`) and `next_cur`
3. Arrow geometry/label anchor for overview/play now uses lifted points, while state/path data remains unchanged.
4. Purpose:
   - reduce shaft flicker/skip that can occur from depth overlap with overview path line rendering.

### �ڵ�/���� ���� ���� (KO)
1. `refresh_ui()`�� overview/play �б⿡ `z_lift_ft = 12.0` �߰�.
2. Z ������ ���� ���:
   - ���� ���� ȭ��ǥ ������(`st_pt`)�� `next_pt`
   - ���� ȭ��ǥ ������(`cur_pt_over`)�� `next_cur`
3. overview/play ȭ��ǥ/�� ��Ŀ�� ��� �����ϸ�, ���� ���°�/��� �����ʹ� �������� ����.
4. ����:
   - overview ��μ����� ���� ��ħ���� �߻��� �� �ִ� shaft �����/���� ��ȭ.

### Verification (EN)
- Validation report: `fa50_0.5.18_validation_report.txt`
- Simple validation policy: 3 runs only
- Results:
  - PASS: `V1_py_compile_fa50_0.5.18`
  - PASS: `V2_overview_arrow_z_lift_applied`
  - PASS: `V3_offscreen_4vs2_fwd5_overview_labels`
- Summary: Passed 3, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.18_validation_report.txt`
- �ܼ� ���� ��å: 3ȸ�� ����
- ���:
  - ���: `V1_py_compile_fa50_0.5.18`
  - ���: `V2_overview_arrow_z_lift_applied`
  - ���: `V3_offscreen_4vs2_fwd5_overview_labels`
- ���: 3 ���, 0 ����

---

## v0.5.21
- Date/Time (KST): 2026-03-02 16:41
- Request Summary (EN): Fixed persistent Overview/Play arrow issue where #4~#8 shafts appeared every other step; render now always creates one shaft per step from state heading.
- ��û ��� (KO): Overview/Play���� #4~#8 shaft�� �� ĭ�� ��� ���̴� ������ ����. ���� state heading ������� ���ܸ��� shaft�� �׻� ������.

### Changed Files
- `fa50_0.5.21.py` (new version from `fa50_0.5.20.py`)
- `fa50_0.5.21_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Updated `MainWindow.refresh_ui()` overview/play historical-step arrow path.
2. Removed pair-distance-driven drawing path from overview/play historical loop:
   - no longer uses `self._draw_overview_step_arrow_from_pair(...)` in that loop.
3. Added heading-based draw path for every historical step:
   - computes `draw_hdg = self._overview_arrow_hdg_deg(...)`
   - renders with `self._draw_arrow_dashed(..., draw_hdg, ..., next_pos=None)`
4. Stabilized variable usage:
   - `hlen_hist` is assigned before drawing/label call and reused consistently.
5. Effect:
   - even when `p0->p1` displacement is tiny/zero, each step still gets an explicit shaft, matching step-view expectation.

### �ڵ�/���� ���� ���� (KO)
1. `MainWindow.refresh_ui()`�� overview/play ���� ���� ȭ��ǥ ���� ��θ� ������.
2. overview/play ���� �������� �Ÿ� ��� ��� ���� ��θ� ������:
   - �ش� �������� `self._draw_overview_step_arrow_from_pair(...)`�� �� �̻� ������� ����.
3. ��� ���� ���ܿ� ���� heading ��� ������ ������:
   - `draw_hdg = self._overview_arrow_hdg_deg(...)` ���
   - `self._draw_arrow_dashed(..., draw_hdg, ..., next_pos=None)`�� ����
4. ���� ��� ����ȭ:
   - `hlen_hist`�� draw/label ȣ�� ���� ���� �Ҵ��Ͽ� �ϰ��ǰ� ���.
5. ȿ��:
   - `p0->p1` �̵����� �ſ� �۰ų� 0�̾ �� ���� shaft�� ��������� �����Ǿ� step-view�� �ϰ��� ǥ�ø� ����� �� ����.

### Verification (EN)
- Validation report: `fa50_0.5.21_validation_report.txt`
- Simple validation policy: 3 runs only (per user request for this type of simple verification)
- Results:
  - PASS: `V1_py_compile_fa50_0.5.21`
  - PASS: `V2_overview_loop_uses_heading_based_dashed_draw`
  - PASS: `V3_hlen_hist_defined_before_attached_label_draw`
- Summary: Passed 3, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.21_validation_report.txt`
- �ܼ� ���� ��å: 3ȸ�� ����(����� ��û �ݿ�)
- ���:
  - ���: `V1_py_compile_fa50_0.5.21`
  - ���: `V2_overview_loop_uses_heading_based_dashed_draw`
  - ���: `V3_hlen_hist_defined_before_attached_label_draw`
- ���: 3 ���, 0 ����

### Remaining Risks / Notes (EN)
- This environment currently lacks `PyQt6`, so direct offscreen GUI runtime verification could not be executed here in this cycle.
- Real visual confirmation on your runtime is still required for final acceptance.

### ���� ����ũ / ���� (KO)
- ���� ���� ȯ�濡 `PyQt6`�� ���� �̹� ����Ŭ������ ������ũ�� GUI ��Ÿ�� ������ ���� �������� ����.
- ���� �Ǵ��� ���� ����� ���� ȯ�濡�� ���� �ð� Ȯ���� �ʿ���.

---

## v0.5.22
- Date/Time (KST): 2026-03-02 16:58
- Request Summary (EN): Added a visual-layer enforcement for step arrow segments to stop shaft disappearance that occurs only in actual Overview/Play rendering.
- ��û ��� (KO): ���� Overview/Play ȭ�鿡���� �߻��ϴ� shaft ������ ���� ���� step ȭ��ǥ ���׸�Ʈ ���� ���̾� �켱������ ���� ����.

### Changed Files
- `fa50_0.5.22.py` (new version from `fa50_0.5.21.py`)
- `fa50_0.5.22_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Updated `MainWindow._add_step_arrow_segment(...)`:
   - added `item.setGLOptions("additive")`
   - added `item.setDepthValue(100.0)`
2. Updated `MainWindow._add_step_arrow_poly(...)` with same render-priority options.
3. Effect:
   - step arrow shaft/head lines are rendered with stronger foreground priority, reducing depth-fighting with overview path/grid/other lines.

### �ڵ�/���� ���� ���� (KO)
1. `MainWindow._add_step_arrow_segment(...)` ����:
   - `item.setGLOptions("additive")` �߰�
   - `item.setDepthValue(100.0)` �߰�
2. `MainWindow._add_step_arrow_poly(...)`���� ������ ���� �켱���� �ɼ� ����.
3. ȿ��:
   - overview ��μ�/�׸���/��Ÿ ������ ���� �浹�� �ٿ� step arrow shaft/head�� ���濡�� ���������� ���̵��� ��.

### Verification (EN)
- Validation report: `fa50_0.5.22_validation_report.txt`
- Simple validation policy: 3 runs only
- Results:
  - PASS: `V1_py_compile_fa50_0.5.22`
  - PASS: `V2_step_arrow_segment_uses_additive_and_depth100`
  - PASS: `V3_step_arrow_poly_uses_additive_and_depth100`
- Summary: Passed 3, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.22_validation_report.txt`
- �ܼ� ���� ��å: 3ȸ�� ����
- ���:
  - ���: `V1_py_compile_fa50_0.5.22`
  - ���: `V2_step_arrow_segment_uses_additive_and_depth100`
  - ���: `V3_step_arrow_poly_uses_additive_and_depth100`
- ���: 3 ���, 0 ����

### Remaining Risks / Notes (EN)
- Full human visual validation is still required on your GUI runtime.
- In this environment, direct GL framebuffer capture is currently unstable for this app stack.

### ���� ����ũ / ���� (KO)
- ���� �ð� ������ ����� GUI ���� ȯ�濡�� Ȯ���� �ʿ���.
- ���� �� ���� ȯ�濡���� �ش� �� ������ GL �����ӹ��� ĸó�� ���������� �������� ����.

---

## v0.5.23
- Date/Time (KST): 2026-03-02 17:11
- Request Summary (EN): Implemented option #2 visual verification automation with Top View capture: auto-run 4vs2, fwd x5, and export Overview/Play PNG plus probe log.
- ��û ��� (KO): ��û�� 2�� ���(�ڵ� �ð�����)�� Top View ĸó�� ����: 4vs2 �ڵ� ���� �� fwd 5ȸ, Overview/Play PNG �� �α� �ڵ� ����.

### Changed Files
- `fa50_0.5.23.py` (new version from `fa50_0.5.22.py`)
- `fa50_0.5.23_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Added CLI auto-probe mode in `main()`:
   - `--auto-visual-probe`
   - optional `--probe-prefix=<name>`
2. In auto-probe mode:
   - skip `run_sanity_tests()` to avoid long startup delay
   - force scenario: `4vs2 BA OFFSET BOX + RA RANGE`
   - run `advance_steps(5)`
   - set `Overview View` + `Top View`
   - capture window PNG: `<prefix>_overview.png`
   - set playback-like frame (`playback_active=True`, `playback_step_float=3.4`, `current_step=3`)
   - capture window PNG: `<prefix>_play.png`
   - write `<prefix>.txt` with action metadata and `step_arrow_items` counts by aircraft
3. Auto mode exits immediately after capture/log write (no interactive loop).

### �ڵ�/���� ���� ���� (KO)
1. `main()`�� CLI �ڵ����� ��� �߰�:
   - `--auto-visual-probe`
   - ���� �ɼ� `--probe-prefix=<name>`
2. �ڵ����� ��� ����:
   - ���� �� `run_sanity_tests()` �ǳʶ�(�� �ʱ� ���� ����)
   - �ó������� `4vs2 BA OFFSET BOX + RA RANGE`�� ����
   - `advance_steps(5)` ����
   - `Overview View` + `Top View` ����
   - ������ PNG ����: `<prefix>_overview.png`
   - playback ���� ������(`playback_active=True`, `playback_step_float=3.4`, `current_step=3`)���� ��ȯ
   - ������ PNG ����: `<prefix>_play.png`
   - `<prefix>.txt`�� ���� ��Ÿ�����Ϳ� ��ü�� `step_arrow_items` ���� ���
3. �ڵ����� ĸó/�α� ���� �� ��� ����Ǹ�, ���ͷ�Ƽ�� ������ Ÿ�� ����.

### Verification (EN)
- Validation report: `fa50_0.5.23_validation_report.txt`
- Simple validation policy: 3 runs only
- Results:
  - PASS: `V1_py_compile_fa50_0.5.23`
  - PASS: `V2_auto_probe_cli_and_topview_capture_path_present`
  - PASS: `V3_auto_probe_skips_sanity_and_emits_probe_log_fields`
- Summary: Passed 3, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.23_validation_report.txt`
- �ܼ� ���� ��å: 3ȸ�� ����
- ���:
  - ���: `V1_py_compile_fa50_0.5.23`
  - ���: `V2_auto_probe_cli_and_topview_capture_path_present`
  - ���: `V3_auto_probe_skips_sanity_and_emits_probe_log_fields`
- ���: 3 ���, 0 ����

### Remaining Risks / Notes (EN)
- In this sandbox environment, offscreen OpenGL runtime is unstable (command timed out), so PNG generation could not be confirmed here.
- Feature is designed for user runtime verification with actual display/OpenGL stack.

### ���� ����ũ / ���� (KO)
- �� ����ڽ� ȯ�濡���� offscreen OpenGL ��Ÿ���� �Ҿ�����(Ÿ�Ӿƿ�) PNG ���� ���� Ȯ���� �Ϸ����� ����.
- ����� ����� ���� ���� ȯ��(���÷���/OpenGL ����)���� �����ϵ��� �����.

---

## v0.5.24
- Date/Time (KST): 2026-03-02 17:14
- Request Summary (EN): Clarified probe output visibility by fixing output folder and auto-opening generated PNG/log files.
- ��û ��� (KO): PNG ���� ��ġ�� ��Ȯ�� �ϰ�, ������ PNG/�α׸� �ڵ����� ���� ����� �ð� Ȯ���� �ٷ� �����ϵ��� ����.

### Changed Files
- `fa50_0.5.24.py` (new version from `fa50_0.5.23.py`)
- `fa50_0.5.24_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. Auto probe output directory changed:
   - from script root to fixed folder: `visual_probes/`
   - ensures probe artifacts are grouped and easy to find.
2. Auto-open behavior added (default ON) after capture:
   - opens `<prefix>_overview.png`
   - opens `<prefix>_play.png`
   - opens `<prefix>.txt`
3. Added optional flag:
   - `--no-open-probe` to disable auto-opening.

### �ڵ�/���� ���� ���� (KO)
1. �ڵ� ���� ��� ���� ��θ� ����:
   - ��ũ��Ʈ ��Ʈ���� `visual_probes/` ������ ����
   - ���⹰�� �� ���� �� ã�� ����.
2. ĸó �� �ڵ� ���� ��� �߰�(�⺻ ON):
   - `<prefix>_overview.png`
   - `<prefix>_play.png`
   - `<prefix>.txt`
3. �ɼ� �߰�:
   - �ڵ� ���� ��Ȱ��ȭ: `--no-open-probe`

### Verification (EN)
- Validation report: `fa50_0.5.24_validation_report.txt`
- Simple validation policy: 3 runs only
- Results:
  - PASS: `V1_py_compile_fa50_0.5.24`
  - PASS: `V2_output_path_fixed_to_visual_probes`
  - PASS: `V3_auto_open_and_no_open_flag_present`
- Summary: Passed 3, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.24_validation_report.txt`
- �ܼ� ���� ��å: 3ȸ�� ����
- ���:
  - ���: `V1_py_compile_fa50_0.5.24`
  - ���: `V2_output_path_fixed_to_visual_probes`
  - ���: `V3_auto_open_and_no_open_flag_present`
- ���: 3 ���, 0 ����

### Remaining Risks / Notes (EN)
- If OpenGL capture itself fails in runtime, files may still not appear; in that case probe txt will include error context.

### ���� ����ũ / ���� (KO)
- ��Ÿ�� OpenGL ĸó ��ü�� �����ϸ� PNG�� �������� ���� �� ������, �� ��� probe txt�� ���� ������ ��ϵ�.

---

## v0.5.25
- Date/Time (KST): 2026-03-02 17:17
- Request Summary (EN): Fixed "no PNG/no open" diagnosis gap by forcing probe log generation at all failure points and adding a one-click probe runner batch.
- ��û ��� (KO): "PNG �̻���/�̿���" ��Ȳ���� ���� ������ �����ϵ��� ��� �ʱ� ���� ���������� probe �α׸� ���� �����ϰ� ��Ŭ�� ���� ��ġ���� �߰�.

### Changed Files
- `fa50_0.5.25.py` (new version from `fa50_0.5.24.py`)
- `run_visual_probe_0.5.25.bat` (new)
- `fa50_0.5.25_validation_report.txt`
- `CHANGELOG_FA50.md` (this file)

### Code/Logic Changes (EN)
1. In `main()`, auto-probe paths are precomputed at startup (`visual_probes/<prefix>.*`).
2. Added guaranteed early-failure logging in auto-probe mode:
   - OpenGL import failure
   - missing NPZ
   - `MainWindow` initialization failure
   -> all now write `visual_probes/<prefix>.txt` before return.
3. Added probe progress checkpoints to log:
   - `checkpoint=apply_startup_profile`
   - `checkpoint=advance_steps_5`
   - `checkpoint=set_overview_top`
   - `checkpoint=playback_like_frame`
4. Added one-click runner script:
   - `run_visual_probe_0.5.25.bat`
   - forces `.venv_pack\Scripts\python.exe`
   - runs auto-probe and opens generated files if present.

### �ڵ�/���� ���� ���� (KO)
1. `main()` ���� �� �ڵ����� ��� ���(`visual_probes/<prefix>.*`)�� �����.
2. �ڵ����� ��忡�� �ʱ� ���е� �α� ���� ���:
   - OpenGL import ����
   - NPZ ���� ����
   - `MainWindow` �ʱ�ȭ ����
   -> ��� `visual_probes/<prefix>.txt`�� ����� ����.
3. �α׿� �ܰ� üũ����Ʈ �߰�:
   - `checkpoint=apply_startup_profile`
   - `checkpoint=advance_steps_5`
   - `checkpoint=set_overview_top`
   - `checkpoint=playback_like_frame`
4. ��Ŭ�� ���� ��ġ �߰�:
   - `run_visual_probe_0.5.25.bat`
   - `.venv_pack\Scripts\python.exe` ���� ���
   - ���� ������ ������ �ڵ� ����.

### Verification (EN)
- Validation report: `fa50_0.5.25_validation_report.txt`
- Simple validation policy: 3 runs only
- Results:
  - PASS: `V1_py_compile_fa50_0.5.25`
  - PASS: `V2_auto_probe_early_failure_logging_paths_present`
  - PASS: `V3_probe_runner_batch_exists`
- Summary: Passed 3, Failed 0

### ���� (KO)
- ���� ����Ʈ: `fa50_0.5.25_validation_report.txt`
- �ܼ� ���� ��å: 3ȸ�� ����
- ���:
  - ���: `V1_py_compile_fa50_0.5.25`
  - ���: `V2_auto_probe_early_failure_logging_paths_present`
  - ���: `V3_probe_runner_batch_exists`
- ���: 3 ���, 0 ����

### Remaining Risks / Notes (EN)
- If process is externally killed, partial logs may be produced.

### ���� ����ũ / ���� (KO)
- ���μ����� �ܺο��� ���� ����Ǹ� �αװ� �Ϻθ� ���� �� ����.


---

## v0.5.29
- Date/Time (KST): 2026-03-02 17:27
- Request Summary (EN): Auto popup handling now prioritizes Apply, while explicitly blocking panel-detach affirmative button.
- ��û ��� (KO): �ڵ� �˾� ó������ Apply�� �켱 �����ϰ�, �гκи� Ȯ�� ��ư�� ��������� ����.

### Changed Files
- `fa50_0.5.29.py`
- `fa50_0.5.29_validation_report.txt`
- `CHANGELOG_FA50.md`

### Verification
- See `fa50_0.5.29_validation_report.txt` (3/3 PASS)

---

## v0.5.30
- Date/Time (KST): 2026-03-02 17:30
- Request Summary (EN): DCA setup progression fixed by auto-clicking Apply in QDialog-based setup dialogs.
- ��û ��� (KO): DCA setup�� ���� �ܰ�� ����ǵ��� QDialog ��� setup���� Apply �ڵ� Ŭ�� ó��.

### Changed Files
- `fa50_0.5.30.py`
- `fa50_0.5.30_validation_report.txt`
- `CHANGELOG_FA50.md`

### Verification
- See `fa50_0.5.30_validation_report.txt` (3/3 PASS, runtime auto-probe included)


---

## v0.5.31
- Date/Time (KST): 2026-03-02 17:30
- Request Summary (EN): Repositioned auto-probe capture camera so #1/#2/#3/#4 arrows are all visible in generated PNG.
- ��û ��� (KO): �ڵ� ���� PNG���� #1/#2/#3/#4 ȭ��ǥ�� ��� ���̵��� ī�޶� ��ġ/�Ÿ� �����̹� ����.

### Changed Files
- `fa50_0.5.31.py`
- `fa50_0.5.31_validation_report.txt`
- `CHANGELOG_FA50.md`

### Verification
- See `fa50_0.5.31_validation_report.txt` (3/3 PASS)


---

## v0.5.32
- Date/Time (KST): 2026-03-02 17:33
- Request Summary (EN): Increased Z-layer separation between overview trails and arrows to reduce apparent shaft skipping.
- ��û ��� (KO): overview ��μ��� ȭ��ǥ�� Z �и��� ũ�� �÷� shaft ����ó�� ���̴� ���� ��ȭ.

### Changed Files
- `fa50_0.5.32.py`

---

## v0.5.33
- Date/Time (KST): 2026-03-02 17:34
- Request Summary (EN): Changed overview/play shaft rendering to true step-segment (p0->p1) basis to align #4 with #1/#2/#3 continuity.
- ��û ��� (KO): overview/play shaft�� ���� step ����(p0->p1) ������� �ٲ� #4�� #1/#2/#3�� ���� ���Ӽ����� ���̵��� ����.

### Changed Files
- `fa50_0.5.33.py`
- `fa50_0.5.33_validation_report.txt`
- `CHANGELOG_FA50.md`

### Verification
- See `fa50_0.5.33_validation_report.txt` (3/3 PASS)


---

## v0.5.34
- Date/Time (KST): 2026-03-02 17:42
- Request Summary (EN): Removed all popup auto-close hooks and restored fully manual popup handling.
- 요청 요약 (KO): 자동 팝업 닫기 훅을 모두 제거하고 수동 팝업 처리로 복귀.

### Changed Files
- `fa50_0.5.34.py`
- `fa50_0.5.34_validation_report.txt`
- `CHANGELOG_FA50.md`

### Debug Note (EN)
- For future debugging reuse, the removed popup auto-close hook implementation can be referenced from `fa50_0.5.30.py` to `fa50_0.5.33.py`.

### 디버그 참고 (KO)
- 추후 디버깅 시 재사용할 자동 팝업 훅 코드는 `fa50_0.5.30.py` ~ `fa50_0.5.33.py`에 남아있음.

### Verification
- See `fa50_0.5.34_validation_report.txt` (3/3 PASS)

---

## v0.5.35
- Date/Time (KST): 2026-03-02 17:49
- Request Summary (EN): Open DCA setup dialog in full-window mode when launched.
- 요청 요약 (KO): DCA setup 다이얼로그를 띄울 때 전체 창(최대화) 모드로 열리게 변경.

### Changed Files
- 
a50_0.5.35.py
- 
a50_0.5.35_validation_report.txt
- CHANGELOG_FA50.md

### Verification
- See 
a50_0.5.35_validation_report.txt (3/3 PASS)


---

---

---

## v0.5.36
- Date/Time (KST): 2026-03-02 17:58
- Request Summary (EN): Enabled direct mouse drag for HMRL/INNER DEZ/OUTER DEZ/COMMIT and corner-based mission area resize in DCA setup preview, with real-time left-panel sync and nm hints.
- 요청 요약 (KO): DCA setup 미리보기에서 HMRL/INNER DEZ/OUTER DEZ/COMMIT 라인을 마우스로 옮기고 mission area를 코너 핸들로 조절할 수 있게 했으며, 좌측 패널 동기화와 nm 실시간 힌트를 추가.

### Changed Files
- fa50_0.5.36.py
- fa50_0.5.36_validation_report.txt
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Added preview drag state/caches for line hit-test and mission corner hit-test in `DcaSetupDialog`.
2. Extended `eventFilter` to prioritize drag modes in order: mission corner -> tactical lines -> aircraft points.
3. Added draggable tactical lines (`hmrl`, `ldez`, `hdez`, `commit`) with direct spinbox updates and B.E distance hint text.
4. Added mission corner handles and corner drag logic to update mission width/height in real time.
5. Added drag hint overlay near cursor to show current adjustment values in nm.

### 코드/로직 변경 (KO)
1. `DcaSetupDialog`에 라인/코너 히트테스트용 프리뷰 드래그 상태와 캐시를 추가.
2. `eventFilter`를 코너 -> 전술선 -> 항공기 순으로 드래그 우선 처리하도록 확장.
3. `hmrl`, `ldez`, `hdez`, `commit` 라인 드래그 시 스핀박스 실시간 반영 및 B.E 거리 힌트 표시 추가.
4. mission area 코너 핸들과 코너 드래그 로직을 추가해 width/height를 실시간 변경.
5. 커서 주변에 현재 조절값(nm)을 보여주는 힌트 오버레이 추가.

### Verification
- See `fa50_0.5.36_validation_report.txt` (3/3 PASS)

---

## v0.5.37
- Date/Time (KST): 2026-03-02 18:08
- Request Summary (EN): Removed zoom-out feeling during mission-area resizing, stabilized lower-corner resize behavior, and added BA #1 heading cone overlay (+-60deg, 40nm, light sky-blue transparent).
- ?? ?? (KO): mission area ???? ? ?? ?? ???? ?? ???? ?? ?? ?? ? height ???? ????? BA #1 ???? ?? ? ????? ??.

### Changed Files
- fa50_0.5.37.py
- fa50_0.5.37_validation_report.txt
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Added preview view-lock state (`_preview_view_lock`) and fixed map scale/center across drag updates (except window size changes) to prevent auto zoom-out while mission area is resized.
2. Reworked mission-corner drag using per-drag start context (`_preview_corner_drag_ctx`) so width/height updates are incremental and stable.
3. Tuned corner behavior for this mission-anchor model:
   - front corners: width + height
   - rear corners: width only (prevents sudden height collapse when grabbing lower corners)
4. Added BA #1 forward cone in DCA preview:
   - center: BA #1 position (fallback: BA lead)
   - span: heading +-60deg
   - radius: 40nm
   - style: light sky-blue with 70% transparency (`QColor(135, 206, 250, 77)`).

### ??/?? ?? (KO)
1. `_preview_view_lock`? ??? ???? ??? ? ???/??? ??(? ?? ?? ?? ???)?? ?? ??? ???? ??.
2. `_preview_corner_drag_ctx` ?? ?? ???? ?? ??? ? width/height ??? ???.
3. ?? mission anchor ??? ?? ?? ??? ??:
   - ?? ??: width + height ?? ??
   - ?? ??: width ?? ??(?? ??? ??)
4. BA #1 ?? ? ???? ??:
   - ??: BA #1 ??(??? BA ??)
   - ??: ???? ?60?
   - ??: 40nm
   - ???: ?? ???, ??? 70%.

### Verification
- See `fa50_0.5.37_validation_report.txt` (3/3 PASS)

---

## v0.5.38
- Date/Time (KST): 2026-03-02 18:12
- Request Summary (EN): Added draggable C.F/C.R/B.E points in DCA preview and improved mission-area view behavior to avoid clipping while preserving a fixed-zoom feel.
- 요청 요약 (KO): DCA 미리보기에서 C.F/C.R/B.E를 마우스로 움직일 수 있게 하고, mission area는 일반적으로 고정 뷰 감각을 유지하되 잘림(클리핑) 발생 시에만 최소 줌아웃으로 보정.

### Changed Files
- fa50_0.5.38.py
- fa50_0.5.38_validation_report.txt
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Added new preview point hit-test cache (`_preview_point_screen`) and point drag flow in `eventFilter`.
2. Implemented `_apply_drag_preview_point_nm()`:
   - `cf` / `cr` drag updates CAP front/rear distances with order-safe clamping.
   - `be` drag recalculates `asset_bearing_deg` and `asset_range_nm` from dragged B.E position.
3. Updated preview drawing to register draggable screenspace anchors for `C.F`, `C.R`, and `B.E`.
4. Refined view-lock behavior:
   - Keep locked zoom for stable resize feel.
   - Recenter Y when possible without zoom change.
   - If geometry exceeds current viewport capacity, apply only minimal zoom-out to fitted scale.

### 코드/로직 변경 (KO)
1. `DcaSetupDialog` 미리보기에 `point` 드래그 모드를 추가해 `C.F`, `C.R`, `B.E` 포인트 히트테스트/드래그를 처리.
2. `C.F/C.R` 드래그는 `cap_front_nm`, `cap_rear_nm`에 실시간 연동되며 앞/뒤 관계역전을 방지하도록 보정.
3. `B.E` 드래그는 `asset_bearing_deg`, `asset_range_nm`을 재계산하여 좌측 컨트롤에 실시간 반영(필요 시 `same as B.E` 해제).
4. mission area 뷰 보정은 고정 줌 감각을 유지하고, 클리핑 없이 표시 가능할 땐 Y 중심만 재조정, 정말 필요할 때만 fit scale까지 최소 줌아웃.

### Verification
- See `fa50_0.5.38_validation_report.txt` (3/3 PASS)

---

## v0.5.39
- Date/Time (KST): 2026-03-02 18:22
- Request Summary (EN): Decoupled CAP FRONT and BA #1 movement after initial default alignment, constrained B.E drag to vertical-only, and added mouse-wheel zoom in DCA preview.
- 요청 요약 (KO): CAP FRONT와 BA #1 연동을 풀고, B.E를 전장 중심 기준 수직으로만 움직이게 하며, 전장 미리보기에 휠 줌인/줌아웃을 추가.

### Changed Files
- fa50_0.5.39.py
- fa50_0.5.39_validation_report.txt
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Removed BA auto-follow from `_sync_ba_ra_defaults_from_mission_and_cap()` so BA distance no longer tracks CAP FRONT after initial setup.
2. Changed preview mouse hit priority to `corner -> line -> aircraft -> point`, preventing C.F from stealing BA #1 drag when overlapped.
3. Updated B.E point drag to vertical-only by fixing current B.E X and applying cursor Y only.
4. Added wheel zoom handler (`QEvent.Type.Wheel`) and cursor-anchored preview zoom transform.

### 코드/로직 변경 (KO)
1. `DcaSetupDialog._sync_ba_ra_defaults_from_mission_and_cap()`에서 BA 자동 동기화를 제거해, BA는 초기값 이후 CAP FRONT에 끌려가지 않도록 수정.
2. 미리보기 클릭 우선순위를 `aircraft` > `point`로 바꿔, #1과 C.F가 겹칠 때 #1 이동이 우선되도록 수정.
3. `B.E` 드래그는 X 좌표를 고정하고 Y만 변경하는 수직 이동 제약으로 수정.
4. `QEvent.Type.Wheel` 처리와 `_apply_preview_wheel_zoom()`을 추가해 커서 기준 줌인/줌아웃 가능하도록 수정.

### Verification
- See `fa50_0.5.39_validation_report.txt` (3/3 PASS)

---

## v0.5.40
- Date/Time (KST): 2026-03-02 18:29
- Request Summary (EN): Improved readability of the CAP FRONT to CAP REAR separation in DCA preview.
- 요청 요약 (KO): 미리보기에서 CAP REAR와 CAP FRONT 사이의 거리를 보기 쉽게 표시.

### Changed Files
- fa50_0.5.40.py
- fa50_0.5.40_validation_report.txt
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Added a dashed connector line between C.F and C.R in DCA preview.
2. Added a centered distance label (`C.F-C.R: x.x nm`) with a white rounded background for high visibility.

### 코드/로직 변경 (KO)
1. `C.F`와 `C.R` 포인트 사이에 점선 연결선을 추가해 거리 직관성을 개선.
2. 중앙 인근에 `C.F-C.R: x.x nm` 라벨을 흰색 배경(라운드 박스)으로 표시하여 가독성을 높임.

### Verification
- See `fa50_0.5.40_validation_report.txt` (3/3 PASS)

---

## v0.5.42
- Date/Time (KST): 2026-03-02 18:32
- Request Summary (EN): Reduced verbosity of preview helper labels and pinned the main guide overlay to top.
- ?? ?? (KO): ???? ?? ??? ?? ??? ?? ?? ????? ??? ??.

### Changed Files
- fa50_0.5.42.py
- fa50_0.5.42_validation_report.txt
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Changed individual-drag prompt text from long sentence to compact labels.
2. Main guide text was already shortened and now top-fixed (`gy = 12`) instead of center placement.

### ??/?? ?? (KO)
1. ?? ??? ?? ??? ?? ?? ??? ??.
2. ?? ?? ?? ??? ?? ??(`gy = 12`)?? ??.

### Verification
- See `fa50_0.5.42_validation_report.txt` (3/3 PASS)

---

## v0.5.43
- Date/Time (KST): 2026-03-02 18:38
- Request Summary (EN): Added mode-based BA nose-cone rendering (#2 for 2vs2, #3 for 4vs2) and implemented CAP dual-point creation with mirrored left/right slide control.
- ?? ?? (KO): 2vs2??? #2, 4vs2??? #3?? BA ?? ????, CAP ??? 2?? ??? ?? ?? ????? ????? ??.

### Changed Files
- fa50_0.5.43.py
- fa50_0.5.43_validation_report.txt
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. BA cone drawing generalized with per-mode IDs:
   - always `#1`
   - add `#2` when BA count is 2
   - add `#3` when BA count is 4+
2. Added `CAP 2-point` toggle in DCA setup CAP section.
3. When CAP 2-point is enabled:
   - CAP pair is initialized at left/right outer lanes (0.375 * mission width from center).
   - pair keeps the same CAP FRONT distance and only slides laterally.
   - dragging either CAP point updates one symmetric half-separation and mirrors the opposite side.

### ??/?? ?? (KO)
1. BA ? ??? ?? ???? ??:
   - ?? `#1`
   - BA 2? ??? `#2` ??
   - BA 4? ???? `#3` ??
2. CAP ??? `CAP 2-point` ?? ??.
3. CAP 2-point ?? ?:
   - ?? ?? ??(???? mission width? 0.375)?? ?? ??
   - CAP FRONT ??(??)? ???? ?? ????? ??
   - ??? ????? ???? ?? ??? ?? ??

### Verification
- See `fa50_0.5.43_validation_report.txt` (3/3 PASS)

---

## v0.5.44
- Date/Time (KST): 2026-03-02 18:42
- Request Summary (EN): Enabled DCA preview panning via right-click drag and arrow keys, moved CAP add control to preview bottom-right, and kept CAP pair as symmetric C.F-like points initialized at quarter lanes.
- ?? ?? (KO): DCA ?????? ??? ???/???? ???? ??? ????? ??, CAP ??? ???? ?????? ????? CAP ??? ?? C.F? ?? ??? ?? ??? 1/4 ??? ??.

### Changed Files
- fa50_0.5.44.py
- fa50_0.5.44_validation_report.txt
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Added preview pan interactions:
   - right mouse drag pan (`_preview_pan_active`, `_preview_pan_last_px`)
   - arrow-key pan in event filter (`Left/Right/Up/Down`)
2. Added `_pan_preview_by_pixels()` to update preview center while preserving current zoom lock.
3. Moved CAP-add control from CAP form to preview bottom-right as a checkable button (`btn_cap_front_pair`).
4. CAP pair rendering remains same point style as C.F, initialized to quarter-lane placement and mirrored by equal slide distance.

### ??/?? ?? (KO)
1. ???? ? ?? ??:
   - ??? ??? ?
   - ???(`?/?/?/?`) ?
2. `_pan_preview_by_pixels()`? ?? ?? ??? ? ???? ??.
3. CAP ?? UI? CAP ????? ???? ???? ??? ???? ??.
4. CAP ?? ?? C.F? ??? ??? ??? ????, 1/4 ?? ?? ?? + ?? ?? ???? ??.

### Verification
- See `fa50_0.5.44_validation_report.txt` (3/3 PASS)

---

## v0.5.45
- Date/Time (KST): 2026-03-02 18:46
- Request Summary (EN): Changed CAP add behavior so the existing center CAP pair (C.F/C.R) is duplicated and split to left/right pairs instead of only adding front points.
- ?? ?? (KO): CAP ?? ? ??? C.F/C.R ??? ??? ??? ??/????? ??.

### Changed Files
- fa50_0.5.45.py
- fa50_0.5.45_validation_report.txt
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Added rear CAP pair geometry (`cap_r_pair`) in addition to front pair (`cap_f_pair`).
2. In CAP-pair mode, preview now renders four CAP points:
   - left C.F + left C.R
   - right C.F + right C.R
3. Dashed C.F-C.R distance connector now draws per side (left and right), matching duplicated CAP lanes.
4. Expanded CAP drag keys to include all four pair points (`cap_lf/cap_rf/cap_lr/cap_rr`) while preserving mirrored slide behavior.

### ??/?? ?? (KO)
1. CAP ? ?????? ?? ?(`cap_r_pair`)? ??.
2. CAP ? ???? ????? 4? CAP ???(?/? C.F, ?/? C.R)? ????? ??.
3. C.F-C.R ?? ??? ??/?? ?? ????? ??.
4. CAP ??? ?? 4???(`cap_lf/cap_rf/cap_lr/cap_rr`)? ???? ?? ???? ??? ??.

### Verification
- See `fa50_0.5.45_validation_report.txt` (3/3 PASS)

---

## v0.5.46
- Date/Time (KST): 2026-03-02 18:50
- Request Summary (EN): Changed CAP-pair initial spawn to left/right one-third points and linked BA side groups to CAP side movement.
- ?? ?? (KO): CAP ? ?? ?? ??? ?/? 1/3? ??? BA ??? ?/? CAP ?? ??? ????? ??.

### Changed Files
- fa50_0.5.46.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. CAP pair initial half-separation changed from `0.375 * mission_width` to `(1/3) * mission_width`.
2. In CAP-pair mode, BA points now receive CAP-side lateral deltas:
   - `#1`, `#2` follow left CAP lateral offset
   - `#3`, `#4` follow right CAP lateral offset
3. This linkage is applied in preview geometry generation, so drag/preview updates reflect immediately.

### ??/?? ?? (KO)
1. CAP ? ?? ?? ??? `0.375 * mission_width`?? `(1/3) * mission_width`? ??.
2. CAP ? ???? BA ???? CAP ?? ???? ??:
   - `#1`, `#2`? ?? CAP ??? ??
   - `#3`, `#4`? ?? CAP ??? ??
3. ???? ????? ???? ?? ????? ??.

### Verification
- `python -m py_compile fa50_0.5.46.py` PASS

---

## v0.5.47
- Date/Time (KST): 2026-03-02 18:57
- Request Summary (EN): Adjusted CAP pair spawn to quarter points, aligned #3 with right CAP FRONT, and enabled lateral slide by dragging each CAP-side C.F-C.R connector line.
- ?? ?? (KO): CAP ? ?? ??? 1/4 ???? ??? ?? CAP FRONT? #3? ??????, ?/? C.F-C.R ??? ???? ???? ???? ??.

### Changed Files
- fa50_0.5.47.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. CAP pair initialization changed to `0.25 * mission_width` half-separation.
2. BA side-follow anchor updated:
   - left group anchored by `#1` to left CAP FRONT
   - right group anchored by `#3` to right CAP FRONT
3. Added CAP side connector line hit targets (`cap_left`, `cap_right`) and mapped them to CAP lateral slide drag logic.

### ??/?? ?? (KO)
1. CAP ? ?? ???? `0.25 * mission_width`? ??.
2. BA ?? ??? ??:
   - ??? `#1` ???? ? CAP FRONT ??
   - ??? `#3` ???? ? CAP FRONT ??
3. CAP ?/? C.F-C.R ???(`cap_left`, `cap_right`)? ??? ???? ??? ?? ??? ?? ???? ??.

### Verification
- `python -m py_compile fa50_0.5.47.py` PASS

---

## v0.5.48
- Date/Time (KST): 2026-03-02 19:05
- Request Summary (EN): Implemented split-squad drag control rules for CAP-split state, added clickable squad 180? heading flip control, and changed preview aircraft symbols from dots to heading arrows.
- ?? ?? (KO): CAP ?? ???? ??? ??? ?? ??? ????, ?? ?? ? 180? ?? ??? ????, ???? ??? ??? ??? ?? ???? ??.

### Changed Files
- fa50_0.5.48.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. CAP-split BA drag control rules in preview:
   - 2-ship BA (`2vs2`): `#1` and `#2` move independently.
   - 4-ship BA (`4vs2`, `4vs4`): `#1/#2` move together, `#3/#4` move together.
2. Added squad selection + flip button (`?? 180?`):
   - Click BA aircraft in CAP-split mode to select squad.
   - Click button to rotate selected squad heading by +180?.
3. Heading override persistence path added:
   - Dialog returns `ba_heading_override_deg`.
   - `_apply_dca_ba_ra_layout_via_be()` now accepts `ba_heading_overrides` and applies per-aircraft BA heading.
4. Replaced preview aircraft dot markers with arrow symbols showing nose direction (BA/RA).
5. CAP side connector drag support (`cap_left`, `cap_right`) remains linked to mirrored CAP lateral slide.

### ??/?? ?? (KO)
1. CAP ?? ? BA ??? ?? ??:
   - BA 2?(`2vs2`): `#1`, `#2` ?? ??
   - BA 4?(`4vs2`, `4vs4`): `#1/#2` ??, `#3/#4` ?? ??
2. ?? ?? + 180? ?? ??(`?? 180?`) ??:
   - CAP ?? ???? BA? ???? ?? ??
   - ?? ?? ? ?? ?? ??? 180? ??
3. ??? ???? ?? ?? ??? ????? ??:
   - Dialog selection? `ba_heading_override_deg` ??
   - `_apply_dca_ba_ra_layout_via_be()`?? per-aircraft BA heading ??
4. ???? ??? ??? ??? ???? ??? ?? ?? ???.
5. CAP ?/? ??? ???(`cap_left`, `cap_right`)? ?? ????? ?? ??.

### Verification
- `python -m py_compile fa50_0.5.48.py` PASS

---

## v0.5.49
- Date/Time (KST): 2026-03-02 19:13
- Request Summary (EN): Made #1/#2 and #3/#4 drag together when either member is grabbed, and ensured aircraft are picked before CAP elements.
- ?? ?? (KO): #1/#2, #3/#4? ? ? ??? ??? ?? ???? ??, CAP ???? ???? ?? ???? ????? ??.

### Changed Files
- fa50_0.5.49.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. In CAP-split BA drag logic, 2-ship case changed to paired movement (`#1` + `#2`) instead of individual.
2. 4-ship paired movement remains (`#1/#2` group, `#3/#4` group).
3. Squad selection helper now returns paired squad for 2-ship CAP-split state.
4. Preview mouse pick order adjusted to prioritize aircraft before line/point CAP picks.

### Verification
- `python -m py_compile fa50_0.5.49.py` PASS

---

## v0.5.50
- Date/Time (KST): 2026-03-02 19:15
- Request Summary (EN): Changed squad heading control to an in-preview rotate icon that appears next to clicked squad, and fixed CAP-split squad movement consistency.
- ?? ?? (KO): ?? ?? ? ?? ?? ???? ?? ???? ????, CAP ?? ???? ?? ??? ????? ????? ??.

### Changed Files
- fa50_0.5.50.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Removed top-row textual squad-rotate UI usage and switched to in-preview overlay button (`?`) attached near selected squad centroid.
2. Clicking BA squad in CAP-split mode now selects squad and shows rotate icon near that squad.
3. Rotate icon click applies heading rotation to selected squad (+180deg per click) via per-aircraft BA heading override map.
4. CAP-split BA movement was hardened: BA drags use squad-group logic even when individual-drag checkbox is enabled, preventing inconsistent behavior.

### Verification
- `python -m py_compile fa50_0.5.50.py` PASS

---

## v0.5.51
- Date/Time (KST): 2026-03-02 19:12
- Request Summary (EN): When CAP split is enabled, automatically set BA squads other than #1 squad to heading 180deg.
- ?? ?? (KO): CAP ?? ?? ? #1 ??? ??? BA ??? ???? 180? ??? ????? ??.

### Changed Files
- fa50_0.5.51.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Added `_apply_cap_pair_default_headings()` in `DcaSetupDialog`.
2. On CAP split enable, after alignment, applies heading override of `180.0` to non-#1 BA squad (`#3/#4` when present).
3. Existing manual squad rotate icon behavior remains available after auto default is applied.

### Verification
- `python -m py_compile fa50_0.5.51.py` PASS

---

## v0.5.52
- Date/Time (KST): 2026-03-02 19:20
- Request Summary (EN): Updated CAP-split squad placement/heading rules so non-#1 squads are positioned on CAP REAR in 2vs2/4vs2/4vs4, and 2vs2 maps #1 to left CAP and #2 to right CAP.
- ?? ?? (KO): CAP ?? ? 2vs2/4vs2/4vs4?? #1 ?? ?? CAP REAR? ???? 2vs2? #1 ?? CAP, #2 ?? CAP? ????? ??.

### Changed Files
- fa50_0.5.52.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. 2vs2 CAP-split squad model changed to independent squads:
   - `#1` follows left CAP lane (front)
   - `#2` follows right CAP lane (rear)
2. Non-#1 squad default heading at CAP-split:
   - 2vs2: `#2 -> 180deg`
   - 4vs2/4vs4: `#3/#4 -> 180deg`
3. CAP alignment logic updated to anchor non-#1 squad to CAP REAR lane.
4. 2vs2 CAP-split drag behavior updated to independent control per squad (`#1`, `#2`).

### Verification
- `python -m py_compile fa50_0.5.52.py` PASS
- Offscreen probe PASS:
  - 2vs2: `#1 == left CAP FRONT`, `#2 == right CAP REAR`, `#2 heading == 180`, and `#1 drag` keeps `#2` independent.
  - 4vs2: `#3 == right CAP REAR`, `#3/#4 heading == 180`.

---

## v0.5.53
- Date/Time (KST): 2026-03-02 21:54
- Request Summary (EN): Ensured DCA setup preview state is carried into actual start state, including CAP-split config and BA per-aircraft heading overrides; audited mission/dez propagation and fixed missing runtime reflections.
- ?? ?? (KO): DCA setup ?????? ?? ??? ?? ?? ??? ????? CAP ??/BA ?? ??? ??? ?? ??? ???? mission/dez ?? ?? ??? ??/??.

### Changed Files
- fa50_0.5.53.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. DCA dialog state propagation expanded:
   - `cap_pair_enabled`, `cap_pair_half_sep_nm` are now part of dialog init/selection roundtrip.
   - Existing `ba_heading_overrides` propagation kept and verified.
2. Runtime defaults/state fields added:
   - `dca_cap_pair_enabled_default`, `dca_cap_pair_half_sep_nm_default`
   - `dca_cap_front_split_centers_ft`, `dca_cap_rear_split_centers_ft`
3. `_set_dca_operational_lines()` extended to compute/store CAP split centers in runtime when CAP split is enabled.
4. Output-view rendering updated:
   - Added `dca_cap_split_dots` GL item and render path.
   - When CAP split is enabled, split CAP dots are rendered instead of only center CAP dots.
5. Prompt/apply/load/save paths updated so CAP split config persists through:
   - DCA setup dialog open defaults
   - apply-to-runtime
   - metadata load (`dca_cap_pair_enabled`, `dca_cap_pair_half_sep_nm`)
   - metadata save rows
6. `_apply_dca_ba_ra_layout_via_be()` BA heading assignment fixed to respect per-aircraft override values (no overwrite by global BA heading).

### Verification
- `python -m py_compile fa50_0.5.53.py` PASS
- Offscreen runtime probe PASS:
  - dialog selection contains CAP split state + BA heading override
  - runtime stores/uses CAP split flags and split CAP points
  - BA heading overrides (`#3/#4=180`) applied to controls in actual layout call
  - mission/dez defaults (`width/ldez/hdez`) reflect applied values

---

## v0.5.54
- Date/Time (KST): 2026-03-02 22:02
- Request Summary (EN): In DCA setup, generate grid only within mission area.
- ?? ?? (KO): DCA setup?? grid ??? mission area ???? ????? ??.

### Changed Files
- fa50_0.5.54.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Updated `_build_or_update_dashed_grids()` branch logic.
2. When DCA mission area exists (`_has_dca_mission_area()`):
   - `XY` grid uses `_build_mission_xy_grid_points()`
   - `XZ/YZ` grids use `_build_mission_vertical_grid_points()` (mission-footprint vertical columns only)
3. Fallback to existing full-plane grid generation remains unchanged when no DCA mission area is defined.

### Verification
- `python -m py_compile fa50_0.5.54.py` PASS
- Offscreen probe PASS:
  - mission-present: mission-only XY/vertical grid point builders return non-empty
  - mission-cleared: fallback full-plane grid builder returns non-empty

---

## v0.5.55
- Date/Time (KST): 2026-03-02 22:08
- Request Summary (EN): Revert vertical grid behavior to v0.5.53 style and keep only XY grid constrained to mission area.
- ?? ?? (KO): ??? ??? 0.5.53 ???? ???? XY? mission area ?? ?? ??.

### Changed Files
- fa50_0.5.55.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. In `_build_or_update_dashed_grids()`, when DCA mission exists:
   - `XY`: mission-area grid (`_build_mission_xy_grid_points`) ??
   - `XZ/YZ`: legacy full-plane axis-aligned grid (`_build_plane_solid_points`) ??

### Verification
- `python -m py_compile fa50_0.5.55.py` PASS

---

## v0.5.57
- Date/Time (KST): 2026-03-02 22:12
- Request Summary (EN): In DCA setup, restrict grid rendering to mission area only.
- ?? ?? (KO): DCA setup? ? grid? mission area ???? ???? ??.

### Changed Files
- fa50_0.5.57.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. `_build_or_update_dashed_grids()` updated:
   - DCA mission active: `XY -> _build_mission_xy_grid_points()`, `YZ -> _build_mission_vertical_grid_points()`
   - Non-DCA: fallback full-plane behavior unchanged
2. Prior removal of X-axis vertical grid (`XZ`) is kept.

### Verification
- `python -m py_compile fa50_0.5.57.py` PASS

---

## v0.5.58
- Date/Time (KST): 2026-03-02 22:07
- Request Summary (EN): Keep grid constrained to mission area and make Plan View work only as Y-axis left/right views.
- 요청 요약 (KO): 그리드를 mission area 내부로 제한하고, Plan View를 Y축 좌/우 시점 2개만 동작하도록 수정.

### Changed Files
- fa50_0.5.58.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Updated plan-view camera axis mapping:
   - `_apply_plan_view_camera()`: azimuth now toggles only `90` and `270` (removed `180` path).
2. Updated plan-view detection:
   - `_detect_camera_view_kind()`: plan recognized only near `90`/`270` azimuth at low elevation.
3. Updated plan-view mode sync:
   - `_update_view_mode_from_camera()`: `plan_view_axis_idx` now resolves against `90` vs `270`.
4. Updated grid visibility in plan mode:
   - `_apply_grid_visibility_for_view()`: Plan mode now shows only `YZ` grid and hides `XY/XZ`.
5. Mission-area-constrained grid generation/extent logic from prior step remains in effect in `fa50_0.5.58.py`.

### Verification
- `python -m py_compile fa50_0.5.58.py` PASS

---

## v0.5.59
- Date/Time (KST): 2026-03-02 22:11
- Request Summary (EN): Switch plan view from YZ-oriented side views to XZ-only two-way views, and keep vertical grid on Y-axis plane only.
- 요청 요약 (KO): Plan view를 YZ 기준에서 XZ 기준 2방향으로 바꾸고, 수직 그리드는 Y축 평면만 보이도록 조정.

### Changed Files
- fa50_0.5.59.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. `_apply_plan_view_camera()` changed to use only `azimuth 0/180` (XZ projection pair).
2. `_detect_camera_view_kind()` and `_update_view_mode_from_camera()` updated to detect/track plan mode against `0/180`.
3. `_build_or_update_dashed_grids()` now builds `XZ` grid item as well (`["XY","XZ","YZ"]`).
4. `_apply_grid_visibility_for_view()` changed:
   - `plan`: show only `XZ`, hide `XY/YZ`
   - `free`: show `XY + YZ`, hide `XZ` (Y-axis vertical grid only)
   - `top`: unchanged (`XY` only)

### Verification
- `python -m py_compile fa50_0.5.59.py` PASS

---

## v0.5.60
- Date/Time (KST): 2026-03-02 22:13
- Request Summary (EN): Remove all XZ grids, keep only YZ on x=0 axis, and use YZ-only plan views.
- 요청 요약 (KO): XZ 그리드를 전부 제거하고 x=0축의 YZ만 유지, plan view도 YZ만 사용.

### Changed Files
- fa50_0.5.60.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. `_build_or_update_dashed_grids()` changed grid build set from `["XY","XZ","YZ"]` to `["XY","YZ"]`.
2. In DCA mission path, vertical grid now uses `_build_plane_solid_points("YZ", ...)` only (x=0 plane), not mission-column verticals.
3. Plan view axis handling restored to YZ-side pair:
   - `_detect_camera_view_kind()` and `_update_view_mode_from_camera()` now use `90/270`.
   - `_apply_plan_view_camera()` now uses `azimuth 90/270`.
4. Grid visibility in plan mode changed to YZ-only (`XY/XZ` hidden).

### Verification
- `python -m py_compile fa50_0.5.60.py` PASS

---

## v0.5.61
- Date/Time (KST): 2026-03-02 22:15
- Request Summary (EN): Use XZ-only two-way plan views and improve YZ-vs-XY grid visual alignment.
- 요청 요약 (KO): Plan view를 XZ 2방향으로 두고, YZ와 XY 그리드 교차가 더 예쁘게 맞도록 정렬.

### Changed Files
- fa50_0.5.61.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Plan view camera/detection reverted to XZ pair:
   - `_detect_camera_view_kind()` uses azimuth `0/180`.
   - `_update_view_mode_from_camera()` resolves plan index by `0` vs `180`.
   - `_apply_plan_view_camera()` applies `azimuth 0/180`.
2. Plan grid visibility updated:
   - `plan`: show `XZ` only, hide `XY/YZ`.
3. Reintroduced `XZ` grid item generation in `_build_or_update_dashed_grids()` (`["XY","XZ","YZ"]`).
4. Added `_preferred_yz_plane_x_ft(extent, spacing)` and changed YZ builder:
   - YZ plane x-position is snapped to current XY spacing lattice (mission center-based when available), so vertical/horizontal checkerboard intersections align cleanly.

### Verification
- `python -m py_compile fa50_0.5.61.py` PASS

---

## v0.5.62
- Date/Time (KST): 2026-03-02 22:17
- Request Summary (EN): Show YZ instead of XZ in Plan View.
- 요청 요약 (KO): Plan View에서 XZ 대신 YZ를 보이도록 수정.

### Changed Files
- fa50_0.5.62.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. `_apply_grid_visibility_for_view()` updated for `view_kind == "plan"`:
   - `XZ -> hidden`
   - `YZ -> visible`
   - `XY -> hidden` (unchanged)

### Verification
- `python -m py_compile fa50_0.5.62.py` PASS

---

## v0.5.63
- Date/Time (KST): 2026-03-02 22:21
- Request Summary (EN): On launch, show 3D view as Top View + North-up + clean whole-battlefield framing.
- 요청 요약 (KO): 실행 시 3D 화면을 Top View + 북쪽 12시 + 전장 전체 프레이밍으로 시작.

### Changed Files
- fa50_0.5.63.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Added `_apply_top_north_startup_frame()`:
   - Collects active aircraft positions (and mission-area corners if present).
   - Computes center/span and auto camera distance with margin.
   - Applies top-view camera and calls `_set_top_view_cardinal("N")` for strict north-up orientation.
2. Hooked startup framing into:
   - `reset_sim()` end (initial launch reset path)
   - `apply_startup_profile()` end (after startup scenario selection/apply)

### Verification
- `python -m py_compile fa50_0.5.63.py` PASS

---

## v0.5.64
- Date/Time (KST): 2026-03-02 22:23
- Request Summary (EN): In DCA startup, fit mission-area vertical bounds to viewport top/bottom.
- 요청 요약 (KO): DCA 시작 시 mission area 상/하단이 화면 상/하단에 맞게 보이도록 조정.

### Changed Files
- fa50_0.5.64.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Updated `_apply_top_north_startup_frame()`:
   - Detects mission area points when DCA mission is active.
   - Uses mission-area Y span (`maxY-minY`) and camera FOV to compute top-view distance so vertical fit approaches edge-to-edge.
   - Keeps North-up (`_set_top_view_cardinal("N")`) and mission center alignment.
2. Non-DCA/default startup framing logic remains unchanged.

### Verification
- `python -m py_compile fa50_0.5.64.py` PASS

---

## v0.5.65
- Date/Time (KST): 2026-03-02 22:28
- Request Summary (EN): Use yellow mission width/height as DCA startup fit target; switch orientation/fit behavior by panel detached state.
- 요청 요약 (KO): DCA 시작 프레이밍을 노란 width/height 기준으로 하고, 패널 분리 여부에 따라 정렬/맞춤 방향을 분기.

### Changed Files
- fa50_0.5.65.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. `_apply_top_north_startup_frame()` updated mission fit source:
   - Uses yellow mission height line length (`rear_left -> front_left`) instead of full battlefield bounds.
2. DCA + panel not detached:
   - Keeps `N` at 12 o'clock (`_set_top_view_cardinal("N")`)
   - Fits mission height to screen top/bottom.
3. DCA + panel detached (`_left_ui_popped=True`):
   - Rotates top view so `N` is at 3 o'clock (`_set_top_view_cardinal("W")`)
   - Fits mission height to screen left/right using aspect-correct distance.
4. Added one-step zoom-out margin for both detached/non-detached DCA fits (`x 1/0.85`).

### Verification
- `python -m py_compile fa50_0.5.65.py` PASS

---

## v0.5.66
- Date/Time (KST): 2026-03-02 22:30
- Request Summary (EN): Reapply as strict rule: non-detached startup = Top/N + zoom-in x5, detach click = compass W behavior.
- 요청 요약 (KO): 규칙을 강제 단순화: 미분리 시작=Top/N+확대5회, 분리 클릭=W 나침반 효과.

### Changed Files
- fa50_0.5.66.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Rewrote `_apply_top_north_startup_frame()` to deterministic behavior:
   - Set Top View + `N` cardinal.
   - If panel is not detached (`_left_ui_popped=False`), apply `_adjust_view_zoom(0.85)` exactly 5 times.
   - Keeps prior center/distance auto-framing baseline before the fixed zoom sequence.
2. Updated `_toggle_left_ui_popout()`:
   - Right after panel detach is activated, immediately call Top View + `W` cardinal effect.

### Verification
- `python -m py_compile fa50_0.5.66.py` PASS

---

## v0.5.67
- Date/Time (KST): 2026-03-02 22:33
- Request Summary (EN): Change non-detached startup zoom to x3 and detached-click behavior to zoom-out x8.
- 요청 요약 (KO): 미분리 시작 확대를 3회로 줄이고, 분리 클릭 시 축소 8회를 적용.

### Changed Files
- fa50_0.5.67.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. `_apply_top_north_startup_frame()`:
   - non-detached startup zoom-in loop changed `5 -> 3`.
2. `_toggle_left_ui_popout()` detach branch:
   - after `Top + W` cardinal effect, added zoom-out loop `8` times via `_adjust_view_zoom(1.0 / 0.85)`.

### Verification
- `python -m py_compile fa50_0.5.67.py` PASS

---

## v0.5.68
- Date/Time (KST): 2026-03-02 22:35
- Request Summary (EN): Add 3 more zoom-out steps when panel is detached.
- 요청 요약 (KO): 패널 분리 시 축소를 3회 더 추가.

### Changed Files
- fa50_0.5.68.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. `_toggle_left_ui_popout()` detach branch:
   - zoom-out loop changed from `8` to `11`.

### Verification
- `python -m py_compile fa50_0.5.68.py` PASS

---

## v0.5.69
- Date/Time (KST): 2026-03-02 22:36
- Request Summary (EN): Add 2 more zoom-out steps on panel detach.
- 요청 요약 (KO): 패널 분리 시 축소를 2회 더 추가.

### Changed Files
- fa50_0.5.69.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. `_toggle_left_ui_popout()` detach branch:
   - zoom-out loop changed from `11` to `13`.

### Verification
- `python -m py_compile fa50_0.5.69.py` PASS

---

## v0.5.71
- Date/Time (KST): 2026-03-02 22:46
- Request Summary (EN): Remove level-state 4G cap and use PS-feasible G.
- 요청 요약 (KO): level 상태의 4G 제한을 제거하고 PS 가용 G를 사용.

### Changed Files
- fa50_0.5.71.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. `_simulate_one()`:
   - Removed level-specific command quantize cap (`max_g=4.0` -> `9.0`).
   - In `level_hold + turn S` and `level_hold + turn` branches, replaced fixed 4G clipping with:
     - target G up to 9G
     - final clamp by `_find_g_max(power, cas, alt, 9.0)` (PS-feasible G)
2. `_enforce_level_and_pull_logic()`:
   - Removed UI-side 4G cap in LEVEL assist.
   - Applies PS-based G cap (`_find_g_max`) using current CAS/ALT/POWER before bank scheduling.
3. Step-advance UI seed sync:
   - LEVEL `g_auto` reflection cap changed from 4G to 9G.

### Verification
- `python -m py_compile fa50_0.5.71.py` PASS

---

## v0.5.72
- Date/Time (KST): 2026-03-02 23:01
- Request Summary (EN): Dynamic max G in command input + Pull-Up pitch/bank auto conversion logic.
- 요청 요약 (KO): Command G 동적 최대치 적용 + Pull Up에서 pitch/bank 자동 변환 로직.

### Changed Files
- fa50_0.5.72.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Command G dynamic max:
   - Added `_compute_cmd_g_ps_max()` and `_update_cmd_g_dynamic_cap()`.
   - Command G spin max is now updated from current PS-feasible G (`CAS/ALT/POWER` state based, up to 9G).
   - Tooltips now show current max G and values above cap are auto-clamped.
2. Pitch input enabled in command UI:
   - `pitch_deg` is now editable (`readOnly=False`) and participates in command-change events.
   - `read_command()` now exports actual pitch input value.
3. Pull-Up pitch/bank bidirectional coupling:
   - Added user-intent tracking for pitch (`_pitch_user_set`) and auto-write guard.
   - If Pull-Up context and user edits pitch (without manual bank), bank is auto-calculated from G/pitch.
   - If user edits bank, pitch is auto-calculated from G/bank.
4. Level conflict handling:
   - In turn+G input intent (pitch or bank), Level is auto-cleared and Pull Up is auto-selected.

### Verification
- `python -m py_compile fa50_0.5.72.py` PASS

---

## v0.5.73
- Date/Time (KST): 2026-03-02 23:06
- Request Summary (EN): Add max-G checkbox behavior and fix pitch input usability.
- 요청 요약 (KO): max G 체크 기능 추가 및 pitch 입력 문제 수정.

### Changed Files
- fa50_0.5.73.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Added `G MAX` checkbox to each aircraft command panel:
   - When checked, `g_cmd` auto-follows current PS-feasible max G (up to 9G).
   - Stored in command payload as `g_use_max`.
2. Pitch input usability fix:
   - Root cause: auto preview (`_auto_apply_cmd_limits_for_aid`) always overwrote pitch field.
   - Fix: during Pull-Up with user-authored pitch, skip auto overwrite so typed pitch remains editable.
3. Command defaults updated:
   - Added `g_use_max: False` to default command template.

### Verification
- `python -m py_compile fa50_0.5.73.py` PASS

---

## v0.5.74
- Date/Time (KST): 2026-03-02 23:17
- Request Summary (EN): Recompute G MAX at each next step and add pitch-fix behavior that derives bank from G.
- 요청 요약 (KO): 다음 step마다 G MAX를 재계산 반영하고, pitch 고정 시 G로 bank를 계산하도록 추가.

### Changed Files
- fa50_0.5.74.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Step-by-step G MAX refresh:
   - In `advance_steps()`, when `g_use_max` is on, `g_cmd` is recalculated from newly reached state (`CAS/ALT/POWER`) and written into next-step command seed.
   - If next step already exists, its `g_cmd` is also refreshed for `g_use_max` aircraft.
   - `_simulate_one()` also respects `g_use_max` at runtime by replacing `g_cmd_user` with current PS-feasible max G.
2. Added `Pitch Hold` checkbox:
   - New command field `pitch_hold` in UI/read/write/default/export/import paths.
   - When enabled (turning command), level mode is released, pull mode is neutralized, and bank is auto-calculated from (`G`, fixed pitch).
   - During simulation, turning with `pitch_hold` keeps commanded pitch angle and solves bank accordingly.
3. Pitch edit stability:
   - Auto preview no longer overwrites user pitch while `pitch_hold` (and user pitch intent) is active.
4. Command change detection:
   - `_cmd_values_equal()` now includes `g_use_max`, `pitch_hold`, and `pitch_deg`.

### Verification
- `python -m py_compile fa50_0.5.74.py` PASS

---

## v0.5.75
- Date/Time (KST): 2026-03-02 23:19
- Request Summary (EN): Ensure Pitch Hold means “hold user input pitch setpoint”, not leveling to zero.
- 요청 요약 (KO): Pitch Hold가 0도 수평이 아닌 사용자 입력 pitch setpoint 유지 의미가 되도록 보정.

### Changed Files
- fa50_0.5.75.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. `sync_ui_from_step()`:
   - If `pitch_hold` is ON, pitch field now displays/keeps command pitch setpoint (`cmd.pitch_deg`) instead of current state pitch.
2. `_auto_apply_cmd_limits_for_aid()`:
   - When `pitch_hold` is ON, auto-preview no longer overwrites pitch input.
   - This preserves user setpoint while bank continues to be auto-solved from G in real time.

### Verification
- `python -m py_compile fa50_0.5.75.py` PASS

---

## v0.5.76
- Date/Time (KST): 2026-03-02 23:48
- Request Summary (EN): Prevent false “Apply changed aircraft / Keep old next step” prompts when just doing Back/Fwd.
- 요청 요약 (KO): 단순 Back/Fwd에서도 뜨던 “변경 적용” 프롬프트 오검출 방지.

### Changed Files
- fa50_0.5.76.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. `AircraftControl.read_command()` refined:
   - `pitch_deg` is now emitted as command only when pitch-command mode is active (`pitch_hold` or pull mode UP/DOWN).
   - This prevents display-state pitch from being treated as edited command.
2. `_cmd_values_equal()` dirty-check normalization:
   - If `g_use_max` is on, `g_cmd` differences are ignored (auto-derived by state).
   - `pitch_deg` is compared only in pitch-command mode (`pitch_hold` or pull UP/DOWN).
   - `pitch_hold` mode ignores `bank_deg` diff for dirty detection (bank is auto-derived).
3. Result:
   - Back -> Fwd with no intentional edits no longer triggers future-step policy prompt from auto-updated fields.

### Verification
- `python -m py_compile fa50_0.5.76.py` PASS

---

## v0.5.77
- Date/Time (KST): 2026-03-02 23:51
- Request Summary (EN): Include per-mode aircraft enable state in scenario save/load.
- 요청 요약 (KO): 모드 내 개별 항공기 enable 상태를 저장/불러오기에 포함.

### Changed Files
- fa50_0.5.77.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. Added `_enabled_aircraft_ids_for_save()` helper.
2. `export_scenario_csv()` now writes `META.enabled_ids`.
3. `import_scenario_csv()` now reads `META.enabled_ids` and reapplies checkbox state (where checkbox map exists) for loaded mode aircraft.

### Verification
- `python -m py_compile fa50_0.5.77.py` PASS

---

## v0.5.78
- Date/Time (KST): 2026-03-03 00:34
- Request Summary (EN): Reduce false “changed aircraft” prompt after Back/Fwd when no real edits were made.
- 요청 요약 (KO): 실제 수정이 없을 때 Back/Fwd 후 “changed aircraft” 프롬프트 오검출을 줄이기 위한 보정.

### Changed Files
- fa50_0.5.78.py
- CHANGELOG_FA50.md

### Code/Logic Changes (EN)
1. `_update_cmd_g_dynamic_cap()` behavior refined:
   - If `G MAX` is unchecked:
     - `g_cmd` range remains full (`up to 9.0`)
     - no auto-clipping of `g_cmd`
   - If `G MAX` is checked:
     - dynamic PS max is used as spin max
     - `g_cmd` is auto-clipped to max
2. This removes one major non-user-change source that could trigger future-step dirty detection after Back/Fwd.

### Verification
- `python -m py_compile fa50_0.5.78.py` PASS
- Runtime UI loop check in this CLI environment could not be executed (`PyQt6` not available in tool runtime).

