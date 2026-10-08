from PySide6.QtCore import QTimer


def apply_inspection_cancel_state_patch(InspectionPage):
    if getattr(InspectionPage, "_cancel_state_patch_applied", False):
        return

    original_cancelled = InspectionPage._inspection_cancelled

    def patched_cancelled(self):
        # 기존 취소 처리로 검사 준비 화면을 복원한다.
        # selected_files 자체는 유지되므로 데이터를 지우지 않는다.
        original_cancelled(self)

        # 취소 직후 _refresh_file_view()가 기존 row 위젯을 deleteLater()로
        # 정리하는 시점과 겹치면 파일 개수는 남아도 행만 비어 보일 수 있다.
        # 이벤트 루프가 한 번 정리된 뒤 동일 selected_files로 다시 그려
        # 등록 파일 목록을 확실하게 복원한다.
        QTimer.singleShot(50, self._refresh_file_view)

    InspectionPage._inspection_cancelled = patched_cancelled
    InspectionPage._cancel_state_patch_applied = True
