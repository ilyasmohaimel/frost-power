# Film credits

The 20-second film combines a new 60 FPS camera render of the existing G513QY model, measured preset data, an existing cutaway illustration, and an isolated full-desktop capture with the actual Battery menu open. Personal reference photographs do not appear in the film.

The model and studio were developed for [Frost GPU](https://github.com/ilyasmohaimel/frost-gpu) and the Hyprland daily-use film. The laptop is an illustration based on the ASUS G513QY, not a factory CAD model. ASUS and ROG marks belong to ASUSTeK. No endorsement is implied.

Music: [Machina](https://www.scottbuckley.com.au/library/machina/) by Scott Buckley, used under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The film uses a trimmed excerpt with level adjustment and fades.

Barlow and Barlow Condensed by Jeremy Tribby, and JetBrains Mono by JetBrains, are included under the SIL Open Font License. License files accompany the fonts. GSAP and HyperFrames retain their upstream licenses. See [third-party notices](../THIRD_PARTY.md).

## Motion

The camera and desktop-menu push-in use the continuous fifth-order easing from the revised Between windows film: `u³ × (10 − 15u + 6u²)`. Position, scale and camera parameters retain fractional precision. Both velocity and acceleration reach zero at the ends of each move. The full film runs at 1920 × 1080, 60 FPS; the README uses a smaller full-length animated preview.

The rendered model assets are included so the composition can be rebuilt without the local Blender scene. To remake the camera footage, provide `FROST_MODEL_FILE` to `production/render-model.py`. The original scene and personal reference files are not bundled.
