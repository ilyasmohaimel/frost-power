# Bring the method to another machine

The useful portable part is the process: capture a recoverable baseline, measure matched workloads, change one policy at a time, read back the settings and test rollback. The 38 W / 20 W limits and voltage values belong to this G513QY experiment.

## Another AMD laptop

1. Identify the exact CPU, GPUs, driver, internal panel wiring and power supplies. Start with the read-only inspector.
2. Confirm which profile owner is active. This machine uses asusd; do not add another competing profile daemon.
3. Verify the installed RyzenAdj revision supports the CPU and exposes readable limits. The CPU curve request here does not have a direct voltage readback.
4. Capture per-profile firmware limits and fan settings. Do not reuse the 50 / 74 / 90 W fallbacks without measuring them on the new machine.
5. Run stock and candidate workloads with the same cooling, charger, renderer and duration. Separate CPU socket power, GPU power, wall power and battery discharge.
6. Keep boost ownership and a lower setting chosen elsewhere intact. Recheck burst behavior, idle transitions, memory, graphics and mixed loads.
7. Verify reset, re-enable, reboot and resume before treating the configuration as complete.

Change the model guards, PCI addresses, UID assumptions, display output and charger classification deliberately. The exact integration points are in [the reference map](../reference/g513qy/README.md). Do not bypass the guards merely to make the service start.

## Intel plus NVIDIA

The controller in `src/` uses RyzenAdj and AMD Overdrive interfaces. It does not undervolt Intel CPUs or NVIDIA GPUs. An unsupported interface or locked voltage control is a reason to use supported power/boost limits, not to translate −5 or −30 mV into guessed settings.

The GPU-policy structure can still be useful: choose the compositor GPU at login, keep the internal panel's wiring clear, classify USB-C versus barrel power correctly and verify that the dedicated GPU can suspend. GPU-specific environment variables, driver power management, application offload and compositor support need a separate implementation and physical tests.

[The Frost GPU porting guide](https://github.com/ilyasmohaimel/frost-gpu/blob/main/docs/porting.md) discusses rendering, synchronization and offload boundaries. Launch-time offload does not transfer an already running application between GPUs.

## Performance goals

Treat a percentage as a workload result. A CPU prime test, matrix test, game, video decoder and compositor can respond very differently to the same power policy. Eco's 60 Hz panel mode also changes visible smoothness independently of CPU throughput.

Measure unplugged runtime separately. Processor power savings alone do not establish battery hours, charger adequacy or charging behavior.
