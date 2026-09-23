"""AI Auditor 문서 검사체계 공통 기준정보.

제품 전체 검사체계(105개)와 해커톤 MVP 실행 대상(20개)의
영역별 기준을 Administration과 Inspection에서 공통으로 사용한다.

주의:
- 전체 Rule 수와 MVP 구현 수는 서로 다른 개념이다.
- 실제 MVP Rule 상세 정의는 document_mvp_rules.py에서 관리한다.
- 기존 소스코드 정적분석 Rule(default_rules.py)은 별도로 유지한다.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentRuleCategory:
    code: str
    name: str
    total_count: int
    mvp_count: int


DOCUMENT_RULE_CATEGORIES = (
    DocumentRuleCategory("AUD", "감리 사전점검", 24, 4),
    DocumentRuleCategory("REQ", "요구사항 정합성", 28, 6),
    DocumentRuleCategory("CHG", "변경영향도", 18, 4),
    DocumentRuleCategory("FP", "FP 검증", 12, 2),
    DocumentRuleCategory("AI", "AI 특화 검증", 23, 4),
)


def get_document_rule_categories():
    """최종 5대 문서 검사영역 기준을 반환한다."""
    return DOCUMENT_RULE_CATEGORIES


def get_total_rule_count():
    """제품 전체 검사기준 수를 반환한다."""
    return sum(category.total_count for category in DOCUMENT_RULE_CATEGORIES)


def get_total_mvp_count():
    """현재 해커톤 MVP 대상 Rule 수를 반환한다."""
    return sum(category.mvp_count for category in DOCUMENT_RULE_CATEGORIES)

# === GENERATED DOCUMENT RULE DETAILS START ===


@dataclass(frozen=True)
class DocumentRuleCatalogItem:
    code: str
    name: str
    category_code: str
    category: str
    description: str
    execution_type: str


DOCUMENT_RULES = (
    DocumentRuleCatalogItem(
        code='AUD-001',
        name='필수 산출물 누락 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='사업/단계별 필수 산출물 제출 여부',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='AUD-002',
        name='산출물 작성완전성 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='필수항목, 공란, TBD 등 미작성 영역',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AUD-003',
        name='산출물 기본정보 일치 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='프로젝트명, 작성일, 작성자, 버전 등 일치 여부',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='AUD-004',
        name='문서 버전정보 적정성 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='버전, 개정일, 변경이력 관리 적정성',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='AUD-005',
        name='문서 간 용어 일관성 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='동일 대상을 서로 다른 용어로 기술하는지',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='AUD-006',
        name='문서 내 참조 오류 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='존재하지 않는 표·그림·절·문서 참조',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='AUD-007',
        name='미확정 표현 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='TBD, 미정, 추후협의 등 미확정 표현',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AUD-008',
        name='계획 대비 산출물 작성상태 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='계획된 산출물과 실제 작성·제출상태 비교',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='AUD-009',
        name='일정정보 일관성 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='계획서·WBS 등 일정정보 간 불일치',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='AUD-010',
        name='WBS 완전성·비정상 항목 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='작업, 기간, 담당자 누락 및 비정상 기간 후보',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AUD-011',
        name='일정 선후행 관계 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='WBS 선행·후행 관계의 논리적 오류',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='AUD-012',
        name='형상관리 대상 누락 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='관리대상 산출물의 형상관리 등록 누락',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='AUD-013',
        name='형상 버전·변경이력 일치 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='형상대장과 실제 버전 및 변경이력 비교',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='AUD-014',
        name='시험계획 완전성 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='시험항목, 방법, 예상결과 등 필수정보',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='AUD-015',
        name='시험 수행·결과 완전성 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='대상 시험의 결과 작성 및 수행상태',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='AUD-016',
        name='시험결함 조치상태 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='미조치·미종결 결함 존재 여부',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='AUD-017',
        name='시험 증적 적정성 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='시험결과를 뒷받침하는 증적의 존재·연결',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AUD-018',
        name='품질활동 계획 대비 수행 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='계획된 품질활동의 실제 수행 여부',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AUD-019',
        name='품질지적사항 미조치 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='검토·품질점검 지적사항의 미조치 여부',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='AUD-020',
        name='인터페이스 정의 완전성 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='필요한 연계/인터페이스 정의 누락',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AUD-021',
        name='인터페이스 문서정보 일치 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='시스템, 방식, 주기 등 문서 간 불일치',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AUD-022',
        name='계약·과업내용 반영 및 이행 증적 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='계약/RFP/과업의 계획·산출물 반영과 수행 증거',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AUD-023',
        name='관련 기준·지침 준수 점검',
        category_code='AUD',
        category='감리 사전점검',
        description='적용 법령·지침·표준의 준수 여부와 증적',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AUD-024',
        name='감리 예상 지적사항 후보 도출',
        category_code='AUD',
        category='감리 사전점검',
        description='개별 결과를 종합해 근거 기반 지적 후보 제시',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='REQ-001',
        name='요구사항 ID 누락·중복 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='ID 미부여 및 중복 여부',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='REQ-002',
        name='요구사항 내용 중복 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='표현은 다르지만 의미가 같은 요구사항 후보',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='REQ-003',
        name='요구사항 모호성 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='적절히, 필요시 등 판단기준 불명확 표현·문맥',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='REQ-004',
        name='요구사항 상충 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='동시에 만족하기 어려운 요구사항 후보',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='REQ-005',
        name='요구사항 필수정보 누락 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='명칭, 내용, 분류, 우선순위 등 필수정보',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='REQ-006',
        name='요구사항 완전성 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='구현대상·조건·범위가 충분히 정의됐는지',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='REQ-007',
        name='요구사항 검증가능성·검증방법 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='객관적 검증 가능성과 시험/분석/검토 방법 정의',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='REQ-008',
        name='요구사항 분류 적정성 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='기능/비기능 등 분류와 실제 내용의 적합성',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='REQ-009',
        name='요구사항 설계 반영 정합성 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='요구사항의 설계·화면·데이터·인터페이스 반영',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='REQ-010',
        name='설계 근거 요구사항 누락 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='설계 요소의 상위 요구 근거 부재',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='REQ-011',
        name='요구사항-설계 내용 불일치 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='조건·처리내용 등 의미 불일치',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='REQ-012',
        name='요구사항 시험항목 누락 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='요구사항에 대응하는 시험항목 부재',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='REQ-013',
        name='시험항목 근거 요구사항 누락 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='시험항목의 상위 요구 근거 부재',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='REQ-014',
        name='요구사항-시험내용 불일치 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='요구내용과 시험방법·조건 불일치',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='REQ-015',
        name='요구사항-예상결과 불일치 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='요구조건과 시험 예상결과 불일치',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='REQ-016',
        name='중요 요구사항 시험범위 누락 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='중요 요구사항의 시험 제외·누락',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='REQ-017',
        name='요구사항 추적관계 누락 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='후속 산출물과의 추적 링크 누락',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='REQ-018',
        name='양방향 추적성 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='상위→하위 및 하위→상위 추적 가능 여부',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='REQ-019',
        name='추적표와 실제 산출물 불일치 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='추적표 연결과 실제 내용의 일치 여부',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='REQ-020',
        name='잘못된 요구사항 참조 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='존재하지 않거나 잘못된 ID 참조',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='REQ-021',
        name='요구사항 상태·승인정보 정합성 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='완료/보류/삭제 및 승인·확정상태 불일치',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='REQ-022',
        name='동일 기능 명칭 불일치 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='문서별 동일 기능의 명칭 차이',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='REQ-023',
        name='업무규칙 불일치 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='요구와 설계의 조건·처리규칙 불일치',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='REQ-024',
        name='입력·출력 정의 불일치 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='요구와 설계의 입력/출력 차이',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='REQ-025',
        name='예외처리 정의 불일치 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='요구된 예외조건의 설계·시험 반영 누락',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='REQ-026',
        name='사용자·권한 정의 불일치 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='사용자/역할/권한 정의의 문서 간 불일치',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='REQ-027',
        name='요구사항 출처·상위요구 및 추가기능 근거 점검',
        category_code='REQ',
        category='요구사항 정합성',
        description='RFP/계약 등 출처 추적과 근거 없는 추가기능 후보',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='REQ-028',
        name='요구사항 정합성 종합 위험 후보 도출',
        category_code='REQ',
        category='요구사항 정합성',
        description='정합성 결과를 종합해 근거 기반 위험 후보 제시',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='CHG-001',
        name='변경사항 식별 점검',
        category_code='CHG',
        category='변경영향도',
        description='이전/현재 산출물 간 실제 변경 식별',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='CHG-002',
        name='변경이력 누락 점검',
        category_code='CHG',
        category='변경영향도',
        description='실제 변경 대비 변경이력 미기록',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='CHG-003',
        name='변경이력-실제내용 불일치 점검',
        category_code='CHG',
        category='변경영향도',
        description='기록된 변경과 실제 변경의 차이',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='CHG-004',
        name='변경사유 누락·불명확 점검',
        category_code='CHG',
        category='변경영향도',
        description='변경 목적·근거의 부재 또는 모호성',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='CHG-005',
        name='변경 승인상태 점검',
        category_code='CHG',
        category='변경영향도',
        description='미승인 변경의 후속 반영 여부',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='CHG-006',
        name='변경 영향대상 식별',
        category_code='CHG',
        category='변경영향도',
        description='설계·화면·데이터·인터페이스·시험 영향 후보',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='CHG-007',
        name='프로젝트 영향범위 식별',
        category_code='CHG',
        category='변경영향도',
        description='일정/WBS·공수·운영·이해관계자 영향 후보',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='CHG-008',
        name='관련 설계 변경 미반영 점검',
        category_code='CHG',
        category='변경영향도',
        description='영향받는 설계의 미갱신',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='CHG-009',
        name='관련 화면 변경 미반영 점검',
        category_code='CHG',
        category='변경영향도',
        description='영향받는 화면정의의 미갱신',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='CHG-010',
        name='관련 데이터설계 변경 미반영 점검',
        category_code='CHG',
        category='변경영향도',
        description='영향받는 데이터 정의의 미갱신',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='CHG-011',
        name='관련 인터페이스 변경 미반영 점검',
        category_code='CHG',
        category='변경영향도',
        description='영향받는 연계 정의의 미갱신',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='CHG-012',
        name='관련 시험 변경 미반영 점검',
        category_code='CHG',
        category='변경영향도',
        description='시험항목·조건·예상결과의 변경 누락',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='CHG-013',
        name='관련 문서 변경 미반영 점검',
        category_code='CHG',
        category='변경영향도',
        description='운영·사용자 등 관련 문서의 미갱신',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='CHG-014',
        name='삭제 요구사항·기능 잔존 점검',
        category_code='CHG',
        category='변경영향도',
        description='삭제 대상의 설계·화면·시험 잔존',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='CHG-015',
        name='폐기 인터페이스·데이터 정의 잔존 점검',
        category_code='CHG',
        category='변경영향도',
        description='폐기 대상 정의의 문서 잔존',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='CHG-016',
        name='변경 영향범위 누락 후보 도출',
        category_code='CHG',
        category='변경영향도',
        description='선언된 영향범위 밖의 추가 영향 후보',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='CHG-017',
        name='회귀검증 필요성 점검',
        category_code='CHG',
        category='변경영향도',
        description='변경으로 재검증이 필요한 기존 기능·시험 후보',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='CHG-018',
        name='변경영향도 종합 위험 후보 도출',
        category_code='CHG',
        category='변경영향도',
        description='변경·영향·반영 결과를 종합한 위험 후보',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='FP-001',
        name='FP 산정대상 누락 점검',
        category_code='FP',
        category='FP 검증',
        description='요구기능 대비 FP 미산정 대상',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='FP-002',
        name='FP 산정대상 중복 점검',
        category_code='FP',
        category='FP 검증',
        description='동일 기능의 중복 산정',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='FP-003',
        name='FP 산정 제외대상 적정성 점검',
        category_code='FP',
        category='FP 검증',
        description='제외 기능과 제외사유의 적정성',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='FP-004',
        name='애플리케이션 경계 설정 적정성 점검',
        category_code='FP',
        category='FP 검증',
        description='FP 산정 경계와 기능 사용자 관점의 적정성',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='FP-005',
        name='기능유형 분류 적정성 점검',
        category_code='FP',
        category='FP 검증',
        description='EI/EO/EQ/ILF/EIF 분류의 적정성',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='FP-006',
        name='기능 단위 분할·통합 적정성 점검',
        category_code='FP',
        category='FP 검증',
        description='과도한 분할 또는 서로 다른 기능의 부적절한 통합',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='FP-007',
        name='FP 산정방식·적용기준 적정성 점검',
        category_code='FP',
        category='FP 검증',
        description='적용 산정방식과 기준의 적합성',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='FP-008',
        name='상세 산정정보 적정성 점검',
        category_code='FP',
        category='FP 검증',
        description='적용 방식에 따라 필요한 DET/FTR/RET 등 근거정보',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='FP-009',
        name='FP 산정값 재계산 검증',
        category_code='FP',
        category='FP 검증',
        description='입력 근거와 산식에 따른 수치 재계산',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='FP-010',
        name='요구사항-FP 추적성 점검',
        category_code='FP',
        category='FP 검증',
        description='FP 항목과 근거 요구사항 연결',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='FP-011',
        name='FP 변경반영 누락 점검',
        category_code='FP',
        category='FP 검증',
        description='요구 변경에 따른 FP 갱신 누락',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='FP-012',
        name='비기능 요구사항 FP 포함 적정성 점검',
        category_code='FP',
        category='FP 검증',
        description='비기능 요구의 일반 FP 오산정 여부',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AI-001',
        name='AI 적용 목적·범위 정의 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='AI 사용 목적, 대상 업무, 책임범위 명확성',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AI-002',
        name='AI 기능 요구사항 정의 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='입력·출력·처리조건 등 AI 기능 요구사항',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AI-003',
        name='AI 성능·품질 목표 정의 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='평가기준·목표값·허용수준 정의',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AI-004',
        name='AI 모델·서비스 정보 관리 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='모델/서비스명, 버전, 용도 등 관리',
        execution_type='Rule',
    ),
    DocumentRuleCatalogItem(
        code='AI-005',
        name='AI 출력 신뢰성·환각 대응 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='정확성·근거성 검증과 허위/환각 대응',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='AI-006',
        name='AI 출력 일관성 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='동일·유사 입력에 대한 과도한 모순 여부',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='AI-007',
        name='AI 실패·불확실성 처리 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='낮은 확신·실패 상황의 처리 및 안내',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='AI-008',
        name='민감정보 입력·출력 통제 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='개인정보·기밀의 부적절한 입력/노출 방지',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AI-009',
        name='Prompt Injection 대응 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='악의적 지시에 의한 통제 우회 대응',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AI-010',
        name='시스템 프롬프트 보안설계 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='민감정보 포함 및 프롬프트에 대한 보안통제 의존',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AI-011',
        name='AI 권한·자율행위 통제 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='도구·시스템 접근권한과 자율행위 최소화',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AI-012',
        name='AI 출력 후속처리 안전성 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='AI 출력을 검증 없이 명령/API/DB 등에 실행하는 위험',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AI-013',
        name='학습·참조데이터 적정성 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='데이터 출처·품질·적합성 관리',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AI-014',
        name='데이터·모델 오염 위험 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='악성·오류 데이터에 의한 오염 위험',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AI-015',
        name='RAG 검색근거 적정성 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='검색 문서와 실제 답변 근거의 적합성',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='AI-016',
        name='RAG·Embedding 접근통제 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='권한 없는 자료의 검색·노출 위험',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AI-017',
        name='AI 평가·테스트 체계 적정성 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='대표성 있는 평가데이터와 정상/예외/위험 입력 시험',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AI-018',
        name='AI 편향·공정성 위험 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='데이터·사용자 조건별 편향 및 결과 편차 위험',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='AI-019',
        name='Human-in-the-loop 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='중요 판단의 사람 확인·승인 구조',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AI-020',
        name='AI 판단 설명·근거 제공 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='중요한 결과의 근거·설명 제공 가능성',
        execution_type='AI',
    ),
    DocumentRuleCatalogItem(
        code='AI-021',
        name='AI 로그·추적성 및 운영 모니터링 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='입력·모델·조건·결과 추적과 운영 품질/이상 모니터링',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AI-022',
        name='AI 모델·프롬프트 변경관리 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='모델/프롬프트 변경기록 및 재검증',
        execution_type='Hybrid',
    ),
    DocumentRuleCatalogItem(
        code='AI-023',
        name='AI 자원사용·호출 제한 적정성 점검',
        category_code='AI',
        category='AI 특화 검증',
        description='요청·입력·출력·반복호출 등 자원사용 통제',
        execution_type='Rule',
    ),
)


def get_document_rules():
    """제품 전체 105개 문서 검사기준을 반환한다."""
    return DOCUMENT_RULES


def get_document_rules_by_category(category_code):
    """영역 코드에 해당하는 문서 검사기준을 반환한다."""
    return tuple(
        rule
        for rule in DOCUMENT_RULES
        if rule.category_code == category_code
    )


def get_document_rule(code):
    """Rule 코드에 해당하는 검사기준 하나를 반환한다."""
    for rule in DOCUMENT_RULES:
        if rule.code == code:
            return rule
    return None

# === GENERATED DOCUMENT RULE DETAILS END ===
