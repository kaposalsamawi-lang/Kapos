# نظام إدارة الكميات - نسخة Android

هذه النسخة تعيد بناء النظام كـ Android APK باستخدام Kivy + SQLite.

## المميزات
- تسجيل الدخول: admin / 1234
- لوحة تحكم
- وارد ومصروف ورصيد
- الجهات
- البحث والاستعلام
- التقارير CSV وTXT
- نسخة احتياطية SQLite
- المستخدمون والصلاحيات
- قاعدة البيانات محفوظة داخل مساحة التطبيق

## بناء APK

يفضل تنفيذ البناء على Linux أو WSL2.

1. ثبّت Buildozer:
   python3 -m pip install --upgrade buildozer cython

2. من داخل مجلد المشروع:
   buildozer android debug

3. بعد اكتمال البناء ستجد ملف APK داخل مجلد:
   bin/

لنسخة إصدار:
   buildozer android release

ملاحظة:
النسخة الحالية هي مشروع APK جاهز للبناء، وليست APK مبنيًا مسبقًا؛ بناء APK يحتاج Android SDK/NDK وبيئة بناء Android.
