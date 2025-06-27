from parser_service.app.parsers.parser import Parser
import docx

class DocxParser(Parser):
    def extract_text(self, file: str) -> str:
        doc = docx.Document(file)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return "\n".join(text)


