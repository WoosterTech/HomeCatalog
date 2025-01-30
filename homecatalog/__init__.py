try:
    from icecream import ic  # type: ignore[import-untyped]
except ImportError:

    def ic(*a):
        return None if not a else (a[0] if len(a) == 1 else a)
