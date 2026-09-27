[app]

# (str) Title of your application
title = نظام إدارة الكميات

# (str) Package name
package.name = quantitymanager

# (str) Package domain (needed for android/ios packaging)
package.domain = org.qaboos

# (str) Source code where main.py live
source.dir = .

# (str) Main Python file
source.main = main.py

# (str) Application version
version = 1.0

# (str) Python source extension
source.include_exts = py,kv,png,jpg,jpeg,atlas,txt

# (list) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to start on boot
services =

# (str) Supported Python version
requirements = python3,kivy

# (str) Custom source folders for requirements
# requirements.source.kivy = ../../kivy

# (str) Icon of the application
# icon.filename = %(source.dir)s/icon.png

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/presplash.png

# (str) Supported architectures
android.archs = arm64-v8a, armeabi-v7a

# (bool) Indicate if the application should be fullscreen
fullscreen = 0

# (list) List of Java classes to include
# android.add_src =

# (str) Android entry point, default is org.kivy.android.PythonActivity
# android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme, default is used
# android.apptheme =

# (str) Android SDK version
android.api = 35

# (str) Android NDK version
# android.ndk = 28b

# (int) Android NDK API to use
# android.ndk_api = 23

# (bool) Copy library to arm
# android.copy_libs = 1

# (str) Android app permissions
android.permissions =

# (bool) AndroidX support
android.enable_androidx = 1

# (str) Python-for-Android branch to use
# p4a.branch = master

# (str) python-for-android URL to use
# p4a.url =

# (str) Android release artifact
# android.release_artifact = aab

# (str) Android debug artifact
# android.debug_artifact = apk

[buildozer]

# (int) log level
log_level = 2

# (int) warn if buildozer is run as root
warn_on_root = 1
