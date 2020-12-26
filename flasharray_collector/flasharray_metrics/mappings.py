array_latency_mapping = {'usec_per_read_op': 'read',
                         'usec_per_write_op': 'write',
                         'usec_per_mirrored_write_op': 'mirrored_write',
                         'local_queue_usec_per_op': 'local_queue',
                         'san_usec_per_read_op': 'san_read',
                         'san_usec_per_write_op': 'san_write',
                         'san_usec_per_mirrored_write_op': 'san_mirrored_write',
                         'queue_usec_per_read_op': 'queue_read',
                         'queue_usec_per_write_op': 'queue_write',
                         'queue_usec_per_mirrored_write_op': 'queue_mirrored_write',
                         'qos_rate_limit_usec_per_read_op': 'qos_read',
                         'qos_rate_limit_usec_per_write_op': 'qos_write',
                         'qos_rate_limit_usec_per_mirrored_write_op': 'qos_mirrored'}

array_bandwidth_mapping = {'output_per_sec': 'read',
                           'input_per_sec': 'write',
                           'mirrored_input_per_sec': 'mirrored_write'}

array_iops_mapping = {'reads_per_sec': 'read',
                      'writes_per_sec': 'write',
                      'mirrored_writes_per_sec': 'mirrored_write'}

array_bsize_mapping = {'bytes_per_read': 'read',
                       'bytes_per_write': 'write',
                       'bytes_per_mirrored_write': 'mirrored_write'}

array_qdepth_mapping = {'queue_depth': ''}

array_used_mapping = {'shared_space': 'shared', 
                      'system': 'system',
                      'volumes': 'volumes',
                      'snapshots': 'snapshots',
                      'replication': 'replication'}

array_drr_mapping = {'data_reduction': ''}

array_capacity_mapping = {'capacity': ''}

array_provisioned_mapping = {'provisioned': ''}
                        
volume_latency_mapping = array_latency_mapping
volume_bandwidth_mapping = array_bandwidth_mapping
volume_iops_mapping = array_iops_mapping

host_latency_mapping = array_latency_mapping
host_bandwidth_mapping = array_bandwidth_mapping
host_iops_mapping = array_iops_mapping

pod_latency_mapping = array_latency_mapping
pod_bandwidth_mapping = array_bandwidth_mapping
pod_iops_mapping = array_iops_mapping
