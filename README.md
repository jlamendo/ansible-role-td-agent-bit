# Ansible Role: td-agent-bit

## Description:
Installs and configures td-agent-bit on Debian/RedHat based systems.
Defaults to installing via binary packages, but falls back to building from source where no binary is available, such as for Ubuntu 14.x.
Includes extremely simple interfaces for Tail and SystemD inputs, and the capability to automatically install and configure logrotate for Tail inputs.

## Installation:
```
ansible-galaxy install jlamendo.td_agent_bit
```


##  Example Playbook:
```
---
- hosts: all
  vars:
    SPLUNK_HOST: "splunk.example.com"
    SPLUNK_PORT: "8088"
    SPLUNK_TOKEN: ""
    flb_outputs:
      - Name: splunk
        Match: "*"
        Host: "{{ SPLUNK_HOST }}"
        Port: "{{ SPLUNK_PORT }}"
        Splunk_Token: "{{ SPLUNK_TOKEN }}"
        TLS: "On"
        TLS.Verify: "On"
        Message_Key: "log"
    flb_inputs:
      files:
        - path: "/var/log/syslog"
          parser: "syslog-rfc3164-local"
      services:
        - sshd
  gather_facts: true
  roles:
    - jlamendo.td_agent_bit
```


## Role Variables:

### td-agent-bit Service Variables

#### flb_svc_flush
- Description: Time in seconds.nanoseconds that the engine loop waits before flushing data ingested by input plugins over to output plugins.
- Default: `flb_svc_flush: 5`

#### flb_svc_log_level
- Description: td-agent-bit logs internally to the journal via stdout. This sets the internal log level.
- Default: `flb_svc_log_level: info`


#### flb_metrics_enable
- Description: Whether to enable the internal HTTP Metrics server, used for gathering metrics about td-agent-bit itself.
- Default: `flb_metrics_enable: false`

#### flb_metrics_bind_cidr
- Description:This role attempts to find the server's internal IP by comparing instance interfaces to this CIDR range. If you want to select a specific IP, use a /32. Once discovered, the IP is used to bind the internal metrics server to.
- Default: `flb_metrics_bind_cidr: 172.16.0.0/12`

#### flb_metrics_bind_port
- Description: Which port to bind the metrics server to.
- Default: `flb_metrics_bind_port: 9000`

#### flb_build_vers
- Description: This option defines what version of td-agent-bit will be downloaded and compiled should the install from packages fail.
- Default: `flb_build_vers: "1.4.6"`

#### flb_build_dir
- Description: This option defines where the td-agent-bit sources will be downloaded to and compiled should the install from packages fail.
- Default: `flb_build_dir: "/usr/src/td-agent-bit"`

