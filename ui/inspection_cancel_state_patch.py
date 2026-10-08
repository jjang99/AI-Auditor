def apply_inspection_cancel_state_patch(InspectionPage):
    if getattr(InspectionPage, "_cancel_state_patch_applied", False):
        return

    def patched_cancelled(self):
        # 취소 시 등록 파일/프로젝트/검사기준은 그대로 유지한다.
        # 파일 목록을 다시 그리면 QScrollArea 내부 위젯 deleteLater()와 충돌해
        # 행이 비어 보일 수 있으므로 화면 재구성은 하지 않는다.
        self.progress_card.hide()
        self.complete_card.hide()
        self.summary_card.show()
        self._inspection_thread = None
        self._inspection_worker = None

        if hasattr(self, "_execution_progress_timer"):
            self._execution_progress_timer.stop()
        self._inspection_started_at = None

        button = self.progress_card.findChild(
            __import__("PySide6.QtWidgets", fromlist=["QPushButton"]).QPushButton,
            "inspectionCancelButton",
        )
        if button is not None:
            button.setEnabled(True)
            button.setText("검사 취소")

    InspectionPage._inspection_cancelled = patched_cancelled
    InspectionPage._cancel_state_patch_applied = True
