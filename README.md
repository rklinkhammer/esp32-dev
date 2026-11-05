# esp32-dev

Docker-based ESP32 development using Espressif's native ESP-IDF tools.
Like [edf-dev](https://github.com/rklinkhammer/edf-dev), this repository provides
one command entry point, pinned tooling, persistent caches and build documentation.
Here the build system is **ESP-IDF CMake/Ninja and `idf.py`**, with the official
Espressif container and Component Manager. No Yocto, Arduino or PlatformIO layer.

- [Build guide](docs/build.md): setup, native commands, serial access and updates.
- [DMOTOR](https://github.com/rklinkhammer/dmotor): product firmware belongs in
  `software/esp32/` there, not in this environment repository.

Requires Docker Engine/Desktop (Linux containers), Git and Python 3.9+ on a
Linux/macOS host (or WSL2). ESP-IDF **v6.1** is pinned by multi-platform image digest
in `config/idf-image.txt`; Docker selects native amd64 or arm64. ESP32-S3 is the
default chip, selected with `--target` or `ESP32_TARGET`.

```sh
git clone https://github.com/rklinkhammer/esp32-dev.git
cd esp32-dev
./esp32 pull
./esp32 smoke
./esp32 --project ../dmotor/software/esp32 shell
# Once dmotor contains an ESP-IDF CMake project:
./esp32 --project ../dmotor/software/esp32 build
```

The included smoke application only checks the toolchain; it is not monitor
firmware. DMOTOR's monitor application is still planned. Builds never flash a
board automatically. This repository uses the upstream image directly: no
custom Dockerfile or second toolchain installation is needed.
