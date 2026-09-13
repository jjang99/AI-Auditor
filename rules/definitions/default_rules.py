from rules.core.models import Rule


DEFAULT_RULES = [
    Rule(
        code="SEC-001",
        name="하드코딩된 비밀번호 의심",
        category="보안 취약점",
        severity="High",
        description="소스에 비밀번호 또는 비밀값이 직접 작성되어 있는지 확인합니다.",
        pattern=r"(password|passwd|pwd|secret)\s*[:=]\s*[\"'][^\"']+[\"']",
        file_extensions=(".py", ".java", ".js", ".ts", ".yml", ".yaml", ".properties"),
        recommendation="비밀값은 환경변수 또는 별도의 안전한 비밀정보 저장소에서 관리하세요.",
    ),
    Rule(
        code="SEC-002",
        name="SQL 문자열 직접 조합 의심",
        category="보안 취약점",
        severity="High",
        description="SQL 문에 사용자 입력이 문자열 연결 방식으로 포함될 가능성을 확인합니다.",
        pattern=r"(select|insert|update|delete).*(\+|format\(|f[\"'])",
        file_extensions=(".py", ".java", ".js", ".ts"),
        recommendation="Prepared Statement 또는 파라미터 바인딩을 사용하세요.",
    ),
    Rule(
        code="QUAL-001",
        name="TODO/FIXME 잔존",
        category="코드 품질",
        severity="Low",
        description="완료되지 않은 작업 표시가 운영 대상 소스에 남아 있는지 확인합니다.",
        pattern=r"\b(TODO|FIXME)\b",
        recommendation="배포 전에 잔여 작업을 처리하거나 공식 이슈로 추적하세요.",
    ),
    Rule(
        code="QUAL-002",
        name="디버그 출력 잔존",
        category="코드 품질",
        severity="Medium",
        description="임시 디버그 출력 코드가 남아 있는지 확인합니다.",
        pattern=r"\b(print\s*\(|console\.log\s*\(|System\.out\.print)",
        file_extensions=(".py", ".java", ".js", ".ts"),
        recommendation="운영 코드에서는 표준 로깅 체계를 사용하고 불필요한 디버그 출력을 제거하세요.",
    ),
    Rule(
        code="PERF-001",
        name="무한 반복문 의심",
        category="성능 및 효율성",
        severity="Medium",
        description="종료 조건이 명확하지 않은 반복문 패턴을 확인합니다.",
        pattern=r"\bwhile\s*\(?(true|1)\)?\s*:?",
        file_extensions=(".py", ".java", ".js", ".ts"),
        recommendation="명시적인 종료 조건 또는 안전한 중단 조건이 있는지 검토하세요.",
    ),
]


def get_default_rules() -> list[Rule]:
    return list(DEFAULT_RULES)
