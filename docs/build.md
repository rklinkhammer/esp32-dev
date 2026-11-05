# Build and development

## Environment

`./esp32 doctor` checks Docker connectivity and prints the image pin.
`./esp32 pull` downloads the exact official image. The first download is large;
subsequent commands reuse it. No host ESP-IDF installation is required.

Options precede the command. Arguments following the command pass unchanged to
`idf.py`. Default project is the current directory; `ESP32_PROJECT` or `--project`
selects another. The launcher mounts the project's Git root at the same absolute
path, allowing DMOTOR's shared protocol files outside `software/esp32` to work.
Use `--workspace /path/to/root` to include other adjacent source dependencies.
The workspace is writable because IDF generates sdkconfig and managed components.

```sh
./esp32 --project ../dmotor/software/esp32 shell
# Inside the initialized ESP-IDF shell:
idf.py --version
idf.py menuconfig
idf.py build
exit

# Equivalent direct commands:
./esp32 --project ../dmotor/software/esp32 menuconfig
./esp32 --project ../dmotor/software/esp32 build
./esp32 --project ../dmotor/software/esp32 size
./esp32 --project ../dmotor/software/esp32 idf -B build-debug build
./esp32 --project ../dmotor/software/esp32 idf --list-targets
```

Use the native `idf.py create-project`, `add-dependency`, component manifests,
`dependencies.lock`, sdkconfig.defaults and partition tables in the **firmware
repository**. Commit the dependency lock and intended defaults there. Firmware
build output stays in its normal `build/` directory: application/bootloader BINs,
ELF, map, partition table and flash arguments. IDF's build output is authoritative;
this launcher does not invent another artifact format or rebuild policy.

`IDF_TARGET` defaults to esp32s3. For another chip, use `--target esp32c3`; for an
already configured project, run `--target esp32c3 set-target esp32c3` first.
Native `set-target` resets build configuration; retain intentional settings in
sdkconfig.defaults. Do not use one build directory concurrently from two builds.

Containers run with your numeric UID/GID, with no Linux capabilities or root
entrypoint. Persistent HOME and ccache live in `.cache/<uid>/` in esp32-dev.
Files in the workspace are owned by the caller. The upstream entrypoint activates
ESP-IDF and its Python environment; do not replace it with an uninitialized shell.
`--dry-run` prints the full Docker invocation without running it.

## Flash and monitor (explicit operations)

On a local Linux Docker engine:

```sh
./esp32 --project ../dmotor/software/esp32 --port /dev/ttyACM0 flash monitor
```

Only the selected device is passed through, with its group added to the container.
No privileged container is used. Quit IDF Monitor with Ctrl+]. Re-run after USB
re-enumeration if the port changes. The smoke build does not require hardware.

Docker Desktop on macOS/Windows does not provide this Linux device mapping.
Use Espressif's host `esp_rfc2217_server` and a reachable RFC2217 port instead:

```sh
# Host with Espressif's esptool installed and the board connected:
esp_rfc2217_server -v -p 4000 /dev/cu.usbmodemDEVICE
# Container:
./esp32 --project ../dmotor/software/esp32 \
  --port 'rfc2217://host.docker.internal:4000?ign_set_control' flash
```

Keep the serial service on a trusted network; it provides board control without
authentication. See [Espressif's Docker guide](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32/api-guides/tools/idf-docker-image.html)
for supported serial workflows. A remote Docker context must have the same bind
mount paths and devices on its daemon host; this launcher does not synchronize
remote workspaces. Docker Desktop must permit sharing the workspace and cache.

## Validation and toolchain updates

```sh
python3 -m unittest discover -s tests -v
./esp32 smoke
```

CI runs the launcher tests and compiles the smoke application for ESP32-S3 and
ESP32-C3 to exercise Xtensa and RISC-V toolchains. Hardware flashing, GPIO and
monitor safety behavior are not validated by this build check.

To upgrade IDF, select an official release, inspect its manifest with
`docker buildx imagetools inspect espressif/idf:vX.Y.Z`, and update the single
`config/idf-image.txt` pin (tag plus multi-platform digest). Run tests and both
smoke targets with clean build directories, then rebuild and qualify product
firmware before adopting the toolchain. Never use `latest` or a moving release
branch for release builds. Keep the environment commit/image digest with firmware
release evidence. No global SDK installation or tools from edf-dev are reused.
