import csv
import io
from typing import BinaryIO, Any
from charset_normalizer import from_bytes
from .._base_converter import DocumentConverter, DocumentConverterResult
from .._stream_info import StreamInfo

ACCEPTED_MIME_TYPE_PREFIXES = [
    "text/csv",
    "text/tab-separated-values",
    "application/csv",
]
ACCEPTED_FILE_EXTENSIONS = [".csv", ".tsv"]


class CsvConverter(DocumentConverter):
    """
    Converts CSV files to Markdown tables.
    """

    def __init__(self):
        super().__init__()

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> bool:
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()
        if extension in ACCEPTED_FILE_EXTENSIONS:
            return True
        for prefix in ACCEPTED_MIME_TYPE_PREFIXES:
            if mimetype.startswith(prefix):
                return True
        return False

    def convert(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        content = self._decode(file_stream, stream_info)
        reader = csv.reader(
            io.StringIO(content), dialect=self._dialect(content, stream_info)
        )
        rows = list(reader)

        if not rows:
            return DocumentConverterResult(markdown="")

        width = max(len(row) for row in rows)
        rows = [self._normalize_row(row, width) for row in rows]

        markdown_table = [
            "| " + " | ".join(self._markdown_cell(cell) for cell in rows[0]) + " |",
            "| " + " | ".join(["---"] * width) + " |",
        ]

        for row in rows[1:]:
            markdown_table.append(
                "| " + " | ".join(self._markdown_cell(cell) for cell in row) + " |"
            )

        return DocumentConverterResult(markdown="\n".join(markdown_table))

    def _decode(self, file_stream: BinaryIO, stream_info: StreamInfo) -> str:
        data = file_stream.read()
        if stream_info.charset:
            return data.decode(stream_info.charset)

        match = from_bytes(data).best()
        if match is None:
            return data.decode("utf-8", errors="replace")
        return str(match)

    def _dialect(self, content: str, stream_info: StreamInfo) -> csv.Dialect:
        if (stream_info.extension or "").lower() == ".tsv":
            return csv.excel_tab

        sample = content[:4096]
        try:
            return csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except csv.Error:
            return csv.excel

    def _normalize_row(self, row: list[str], width: int) -> list[str]:
        if len(row) < width:
            return row + [""] * (width - len(row))
        return row

    def _markdown_cell(self, value: str) -> str:
        return value.replace("|", r"\|").replace("\r\n", "<br>").replace("\n", "<br>")
