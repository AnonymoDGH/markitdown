from email import policy
from email.parser import BytesParser
from email.message import Message
from typing import Any, BinaryIO

from ._html_converter import HtmlConverter
from .._base_converter import DocumentConverter, DocumentConverterResult
from .._stream_info import StreamInfo


ACCEPTED_MIME_TYPE_PREFIXES = [
    "message/rfc822",
    "application/eml",
]

ACCEPTED_FILE_EXTENSIONS = [".eml"]


class EmlConverter(DocumentConverter):
    """Converts RFC 822 .eml messages to Markdown."""

    def __init__(self):
        super().__init__()
        self._html_converter = HtmlConverter()

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> bool:
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()

        if extension in ACCEPTED_FILE_EXTENSIONS:
            return True

        return any(
            mimetype.startswith(prefix) for prefix in ACCEPTED_MIME_TYPE_PREFIXES
        )

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> DocumentConverterResult:
        message = BytesParser(policy=policy.default).parse(file_stream)
        subject = self._header(message, "subject")

        markdown = ["# Email Message", ""]
        for key in ["from", "to", "cc", "bcc", "date", "subject"]:
            value = self._header(message, key)
            if value:
                markdown.append(f"**{key.title()}:** {value}")

        body = self._body_markdown(message, **kwargs)
        if body:
            markdown.extend(["", "## Content", "", body.strip()])

        attachments = self._attachment_names(message)
        if attachments:
            markdown.extend(["", "## Attachments", ""])
            markdown.extend(f"- {name}" for name in attachments)

        return DocumentConverterResult(
            markdown="\n".join(markdown).strip(), title=subject
        )

    def _header(self, message: Message, key: str) -> str | None:
        value = message.get(key)
        return str(value).strip() if value else None

    def _body_markdown(self, message: Message, **kwargs: Any) -> str | None:
        plain_parts: list[str] = []
        html_parts: list[str] = []

        for part in message.walk():
            if part.is_multipart() or self._is_attachment(part):
                continue

            content_type = part.get_content_type()
            try:
                content = part.get_content()
            except Exception:
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                charset = part.get_content_charset() or "utf-8"
                content = payload.decode(charset, errors="replace")

            if content_type == "text/plain":
                plain_parts.append(str(content))
            elif content_type == "text/html":
                html_parts.append(str(content))

        if plain_parts:
            return "\n\n".join(plain_parts)

        if html_parts:
            html = "\n".join(html_parts)
            return self._html_converter.convert_string(html, **kwargs).markdown

        return None

    def _attachment_names(self, message: Message) -> list[str]:
        names = []
        for part in message.walk():
            if self._is_attachment(part):
                filename = part.get_filename()
                names.append(filename or "attachment")
        return names

    def _is_attachment(self, message: Message) -> bool:
        return message.get_content_disposition() == "attachment"
