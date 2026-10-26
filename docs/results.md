# Measurements and decisions

All values below come from the selected JSON under [data](../data/). Measurements were collected on October 25 and 26, 2026. Cooler use, charger source, session GPU and the baseline are part of each result.

## October 26: Balanced and Eco

The reference was tuned Performance in an iGPU Hyprland session: CPU curve request −5, 90°C target, native Performance power limits and boost enabled. The machine was on barrel power and a laptop cooler. CPU voltage was not measured directly.

| Candidate | Single-thread loss | Multi-thread prime loss | Matrix loss | Matrix socket power | Matrix mean CPU |
| --- | ---: | ---: | ---: | ---: | ---: |
| Balanced 38 W | 0.14% | 9.66% | 19.67% | 37.98 W | 68.44°C |
| Eco 20 W, boost off | 29.61% | 32.85% | 46.94% | 20.00 W | 57.77°C |

Prime tests used sysbench, 12 seconds per run, with one and sixteen threads. Candidate matrix tests used 16 verified stress-ng workers for 45 seconds. CPU temperature and cached RX state were sampled every 0.2 seconds; SMU power was sampled every 0.5 seconds during the middle of the matrix run.

The sweep compared Balanced at 30, 35, 38 and 40 W, and Eco at 20, 18 and 15 W. 30 W lost about 28% in the matrix test. 35 W lost about 22%. 38 W and 40 W were close in throughput, so 38 W was chosen. 18 W Eco lost about 58%; 15 W about 67%. Both missed the requested 30–50% CPU loss range.

These are individual runs rather than a repeated randomized experiment. They establish useful settings for this machine, with ordinary run variance. They do not establish a universal percentage for all applications.

## Repeat with the installed service

The final run waited for firmware profile settings to settle before starting each phase. Each preset had a 60-second verified matrix test; Balanced and Eco also had 120 seconds of verified CPU stress across the selected all-method routine.

| Preset | Matrix score, operations/s | Loss | CPU socket power | Mean / peak CPU |
| --- | ---: | ---: | ---: | ---: |
| Performance | 10032.27 | baseline | 73.06 W | 89.76 / 90.38°C |
| Balanced | 8122.26 | 19.04% | 38.01 W | 70.79 / 72.25°C |
| Eco | 5696.66 | 43.22% | 20.02 W | 57.47 / 58.38°C |

In the separate 120-second CPU routines, Balanced averaged 72.74°C and peaked at 86.12°C. Eco averaged 58.84°C and peaked at 64.12°C. Short boost behavior is not bounded by the same sustained power number.

The RX was suspended at every sampled point in the CPU workloads. A final 30-second idle observation confirmed `suspended` plus `D3cold` with Balanced active.

### Integrated graphics

Each preset ran native Wayland vkmark on RADV RENOIR at 1920×1080, immediate presentation, with four six-second scenes:

| Preset | Vertex | Texture | Phong | Blur |
| --- | ---: | ---: | ---: | ---: |
| Performance | 2560 FPS | 2114 FPS | 1991 FPS | 729 FPS |
| Balanced | 2730 FPS | 2255 FPS | 2146 FPS | 839 FPS |
| Eco | 3806 FPS | 3367 FPS | 3181 FPS | 1051 FPS |

These short scenes showed no graphics regression and scored higher at the lower presets. They are not representative of every game, sustained game frame rates or battery life. Immediate-presentation FPS is also not the panel's visible refresh rate.

Balanced still reached about 90°C in the graphics test. Eco graphics peaked at about 67°C. Vulkan startup enumerated the RX and briefly woke it, despite rendering on the iGPU. It returned to sleep afterward.

## October 25: the undervolt baseline

This earlier experiment compared stock and tuned Performance in an RX desktop session. It is separate from October 26's iGPU preset comparison.

| CPU matrix, 60 seconds | Throughput | CPU socket power | Mean / peak CPU |
| --- | ---: | ---: | ---: |
| Stock Performance | 9965.83 operations/s | 72.64 W | 94.60 / 95.38°C |
| Tuned Performance | 9708.75 operations/s | 61.27 W | 89.81 / 90.25°C |

The combined CPU curve / thermal policy lost 2.58% throughput and reduced the sampled socket power by 15.65%. This does not isolate the effect of voltage from the thermal target.

The earlier 30 W Quiet setting lost 18.47% against original Quiet, not against Performance. It has been superseded by the current presets. Comparing those different baselines as if they were the same would be misleading.

### Dedicated RX

The driver exposed a readable −30 mV offset, with automatic clocks. A stock blur run measured 7884 FPS and about 81.32 W GPU power; the tuned run measured 7768 FPS and about 76.95 W. Both reached 101°C junction.

The stock run lasted 60 seconds and used full fans. The tuned run lasted 120 seconds with the earlier Performance fan ramp. These are **directional figures, not a matched power comparison**. The voltage offset did not make the RX cool under an uncapped workload.

Earlier validation included 300 seconds of verified CPU stress, 240 seconds of load transitions, 90 seconds of verified memory stress, 120-second RX offset runs and a 180-second combined CPU/RX load. The original independent recovery boot, normal reboot and hibernation/resume passed.

88°C and 87°C CPU targets exceeded the 5% performance-loss goal on repetition. Broad platform-power caps also lost too much performance. The iGPU remained at stock voltage because the investigation did not establish useful verified voltage control.

## What is established now

- Eight final CPU/graphics workload runs completed successfully.
- 64 focused controller, profile, registration and rollback checks passed; portable versions ship in this repo.
- The restored Caelestia sliding selector uses the same preset backend. A later IPC-path check selected Performance, Eco and Balanced, verified settled profile, boost and 300 / 60 / 300 Hz refresh, and left Balanced active. This was not a physical charger transition or a mouse-injection test.
- An intentional automatic service restart preserved Eco's original power limit and boost ownership.
- Full reset restored the recorded native 50 W Quiet limit and enabled boost. Re-enable and return to Balanced passed.
- No matching GPU reset, machine-check, lockup or critical thermal message was observed during the completed runs.
- The new preset revision has not passed a new reboot, hibernation or physical charger-transition test.
- No unplugged battery runtime was measured for the new presets. CPU socket savings cannot be converted directly into extra battery hours.

The repo's evidence check recomputes percentages and validates the saved results. CI does not reproduce the hardware tests.
