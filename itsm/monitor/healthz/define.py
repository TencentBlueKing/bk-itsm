# -*- coding: utf-8 -*-

redis_metrics = [
    {
        "category": "redis",
        "collect_type": "backend",
        "description": "Redis 状态",
        "collect_metric": "redis.status",
        "solution": "",
        "node_name": "redis",
        "metric_alias": "redis.status",
        "collect_args": "{}",
    },
    {
        "category": "redis",
        "collect_type": "backend",
        "description": "Redis 读写状态",
        "collect_metric": "redis.write_and_read.status",
        "solution": "",
        "node_name": "redis",
        "metric_alias": "redis.write_and_read.status",
        "collect_args": "{}",
    },
]

mysql_metrics = [
    {
        "category": "database",
        "collect_type": "backend",
        "description": "数据库状态",
        "collect_metric": "database.status",
        "solution": "",
        "node_name": "mysql",
        "metric_alias": "database.status",
        "collect_args": "{}",
    },
]

rabbitmq_metrics = [
    {
        "category": "rabbitmq",
        "collect_type": "backend",
        "description": "rabbitmq 链接状态",
        "collect_metric": "rabbitmq.status",
        "solution": "",
        "node_name": "rabbitmq",
        "metric_alias": "rabbitmq.status",
        "collect_args": "{}",
    }
]

celery_metrics = [
    {
        "category": "celery_worker",
        "collect_type": "backend",
        "description": "celery worker 状态",
        "collect_metric": "celery_worker.status",
        "solution": "",
        "node_name": "celery_worker",
        "metric_alias": "celery_worker.status",
        "collect_args": "{}",
    }
]

METRICS = redis_metrics + mysql_metrics + rabbitmq_metrics + celery_metrics
