# Minimal imghdr replacement for Python 3.13+
# Just enough for python-telegram-bot to work.

def what(file, h=None):
    """Rudimentary image type detector: returns 'png', 'jpeg', 'gif', 'webp' or None."""
    if h is None:
        # file can be a path or a file-like object
        if hasattr(file, "read"):
            pos = file.tell()
            h = file.read(32)
            file.seek(pos)
        else:
            with open(file, "rb") as f:
                h = f.read(32)

    # PNG
    if h.startswith(b"\211PNG\r\n\032\n"):
        return "png"

    # JPEG
    if h[0:3] == b"\xff\xd8\xff":
        return "jpeg"

    # GIF
    if h[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"

    # WEBP
    if h[:4] == b"RIFF" and h[8:12] == b"WEBP":
        return "webp"

    # Unknown type
    return None
