"""Testinfra checks for the AWS EFS role."""

import re

FSTAB_ENTRY = r"^fs-12345678:/\s+/mnt/efs\s+efs\s+tls,_netdev\s"


def test_packages_installed(host):
    for name in ("amazon-efs-utils", "nfs-utils", "stunnel"):
        assert host.package(name).is_installed


def test_mount_point(host):
    mount_point = host.file("/mnt/efs")
    assert mount_point.is_directory
    assert mount_point.user == "root"
    assert mount_point.mode == 0o644


def test_fstab_entry(host):
    fstab = host.file("/etc/fstab").content_string
    assert re.search(FSTAB_ENTRY, fstab, re.MULTILINE)
