from prometheus_client.core import GaugeMetricFamily


class ArraySpecificPerformanceMetrics():
    """
    Base class for FlashBlade Prometheus array specific performance metrics
    """

    def __init__(self, fb):
        self.fb = fb
        self.latency = None
        self.iops = None

    def _latency(self):
        """
        Create array specific latency performance metrics of gauge type.
        """
        self.latency = GaugeMetricFamily(
                              'purefb_array_specific_performance_latency_usec',
                              'FlashBlade array specific latency',
                              labels=['protocol', 'dimension'])

        m = self.fb.get_array_specific_performance('nfs')
        self.latency.add_metric(['nfs', 'file_metadata_create'],
                                m.aggregate_usec_per_file_metadata_create_op)
        self.latency.add_metric(['nfs', 'file_metadata_modify'],
                                m.aggregate_usec_per_file_metadata_modify_op)
        self.latency.add_metric(['nfs', 'file_metadata_read'],
                                m.aggregate_usec_per_file_metadata_read_op)
        self.latency.add_metric(['nfs', 'share_metadata_read'],
                                m.aggregate_usec_per_share_metadata_read_op)
        self.latency.add_metric(['nfs', 'acces'], m.usec_per_access_op)
        self.latency.add_metric(['nfs', 'create'], m.usec_per_create_op)
        self.latency.add_metric(['nfs', 'fsinfo'], m.usec_per_fsinfo_op)
        self.latency.add_metric(['nfs', 'fsstat'], m.usec_per_fsstat_op)
        self.latency.add_metric(['nfs', 'getattr'], m.usec_per_getattr_op)
        self.latency.add_metric(['nfs', 'link'], m.usec_per_link_op)
        self.latency.add_metric(['nfs', 'lookup'], m.usec_per_lookup_op)
        self.latency.add_metric(['nfs', 'mkdir'], m.usec_per_mkdir_op)
        self.latency.add_metric(['nfs', 'pathconf'], m.usec_per_pathconf_op)
        self.latency.add_metric(['nfs', 'read'], m.usec_per_read_op)
        self.latency.add_metric(['nfs', 'readdir'], m.usec_per_readdir_op)
        self.latency.add_metric(['nfs', 'readdirplus'],
                                m.usec_per_readdirplus_op)
        self.latency.add_metric(['nfs', 'readlink'], m.usec_per_readlink_op)
        self.latency.add_metric(['nfs', 'remove'], m.usec_per_remove_op)
        self.latency.add_metric(['nfs', 'rename'], m.usec_per_rename_op)
        self.latency.add_metric(['nfs', 'rmdir'], m.usec_per_rmdir_op)
        self.latency.add_metric(['nfs', 'setattr'], m.usec_per_setattr_op)
        self.latency.add_metric(['nfs', 'symlink'], m.usec_per_symlink_op)
        self.latency.add_metric(['nfs', 'write'], m.usec_per_write_op)

        m = self.fb.get_array_specific_performance('http')
        self.latency.add_metric(['http', 'read_dir'], m.usec_per_read_dir_op)
        self.latency.add_metric(['http', 'write_dir'], m.usec_per_write_dir_op)
        self.latency.add_metric(['http', 'read_file'], m.usec_per_read_file_op)
        self.latency.add_metric(['http', 'write_file'],
                                m.usec_per_write_file_op)
        self.latency.add_metric(['http', 'other'], m.usec_per_other_op)

        m = self.fb.get_array_specific_performance('s3')
        self.latency.add_metric(['s3', 'other'], m.usec_per_other_op)
        self.latency.add_metric(['s3', 'read_bucket'],
                                m.usec_per_read_bucket_op)
        self.latency.add_metric(['s3', 'read_object'],
                                m.usec_per_read_object_op)
        self.latency.add_metric(['s3', 'write_bucket'],
                                m.usec_per_write_bucket_op)
        self.latency.add_metric(['s3', 'write_object'],
                                m.usec_per_write_object_op)

    def _iops(self):
        """
        Create array specific iops performance metrics of gauge type.
        """
        self.iops = GaugeMetricFamily('purefb_array_specific_performance_iops',
                                      'FlashBlade array specific IOPS',
                                      labels=['protocol', 'dimension'])

        m = self.fb.get_array_specific_performance('nfs')
        self.iops.add_metric(['nfs', 'file_metadata_creates'],
                             m.aggregate_file_metadata_creates_per_sec)
        self.iops.add_metric(['nfs', 'file_metadata_modifies'],
                             m.aggregate_file_metadata_modifies_per_sec)
        self.iops.add_metric(['nfs', 'file_metadata_reads'],
                             m.aggregate_file_metadata_reads_per_sec)
        self.iops.add_metric(['nfs', 'share_metadata_reads'],
                             m.aggregate_share_metadata_reads_per_sec)
        self.iops.add_metric(['nfs', 'accesses'], m.accesses_per_sec)
        self.iops.add_metric(['nfs', 'creates'], m.creates_per_sec)
        self.iops.add_metric(['nfs', 'fsinfos'], m.fsinfos_per_sec)
        self.iops.add_metric(['nfs', 'fsstats'], m.fsstats_per_sec)
        self.iops.add_metric(['nfs', 'getattrs'], m.getattrs_per_sec)
        self.iops.add_metric(['nfs', 'links'], m.links_per_sec)
        self.iops.add_metric(['nfs', 'lookups'], m.lookups_per_sec)
        self.iops.add_metric(['nfs', 'mkdirs'], m.mkdirs_per_sec)
        self.iops.add_metric(['nfs', 'pathconfs'], m.pathconfs_per_sec)
        self.iops.add_metric(['nfs', 'readdirpluses'], m.readdirpluses_per_sec)
        self.iops.add_metric(['nfs', 'readdirs'], m.readdirs_per_sec)
        self.iops.add_metric(['nfs', 'readlinks'], m.readlinks_per_sec)
        self.iops.add_metric(['nfs', 'reads'], m.reads_per_sec)
        self.iops.add_metric(['nfs', 'removes'], m.removes_per_sec)
        self.iops.add_metric(['nfs', 'renames'], m.renames_per_sec)
        self.iops.add_metric(['nfs', 'rmdirs'], m.rmdirs_per_sec)
        self.iops.add_metric(['nfs', 'setattrs'], m.setattrs_per_sec)
        self.iops.add_metric(['nfs', 'symlinks'], m.symlinks_per_sec)
        self.iops.add_metric(['nfs', 'writes'], m.writes_per_sec)

        m = self.fb.get_array_specific_performance('http')
        self.iops.add_metric(['http', 'others'], m.others_per_sec)
        self.iops.add_metric(['http', 'read_dirs'], m.read_dirs_per_sec)
        self.iops.add_metric(['http', 'read_files'], m.read_files_per_sec)
        self.iops.add_metric(['http', 'write_dirs'], m.write_dirs_per_sec)
        self.iops.add_metric(['http', 'write_files'], m.write_files_per_sec)

        m = self.fb.get_array_specific_performance('s3')
        self.iops.add_metric(['s3', 'others'], m.others_per_sec)
        self.iops.add_metric(['s3', 'read_buckets'], m.read_buckets_per_sec)
        self.iops.add_metric(['s3', 'read_objects'], m.read_objects_per_sec)
        self.iops.add_metric(['s3', 'write_buckets'], m.write_buckets_per_sec)
        self.iops.add_metric(['s3', 'write_objects'], m.write_objects_per_sec)

    def get_metrics(self):
        self._latency()
        self._iops()
        yield self.latency
        yield self.iops
