nfs_array_specific_latency = {
        'aggregate_usec_per_file_metadata_create_op': 'file_metadata_create',
        'aggregate_usec_per_file_metadata_modify_op': 'file_metadata_modify',
        'aggregate_usec_per_file_metadata_read_op': 'file_metadata_read',
        'aggregate_usec_per_share_metadata_read_op': 'share_metadata_read',
        'usec_per_access_op': 'acces',
        'usec_per_create_op': 'create',
        'usec_per_fsinfo_op': 'fsinfo',
        'usec_per_fsstat_op': 'fsstat',
        'usec_per_getattr_op': 'getattr',
        'usec_per_link_op': 'link',
        'usec_per_lookup_op': 'lookup',
        'usec_per_mkdir_op': 'mkdir',
        'usec_per_pathconf_op': 'pathconf',
        'usec_per_read_op': 'read',
        'usec_per_readdir_op': 'readdir',
        'usec_per_readdirplus_op': 'readdirplus',
        'usec_per_readlink_op': 'readlink',
        'usec_per_remove_op': 'remove',
        'usec_per_rename_op': 'rename',
        'usec_per_rmdir_op': 'rmdir',
        'usec_per_setattr_op': 'setattr',
        'usec_per_symlink_op': 'symlink',
        'usec_per_write_op': 'write'
        }
http_array_specific_latency = {
        'usec_per_read_dir_op': 'read_dir',
        'usec_per_write_dir_op': 'write_dir',
        'usec_per_read_file_op': 'read_file',
        'usec_per_write_file_op': 'write_file',
        'usec_per_other_op': 'other'
        }
s3_array_specific_latency = {
        'usec_per_other_op': 'other',
        'usec_per_read_bucket_op': 'read_bucket',
        'usec_per_read_object_op': 'read_object',
        'usec_per_write_bucket_op': 'write_bucket',
        'usec_per_write_object_op': 'write_object'
        }


nfs_array_specific_iops = {
        'aggregate_file_metadata_creates_per_sec': 'file_metadata_creates',
        'aggregate_file_metadata_modifies_per_sec': 'file_metadata_modifies',
        'aggregate_file_metadata_reads_per_sec': 'file_metadata_reads',
        'aggregate_share_metadata_reads_per_sec': 'share_metadata_reads',
        'accesses_per_sec': 'accesses',
        'creates_per_sec': 'creates',
        'fsinfos_per_sec': 'fsinfos',
        'fsstats_per_sec': 'fsstats',
        'getattrs_per_sec': 'getattrs',
        'links_per_sec': 'links',
        'lookups_per_sec': 'lookups',
        'mkdirs_per_sec': 'mkdirs',
        'pathconfs_per_sec': 'pathconfs',
        'readdirpluses_per_sec': 'readdirpluses',
        'readdirs_per_sec': 'readdirs',
        'readlinks_per_sec': 'readlinks',
        'reads_per_sec': 'reads',
        'removes_per_sec': 'removes',
        'renames_per_sec': 'renames',
        'rmdirs_per_sec': 'rmdirs',
        'setattrs_per_sec': 'setattrs',
        'symlinks_per_sec': 'symlinks',
        'writes_per_sec': 'writes'
        }
http_array_specific_iops = {
        'others_per_sec': 'others',
        'read_dirs_per_sec': 'read_dirs',
        'read_files_per_sec': 'read_files',
        'write_dirs_per_sec': 'write_dirs',
        'write_files_per_sec': 'write_files'
        }
s3_array_specific_iops = {
        'others_per_sec': 'others',
        'read_buckets_per_sec': 'read_buckets',
        'read_objects_per_sec': 'read_objects',
        'write_buckets_per_sec': 'write_buckets',
        'write_objects_per_sec': 'write_objects'
        }
