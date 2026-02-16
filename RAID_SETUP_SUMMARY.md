# RAID Setup Summary (2026-02-04 to 2026-02-05)

This file consolidates the actions and outcomes from our RAID setup and storage configuration session.

> **Status (2026-02-16): HISTORICAL RECORD**
>
> This document records a prior RAID session. On the current host as of
> 2026-02-16, verification showed no active mdraid arrays in `/proc/mdstat`,
> no active RAID mounts, and no matching RAID mount entries in `/etc/fstab`.
> Treat the remaining content as historical context, not current active state.

```
Storage Map (Mounts -> Devices)

/home/kkk/Apps/srv/raid-small  (label: raid-small)  -> /dev/md0  (RAID6)
  /dev/md0 members: /dev/sda1 /dev/sdb1 /dev/sdc1 /dev/sdd1

/home/kkk/Apps/srv/raid-big    (label: raid-big)    -> /dev/md1  (RAID5)
  /dev/md1 members: /dev/sdb2 /dev/sdc2 /dev/sdd2

/home/kkk/Apps/srv/storage-sdc (label: storage-sdc) -> /dev/sdc3 (standalone)
/home/kkk/Apps/srv/storage-sdd (label: storage-sdd) -> /dev/sdd3 (standalone)
```

## Goals
- Remove duplicate Ubuntu entries from GRUB/EFI.
- Reuse the Intel SSD (`/dev/sda`) as storage, then redesign storage layout.
- Create:
  - Small RAID6 across all 4 disks (`sda/sdb/sdc/sdd`) sized to the smallest disk (`sda`).
  - Large RAID5 across remaining space on `sdb/sdc/sdd`.
  - Leftover non-RAID storage on remaining space of `sdc` and `sdd`.
- Mount all new filesystems under `~/Apps/srv/`.
- Verify read/write access without sudo.
- Provide status check commands.

## System Snapshot (Key Devices)
- Current OS on `nvme0n1p2` (Ubuntu root).
- Disks involved:
  - `sda` ~279.5G (Intel SSD)
  - `sdb` ~1.8T (WDC WD20EFRX)
  - `sdc` ~3.6T (WDC WD40EFRX)
  - `sdd` ~3.6T (WDC WD40EFRX)

## GRUB / EFI Cleanup
- Disabled `os-prober` to remove old Ubuntu entries:
  - `/etc/default/grub`: `GRUB_DISABLE_OS_PROBER=true`
  - `sudo update-grub`
- Removed old EFI boot entry:
  - `sudo efibootmgr -b 0003 -B`
- Removed PXE boot entries:
  - `sudo efibootmgr -b 0001 -B`
  - `sudo efibootmgr -b 0002 -B`

## Final RAID and Storage Layout
### Partitions
- `sda1` = 279G (RAID6 small)
- `sdb1` = 279G (RAID6 small)
- `sdc1` = 279G (RAID6 small)
- `sdd1` = 279G (RAID6 small)

- `sdb2` = 1.5T (RAID5 big)
- `sdc2` = 1.5T (RAID5 big)
- `sdd2` = 1.5T (RAID5 big)

- `sdc3` = 1.8T (standalone storage)
- `sdd3` = 1.8T (standalone storage)

### Arrays
- RAID6 small:
  - `/dev/md0` (level 6, 4 disks)
  - Size ~548G usable
  - Mount: `/home/kkk/Apps/srv/raid-small`
- RAID5 big:
  - `/dev/md1` (level 5, 3 disks)
  - Size ~3.1T usable
  - Mount: `/home/kkk/Apps/srv/raid-big`

### Standalone Storage
- `/dev/sdc3` → `/home/kkk/Apps/srv/storage-sdc`
- `/dev/sdd3` → `/home/kkk/Apps/srv/storage-sdd`

## Key Commands Used (High-Level)
### Partitioning
- Created GPT tables on `sda/sdb/sdc/sdd`.
- Sized RAID6 partition to 279GiB on all four disks.
- RAID5 partitions sized to smallest disk among `sdb/sdc/sdd`.
- Leftover partitions created on `sdc` and `sdd` only.

### RAID Creation
```
sudo mdadm --create /dev/md0 --level=6 --raid-devices=4 /dev/sda1 /dev/sdb1 /dev/sdc1 /dev/sdd1
sudo mdadm --create /dev/md1 --level=5 --raid-devices=3 /dev/sdb2 /dev/sdc2 /dev/sdd2
```

