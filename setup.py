"""
YYS-SQR Watermarking System Setup
macOS Application Bundle Configuration
"""

from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'excludes': ['sitecustomize'],
    'includes': ['PyQt6', 'web3', 'trustmark', 'requests', 'boto3', 'cv2'],
    'iconfile': None,
    'plist': {
        'CFBundleName': 'YYS-SQR',
        'CFBundleDisplayName': 'YYS-SQR Watermarking System',
        'CFBundleIdentifier': 'com.yys.sqr',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
    }
}

setup(
    name='YYS-SQR',
    version='1.0.0',
    description='Advanced watermarking system with computer vision and blockchain integration',
    author='YYS Team',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'PyQt6>=6.9.1',
        'opencv-python>=4.11.0',
        'pillow>=11.2.1',
        'numpy>=1.26.4',
        'trustmark>=0.8.0',
        'web3>=7.12.0',
        'boto3>=1.38.46',
        'requests>=2.32.4',
    ],
)