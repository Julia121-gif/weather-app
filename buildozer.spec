[app]
title = Weather App
package.name = weatherapp
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0
requirements = python3,kivy==2.2.1,urllib3,requests,android
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = armeabi-v7a,arm64-v8a
android.no_ndk_build = False
p4a.branch = master
p4a.bootstrap = sdl2
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 0
