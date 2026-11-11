import unicodedata


def normalizar(texto):
    """Pasa a minúsculas y quita tildes: 'Cóctel Ñuble' -> 'coctel nuble'."""
    texto = unicodedata.normalize('NFKD', texto or '')
    sin_tildes = ''.join(c for c in texto if not unicodedata.combining(c))
    return sin_tildes.lower().strip()