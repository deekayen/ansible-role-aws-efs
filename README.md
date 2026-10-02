# deekayen.aws_efs

[![CI](https://github.com/deekayen/ansible-role-aws-efs/actions/workflows/ci.yml/badge.svg)](https://github.com/deekayen/ansible-role-aws-efs/actions/workflows/ci.yml) [![Ansible Galaxy](https://img.shields.io/badge/galaxy-deekayen.aws__efs-blue.svg)](https://galaxy.ansible.com/ui/standalone/roles/deekayen/aws_efs/) [![Project Status: Inactive – The project has reached a stable, usable state but is no longer being actively developed; support/maintenance will be provided as time allows.](https://www.repostatus.org/badges/latest/inactive.svg)](https://www.repostatus.org/#inactive) ![BSD 3-Clause license](https://img.shields.io/badge/license-BSD%203--Clause-blue)

An Ansible role that mounts one or more Amazon EFS file systems on a Linux host through the [Amazon EFS mount helper](https://docs.aws.amazon.com/efs/latest/ug/using-amazon-efs-utils.html) and records each mount in `/etc/fstab`.

The role installs `amazon-efs-utils` and the NFS client from the system package manager, creates each mount point directory, and uses `ansible.posix.mount` to write an `<filesystem_id>:/ <path> efs tls,_netdev` entry to `/etc/fstab`. With the default `aws_efs_mount_state: mounted`, it also mounts the file system.

## Requirements

- ansible-core 2.15 or newer on the controller.
- The `ansible.posix` collection: `ansible-galaxy collection install ansible.posix`.
- An Amazon Linux 2023 target, which ships `amazon-efs-utils` in its default repository. Other distributions need a repository that carries the package before this role runs.
- Network access from the host to the EFS mount targets when `aws_efs_mount_state` is `mounted`.
- Privilege escalation on the target. Run the play with `become: true`; the role installs packages, creates directories, and edits `/etc/fstab`.

## Supported platforms

From `meta/main.yml`, and it runs through Molecule in CI:

| Platform | Versions |
| --- | --- |
| Amazon Linux | 2023 |

Molecule runs on `amazonlinux2023` with `aws_efs_mount_state: present`, since a container cannot reach a real EFS file system.

## Installation

From Ansible Galaxy:

```bash
ansible-galaxy role install deekayen.aws_efs
ansible-galaxy collection install ansible.posix
```

Or pin it in `requirements.yml`:

```yaml
---
roles:
  - name: deekayen.aws_efs
    src: https://github.com/deekayen/ansible-role-aws-efs.git
    scm: git
    version: main

collections:
  - name: ansible.posix
```

```bash
ansible-galaxy install -r requirements.yml
```

## Role variables

| Variable | Default | Description |
| --- | --- | --- |
| `aws_efs_mount_state` | `mounted` | Passed to `ansible.posix.mount` as `state`. `mounted` mounts each file system and writes `/etc/fstab`; `present` only writes `/etc/fstab`, for machine images that should mount at first boot. `meta/argument_specs.yml` limits it to these two values. |

### Required variables

`aws_efs_paths` has no default, and `meta/argument_specs.yml` marks it required. It is a list of mounts. Each entry takes these keys:

| Key | Default | Description |
| --- | --- | --- |
| `filesystem_id` | none, required | EFS file system ID. `tasks/assert.yml` requires it to match `fs-` followed by lowercase hex digits. |
| `path` | `/mnt/efs` | Mount point. Must be absolute; the role asserts this. |
| `owner` | `root` | Owner of the mount point directory. |
| `group` | `root` | Group of the mount point directory. |
| `mode` | `0644` | Mode of the mount point directory. See [Known issues](#known-issues). |
| `defaults` | `tls` | First mount option, followed by `,_netdev`. `tls` sends traffic through the mount helper's TLS tunnel. `meta/argument_specs.yml` also accepts `default`, which the role writes as `default,_netdev`. |

## Dependencies

None. The `ansible.posix` collection is a requirement, not a role dependency.

## Example playbook

```yaml
---
- name: Mount shared EFS file systems.
  hosts: app_servers
  become: true

  vars:
    aws_efs_paths:
      - filesystem_id: fs-0123456789abcdef0
        path: /srv/shared
        owner: ec2-user
        group: ec2-user
        mode: "0755"
      - filesystem_id: fs-0fedcba9876543210
        path: /mnt/efs-archive

  roles:
    - deekayen.aws_efs
```

The file system IDs are placeholders.

## Known issues

- `tasks/main.yml:9-14` installs `gcc` and `openssl-devel` on every host, but no task compiles anything.
- `tasks/main.yml:24-28` has a Debian branch that installs `nfs-common`, but the earlier `openssl-devel` install is unconditional, and Debian and Ubuntu name that package `libssl-dev`. `meta/main.yml` lists neither platform.
- The default mount point `mode` is `0644` (`tasks/main.yml:41`). A directory without the execute bit cannot be entered by non-root users while nothing is mounted on it. Set `mode: "0755"` per entry if that matters.

## Development

CI runs on every push to `main` and every pull request (see `.github/workflows/ci.yml`):

1. Lint: installs `ansible.posix` from `molecule/default/requirements.yml`, then runs `ansible-lint --profile production` and `flake8 molecule/`.
2. Molecule: converge, idempotence, and testinfra verification in Docker on `amazonlinux2023`.

To run the same checks locally with Docker available:

```bash
pip3 install ansible-core ansible-lint flake8 molecule "molecule-plugins[docker]" docker pytest-testinfra
ansible-galaxy install -r molecule/default/requirements.yml
ansible-lint --profile production
flake8 molecule/
MOLECULE_DISTRO=amazonlinux2023 molecule test
pre-commit run --all-files
```

`molecule/default/converge.yml` mounts placeholder `fs-12345678` at `/mnt/efs` with `aws_efs_mount_state: present`. The testinfra checks in `molecule/default/tests/test_default.py` confirm that `amazon-efs-utils`, `nfs-utils`, and `stunnel` are installed, `/mnt/efs` is a root-owned directory with mode `0644`, and `/etc/fstab` has the `fs-12345678:/ /mnt/efs efs tls,_netdev` entry. `.pre-commit-config.yaml` runs `check-yaml`, `end-of-file-fixer`, `trailing-whitespace`, `yamllint`, `flake8`, and `ansible-lint --profile production`.

### Repository layout

| Path | Purpose |
| --- | --- |
| `tasks/main.yml` | Package installs, mount point directories, and `fstab` entries. |
| `tasks/assert.yml` | Validates `filesystem_id` and `path` in each entry, tagged `always`. |
| `defaults/main.yml` | `aws_efs_mount_state`. |
| `meta/argument_specs.yml` | Argument spec, including the `aws_efs_paths` entry keys. |
| `molecule/default/` | Molecule scenario: `prepare.yml`, `converge.yml`, requirements, and testinfra tests. |
| `.github/workflows/` | `ci.yml` for lint and Molecule, `release.yml` for Galaxy import. |

## Releases

Pushing a git tag runs `.github/workflows/release.yml`, which imports the tagged commit into Ansible Galaxy as `deekayen.aws_efs`. The import needs a `GALAXY_API_KEY` repository or organization secret.

## License

BSD 3-Clause. See [LICENSE](LICENSE).

## Author

[David Norman](https://github.com/deekayen). Sponsorship links are in [.github/FUNDING.yml](.github/FUNDING.yml).
