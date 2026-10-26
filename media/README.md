# Frost Power film

[Watch the film](frost-power.mp4). The full render is 20 seconds at 1920×1080 and 60 FPS, with music. The README preview loops the entire film at a smaller size without audio.

The motion follows the revised Between windows film: fractional transforms, smooth camera acceleration and deceleration, and readable holds. The laptop push is a real Blender camera move. The cutaway and Battery pullback use the same fifth-order easing in the composition.

## Rebuild the film

Node.js 22 or newer, npm and FFmpeg are required by the pinned HyperFrames release. A Chromium runtime may be downloaded on first use. From this directory:

```sh
cd composition
npm ci
npm run check
npm run preview
npm run render
```

The last command writes `../frost-power.render.mp4`. Inspect it before replacing the published film. The model footage, menu capture, fonts and music excerpt are bundled, so the composition does not need the original scene or a live desktop.

The Blender recipe in `production/render-model.py` accepts an existing matching studio scene through `FROST_MODEL_FILE`. It expects the model's named screen object and materials. It renders 240 frames at 60 FPS; encode them as `composition/assets/model-intro.mp4`. `production/make-figures.py` uses Matplotlib to rebuild the README chart and original measurement display from the saved data.

The Battery picture is a direct isolated capture of the installed menu. It is not a mock-up or a demonstration of live GPU migration. [Credits and motion details](CREDITS.md), [design](design.md), [storyboard](brag-plan.md).

## Validation

The composition passed static, runtime, layout and motion checks, with all 59 sampled text contrast checks passing. Settled and moving frames were inspected before the full render. Media metadata and decoding were checked after export. These are film checks, separate from the hardware tests documented in the repository.
