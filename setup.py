from setuptools import setup
import sys
sys.setrecursionlimit(5000)

APP = ['jigglypuff.py']
OPTIONS = {
    'argv_emulation': False,
    'packages': ['customtkinter', 'pyautogui'],
    'includes': ['tkinter'],
    'iconfile': None,
    'plist': {
        'CFBundleName': 'JigglyPuff',
        'CFBundleDisplayName': 'JigglyPuff',
        'CFBundleVersion': '2.0.0',
        'NSAccessibilityUsageDescription': 'JigglyPuff requires Accessibility access to move the mouse and simulate keypresses.',
    },
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
