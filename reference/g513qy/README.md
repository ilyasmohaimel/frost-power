# G513QY integration map

These files document the installed system. There is no unattended installer. Reading or running the offline tests does not apply tuning.

| Repository path | Installed destination |
| --- | --- |
| `src/frost-thermal-tuning` | `/usr/local/libexec/frost-thermal-tuning` |
| `src/frost_cpu_power.py` | `/usr/local/libexec/frost_cpu_power.py` |
| `src/frost_rx_efficiency.py` | `/usr/local/libexec/frost_rx_efficiency.py` |
| `src/frost-thermal-reset`, `src/frost-thermal-enable` | Matching paths under `/usr/local/libexec/` |
| `config/g513qy.json` | `/etc/frost-thermal-tuning.json` |
| `config/frost-thermal-tuning.service` | `/etc/systemd/system/frost-thermal-tuning.service` |
| `integration/hyprland/gpu.py`, `power.py` | `~/.local/libexec/frost-hyprland/` |
| `integration/hyprland/frost-*` launchers | Matching files under `~/.local/bin/` |
| `integration/hyprland/frost_usb_charge.py` | `~/.local/libexec/frost_usb_charge.py` |
| `AsusPower.qml` | `~/.config/quickshell/caelestia/services/AsusPower.qml` |
| `Battery.qml`, `Wrapper.qml`, `FrostGpu.qml` | Caelestia `modules/bar/popouts/` overrides |
| Reference `frost-gpu-power`, `frost_power.py` | Existing matching `/usr/local/libexec/` dependencies |

Caelestia files are overrides for the installed upstream shell, not a replacement shell. Preserve its imports, configuration and license. The full desktop configuration is in [dotfiles-linux](https://github.com/ilyasmohaimel/dotfiles-linux).

## Dependencies and assumptions

- ASUS ROG G513QY, Ryzen 9 5900HX, AMD Vega iGPU and RX 6800M.
- RX PCI `0000:03:00.0`, iGPU PCI `0000:07:00.0`, internal output `eDP-1`.
- asusd owns the ASUS platform profile; power-profiles-daemon is not another owner.
- Root-owned RyzenAdj at `/usr/local/lib/frost-thermal/ryzenadj`, built from [revision 5775fc3](https://github.com/FlyGoat/RyzenAdj/tree/5775fc3e6dbb25c7030ee2d100a1bdd6e8bf2d0a). No binary or upstream source is vendored.
- The existing AMD driver Overdrive voltage interface, verified on this device after reboot. The earlier preparation enabled only its feature bit 0x4000 and retained a separate recovery kernel/initramfs. This repo does not silently alter kernel options.
- The original fan-restore helper under `/var/lib/frost-thermal-recovery/20261025-before-thermal-tuning/restore-test-fans`, produced by the machine's recovery preparation.
- Existing Frost GPU root policy units, charger detection and session wiring. The root integration currently assumes UID 1000; it must be reviewed for another account.
- Hyprland with the tested Lua `hl.monitor` interface, Caelestia/Quickshell, the user activation environment and an ASUS authorization agent.

The thermal service runs as root. It needs the SMU access used by the tested RyzenAdj build. Its hardware/configuration guards reject unsupported models and settings. The preset helper runs as the desktop user and asks the existing ASUS service to choose a profile.

Before adapting, follow [recovery](../../docs/recovery.md) and [porting](../../docs/porting.md). The reference reset helper depends on the original backup, which is not part of this public repo.
