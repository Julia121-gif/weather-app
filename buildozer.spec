[app]
title = Weather App
package.name = weatherapp
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0
requirements = python3,kivy==2.0.0,urllib3,sdl2_ttf==2.0.15
orientation = portrait
android.permissions = INTERNET
android.api = 30
android.minapi = 21
android.ndk = 25b
android.copy_libs = 1
android.arch = armeabi-v7a
p4a.branch = develop
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 0