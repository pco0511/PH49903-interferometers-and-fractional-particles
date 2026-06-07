# 시각화 후보 정리 — Nakamura et al. 2020 (anyonic braiding, ν=1/3 FQH)

> arXiv:2006.14115v1 *"Direct observation of anyonic braiding statistics at the ν=1/3 fractional quantum Hall state"*
> 목표: 논문에서 interactive하게 시각화할 만한 것을 **거의 모두** 추려, 무엇을 / 어떤 물리로 / 어떤 슬라이더로 보여줄지 정리한다.
> 발표 흐름과 매핑되도록 4개 그룹(개념 → 소자 → 측정결과 → 시뮬레이션)으로 묶었다.

---

## 구현 상태 (2026-06-05): 전부 완료 ✅

아래 후보를 **모두** 구현했다. 갤러리: **`final-presentation/viz/index.html`**

```
final-presentation/viz/
  index.html                      # 갤러리 랜딩 (그룹별 타일)
  shared/  physics.js render.js style.css   # 공유 엔진(JS≡Python 검증) + 렌더 헬퍼 + 테마
  concepts/     a1-braiding · a2-phase-decomposition · a3-dos-regimes · a4-energy-occupation
  device/       b1-device-edge · b2-layer-stack
  measurements/ c2-linecut · c3-lever-arm · c4-temperature · c5-velocity-checkerboard · c6-nu1-control
  simulation/   d1-heatmap · d3-width-calculator
```

