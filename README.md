[![Build Status](https://travis-ci.org/deekayen/ansible-role-aws-efs.svg?branch=main)](https://travis-ci.org/deekayen/ansible-role-aws-efs) [![Project Status: Inactive – The project has reached a stable, usable state but is no longer being actively developed; support/maintenance will be provided as time allows.](https://www.repostatus.org/badges/latest/inactive.svg)](https://www.repostatus.org/#inactive)

AWS EFS
=======

Mount an EFS share on an AWS server.

AWS docs: https://docs.aws.amazon.com/efs/latest/ug/using-amazon-efs-utils.html

Requirements
------------

Access to a repository that has the amazon-efs-utils.

Role Variables
--------------

`aws_efs_paths` is the only variable, which comes with assumed defaults if
not overridden by the variable. The `filesystem_id` is the only required item.
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

A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

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
         - deekayen.aws-efs

License
-------

BSD
