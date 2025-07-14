import magic

def detect_file_type(file_path: str) -> tuple[str, str]:
    ext = file_path.lower().split('.')[-1]
    mime = magic.from_file(file_path, mime=True)
    return ext, mime