#### flb_custom_parsers
- Description: A list of custom parser files that will be templated out and injected into the td-agent-bit configuration.
- Default: none
- Example: 
>``` 
>flb_custom_parsers:
>  - ./templates/parsers/json_parsers.conf.j2
>```
>_Note: You can see the built-in parsers [here](https://github.com/fluent/fluent-bit/blob/master/conf/parsers.conf). Be sure to look at this before writing your own custom parser, as it is likely one already exists that will fit your need._

#### flb_custom_includes
- Description: A list of files that will be included into the main td-agent-bit config file via `@INCLUDE` statements.
- Default: none
- Example: 
>```
>flb_custom_includes:
>  - ./templates/includes/custom_dynamic_output.conf.j2
>```

### Tail Default Variables
_Note: All of the tail plugin defaults can also be set on a per-input basis, using the same syntax._

#### tail_input.buffer_chunk_sz
- Description: This sets the default for the maximum chunk size that the tail plugin will read from a file. This effectively limits the maximum size of a single log line as well.
- Default: `tail_input.buffer_chunk_sz: 512k`

#### tail_input.buffer_max_sz
- Description: This sets the default for the maximum amount of data the tail plugin will buffer before forcing a flush. This limit is permissive, and may be exceeded by the value of `tail_input.buffer_chunk_sz - 1`.
- Default: `tail_input.buffer_max_sz: 5M`

#### tail_input.state_db
- Description: This sets the default path for the internal state databases that the tail plugin will create. One database will be created for each monitored file. The database helps td-agent-bit retain state in the event of a system failure, and also helps the agent track with logrotate more effectively.
- Default: `tail_input.state_db: /var/log/.flb-buffer`

#### tail_input.state_db_sync
- Description: Sets the default mode that the tail plugin's internal state database will use to persist data to disk. More information about the available options and what they do can be found [here](https://www.sqlite.org/pragma.html#pragma_synchronous).
- Default: `tail_input.state_db_sync: Normal`

#### tail_input.mem_max_sz
- Description: The maximum memory that a single instance of the tail plugin can consume. The default is set quite permissively - if this limit is hit, the plugin will pause reading log lines from disk until the data is flushed to the outputs. 
- Default: `tail_input.mem_max_sz: 56M`

### Auto-Logrotate Variables
This role automatically generates logrotate configs for each input defined via `flb_inputs.files`. These variables define various defaults and options for the logrotate configs that will be generated. All of the options here can additionally be set as options on individual `flb_inputs.files` entries.

#### tail_input.rotate_enabled
- Description: Enables the generation of logrotate configs for each entry in `flb_inputs.files`
- Default: `tail_input.rotate_enabled: true`

#### tail_input.rotate_interval
- Description: How often the logrotate script will run.
- Default: `tail_input.rotate_interval: "hourly"`

#### tail_input.rotate_missingok
- Description: Whether to generate an error when a log file is missing or not. Changing this is not recommended.
- Default: `tail_input.rotate_missingok: true`

#### tail_input.rotate_retention
- Description: How many rotated log files to retain. Be aware that setting this to a value above 0 may result in td-agent-bit ingesting your archives.
- Default: `tail_input.rotate_retention: 0`

#### tail_input.rotate_maxsize
- Description: How large a log file can be before logrotate forces a rotation regardless of interval. This can be very useful in tandem with adding a cron job to run logrotate more frequently, but the default logrotate cronjob on most systems will not run more frequently than once per hour.
- Default: `tail_input.rotate_maxsize: 5M`

#### tail_input.rotate_strategy
- Description: The strategy used to rotate logs. td-agent-bit supports `create` and `copytruncate` modes.
- Default: `tail_input.rotate_strategy: copytruncate`

#### flb_rotate_scripts
- Description: Custom scripts for logrotate to run at defined phases of the log rotation lifecycle.
- Default: none
- Example: 
>```
>  flb_rotate_scripts:
>    - name: postrotate
>      script: "/usr/bin/systemctl restart apache"
>```

## Host/Group Variables:
These options primarily define the per-host/group settings you will use to monitor specific log files, services, and other input sources supported by td-agent-bit.

### flb_inputs.files
The files key is a list of entries that will be templated into individual `[INPUT]` sections using the tail plugin in the td-agent-bit configuration. This option is primarily a convenience that is intended to significantly reduce the effort required to monitor lots of files on lots of hosts, and won't be suitable for every need. If more custom configuration is necessary, or if you want to be closer to the config and have less configured for you automatically, a custom input entry is a better choice. In addition to the options listed here, each entry can also be configured with all of the options listed in the [Tail Defaults](#tail-default-variables) and [Auto-Logrotate Variables](#auto-logrotate-variables) sections.


#### flb_inputs.files[].path
- Description: Path to an individual log file which td-agent-bit should tail and ingest.
- Default: none
- Example: `flb_inputs.files[].path: "/var/log/syslog"`

#### flb_inputs.files[].parser
- Description: Select a parser to parse the input file into individual keys before sending it to the output buffer. More information about available built-in parsers can be found [here](https://github.com/fluent/fluent-bit/blob/master/conf/parsers.conf).
- Default: none
- Example: `flb_inputs.files[].parser: "syslog-rfc3164-local"`

#### flb_inputs.files[].tag
- Description: Append a tag to each event created by this entry. Primarily useful for routing specific inputs to specific outputs via the `Match` key on outputs, but can also be used to enrich data with variables available from ansible.
- Default: none
- Example: `flb_inputs.files[].tag: syslog::{{ ansible_hostname }}`


#### flb_inputs.services
- Description: A very simple input format that accepts a list of strings that represent the names of services running on the target host. td-agent-bit will then tail the journald entries for these services. No logrotate configuration is generated, because journald handles this and none is needed.
- Default: none
- Example: 
>```
>  flb_inputs.services:
>    - sshd
>```

#### flb_inputs.custom:
- Description: Custom inputs for td-agent-bit. No changes are made to the config, instead this is a 1:1 map from YAML to the td-agent-bit config. Keys are case-sensitive.
- Default: none
- Example: 
>```
>  flb_inputs.custom:
>    - Name: systemd
>      Read_From_Tail: true
>      Strip_Underscores: true
>      Systemd_Filter: _SYSTEMD_UNIT=sshd.service
>      Tag: "{{ ansible_hostname }}::*"
>```

#### flb_outputs:
- Description: Configuration of outputs for td-agent-bit. Similar to custom inputs, this is a 1:1 YAML:config mapping, and no changes are made.
- Default: none
- Example: 
>```
>  flb_outputs:
>    - Name: splunk
>      Match: "*"
>      Host: "{{ SPLUNK_HOST }}"
>      Port: "{{ SPLUNK_PORT }}"
>      Splunk_Token: "{{ SPLUNK_TOKEN }}"
>      TLS: "On"
>      TLS.Verify: "Off"
>      Message_Key: "log"
>```


## Dependencies:
None.

## Author: 
- [Jon Lamendola](https://blog.vrtx.ai)

## License:
Licensed under the [MIT license](https://tldrlegal.com/license/mit-license#summary). Full license text available in the [LICENSE](./LICENSE) file.

