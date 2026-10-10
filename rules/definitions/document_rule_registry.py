"""실제 실행 가능한 문서 Rule을 관리하는 중앙 Registry.

Full Catalog 105개와 실제 실행 가능한 Rule은 분리해서 관리한다.
새 Priority Rule은 상세 구현과 targeted regression을 통과한 뒤 이 Registry에
등록하고, 등록 후 전체 회귀검증으로 제품 통합 안정성을 다시 확인한다.

현재 기준:
- Full Catalog: 105개
- 기존 MVP 실행 Rule: 20개
- P1 활성 Rule: 13개
- P2-A 활성 Rule: 7개
- P2-B 활성 Rule: 6개
- P2-C 활성 Rule: 4개
- P2-D 활성 Rule: 6개
- 총 실제 실행 가능 Rule: 56개
- P1 13개 전체 활성 완료
- P2 23