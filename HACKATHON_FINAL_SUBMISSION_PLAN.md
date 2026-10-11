# AI Auditor 해커톤 최종 제출 계획

## 1. 목적

현재 구현·검증 완료된 AI Auditor를 기준으로 해커톤 최종 제출물을 구성한다.

이번 제출 준비 기간에는 **P3/P4 49개 공식기준 재매핑과 추가 구현을 잠시 보류**한다.
P1/P2까지의 실제 실행 Registry 56개는 Freeze 상태를 유지하며, 새 결함이 확인되지 않는 한 재구현·재설계하지 않는다.

기준선:
- Full Catalog 105개
- 실제 실행 Registry 56개 = MVP20 + P1 13 + P2 23
- Rule 14 / AI 11 / Hybrid 31
- Parser 9종
- 감리자료 114개 실무 매핑
- Portable ZIP(EXE) 최종 검증 완료
- MSI 실제 설치 및 Local AI 검증 완료

---

## 2. 제출 산출물

### 2.1 3분 시연 영상 또는 라이브 데모

Canonical:
- `DEMO_3MIN_SCRIPT.md`

시연 흐름:
`프로젝트/파일 → Rule 선택 → 검사 → Issue 근거 확인 → Re-Inspect/History → Report Export`

원칙:
- 105개를 모두 구현했다고 표현하지 않는다.
- 반드시 **Full Catalog 105개 / 실제 실행 Registry 56개**를 구분한다.
- 실제 검사결과나 처리시간을 임의로 변경하지 않는다.
- 영상에서는 Local AI 대기구간을 편집할 수 있으나 결과값을 조작하지 않는다.
- 라이브는 작은 샘플/핵심 Rule 또는 사전 완료된 Inspection History를 준비한다.

### 2.2 발표 PPT — 10슬라이드 이내

구성 기준:
1. 작품명/한 줄 소개
2. 문제
3. 해결방법
4. 검사체계 및 실행범위
5. Rule / AI / Hybrid 구조
6. 실제 감리자료 114개 사례근거
7. 3분 데모 흐름
8. 제품·배포 검증상태
9. 정량 효과측정
10. 기대효과 및 향후 확장

### 2.3 소스코드 또는 워크플로우

제출 저장소:
- GitHub: `jjang99/AI-Auditor`

제출 기준:
- `main` 브랜치를 기준으로 한다.
- Local AI 모델 및 runtime 대용량 바이너리는 Git 소스관리 대상에서 제외한다.
- README / HACKATHON_SUBMISSION / 본 최종 제출계획을 함께 제출 설명자료로 사용한다.

### 2.4 효과측정지표 1장

Canonical:
- `EFFECT_MEASUREMENT.md`

확정 가능한 수치:
- 실제 실행 Rule: 56개
- Full Catalog 대비 실행률: 56 / 105 = 53.3%
- 감리자료 실무 매핑: 114개
- Parser 지원: 9종
- 사용자 실문서 실행기록: HWP 8,657 blocks, AUD-002/AUD-007 검사 13.71초
- 사용자 Qwen 검증기록: REQ-004 12 evidence, 5 candidate groups, 27.79초
- 외부 AI API 사용료: Local AI 추론 기준 0원(장비·전력비 제외)

아직 실측되지 않은 항목:
- 동일 샘플의 수동 검토시간
- 동일 샘플의 AI Auditor 전체 검사시간과의 A/B 비교
- 시간절감률
- 오류율 변화

따라서 제출 전 동일 문서·동일 점검범위로 마지막 A/B 실측 1회를 실시하고,
`(수동시간 - 자동시간) / 수동시간 × 100`으로 시간절감률을 확정한다.
임의 수치는 사용하지 않는다.

---

## 3. 제출 시 핵심 메시지

**AI Auditor는 일반 문서 요약 AI가 아니라, 실제 감리사례를 검증근거로 활용하고 Rule + Local AI + Hybrid 방식을 결합해 프로젝트 산출물의 품질 위험을 감리 전에 사전 점검하는 폐쇄망 대응형 품질 감사 플랫폼이다.**

강조 포인트:
- 105개 품질감사 Catalog 설계
- 그중 검증을 통과한 56개를 실제 제품에서 실행
- 실제 감리자료 114개와 Rule 체계 연결
- 9종 프로젝트 문서 지원
- Qwen3-4B + llama.cpp Local AI
- AI가 최종 Severity를 임의 결정하지 않고 deterministic Matrix 적용
- Portable EXE와 MSI 실제 설치본까지 검증

---

## 4. 제출 준비 우선순위

1. 3분 데모 시나리오 확정 및 리허설
2. 10장 이내 PPT 최종 검토
3. 효과측정 1장 최종화
4. 동일 샘플 수동/자동 A/B 시간 측정
5. GitHub README/HACKATHON_SUBMISSION과 제출자료 간 숫자·표현 교차검증
6. 최종 제출 패키지 확인

P3/P4 49개 공식기준 재매핑은 위 제출작업 완료 후 재개한다.
