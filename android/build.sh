#!/usr/bin/env bash
# Ekranchi_Bola APK ni Gradle'siz, faqat Android SDK vositalari bilan yig'adi.
# Kerak: ANDROID_HOME (build-tools va platforms o'rnatilgan) va JDK.
set -euo pipefail
cd "$(dirname "$0")"

SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:?ANDROID_HOME berilmagan}}"
BT="$(ls -d "$SDK"/build-tools/* | sort -V | tail -1)"
ANDROID_JAR="$(ls "$SDK"/platforms/android-*/android.jar | sort -V | tail -1)"
MIN_SDK=26
TARGET_SDK=34
VERSION_CODE="${VERSION_CODE:-1}"
VERSION_NAME="${VERSION_NAME:-0.1.$VERSION_CODE}"
echo "build-tools: $BT"; echo "platform: $ANDROID_JAR"

rm -rf build && mkdir -p build/gen build/classes build/dex
"$BT/aapt2" compile --dir res -o build/res.zip
"$BT/aapt2" link -o build/app.unsigned.apk -I "$ANDROID_JAR" --manifest AndroidManifest.xml \
  --min-sdk-version "$MIN_SDK" --target-sdk-version "$TARGET_SDK" \
  --version-code "$VERSION_CODE" --version-name "$VERSION_NAME" --java build/gen build/res.zip

javac -source 8 -target 8 -Xlint:-options -cp "$ANDROID_JAR" -d build/classes \
  $(find src build/gen -name '*.java')
"$BT/d8" --release --min-api "$MIN_SDK" --lib "$ANDROID_JAR" --output build/dex $(find build/classes -name '*.class')
(cd build/dex && zip -q ../app.unsigned.apk classes.dex)
"$BT/zipalign" -f -p 4 build/app.unsigned.apk build/app.aligned.apk

# Imzo: KEYSTORE_B64 berilsa doimiy kalit, bo'lmasa har safar yangi sinov kaliti
KS=build/sign.jks; KS_PASS="${KEYSTORE_PASS:-ekranchi-demo}"; KS_ALIAS="${KEYSTORE_ALIAS:-ekranchi}"
if [ -n "${KEYSTORE_B64:-}" ]; then
  echo "$KEYSTORE_B64" | base64 -d > "$KS"
else
  echo "DIQQAT: sinov kaliti bilan imzolanmoqda (keyingi yig'ilgan APK buning ustiga o'rnatilmaydi)"
  keytool -genkeypair -keystore "$KS" -storepass "$KS_PASS" -keypass "$KS_PASS" -alias "$KS_ALIAS" \
    -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Ekranchi_Bola, C=UZ" >/dev/null 2>&1
fi
"$BT/apksigner" sign --ks "$KS" --ks-pass "pass:$KS_PASS" --ks-key-alias "$KS_ALIAS" --out build/Ekranchi_Bola.apk build/app.aligned.apk
"$BT/apksigner" verify --verbose build/Ekranchi_Bola.apk | head -4
"$BT/aapt2" dump badging build/Ekranchi_Bola.apk | head -4
ls -la build/Ekranchi_Bola.apk
