from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import testinfra.utils.ansible_runner
import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_directories(host):
    dirs = [
        "/etc/smokeping_prober"
    ]
    for dir in dirs:
        d = host.file(dir)
        assert d.is_directory
        assert d.exists


def test_service(host):
    s = host.service("smokeping_prober")
    try:
        assert s.is_running
    except AssertionError:
        # Capture service logs
        journal_output = host.run('journalctl -u smokeping_prober --since "1 hour ago"')
        print("\n==== journalctl -u smokeping_prober Output ====\n")
        print(journal_output)
        print("\n============================================\n")
        raise  # Re-raise the original assertion error


def test_protecthome_property(host):
    s = host.service("smokeping_prober")
    p = s.systemd_properties
    assert p.get("ProtectHome") == "yes"


@pytest.mark.parametrize("sockets", [
    "tcp://127.0.0.1:8080",
    "tcp://127.0.1.1:8080",
])
def test_socket(host, sockets):
    assert host.socket(sockets).is_listening
