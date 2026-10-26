# Recovery before tuning

The original work began with a read-only Btrfs baseline and a separately bootable writable recovery root. Its GRUB entry was boot-tested before accepting the undervolt.

## What was preserved

- A read-only root snapshot and a separate home baseline.
- A writable recovery root made from the pre-tuning baseline.
- Independent preserved kernel and initramfs files.
- Original boot configuration, ASUS configuration and fan curves.
- A recovery boot entry using the preserved files and `noresume`.

A root snapshot does not include nested or separately mounted home, swap or boot files. Keeping an old root snapshot while replacing the only kernel/initramfs is not the same recovery plan. The tested entry reused the current home; it did not silently roll user files back.

Disk identifiers, partition paths, resume offsets, original configuration backups and private recovery contents are deliberately absent from this public repo. The [private recovery repository](https://github.com/ilyasmohaimel/linux-setup-recovery) has a different scope from these public tuning notes.

## Reset the installed reference

On the machine where these helpers and its original backup already exist:

```sh
sudo /usr/local/libexec/frost-thermal-reset
```

This disables the tuning service, requests CPU curve zero, releases owned power/thermal/boost settings, clears the matching RX offset, restores automatic clocks and restores the original Performance fan curves. It preserves a lower limit or different voltage selected elsewhere.

The RX may wake briefly during an explicit reset. The helper restores its previous runtime policy afterward. It does not disable thermal protection or change the BIOS/VBIOS.

Re-enable the tested cooling curves and tuning:

```sh
sudo /usr/local/libexec/frost-thermal-enable
```

The helpers expect the original fan-restore program created during recovery preparation, at the path visible in `src/frost-thermal-reset`. That machine backup is not distributed. Copying the reset helper alone does not create it. Capture and verify your own baseline before adapting these files.

GPU choices and the display policy are user preferences, separate from the root thermal service. Choose Balanced or Performance in Battery to leave Eco and restore the refresh that Eco changed.

## Verification timeline

| Check | Original tuning | October 26 preset revision |
| --- | --- | --- |
| Independent GRUB recovery boot | Passed | Entry and preserved files retained |
| Normal reboot | Passed | Not repeated |
| Hibernate / resume | Passed | Not repeated |
| Full installed reset / re-enable | Passed | Passed, including Eco boost and power cap |
| Automatic controller restart | Earlier checks | Passed with ownership retained |
| CPU / graphics workloads | Passed | Eight final runs passed |
| Unplugged runtime for these presets | Earlier partial observation only | Not measured |

The new revision's rollback test caught an actual failure: voltage-control reads returned `EBUSY` while the RX was deeply asleep. The bounded wake-and-release path fixed it, and the full reset/re-enable sequence was rerun successfully. The source and three dedicated regression cases are included.

For another machine, boot the independent recovery path first. Preserve the original fan data, power limits and firmware/kernel configuration. A successful configuration check or service start does not replace a boot or resume test.
