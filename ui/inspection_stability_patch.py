from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QMessageBox

from app.services.inspection_service import (
    SUPPORTED_DOCUMENT_EXTENSIONS,
    SUPPORTED_TEXT_EXTENSIONS,
)
from ui.inspection_execution_patch import _ProgressIssueAssessor


def _mark_selected_rules_complete(tracker):
    """Mark rule execution complete before post-inspection assessment begins.

    Impact/Likelihood and audit-improvement judgment run only after all selected
    inspection rules have finished. Some Hybrid rules can finish through
    deterministic pre-analysis without calling the AI provider, so the normal
    provider progress hook may never see those rule codes. Completing the set at
    the assessment boundary keeps the displayed completed-rule count accurate.
    """
    tracker.completed_codes.update(tracker._rule_codes)


def _patch_issue_assessor_progress():
    if getattr(_ProgressIssueAssessor, "_stability_progress_patch_applied", False):
        return

    original_assess = _ProgressIssueAssessor.assess
    original_assess_many = _ProgressIssueAssessor.assess_many
    original_judge_audit_many = _ProgressIssueAssessor.judge_audit_many

    def patched_assess(self, issue):
        _mark_selected_rules_complete(self._tracker)
        return original_assess(self, issue)

    def patched_assess_many(self, issues, batch_size=2):
        _mark_selected_rules_complete(self._tracker)
        return original_assess_many(self, issues, batch_size=batch_size)

    def patched_judge_audit_many(self, issues, batch_size=2):
        _mark_selected_rules_complete(self._tracker)
        return original_judge_audit_many(self, issues, batch_size=batch_size)

    _ProgressIssueAssessor.assess = patched_assess
    _ProgressIssueAssessor.assess_many = patched_assess_many
    _ProgressIssueAssessor.judge_audit_many = patched_judge_audit_many
    _ProgressIssueAssessor._stability_progress_patch_applied = True


def apply_inspection_stability_patch(InspectionPage):
    """Apply Windows/Qt stability hardening to the Inspection page."""
    if getattr(InspectionPage, "_stability_patch_applied", False):
        return

    _patch_issue_assessor_progress()

    def select_inspection_files(self):
        document_patterns = " ".join(
            f"*{extension}"
            for extension in sorted(SUPPORTED_DOCUMENT_EXTENSIONS)
        )

        # The native Windows file picker repeatedly raises handled native
        # exceptions under Qt 6.11 on this application and was present in the
        # Qt6Gui crash path of the packaged build. Use Qt's own dialog instead
        # to remove the Windows shell/native-dialog layer from this workflow.
        dialog = QFileDialog(self, "검사 대상 파일 선택")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dialog.setNameFilters(
            [
                f"문서 파일 ({document_patterns})",
                "텍스트/소스 파일 (*.py *.java *.js *.ts *.yml *.yaml *.xml *.json *.md *.txt *.properties *.sql)",
                "모든 지원 파일 (*.*)",
            ]
        )
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)

        if not dialog.exec():
            return

        paths = dialog.selectedFiles()
        if not paths:
            return

        existing = set(self.selected_files)
        unsupported = []
        for path in paths:
            suffix = Path(path).suffix.lower()
            if (
                suffix not in SUPPORTED_TEXT_EXTENSIONS
                and suffix not in SUPPORTED_DOCUMENT_EXTENSIONS
            ):
                unsupported.append(Path(path).name)
                continue
            if path not in existing:
                self.selected_files.append(path)
                existing.add(path)

        self._refresh_file_view()

        if unsupported:
            names = "\n".join(f"• {name}" for name in unsupported[:8])
            more = f"\n외 {len(unsupported) - 8}개" if len(unsupported) > 8 else ""
            warning = QMessageBox(self)
            warning.setIcon(QMessageBox.Warning)
            warning.setWindowTitle("지원하지 않는 파일 형식")
            warning.setText("지원하지 않는 파일은 등록에서 제외했습니다.")
            warning.setInformativeText(
                f"{names}{more}\n\n"
                "지원 형식: 문서 Parser 지원 형식 및 기존 텍스트/소스 파일"
            )
            warning.setStandardButtons(QMessageBox.Ok)
            warning.setStyleSheet(
                "QLabel { font-size: 12px; }"
                "QLabel#qt_msgbox_label { font-size: 13px; font-weight: 700; }"
                "QPushButton { min-width: 72px; min-height: 28px; font-size: 11px; font-weight: 600; }"
            )
            warning.exec()

    InspectionPage.select_inspection_files = select_inspection_files
    InspectionPage._stability_patch_applied = True