- 모든 페이지는 공유 `shared/physics.js`(픽셀 적합값)를 사용. 단일 HTML, 외부 의존성 없음(file:// 동작).
- 검증: (1) 시스템 Edge 헤드리스 스모크테스트 14/14 콘솔오류 0 (`test_viz.js`), (2) **그룹별 별도-컨텍스트 reviewer 에이전트**가 논문 일치·물리·코드효율 검수 → 발견된 MAJOR 3건(A3 μ–모델 결합, C2 sim/실측 라벨, C6 비교모드 readout) 및 MINOR/NIT 수정 완료.
- 테스트 산출물: `final-presentation/figures/viz-tests/*.png`, 하니스: `final-presentation/test_viz.js` (playwright-core + msedge).

### anchor (검증된 standalone)
- **Supp. Fig. 5 interactive** — `final-presentation/supp-fig5-interactive.html` (= D-1/D-2). viz/simulation/d1-heatmap.html이 동일 물리의 공유-모듈 리팩터 버전.

## 프로토타입 (2026-06-07): outline 갭 채우기 — `viz/prototypes/`

outline 재작성 후 발견된 미구현 그림 4건을 프로토타입으로 구현(슬라이드 형식 아님, 방향 탐색용). 검증: 스모크테스트 20/20 콘솔오류 0 + 그룹별 별도-컨텍스트 reviewer 3개 → 전부 PASS-WITH-FIXES, 발견된 MAJOR 2건(fig3b B-extent 100 mT 오차, 유도 −cosθ→+cosθ 논문관례) 및 MINOR 수정 완료.

- **P-slice** `p-slice-crosshair.html` — (Gap 2+3, 모델) δG 맵 위 드래그 십자선 → 가로컷(δG vs B)·세로컷(δG vs δV_g) 동시 + 음(AB)·양(jump) 기울기 주석.
- **P-slice-meas** `p-slice-measured.html` — (Gap 2+3, 측정) 논문 측정 heatmap(window.MEASURED.fig2/fig3b)에서 직접 가로/세로 컷 + 기울기 가이드선(디폴트는 오버레이에서 추정). **논문 주석 오버레이 토글**: `extract_overlay.py`가 `ref-crops/fig2_overlay.svg`(실선=AB fringe, 점선=phase-slip 경계)를 (B,δV_g) 좌표로 파싱 → `data/fig2_overlay.js`(window.OVERLAY.fig2; 실선 33개 기울기 −239, 점선 4개 +512 mV/T). 오버레이 ON 시 heatmap에 선 표시 + 가로/세로 컷에 slip 위치를 분홍 마커로 표기. 사용자 crop은 extract_measured.py로 추가.
- **P-cmp-A** `p-compare-sidebyside.html` / **P-cmp-B** `p-compare-overlay.html` — (Gap 1) 측정(Fig 2/3b jet 역변환 추출) ↔ 모델 비교. side-by-side / wipe·blend·diff. 실측 geometry 프리셋(A₀=0.259 μm², B-주기≈48 mT) 탑재.
- **P-der-A** `p-derivation-phasor.html` / **P-der-B** `p-derivation-twopath.html` — (Gap 4) r₁+r₂e^{iθ}→|r|²→δG∝cos θ 유도. 복소평면 진폭합 / **실제 소자(B1 geometry) 위** 두 경로(r₁@QPC1, r₂=A_I 둘러싸는 loop) 간섭.

데이터 추출: `extract_measured.py` (jet역변환 → `viz/prototypes/data/measured.js` = window.MEASURED).
- **fig2**: 사용자 제공 **깨끗한 crop** `ref-crops/fig2.png`(주석선은 `ref-crops/fig2_overlay.svg`로 분리)를 데이터 영역 전체로 사용. extent B[8.71,9.03]·δV_g[-31.9,-3.1], **절대 scale ±4 ×10⁻² e²/h(확정)**. 원본 figures/fig2.png 영역과 상관 0.957(주석선 제거분 차이), 방향 일치 확인.
- **fig3b**: figures/fig3.png에서 축프레임 박스 추출, B[8.682,9.396], δV_g 추정, scale ±4(가정).

검증 안 된 잔여(전부 MINOR, 프로토타입 허용): 측정/모델은 각자 진폭 정규화라 절대 스케일 비교 아님(주기·기울기·위상만); fig3b δV_g 축은 근사(눈금 미검출); two-path 막대는 물리 G=G₀(1−R)라 δG(+cosθ 관례)와 위상 반대.

---

## 우선순위 요약표

| # | 후보 | 출처 | interactive 핵심 | 난이도 | 우선 |
|---|------|------|------------------|--------|------|
| A-1 | Braiding = 두 번 교환 ≡ 한 번 encircle | Fig 1a | 경로 애니메이션 + 누적 phase θ_anyon | 중 | ★★★ |
| A-2 | AB + anyonic phase 분해 (Eqn 1) | 본문 Eqn 1 | B·V_g 두 항 기여를 막대/위상바늘로 분해 | 하 | ★★★ |
| A-3 | DOS 3-regime (constant-ν ↔ constant-n) | Supp 5e | μ 슬라이드 → particle/hole 채움 | 중 | ★★★ |
| A-4 | E(N_qp) 포물선 + 열점유 | Supp Eqn 7 | B, kT, Δ_qp 슬라이더 → 점유분포·⟨N⟩ | 중 | ★★ |
| B-1 | 소자 geometry + chiral edge / QPC backscatter | Fig 1b | 전류 흐름 애니메이션, backscatter 토글, 둘러싼 qp 수 | 중 | ★★★ |
| B-2 | Heterostructure layer stack | Supp 1 | 층 hover 설명, screening 거리 d 강조 | 하 | ★ |
| C-1 | Pajama plot (δG heatmap) 생성기 | Fig 2, 3b | = D-1 과 공유 엔진 | (D에 포함) | ★★★ |
| C-2 | Line-cut: δG vs δV_g, 주기/기울기 변화 | Supp 4a | B 위치 슬라이더 → period·slope 변화 | 하 | ★★★ |
| C-3 | 주기/lever-arm 계산기 (α_bulk, α_edge) | Supp Disc 1 | α_total, α_edge 슬라이더 → 예측 주기 | 하 | ★★ |
| C-4 | T_0 온도 감쇠 + topological dephasing | Fig 4 | 영역별 T_0, dephasing on/off | 중 | ★★ |
| C-5 | 미분 conductance checkerboard → v_edge | Supp 7 | v_edge, L 슬라이더 → node 간격 | 중 | ★★ |
| C-6 | ν=1 대조군 (braiding 안 보임) | Supp 6 | ν=1 vs ν=1/3 토글 | 하 | ★★ |
| D-1 | Supp Fig 5 heatmap (3 온도) | Supp 5a-c | **완료** | — | ✅ |
| D-2 | ⟨N_qp⟩ 계단 vs B | Supp 5d | **완료** | — | ✅ |
| D-3 | ΔB_constant-ν 폭 예측 계산기 | 본문 Eqn | Δ, C_SW, d 슬라이더 → 530 mT | 하 | ★ |

★★★ = 발표 핵심/효과 큼, ★★ = 보강용, ★ = 있으면 좋음

---

## A. 개념 (Concepts) — 슬라이더로 "왜"를 보여주는 것

### A-1. Braiding: 두 번 교환 ≡ 한 번 encircle  ★★★
- **출처:** Fig 1a, BACKGROUND
- **시각화:** 두 vortex(빨간 소용돌이)를 평면에 놓고
  - (왼쪽) 위치 두 번 교환 → 제자리 / (오른쪽) 하나가 다른 하나를 닫힌 loop로 한 바퀴
  - 두 과정이 topologically 동등함을 나란히 애니메이션, 누적 위상 θ_anyon을 위상바늘(phasor)로 표시
- **물리:** 2D에서 교환² ≡ braid, 계가 얻는 위상 = θ_anyon = 2π/(2p+1). ν=1/3 → 2π/3.
- **interactive:** ν(=1/3, 1/5, 1) 선택 → θ_anyon 변화 / 재생·일시정지 / 둘러싼 qp 수 N → 총 위상 N·θ_anyon
- **데이터:** 불필요(순수 도식). Canvas 2D 애니메이션.
- **메모:** 발표 도입부 임팩트 큼. "경로 무관, 둘러싼 수에만 의존"을 강조.

### A-2. AB phase + anyonic phase 분해 (Eqn 1)  ★★★
- **출처:** 본문 Eqn 1 `θ = 2π(e*/e)(A_I B/Φ₀) + N_qp·θ_anyon`
- **시각화:** 총 위상 θ를 두 기여로 분해해 위상바늘/누적막대로 표시
  - 연속적 AB 항(B, V_g에 따라 회전) + 이산적 anyon 항(N_qp 계단)
  - 아래에 cos(θ) → δG 실시간
- **interactive:** B, δV_g, N_qp 슬라이더 → 두 바늘이 더해져 δG가 나오는 과정
- **물리:** AB는 연속·음기울기, anyon은 이산 점프. 이 둘의 합이 측정 δG.
- **난이도:** 하. D-1 엔진 재사용.

### A-3. DOS 3-regime: constant-ν ↔ constant-n 전이  ★★★
- **출처:** Supp Fig 5e (Hole-like / μ / Particle-like states)
- **시각화:** energy 축 DOS(두 봉우리: hole-like, particle-like) + chemical potential μ 수직선
  - 중심(μ가 gap 한가운데, 낮은 DOS) → quasiparticle 거의 없음 → constant-ν, 3Φ₀, 음기울기 AB
  - 고/저 field(μ가 봉우리로 접근, 높은 DOS) → qp/qh 다수 생성 → constant-n, Φ₀, thermal smear
- **interactive:** B 슬라이더 → μ가 좌우로 이동, 채워지는 상태(particle/hole) 음영, 현재 regime 라벨
- **물리:** μ가 DOS 높은 곳에 오면 작은 에너지 간격 → thermal smearing → Φ₀ oscillation이 안 보임.
- **메모:** B 슬라이더를 D-1 heatmap의 세로선과 **연동**하면 "이 B에서 왜 이런 패턴인지" 직관적.

### A-4. E(N_qp) 포물선 + 열점유  ★★
- **출처:** Supp Eqn 7 `E = (e²/2C)δq_net² + Δ_qp|N_qp|`, Supp Fig 5d
- **시각화:** N_qp 정수 격자 위 에너지점(charging 포물선 + gap 사다리), Boltzmann 가중 막대
  - B를 바꾸면 포물선 꼭짓점이 정수 사이를 이동 → 최저 N이 바뀌는 순간이 phase slip
- **interactive:** B, kT/E_c, Δ_qp/E_c 슬라이더 → 점유분포·⟨N_qp⟩ 실시간(= D-2의 미시 버전)
- **물리:** δq_net = νA·B/Φ₀ + (e*/e)N − q_donor − α_bulk δV_g. 열평균이 ⟨N_qp⟩ 계단을 만든다.
- **메모:** D-2(계단) 옆에 붙여 "계단 한 칸 = 포물선 최소점 전환"을 보여주면 교육적.

---

## B. 소자 / 실험 셋업 (Device / Setup)

### B-1. 소자 geometry + chiral edge + QPC backscattering  ★★★
- **출처:** Fig 1b (false-color SEM), DEVICE DESIGN
- **시각화:** gate 모양(QPC 2개 + side gate) 위에
  - chiral edge state(빨간 화살표) 흐름 애니메이션
  - 두 QPC에서의 backscatter 경로(점선) → 내부 둘러싼 영역
  - 내부 localized quasiparticle(vortex) 표시
- **interactive:**
  - QPC transmission 슬라이더(~90%) → backscatter 비율 시각화
  - side gate voltage → 면적 A_I 변화(둘레 수축, ~200nm depletion)
  - 내부 qp 수 N → 둘러싸인 vortex 개수 → 위상 기여
- **물리:** weak backscattering, 둘러싼 qp 둘레 braid → θ_anyon 민감. 1.0×1.0 μm 리소, l_B≈9 nm.
- **난이도:** 중(도식 + 간단 애니메이션). SEM 이미지를 배경으로 깔면 효과↑.

### B-2. Heterostructure layer stack  ★
- **출처:** Supp Fig 1
- **시각화:** 층별 막대(GaAs/AlGaAs/AlAs, screening well 2개, primary well, δ-doping)
- **interactive:** 층 hover → 두께·역할 / screening well ↔ primary well 거리 d=48 nm 강조(C_SW=2ε/d 연결)
- **메모:** 대체로 정적. C_SW를 D-3 폭 계산기와 연결할 때만 의미. 우선순위 낮음.

---

## C. 측정 결과 (Measurement results)

### C-1. Pajama plot 생성기 (δG heatmap)  ★★★
- **출처:** Fig 2, Fig 3b (그리고 Supp Fig 5 시뮬레이션)
- **시각화:** δG(B, δV_g) jet heatmap + 음기울기 AB 줄무늬 + 이산 phase jump 안내선
- **상태:** **D-1로 이미 구현** (실데이터 픽셀 적합 완료). Fig 2/3b는 동일 엔진에 B 범위만 넓히면 됨.
- **추가 아이디어:** 실측 데이터(ref-crops)와 모델을 좌우로 토글/오버레이.

### C-2. Line-cut: δG vs δV_g, 영역별 주기·기울기 변화  ★★★
- **출처:** Supp Fig 4a (8.4T/8.85T/9.3T 3선), DISCRETE PHASE SLIPS
- **시각화:** 고정 B에서 δG vs δV_g 1D 곡선; 중심(8.5 mV) vs 고/저 field(5.4–5.8 mV) 주기 차이
- **interactive:** B 위치 슬라이더 → 주기가 3Φ₀↔Φ₀ 사이로, 등위상선 기울기가 음→평평으로 변하는 것
- **물리:** ∂θ/∂V_g = 2π(e*/e)(B/Φ₀)(∂A/∂V_g) + θ_anyon ∂⟨N_L⟩/∂V_g. 두 번째 항이 주기를 줄인다.
- **난이도:** 하. D-1 heatmap에서 세로 line-cut을 빼면 바로 나옴(연동 표시 추천).

### C-3. 주기 / lever-arm 계산기 (α_bulk, α_edge)  ★★
- **출처:** Supp Discussion 1, Supp Fig 4b(CB)/4c(ν=1 AB)
- **시각화:** α_total(=1/ΔV_CB) − α_edge(ν=1 AB) = α_bulk 분해를 막대/수식으로
  - 예측 주기 ΔV_g = 1/[ (B/3Φ₀)(∂A/∂V_g) + α_bulk ] 를 실시간 계산, 측정값(5.8/8.5/5.4)과 비교
- **interactive:** ΔV_CB, ΔV_{ν=1}, B 슬라이더 → α들, ∂A/∂V_g, 예측 주기
- **물리:** q_total = q_edge + q_bulk. 중심은 첫 항만, 고/저 field는 두 항 모두.
- **메모:** transition 선 기울기 dV_g/dB = νA/(Φ₀ α_bulk) 도 같이(≈0.44 mV/mT) → D-1의 양기울기와 연결.

### C-4. T_0 온도 감쇠 + topological dephasing  ★★
- **출처:** Fig 4 (ln δG vs T, 3 field), TEMPERATURE DEPENDENCE
- **시각화:** ln(δG) vs T 직선 3개(8.4/8.85/9.3T), 기울기 = −1/T_0
  - 측정: 중심 94 mK vs 고/저 31·32 mK / edge-velocity 예측: 76·89·85 mK
- **interactive:** topological dephasing on/off 토글 → 고·저 field 직선이 예측(≈85)에서 측정(≈31)로 꺾이는 것
- **물리:** δG ∝ e^{−T/T_0}; 중심은 edge thermal smearing만, 고/저 field는 N_qp 요동에 의한 추가 dephasing[69].
- **데이터:** Fig 4 점들을 디지타이즈하거나 T_0 직선만 모델로.

### C-5. 미분 conductance checkerboard → v_edge  ★★
- **출처:** Supp Fig 7, Supp Discussion 3
- **시각화:** ∂I/∂V_sd 를 (V_sd, δV_g) 평면에 checkerboard로; V_sd 따라 node, 옆에 FFT 진폭 vs V_sd
- **interactive:** v_edge, L(둘레), e* 슬라이더 → node 간격 ΔV_sd 변화
- **물리:** δθ = e δV_sd L/(ħ v_edge); v_edge = e* L ΔV_sd/(2πħ). 세 영역 모두 ~(8–10)×10³ m/s.
- **메모:** "v_edge는 거의 안 변한다 → T_0 차이는 velocity 탓이 아니다"라는 논증을 보여주는 용도.

### C-6. ν=1 대조군  ★★
- **출처:** Supp Fig 6
- **시각화:** ν=1 heatmap은 고/저 field에서도 음기울기 AB 유지(전이 없음) ↔ ν=1/3은 평평해짐
- **interactive:** ν=1 / ν=1/3 토글로 같은 엔진에서 비교(θ=2π fermion이면 braiding 안 보임)
- **물리:** 전자는 fermion(θ=2π) → braiding trivial → 거동 변화 없음. anyon 효과의 결정적 대조.
- **난이도:** 하. D-1 엔진에서 e*/e=1, θ_anyon=2π, 주기 3배 축소만.

---

## D. 시뮬레이션 (Simulation, Supp Fig 5)

### D-1. δG(B, δV_g) thermal-average heatmap (3 온도)  ✅ 완료
- `simulate()` / interactive HTML. 픽셀 적합 완료(관측량 모두 일치).

### D-2. ⟨N_qp⟩ 계단 vs B  ✅ 완료
- 저온 sharp 계단 → 고온 smear. A-4(포물선)와 묶으면 미시→거시 설명 완성.

### D-3. ΔB_constant-ν 폭 예측 계산기  ★
- **출처:** 본문 `ΔB = Δ_{1/3} Φ₀ C_SW /(ν e² e*)`
- **시각화:** Δ_{1/3}(=5.5K), C_SW=2ε/d, d=48nm 슬라이더 → 예측 폭(≈530 mT) vs 관측(≈450 mT) 막대 비교
- **메모:** B-2(layer stack)·D-1(heatmap 중심폭)과 수치로 연결. 작지만 "이론↔실험 정량일치" 한 장.

---

## 제안 빌드 순서 (발표 스토리라인 기준)

1. **A-1 braiding 애니메이션** — 도입(왜 anyon인가)
2. **B-1 소자 + edge/QPC** — 어떻게 측정하나
3. **A-2 / A-3 / A-4** — 위상식·DOS·에너지 모델(핵심 물리)
4. **D-1 + D-2 (완료) + C-1/C-2 line-cut 연동** — 시뮬레이션 ↔ 실데이터
5. **C-3 lever arm / C-4 T_0 / C-5 v_edge / C-6 ν=1** — 정량 검증·대조
6. **D-3 / B-2** — 보조 수치/구조

## 공통 기술 메모
- 공유 physics 엔진: 기존 HTML의 thermal-average 코드(JS===Python 검증됨)를 모듈로 빼서 A-2/A-3/A-4/C-1/C-2/C-6 가 재사용.
- jet colormap 역변환·픽셀 적합 파이프라인은 `fit_to_pixels.py`에 있음(실데이터 오버레이용).
- 렌더: Canvas 2D(heatmap·도식 애니메이션)면 충분, 외부 의존성 없이 단일 HTML 유지 권장.
- 단위/상수·적합 파라미터는 `reproduce_simulation.py` 기본값과 동기화.
