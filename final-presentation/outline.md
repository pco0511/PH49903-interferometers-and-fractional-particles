# Design Style
- 16:9 슬라이드, transition 없음
- 맨 위에 제목, 왼쪽 아래에 작게 어떤 section인지
- 흰 배경, 디자인 요소 없이 minimal하게
- 만들어놓은 시각화 자료 활용, loop 형태의 animation만 과도하지 않게
- 발표 자료에는 영어만 사용

# Outline


## recall (~1 min)
> 강의(ref/lecture_notes)에서 다룬 내용을 recall 하는 파트
- Fractional Braiding Statistics of Laughlin Quasi Particles
    - exchange phase vs braiding(=둘러싸기=두 번 exchange) phase
    - ν=1/3 → braiding phase 2𝜋/3 (이후 phase jump 크기의 출처)
    필요한 시각화: A1, phase 가 2𝜋/3만큼 accumulate됨. laughlin wavefunction (quasi hole, quasi particle excitation)수식과 간단한 정적인 그림(quasi hole, quasi particle이 포함된)
- Quantum Hall Interferometer, weak backscattering regime
    필요한 시각화: quasi hole 없는 B1
## Device Design (~1 min)
- 두 backscattering 경로(QPC1, QPC2)의 phase difference 설명
    - Aharonov-Bohm phase + braiding(anyonic) phase
- interference에 의한 probability current 변화 → conductance(δG) 변화 식 유도
    - θ = 2π(e*/e)(A_I·B/Φ₀) + N_qp·θ_anyon, δG ∝ cos θ 로 귀결
    필요한 시각화: magnetic field, quasi hole에 의한 phase occumulation이 표현된 B1
## Interpretation of Results
### Discrete phase slips (~2 min)
- 측정 결과를 simulation과 나란히 비교 (δG heatmap)
- 가로/세로 slice 그래프 표시 (slice 위치 조절 슬라이더) → 각 slice의 oscillation 해석
- phase jump = 둘러싼 quasiparticle에 의한 phase 로 설명 (N_qp 변화 → 2𝜋/3 jump)
    - (선택) ν=1 대조군 비교: fermion(θ=2π)은 jump 없음 → anyon 효과의 결정적 증거
- "각 기울기들의 의미":
    - 등위상선(iso-phase line)의 음의 기울기 (연속적 AB 항)
    - quasiparticle로 인한 phase jump 절단면의 양의 기울기 (이산적 anyon 항)
필요한 시각화: 필요한 figure들 전부
### Temperature dependence (~2 min)
- 데이터에 나타나는 dephasing들
- Topological dephasing 소개
필요한 시각화: 온도에 따른 실제 실험 데이터와 dwell-time·plasmonic dephasing이 드러나는 그림들, topological dephasing이 일어나는 영역의 실험 결과들 온도 슬라이더가 있는 시뮬레이션
## Summary (~30 sec)
## Auxiliary
- Transition from Constant Filling to Constant density

- Experimental Details
    - 소자 구성
    - Interaction 문제 해결 방법3