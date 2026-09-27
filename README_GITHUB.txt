# نظام إدارة الكميات — APK عبر GitHub Actions

هذه الحزمة مجهزة للبناء السحابي: لا تحتاج إلى كمبيوتر أو Android Studio على جهازك.
GitHub Actions سيشغل Buildozer على خادم Linux ويبني APK ثم يحفظه كـ Artifact.

## الملفات المهمة
- main.py — التطبيق
- buildozer.spec — إعدادات Android
- .github/workflows/build.yml — أمر البناء السحابي

## من الجوال
1. افتح GitHub وسجل الدخول إلى حسابك.
2. أنشئ Repository جديدًا، ويمكن جعله Private.
3. ارفع محتويات هذه الحزمة إلى المستودع، وليس ملف ZIP نفسه.
   يجب أن يظهر في المستودع:
   main.py
   buildozer.spec
   .github/workflows/build.yml
4. افتح تبويب Actions.
5. اختر "Build Android APK".
6. اضغط "Run workflow" إذا لم يبدأ البناء تلقائيًا.
7. انتظر حتى يكتمل البناء.
8. افتح نتيجة التشغيل الناجحة ثم قسم Artifacts.
9. حمّل "نظام-إدارة-الكميات-APK" واستخرج ملف APK.

## بيانات الدخول
admin
1234

## ملاحظة
أول بناء قد يستغرق وقتًا لأن بيئة Android وملفات البناء يتم تجهيزها على الخادم.
