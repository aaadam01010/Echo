"""Transparent, frameless, always-on-top desktop companion overlay."""
import sys
import time
import threading
from pathlib import Path

import pygetwindow as gw
from PyQt6.QtCore import QPoint, QPointF, QRectF, Qt
from PyQt6.QtGui import QAction, QBrush, QColor, QGuiApplication, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon, QWidget

from brain import ask_ai, generate_idle_thought
from ears import listen_and_transcribe, should_respond_to
from voice import speak

APP_NAME = "Echo"
SPRITE_PATH = Path(__file__).resolve().parent / "sprite.png" 
FALLBACK_SIZE = 200

def build_fallback_sprite(size: int = FALLBACK_SIZE) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    margin = size * 0.04
    body = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
    p.setPen(QPen(QColor("#e0508f"), max(2, size * 0.02)))
    p.setBrush(QBrush(QColor("#ffb6d5")))
    p.drawEllipse(body)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(QColor(255, 120, 160, 140)))
    cheek_r = size * 0.07
    for cx in (size * 0.25, size * 0.75):
        p.drawEllipse(QPointF(cx, size * 0.60), cheek_r, cheek_r * 0.75)
    p.setBrush(QBrush(QColor("#4a2040")))
    eye_r = size * 0.055
    for cx in (size * 0.35, size * 0.65):
        p.drawEllipse(QPointF(cx, size * 0.42), eye_r, eye_r * 1.3)
    pen = QPen(QColor("#4a2040"), max(3, size * 0.025))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    smile = QRectF(size * 0.32, size * 0.45, size * 0.36, size * 0.28)
    p.drawArc(smile, 200 * 16, 140 * 16)
    p.end()
    return pm

def load_sprite() -> QPixmap:
    # Returns a 1x1 transparent pixmap so the window is invisible but still exists
    pm = QPixmap(1, 1)
    pm.fill(Qt.GlobalColor.transparent)
    return pm

class CompanionWindow(QWidget):
    def __init__(self, sprite: QPixmap):
        super().__init__()
        self._sprite = sprite
        self._drag_offset = QPoint()
        
        self.last_interaction = time.time()
        self.last_response_time = time.time()
        self.response_cooldown = 15 
        self.idle_timeout = 60 

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setFixedSize(self._sprite.deviceIndependentSize().toSize())
        self._move_to_corner()

        threading.Thread(target=self._continuous_listen, daemon=True).start()

    def _move_to_corner(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None: return
        area = screen.availableGeometry()
        self.move(area.right() - self.width() - 40, area.bottom() - self.height() - 40)

    def _continuous_listen(self) -> None:
        while True:
            try:
                text = listen_and_transcribe()
                current_time = time.time()
                
                if text and should_respond_to(text):
                    self.last_interaction = current_time
                    if current_time - self.last_response_time > self.response_cooldown:
                        print(f"🎯 {APP_NAME} heard: {text}")
                        ai_reply = ask_ai(text)
                        if ai_reply:
                            self._handle_reply(ai_reply, current_time)
                elif (current_time - self.last_interaction > self.idle_timeout) and \
                     (current_time - self.last_response_time > self.response_cooldown):
                    print("💭 Initiating conversation...")
                    try:
                        active_window = gw.getActiveWindowTitle() or "Unknown"
                    except:
                        active_window = "Unknown"
                    idle_thought = generate_idle_thought(active_window)
                    if idle_thought:
                        self._handle_reply(idle_thought, current_time)

            except Exception as e:
                print(f"Listener error: {e}")
            time.sleep(1)

    def _handle_reply(self, reply: str, current_time: float) -> None:
        try:
            current_window = gw.getActiveWindowTitle().lower()
            mute_words = ["game", "netflix", "youtube", "vlc", "spotify", "discord", "valorant", "league", "steam", "movie"]
            should_mute = any(word in current_window for word in mute_words)
        except:
            should_mute = False

        if should_mute:
            print(f"🔇 Muted (Window: {current_window})")
        else:
            speak(reply)
        
        self.last_response_time = current_time
        self.last_interaction = current_time

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_V:
            threading.Thread(target=self._process_speech, daemon=True).start()

    def _process_speech(self) -> None:
        user_text = listen_and_transcribe()
        if user_text:
            ai_reply = ask_ai(user_text)
            if ai_reply:
                self._handle_reply(ai_reply, time.time())

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawPixmap(0, 0, self._sprite)
        painter.end()

    def mousePressEvent(self, event) -> None:
        if event.button() != Qt.MouseButton.LeftButton: return
        if QGuiApplication.platformName() == "wayland" and self.windowHandle():
            if self.windowHandle().startSystemMove(): return
        self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, event) -> None:
        self.setCursor(Qt.CursorShape.OpenHandCursor)

def build_tray(app: QApplication, window: CompanionWindow) -> QSystemTrayIcon:
    icon = app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
    tray = QSystemTrayIcon(icon, app)
    tray.setToolTip(APP_NAME)
    menu = QMenu()
    show_action = QAction("Show", menu)
    show_action.triggered.connect(lambda: (window.show(), window.raise_()))
    quit_action = QAction("Quit", menu)
    quit_action.triggered.connect(app.quit)
    menu.addAction(show_action)
    menu.addSeparator()
    menu.addAction(quit_action)
    tray.setContextMenu(menu)
    tray._menu = menu
    tray.show()
    return tray

def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = CompanionWindow(load_sprite())
    window.show()
    speak(f"Hi there! I'm {APP_NAME}. It's so nice to meet you!")
    
    tray = None
    if QSystemTrayIcon.isSystemTrayAvailable():
        tray = build_tray(app, window)
    else:
        print("Warning: no system tray available.")

    code = app.exec()
    if tray: tray.hide()
    return code

if __name__ == "__main__":
    sys.exit(main())