from pathlib import Path

from app.database.repositories.inspection_repository import save_inspection_result
from rules.core.engine import RuleEngine
from rules.definitions.default_rules import get_default_rules


SUPPORTED_TEXT_EXTENSIONS = {
    ".py", ".java", ".js", ".ts", ".yml", ".yaml", ".xml",
    ".json", ".md", ".txt", ".properties", ".sql",
}


class InspectionService:
    def __init__(self, rules=None):
        self.engine = RuleEngine(rules or get_default_rules())

    def validate_files(self, file_paths):
        valid_paths = []
        errors = []

        for raw_path in file_paths:
            path = Path(raw_path)
            if not path.is_file():
                errors.append(f"파일을 찾을 수 없습니다: {path}")
                continue
            if path.suffix.lower() not in SUPPORTED_TEXT_EXTENSIONS:
                errors.append(f"지원하지 않는 파일 형식입니다: {path.name}")
                continue
            valid_paths.append(path)

        return valid_paths, errors

    def run(self, file_paths, project_id=None, inspection_type="전체 검사", cancel_requested=None):
        valid_paths, errors = self.validate_files(file_paths)
        if errors:
            raise ValueError("\n".join(errors))
        if not valid_paths:
            raise ValueError("검사할 파일이 없습니다.")

        summary = self.engine.inspect_files(valid_paths, cancel_requested=cancel_requested)
        inspection_id = None
        if project_id is not None:
            inspection_id = save_inspection_result(
                project_id=project_id,
                summary=summary,
                inspection_type=inspection_type,
            )

        return inspection_id, summary
