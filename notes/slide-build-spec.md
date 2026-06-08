# Slide build spec — directives from 2026-06-08

> **중요 전제:** 지금 슬라이드들은 *간단히 테스트할 목적*으로 기존 viz를 `?embed`로
> 끼워 넣은 것이다. **실제 발표는 각 슬라이드에 맞게 처음부터 custom으로 다시 만든다.**
> 아래 per-slide 스펙은 그 custom 재작성의 타깃이다. (deck: `final-presentation/slides/index.html`)

## Global directives
- [G1] 화면 비율 정확히 **16:9** (1280×720 스테이지, 균일 scale). — 점검/수정
- [G2] step을 **순차 공개하지 말고 한 슬라이드의 모든 텍스트를 한꺼번에** 표시. (fragment off)
- [G3] 마우스 휠 딜레이(쿨다운) **50 ms**.
- [G4] 이 지시들을 notes/에 기록(=이 파일).
- [G5] embed는 임시. 발표용은 슬라이드별 custom 재작성 예정.

## Per-slide spec  (번호 = 현재 deck 페이지 번호)
1. **Title** — 제목 슬라이드에 anyon braiding + 간섭계(interferometer) 구조 그림 추가.
2. **Recall divider** — "~1 min" 문구 제거.
3+4. **Braiding + Laughlin → 한 슬라이드로 합침.**
   - 왼쪽: Laughlin state / quasiparticles, **wavefunction formula 포함**.
   - 오른쪽: braiding animation. **기존 phasor는 삭제**하고:
     - t=0, t=1 에 **고정 phasor** (각각 θ=0, θ=2π/3),
     - time slice 바로 오른쪽에, slice를 따라 위로 올라가며 회전하는 **움직이는 phasor**,
     - t=0/t=1에서 고정 phasor와 정확히 일치.
5. **Interferometer (b1)** — interferometer에서 **quasihole 제거**. 여기서 바로
   **r₁, r₂, phase difference에 의존하는 probability current, conductance 수식** 제시.
6. **Device divider** — "~1 MIN" 제거.
7. **Two paths** — 지금 임베드된 것 말고 **5번 슬라이드의 device를 사용**(여기는 **quasihole 포함**).
   오른쪽 oscillation 그림 **삭제**(불필요). 여기서 probability current/conductance 수식 작성.
   **phase difference의 두 source만 언급**하면 앞 수식에서 바로 따라 나옴.
8. **(phasor "From Interference to Conductance") — 슬라이드 자체 + 시각화 제거.**
9. **Results divider** — 좋음(유지).
10+11. **Measurement-vs-sim + Slices → 하나로 합침.** 실험·이론 slice들을 함께.
12+13. **(Phase Jumps / Meaning of Slopes)** — 10·11과 같은 그림을 쓰되 **화살표 등으로
   무엇을 말하는지 강조**.
14. **ν=1 control** — 일단 그대로.
15+16. **Temperature → 온도 슬라이더가 있는 이론계산**을 띄움(온도 올릴 때 dephasing이
   나타나는 것을 보여줌). (기존 D1 sim heatmap에 kT/E_c 슬라이더 있음 → 활용 후보)
17. **Summary** — 앞에서 보여준 시각화의 **interaction 불가·animation 없는 정적 버전 6개**
   정도를 한 화면에 배치.

## Status
### Pass 1 (구조 합치기/글로벌, embed 사용)
- G1–G3, 2·6 divider 문구 제거, 8 제거, 3+4 / 10+11 / 15+16 합침, 1 그림 추가,
  17 6-up montage, 14 유지.

### Pass 2 — 16:9 / 글로벌 (2026-06-08)
- **16:9 버그 수정**: `#stage{flex:none}` (1280px보다 좁은 창에서 가로 수축하던 문제).
- 표지: braid ≡ 간섭계 라이트 SVG (인라인).

### Pass 3 — **기존 viz를 recolor**(내부 구현 유지, 색만 흰 배경에 맞게) + phasor 추가 (2026-06-08)
> 중요: Pass 2에서 잠깐 만들었던 `BRAID_ANIM`/`deviceSVG`(처음부터 새로 그린 가짜)는 **삭제**.
> 원본 viz의 3D 시간축·time slice·braiding curve·exchange↔winding 비교·애니메이션 timing은
> 모두 그대로 두고 **색만** 바꾼다. (`?light` → `embed-light` 클래스 → 테마-aware 색)
- **shared/embed.js**: `?light` → `embed-light`. **shared/style.css**: 라이트 배경.
- **a1-braiding**: 색 변수 테마-aware(흰 선→검정 등), canvas 820→1000, 기존 작은 phasor 다이얼
  제거하고 우측에 **phasor 컬럼 추가** — 고정 t=0(θ=0)/t=1(θ=2π/3) + time slice 따라 올라가며
  회전하는 phasor(끝점에서 고정과 일치). 갤러리(다크)는 그대로.
- **b1-device-edge**: 색 변수 테마-aware로 흰 배경 recolor + `?N=` 파라미터(둘러싼 quasiparticle 수).
- deck: 3-우측 = a1(`?embed=fig&light=1`), 4 = b1(`&light=1&N=0`, quasihole 없음),
  6 = b1(`&light=1&N=2`, quasihole 포함). deviceSVG/BRAID_ANIM 제거.

### 남은 custom (다음 단계) — 데이터 viz 라이트화 + 강조
- 데이터 슬라이드(7 슬라이스 ×2, 8 phase jump, 9 slope, 11 온도 D1)도 같은 방식으로
  **`?light` recolor** 하면 됨(p-slice-*, c4, d1, p-compare-* 의 색 변수화). render.js의 축/잉크 색도.
- 12 summary 6-up 정적컷은 라이트 viz로 **재캡처** 필요(현재 다크 썸네일).
- 8·9 강조 화살표.
