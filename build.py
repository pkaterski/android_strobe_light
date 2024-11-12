import subprocess
import time
import pathlib
import os

ANDROID_SDK_PATH = os.getenv("ANDROID_SDK_PATH")
ANDROID_BUILD_TOOL_PATH = ANDROID_SDK_PATH + "/build-tools/34.0.0"
ANDROID_PLATFORM_PATH = ANDROID_SDK_PATH + "/platforms/android-34"

def do_command(c):
    start_time = time.time()
    subprocess.check_output(c)
    end_time = time.time()
    print(f"Command {c} took {end_time - start_time} secs")

if not pathlib.Path("build").exists():
    pathlib.Path("build").mkdir()

if not pathlib.Path("build/java").exists():
    pathlib.Path("build/java").mkdir()

# generate resource file R.java
do_command([
    ANDROID_BUILD_TOOL_PATH + "/aapt",
    "package", "-f", "-m",
    "-S", "resources",
    "-J", "build/java",
    "-M", "src/AndroidManifest.xml",
    "-I", ANDROID_PLATFORM_PATH + "/android.jar",
])

# compile java classes
do_command([
    "javac",
    "--release", "8",
    "-d", "build/obj",
    "-classpath", ANDROID_PLATFORM_PATH + "/android.jar",
    "src/java/com/parkat/strobelight/StartActivity.java",
    "build/java/com/parkat/strobelight/R.java",
])

# dexing java bytecode
do_command([
    ANDROID_BUILD_TOOL_PATH + "/d8",
    "--output", "build/",
    "--classpath", ANDROID_PLATFORM_PATH + "/android.jar",
    # TODO: automatic detection of class files
    "build/obj/com/parkat/strobelight/R$layout.class",
    "build/obj/com/parkat/strobelight/R$attr.class",
    "build/obj/com/parkat/strobelight/R$string.class",
    "build/obj/com/parkat/strobelight/R.class",
    "build/obj/com/parkat/strobelight/StartActivity.class",
])

if pathlib.Path("build/strobelight.unsigned.apk").exists():
    pathlib.Path("build/strobelight.unsigned.apk").unlink()

# generating apk
do_command([
    ANDROID_BUILD_TOOL_PATH + "/aapt",
    "package", "-f",
    "-M", "src/AndroidManifest.xml",
    "-S", "resources",
    "-I", ANDROID_PLATFORM_PATH + "/android.jar",
    "-F", "build/strobelight.unsigned.apk",
    "build"
])

if pathlib.Path("build/strobelight.apk").exists():
    pathlib.Path("build/strobelight.apk").unlink()

# align the apk
do_command([
    ANDROID_BUILD_TOOL_PATH + "/zipalign",
    "-v", "4",
    "build/strobelight.unsigned.apk",
    "build/strobelight.apk",
])

if not pathlib.Path("build/key.keystore").exists():
    do_command([
        "keytool", "-genkeypair",
        "-validity", "1000",
        "-dname", "CN=parkat,O=Android,C=ES",
        "-keystore", "build/key.keystore",
        "-storepass", "password",
        "-keypass", "password",
        "-alias", "strobelightKey",
        "-keyalg", "RSA",
    ])

# sign the apk
do_command([
    ANDROID_BUILD_TOOL_PATH + "/apksigner",
    "sign",
    "--key-pass", "pass:password",
    "--ks-pass", "pass:password",
    "--ks", "build/key.keystore",
    "build/strobelight.apk"
])
