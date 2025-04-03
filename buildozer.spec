[app]
title = Weather App
package.name = weatherapp
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0
requirements = python3,kivy==2.2.1,urllib3,requests,android
orientation = portrait
android.permissions = INTERNET
android.api = 33  # Используйте актуальную версию API
android.minapi = 21
android.ndk = 25b
android.sdk = 34
android.arch = armeabi-v7a,arm64-v8a  # Поддержка 32/64 бит
p4a.branch = master  # Используйте стабильную ветку
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 0
