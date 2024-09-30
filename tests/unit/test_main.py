"""
Simple FASTAPI App for workshop purposes

Returns:
  None
"""

import warnings


def test_read_main():
    """API version warning"""

    warnings.warn(UserWarning("no api version is specified!"))
    return 1