### Formatting
```
sudo mkfs.ext4 -L raid-small /dev/md0
sudo mkfs.ext4 -L raid-big /dev/md1
sudo mkfs.ext4 -L storage-sdc /dev/sdc3
sudo mkfs.ext4 -L storage-sdd /dev/sdd3
```

### Mounts
```
/home/kkk/Apps/srv/raid-small
/home/kkk/Apps/srv/raid-big
/home/kkk/Apps/srv/storage-sdc
/home/kkk/Apps/srv/storage-sdd
```

### Persisting RAID and Mounts
- RAID config saved:
  - `sudo mdadm --detail --scan | sudo tee -a /etc/mdadm/mdadm.conf`
  - `sudo update-initramfs -u`
- `/etc/fstab` entries added for all four mounts.

## Verification Outcomes
- `cat /proc/mdstat` showed:
  - `md0` RAID6: `[UUUU]` (clean)
  - `md1` RAID5: `[UUU]` (clean)
- `df -h` showed mounts:
  - `/dev/md0` at `~/Apps/srv/raid-small`
  - `/dev/md1` at `~/Apps/srv/raid-big`
  - `/dev/sdc3` at `~/Apps/srv/storage-sdc`
  - `/dev/sdd3` at `~/Apps/srv/storage-sdd`
- Ownership set:
  - `sudo chown -R kkk:kkk` on all mount points
  - Verified read/write by creating and deleting test files

## RAID Status Commands
- Quick status:
  - `cat /proc/mdstat`
- Detailed status:
  - `sudo mdadm --detail /dev/md0`
  - `sudo mdadm --detail /dev/md1`

## Notes / Outcomes
- GRUB now shows only the current Ubuntu installation.
- EFI boot entries cleaned (old Ubuntu and PXE removed).
- RAID arrays are healthy and mounted persistently.
- Standalone storage available on `sdc` and `sdd`.

## Naming And Mount Chain (2026-02-05)
This section documents how RAID names and mountpoints are linked.

### Filesystem Labels (Source Of Names)
- `/dev/md0` label `raid-small` mounted at `/home/kkk/Apps/srv/raid-small`
- `/dev/md1` label `raid-big` mounted at `/home/kkk/Apps/srv/raid-big`
- `/dev/sdc3` label `storage-sdc` mounted at `/home/kkk/Apps/srv/storage-sdc`
- `/dev/sdd3` label `storage-sdd` mounted at `/home/kkk/Apps/srv/storage-sdd`

### fstab Mounts (UUID To Mountpoint)
- `UUID=b721f4fc-3eac-486f-9da7-ef1ef1e980dc` -> `/home/kkk/Apps/srv/raid-small`
- `UUID=0eaa801f-d891-4423-a4cf-2558afbd68c1` -> `/home/kkk/Apps/srv/raid-big`
- `UUID=8159ea60-163e-4bb5-a80f-e8f12d85b555` -> `/home/kkk/Apps/srv/storage-sdc`
- `UUID=c120229c-5883-4db4-9d83-841e4d50af5c` -> `/home/kkk/Apps/srv/storage-sdd`

### mdadm Arrays (Array UUIDs)
- `/dev/md0` UUID `9a25a7f8:ed9cee40:25835bce:cccb2a81`
- `/dev/md1` UUID `d989f66a:b8dbfd6b:b20aa23d:dbcfe274`

## RAID Metadata Details (2026-02-05)
### md0 (raid-small)
- RAID level `raid6`
- 4 devices: `/dev/sda1` `/dev/sdb1` `/dev/sdc1` `/dev/sdd1`
- Array size `584839168` sectors (~557.75 GiB)
- Used device size `292419584` sectors (~278.87 GiB)
- Chunk size `512K`, layout `left-symmetric`
- Update time `Thu Feb 5 05:28:22 2026`
- State `active`, devices healthy, no spares

### md1 (raid-big)
- RAID level `raid5`
- 3 devices: `/dev/sdb2` `/dev/sdc2` `/dev/sdd2`
- Array size `3321659392` sectors (~3.09 TiB)
- Used device size `1660829696` sectors (~1583.89 GiB)
- Chunk size `512K`, layout `left-symmetric`
- Update time `Thu Feb 5 05:28:22 2026`
- State `active`, devices healthy, no spares
