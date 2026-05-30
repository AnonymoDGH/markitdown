import requests

from markitdown import MarkItDown


def test_response_uses_rfc5987_content_disposition_filename():
    response = requests.Response()
    response.status_code = 200
    response.url = "https://example.com/download"
    response.headers["content-type"] = "application/octet-stream"
    response.headers["content-disposition"] = "attachment; filename*=UTF-8''data.csv"
    response._content = b"Name,Value\nAlice,42\n"
    response._content_consumed = True

    result = MarkItDown().convert(response)

    assert "| Name | Value |" in result.markdown
    assert "| Alice | 42 |" in result.markdown
