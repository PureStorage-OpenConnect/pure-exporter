import urllib3
import six
from purity_fb import PurityFb, rest

# disable ceritificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FlashBlade():
    """
    Base class for FlashBlade Prometheus array info
    """
    def __init__(self, endpoint, api_token):
        # self.fb = PurityFb(endpoint, conn_timeo=ctimeo, read_timeo=rtimeo,
        #                   retries=retries)
        self.flashblade = PurityFb(host=endpoint)
        self.flashblade.disable_verify_ssl()
        self.flashblade._api_client.user_agent = 'Purity_FB_Prometheus_exporter/1.0'
        self.flashblade.request_timeout = urllib3.Timeout(connect=2.0, read=60.0)
        self.flashblade.login(api_token)
        self.filesystems = None
        self.buckets = None
        self.array_performance = {}
        self.array_performance['nfs'] = None
        self.array_performance['http'] = None
        self.array_performance['s3'] = None
        self.array_performance['smb'] = None
        self.array_specific_perf = {}
        self.array_specific_perf['nfs'] = None
        self.array_specific_perf['http'] = None
        self.array_specific_perf['s3'] = None
        self.array_space = None
        self.nfs_filesystems_performance = None
        self.buckets_performance = None
        self.buckets_replica_links = None
        self.filesystems_replica_links = None
        self.users_usage = None
        self.groups_usage = None
        self.clients_performance = None

    def __del__(self):
        if self.flashblade is not None:
            self.flashblade.logout()

    def get_array_info(self):
        return self.flashblade.arrays.list_arrays().items[0]

    def get_open_alerts(self):
        return self.flashblade.alerts.list_alerts(filter="state='open'").items

    def get_hardware_status(self):
        return self.flashblade.hardware.list_hardware().items

    def get_array_performance(self, proto):
        if self.array_performance[proto] is None:
            self.array_performance[proto] = self.flashblade.arrays.list_arrays_performance(protocol=proto).items[0]
        return self.array_performance[proto]

    def get_array_specific_performance(self, proto):
        if proto == 'http':
            if self.array_specific_perf['http'] is None:
                self.array_specific_perf['http'] = self.flashblade.arrays.list_arrays_http_specific_performance().items[0]
            return self.array_specific_perf['http']
        if proto == 'nfs':
            if self.array_specific_perf['nfs'] is None:
                self.array_specific_perf['nfs'] = self.flashblade.arrays.list_arrays_nfs_specific_performance().items[0]
            return self.array_specific_perf['nfs']
        if proto == 's3':
            if self.array_specific_perf['s3'] is None:
                self.array_specific_perf['s3'] = self.flashblade.arrays.list_arrays_s3_specific_performance().items[0]
            return self.array_specific_perf['s3']

    def get_filesystems(self):
        if self.filesystems is None:
            self.filesystems = self.flashblade.file_systems.list_file_systems().items
        return self.filesystems

    def get_array_space(self):
        if self.array_space is None:
            self.array_space = self.flashblade.arrays.list_arrays_space().items[0]
        return self.array_space

    def get_buckets(self):
        if self.buckets is None:
            self.buckets = self.flashblade.buckets.list_buckets().items
        return self.buckets

    def get_nfs_filesystems_performance(self):
        if self.nfs_filesystems_performance is None:
            self.nfs_filesystems_performance = []
            for f in self.get_filesystems():
                try:
                   self.nfs_filesystems_performance.append(
                           self.flashblade.file_systems.list_file_systems_performance(protocol='nfs',names=[f.name]).items[0])
                except Exception as e:
                    continue
        return self.nfs_filesystems_performance

    def get_buckets_performance(self):
        if self.buckets_performance is None:
            self.buckets_performance = []
            for b in self.get_buckets():
                self.buckets_performance.append(
                        self.flashblade.buckets.list_buckets_s3_specific_performance(names=[b.name]).items[0])
        return self.buckets_performance

    def get_bucket_replica_links(self):
        if self.buckets_replica_links is None:
            self.buckets_replica_links = self.flashblade.bucket_replica_links.list_bucket_replica_links().items
        return self.buckets_replica_links

    def get_filesystem_replica_links(self):
        if self.filesystems_replica_links is None:
            self.filesystems_replica_links = self.flashblade.file_system_replica_links.list_file_system_replica_links().items
        return self.filesystems_replica_links

    def get_users_usage(self):
        if self.users_usage is None:
            self.users_usage = []
            for f in self.get_filesystems():
                uu = self.flashblade.usage_users.list_user_usage(file_system_names=[f.name]).items
                if len(uu) == 0:
                    continue
                self.users_usage = self.users_usage + uu
        return self.users_usage

    def get_groups_usage(self):
        if self.groups_usage is None:
            self.groups_usage = []
            for f in self.get_filesystems():
                gu = self.flashblade.usage_groups.list_group_usage(file_system_names=[f.name]).items
                if len(gu) == 0:
                    continue
                self.groups_usage = self.groups_usage + gu
        return self.groups_usage

    def get_clients_performance(self):
        if self.clients_performance is None:
            self.clients_performance = self.flashblade.arrays.list_clients_performance().items
        return self.clients_performance
