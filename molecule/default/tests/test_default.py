
import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
  os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')
################## TODO 
# - Test logrotate
# - Hit Metrics Endpoint in Test 
# - 
###################
def test_directories(host):
  with host.sudo():
    present = [
        "/etc/td-agent-bit",
        "/etc/td-agent-bit/parsers.d",
        "/etc/td-agent-bit/filters.d",
        "/etc/td-agent-bit/includes",
    ]
    absent = []
    if present:
        for directory in present:
            d = host.file(directory)
            assert d.is_directory
            assert d.exists
    if absent:
        for directory in absent:
            d = host.file(directory)
            assert not d.exists


def test_flb_conf_file(host):
  with host.sudo():
    conf = host.file("/etc/td-agent-bit/td-agent-bit.conf")
    assert conf.exists
    assert conf.contains("/var/log/td_agent_bit.catchall")
    assert conf.contains("syslog-rfc3164-local")
    assert conf.contains("THROTTLED.$TAG false")

def test_flb_service(host):
  with host.sudo():
    flb_svc = host.service("td-agent-bit")
    assert flb_svc.is_enabled
    assert flb_svc.is_running
