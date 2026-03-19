#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab 7: 性能优化模块
实现异步IO、缓存和算法优化
"""

import asyncio
import functools
import hashlib
from typing import Callable, TypeVar, Any, Dict, Optional
from datetime import datetime, timedelta
from functools import wraps
from concurrent.futures import ThreadPoolExecutor


T = TypeVar("T")
R = TypeVar("R")


class AsyncCache:
    """异步缓存管理器"""

    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self._lock = asyncio.Lock()

    def _make_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_str = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_str.encode()).hexdigest()

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        async with self._lock:
            if key not in self._cache:
                return None

            value, timestamp = self._cache[key]
            if datetime.now() - timestamp > timedelta(seconds=self.ttl):
                del self._cache[key]
                return None

            return value

    async def set(self, key: str, value: Any):
        """设置缓存值"""
        async with self._lock:
            self._cache[key] = (value, datetime.now())

    async def clear(self):
        """清除所有缓存"""
        async with self._lock:
            self._cache.clear()

    def cached(self, func: Callable[..., R]) -> Callable[..., R]:
        """装饰器：缓存函数结果"""

        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = self._make_key(func.__name__, *args, **kwargs)

            # 尝试获取缓存
            cached = await self.get(cache_key)
            if cached is not None:
                return cached

            # 执行函数
            result = await func(*args, **kwargs)

            # 设置缓存
            await self.set(cache_key, result)

            return result

        return wrapper


class AsyncProcessor:
    """异步处理器"""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def run_sync(self, func: Callable[..., R], *args, **kwargs) -> R:
        """在线程池中运行同步函数"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, functools.partial(func, *args, **kwargs)
        )

    async def map(self, func: Callable[[T], R], items: list) -> list:
        """并行处理多个项目"""
        tasks = [self.run_sync(func, item) for item in items]
        return await asyncio.gather(*tasks)

    async def close(self):
        """关闭线程池"""
        self.executor.shutdown(wait=True)


class BatchProcessor:
    """批处理器 - 优化大数据量处理"""

    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size

    def process(self, items: list, processor: Callable[[list], list]) -> list:
        """分批处理数据"""
        results = []

        for i in range(0, len(items), self.batch_size):
            batch = items[i : i + self.batch_size]
            batch_results = processor(batch)
            results.extend(batch_results)

        return results

    async def process_async(
        self, items: list, processor: Callable[[list], list]
    ) -> list:
        """异步分批处理"""
        batches = [
            items[i : i + self.batch_size]
            for i in range(0, len(items), self.batch_size)
        ]

        tasks = [
            asyncio.get_event_loop().run_in_executor(None, processor, batch)
            for batch in batches
        ]

        results = await asyncio.gather(*tasks)
        return [item for batch in results for item in batch]


class OptimizedAlgorithms:
    """算法优化工具类"""

    @staticmethod
    def group_by(alerts: list, key_func: Callable) -> Dict[Any, list]:
        """O(n) 分组算法 - 替代双重循环"""
        groups: Dict[Any, list] = {}
        for alert in alerts:
            key = key_func(alert)
            groups.setdefault(key, []).append(alert)
        return groups

    @staticmethod
    def find_chains(alerts: list, time_threshold: int = 300) -> list:
        """时间窗口链式检测 - 优化算法"""
        if not alerts:
            return []

        # 按时间排序
        sorted_alerts = sorted(alerts, key=lambda x: x.timestamp)

        chains = []
        current_chain = [sorted_alerts[0]]

        for i in range(1, len(sorted_alerts)):
            prev = current_chain[-1]
            curr = sorted_alerts[i]

            # 检查时间连续性
            time_diff = (curr.timestamp - prev.timestamp).total_seconds()

            if time_diff <= time_threshold:
                current_chain.append(curr)
            else:
                if len(current_chain) > 1:
                    chains.append(current_chain)
                current_chain = [curr]

        if len(current_chain) > 1:
            chains.append(current_chain)

        return chains

    @staticmethod
    def fuzzy_match(text: str, keywords: list, threshold: float = 0.6) -> Optional[str]:
        """模糊匹配算法"""
        text_lower = text.lower()

        for keyword in keywords:
            if keyword.lower() in text_lower:
                return keyword

        return None


def memoize(func: Callable[..., R]) -> Callable[..., R]:
    """简单记忆化装饰器"""
    cache: Dict = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    wrapper.cache = cache
    wrapper.clear_cache = lambda: cache.clear()

    return wrapper


def timed(func: Callable[..., R]) -> Callable[..., R]:
    """性能计时装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        elapsed = (datetime.now() - start).total_seconds()
        print(f"[TIMING] {func.__name__}: {elapsed:.3f}s")
        return result

    return wrapper
