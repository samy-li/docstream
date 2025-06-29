from parser_service.app.parsers.parser import Parser


class TxtParser(Parser):
    def extract_text(self, file: str) -> str:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                text = f.read()
                return text
        except FileNotFoundError:
            raise FileNotFoundError