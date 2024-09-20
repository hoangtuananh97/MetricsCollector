from collections import OrderedDict


class SyncMetricsStorage:
    def __init__(self):
        self.metrics = OrderedDict()

    def add_metrics(self, func_name, data):
        if func_name not in self.metrics:
            self.metrics[func_name] = {'execution_time': 0, 'call_count': 0, 'error_count': 0}

        # Update metrics
        self.metrics[func_name]['execution_time'] += data['execution_time']
        self.metrics[func_name]['call_count'] += data['call_count']
        self.metrics[func_name]['error_count'] += data['error_count']

    def get_all_metrics(self):
        return dict(self.metrics)

    def is_full(self, max_size=100):
        return len(self.metrics) >= max_size

    def clear_metrics(self):
        self.metrics.clear()
