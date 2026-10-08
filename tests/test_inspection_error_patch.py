from ui.inspection_error_patch import format_inspection_error


def test_format_inspection_error_includes_type_and_message():
    message = format_inspection_error(ValueError("잘못된 입력"))

    assert "오류 유형: ValueError" in message
    assert "상세 내용: 잘못된 입력" in message


def test_format_inspection_error_never_returns_blank_detail():
    message = format_inspection_error(AssertionError())

    assert "오류 유형: AssertionError" in message
    assert "상세 오류 메시지가 제공되지 않았습니다." in message
