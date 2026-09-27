AWS EFS
=======
[![CI](https://github.com/deekayen/ansible-role-aws-efs/actions/workflows/ci.yml/badge.svg)](https://github.com/deekayen/ansible-role-aws-efs/actions/workflows/ci.yml) [![Project Status: Inactive – The project has reached a stable, usable state but is no longer being actively developed; support/maintenance will be provided as time allows.](https://www.repostatus.org/badges/latest/inactive.svg)](https://www.repostatus.org/#inactive)

Mount an EFS share on an AWS server.

AWS docs: https://docs.aws.amazon.com/efs/latest/ug/using-amazon-efs-utils.html

Requirements
------------

Amazon Linux 2023, which ships `amazon-efs-utils` in its default repository.
Other distributions need access to a repository that carries the package.

Role Variables
--------------

`aws_efs_mount_state` defaults to `mounted`. Set it to `present` to write
the `/etc/fstab` entries without mounting, for example when baking an AMI.

`aws_efs_paths` comes with assumed defaults if not overridden by the
variable. The `filesystem_id` is the only required item.
The alternative `defaults` option is "default" to omit encryption over stunnel.

Mount defaults are as follows:

    aws_efs_paths:
      - path: "/mnt/efs"
        owner: "root"
        group: "root"
        mode: "0644"
        defaults: "tls"

Dependencies
------------

None.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    ---

    - name: Mount an Amazon Elastic File System.
      hosts: servers

      vars:
        aws_efs_paths:
          - filesystem_id: "fs-12345678"
          - path: "/efs"
            owner: "root"
            group: "root"
            mode: "0755"
            defaults: "default"
            filesystem_id: "fs-87654321"

      roles:
         - deekayen.aws_efs

License
-------

BSD
