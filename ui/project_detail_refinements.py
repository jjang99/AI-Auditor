import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QFrame,
    QLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


# Runtime historically resets the issue status label to 38px.  Keeping a
# 50px fixed column preserves the same right edge,