# Credits and license map

Original Frost controller code, tools, documentation and authored composition code are GPL-2.0-only, with the license in the root LICENSE. Copyright 2026 Ilyas Mohaimel. Numeric measurement records describe the experiments in docs/results.md.

## Desktop integration

`integration/caelestia/Battery.qml` and `Wrapper.qml` derive from [Caelestia Shell](https://github.com/caelestia-dots/shell), copyright its contributors, under its upstream [GPL-3.0 license](https://github.com/caelestia-dots/shell/blob/main/LICENSE). The local changes preserve that license. Its text is in LICENSES/Caelestia-GPL-3.0.txt. These are separate shell overrides; they are not relicensed under the controller's GPL-2.0-only license.

The custom AsusPower and FrostGpu components implement local controls. The complete shell and its design system remain external dependencies. The full desktop credit belongs to Caelestia, Hyprland, Quickshell and their contributors.

The reference charger/GPU policy and G513QY model work come from [Frost GPU](https://github.com/ilyasmohaimel/frost-gpu). The newer studio was developed for [dotfiles-linux](https://github.com/ilyasmohaimel/dotfiles-linux).

## Hardware tooling

- [RyzenAdj](https://github.com/FlyGoat/RyzenAdj), tested source revision 5775fc3e6dbb25c7030ee2d100a1bdd6e8bf2d0a. The binary and upstream source are not included.
- [asusctl / asusd](https://github.com/OpenGamingCollective/asusctl), AMDGPU, Mesa/RADV, Linux, sysbench, stress-ng and vkmark remain external tools.
- No BIOS, VBIOS, firmware image or vendor binary is distributed.

## Film and artwork

The film uses the existing G513QY model and architectural studio, an internal cutaway illustration, original charts and a direct isolated capture of the Caelestia Battery menu. Personal photographs were modeling references, not film shots. Raw desktop conversations and reference downloads are not included.

ASUS reference imagery supplies keyboard legends and deck materials in the original model. ASUS retains its image copyrights and trademarks. ROG, Ryzen and Radeon names identify the hardware; this is an independent project. The cutaway is an illustration, not an engineering scan or proof of physical chip placement.

Barlow and JetBrains Mono retain their SIL Open Font Licenses, included beside the local fonts. The soundtrack is an edited excerpt of [Machina by Scott Buckley](https://www.scottbuckley.com.au/library/machina/), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Keep that attribution when sharing the film.

The composition uses [HyperFrames](https://github.com/heygen-com/hyperframes) and GSAP, with their own package licenses. The [/brag workflow](https://github.com/latent-spaces/brag) supplied planning and validation guidance. No tooling license is replaced by this repository's license.
