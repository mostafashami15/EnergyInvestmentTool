"""
Cache Manager for the Energy Investment Decision Support System.

This module provides a tiered caching system to improve performance by caching
API responses and calculation results at different levels:
- Short-term cache: For API responses during user sessions (1 hour)
- Medium-term cache: For frequently accessed locations (1 day)
- Long-term cache: For slow-changing data like solar radiation (30+ days)
"""
from typing import Dict, Any, Optional, Union, Tuple, List, Callable
import time
import json
import hashlib
import os
import threading
import sqlite3
from datetime import datetime, timedelta
import logging
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('cache_manager')

class CacheManager:
    """Manages multi-tiered caching for API responses and calculation results."""
    
    def __init__(self, 
                db_path: Optional[str] = None,
                memory_cache_size: int = 1000,
                enable_memory_cache: bool = True,
                enable_disk_cache: bool = True):
        """Initialize the cache manager.
        
        Args:
            db_path: Path to SQLite database for persistent cache
            memory_cache_size: Maximum number of items in memory cache
            enable_memory_cache: Whether to use memory caching
            enable_disk_cache: Whether to use disk caching
        """
        self.memory_cache_size = memory_cache_size
        self.enable_memory_cache = enable_memory_cache
        self.enable_disk_cache = enable_disk_cache
        
        # In-memory cache (short-term)
        self.memory_cache = {}
        self.memory_cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'inserts': 0
        }
        
        # Cache locks for thread safety
        self.memory_cache_lock = threading.RLock()
        
        # Disk cache (medium/long-term)
        self.db_path = db_path or os.environ.get('CACHE_DB_PATH', 'cache.db')
        
        # Initialize disk cache if enabled
        if self.enable_disk_cache:
            self._init_disk_cache()
        
        # Cache tier configurations
        self.cache_tiers = {
            'short': {
                'ttl': 3600,  # 1 hour
                'description': 'Short-term cache for API responses during user sessions'
            },
            'medium': {
                'ttl': 86400,  # 1 day
                'description': 'Medium-term cache for frequently accessed locations'
            },
            'long': {
                'ttl': 2592000,  # 30 days
                'description': 'Long-term cache for slow-changing data like solar radiation'
            }
        }
        
        logger.info(f"Cache manager initialized with memory size: {memory_cache_size}, " + 
                    f"memory cache: {enable_memory_cache}, disk cache: {enable_disk_cache}")
    
    def _init_disk_cache(self) -> None:
        """Initialize the disk cache database."""
        # Create directory if it doesn't exist
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Create cache table if it doesn't exist
        conn = self._get_db_connection()
        try:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                tier TEXT,
                expires_at INTEGER,
                created_at INTEGER,
                access_count INTEGER DEFAULT 0,
                last_accessed_at INTEGER
            )
            """)
            
            # Create index on expires_at for efficient cleanup
            conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_cache_expires
            ON cache (expires_at)
            """)
            
            # Create stats table if it doesn't exist
            conn.execute("""
            CREATE TABLE IF NOT EXISTS cache_stats (
                tier TEXT,
                hits INTEGER DEFAULT 0,
                misses INTEGER DEFAULT 0,
                inserts INTEGER DEFAULT 0,
                evictions INTEGER DEFAULT 0,
                PRIMARY KEY (tier)
            )
            """)
            
            # Initialize stats for each tier
            for tier in self.cache_tiers.keys():
                conn.execute("""
                INSERT OR IGNORE INTO cache_stats (tier, hits, misses, inserts, evictions)
                VALUES (?, 0, 0, 0, 0)
                """, (tier,))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error initializing disk cache: {e}")
        finally:
            conn.close()
    
    def _get_db_connection(self) -> sqlite3.Connection:
        """Get a connection to the cache database.
        
        Returns:
            SQLite connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _generate_cache_key(self, 
                           namespace: str, 
                           key_components: Dict[str, Any]) -> str:
        """Generate a cache key from namespace and components.
        
        Args:
            namespace: Cache namespace (e.g., 'solar_resource', 'production_calc')
            key_components: Dictionary of values that uniquely identify the data
            
        Returns:
            Cache key string
        """
        # Sort the components for consistent key generation
        sorted_components = {k: key_components[k] for k in sorted(key_components.keys())}
        
        # Create a string representation
        key_string = f"{namespace}:{json.dumps(sorted_components, sort_keys=True)}"
        
        # Hash for shorter keys in database
        key_hash = hashlib.md5(key_string.encode('utf-8')).hexdigest()
        
        return f"{namespace}:{key_hash}"
    
    def get(self, 
           namespace: str, 
           key_components: Dict[str, Any],
           tier: str = 'short') -> Optional[Any]:
        """Get an item from the cache.
        
        Args:
            namespace: Cache namespace
            key_components: Dictionary of key components
            tier: Cache tier ('short', 'medium', or 'long')
            
        Returns:
            Cached value or None if not found
        """
        cache_key = self._generate_cache_key(namespace, key_components)
        
        # Check memory cache first if enabled
        if self.enable_memory_cache:
            with self.memory_cache_lock:
                if cache_key in self.memory_cache:
                    entry = self.memory_cache[cache_key]
                    current_time = time.time()
                    
                    # Check if entry is still valid
                    if entry['expires_at'] > current_time:
                        # Update stats
                        self.memory_cache_stats['hits'] += 1
                        
                        # Update access time & count
                        entry['last_accessed_at'] = current_time
                        entry['access_count'] += 1
                        
                        logger.debug(f"Memory cache hit for key: {cache_key}")
                        return entry['value']
                    else:
                        # Remove expired entry
                        del self.memory_cache[cache_key]
                        self.memory_cache_stats['evictions'] += 1
                
                # Memory cache miss
                self.memory_cache_stats['misses'] += 1
        
        # Check disk cache if enabled
        if self.enable_disk_cache:
            try:
                conn = self._get_db_connection()
                current_time = int(time.time())
                
                # Get entry and update access stats in one transaction
                conn.execute("BEGIN TRANSACTION")
                
                # Get entry
                cursor = conn.execute("""
                SELECT value, expires_at FROM cache
                WHERE key = ? AND expires_at > ?
                """, (cache_key, current_time))
                
                row = cursor.fetchone()
                
                if row:
                    # Update access stats
                    conn.execute("""
                    UPDATE cache
                    SET access_count = access_count + 1,
                        last_accessed_at = ?
                    WHERE key = ?
                    """, (current_time, cache_key))
                    
                    # Update tier stats
                    conn.execute("""
                    UPDATE cache_stats
                    SET hits = hits + 1
                    WHERE tier = ?
                    """, (tier,))
                    
                    conn.commit()
                    
                    # Deserialize the value
                    value = json.loads(row['value'])
                    
                    # Add to memory cache if enabled
                    if self.enable_memory_cache:
                        with self.memory_cache_lock:
                            # Check if we need to make room
                            if len(self.memory_cache) >= self.memory_cache_size:
                                # Evict least recently used item
                                lru_key = min(
                                    self.memory_cache.keys(),
                                    key=lambda k: self.memory_cache[k]['last_accessed_at']
                                )
                                del self.memory_cache[lru_key]
                                self.memory_cache_stats['evictions'] += 1
                            
                            # Add to memory cache
                            self.memory_cache[cache_key] = {
                                'value': value,
                                'expires_at': row['expires_at'],
                                'last_accessed_at': current_time,
                                'access_count': 1
                            }
                            self.memory_cache_stats['inserts'] += 1
                    
                    logger.debug(f"Disk cache hit for key: {cache_key}")
                    return value
                else:
                    # Update miss stats
                    conn.execute("""
                    UPDATE cache_stats
                    SET misses = misses + 1
                    WHERE tier = ?
                    """, (tier,))
                    
                    conn.commit()
            except Exception as e:
                logger.error(f"Error reading from disk cache: {e}")
                conn.rollback()
            finally:
                conn.close()
        
        logger.debug(f"Cache miss for key: {cache_key}")
        return None
    
    def set(self, 
           namespace: str, 
           key_components: Dict[str, Any],
           value: Any,
           tier: str = 'short') -> None:
        """Set an item in the cache.
        
        Args:
            namespace: Cache namespace
            key_components: Dictionary of key components
            value: Value to cache
            tier: Cache tier ('short', 'medium', or 'long')
        """
        if tier not in self.cache_tiers:
            raise ValueError(f"Invalid cache tier: {tier}")
        
        cache_key = self._generate_cache_key(namespace, key_components)
        ttl = self.cache_tiers[tier]['ttl']
        current_time = time.time()
        expires_at = current_time + ttl
        
        # Set in memory cache if enabled
        if self.enable_memory_cache:
            with self.memory_cache_lock:
                # Check if we need to make room
                if len(self.memory_cache) >= self.memory_cache_size and cache_key not in self.memory_cache:
                    # Evict least recently used item
                    lru_key = min(
                        self.memory_cache.keys(),
                        key=lambda k: self.memory_cache[k]['last_accessed_at']
                    )
                    del self.memory_cache[lru_key]
                    self.memory_cache_stats['evictions'] += 1
                
                # Add or update cache entry
                self.memory_cache[cache_key] = {
                    'value': value,
                    'expires_at': expires_at,
                    'last_accessed_at': current_time,
                    'access_count': 0
                }
                self.memory_cache_stats['inserts'] += 1
        
        # Set in disk cache if enabled
        if self.enable_disk_cache:
            try:
                conn = self._get_db_connection()
                current_time_int = int(current_time)
                expires_at_int = int(expires_at)
                
                # Serialize the value
                serialized_value = json.dumps(value)
                
                conn.execute("BEGIN TRANSACTION")
                
                # Insert or replace cache entry
                conn.execute("""
                INSERT OR REPLACE INTO cache 
                (key, value, tier, expires_at, created_at, access_count, last_accessed_at)
                VALUES (?, ?, ?, ?, ?, 0, ?)
                """, (cache_key, serialized_value, tier, expires_at_int, current_time_int, current_time_int))
                
                # Update tier stats
                conn.execute("""
                UPDATE cache_stats
                SET inserts = inserts + 1
                WHERE tier = ?
                """, (tier,))
                
                conn.commit()
                logger.debug(f"Set disk cache for key: {cache_key}, tier: {tier}")
            except Exception as e:
                logger.error(f"Error writing to disk cache: {e}")
                conn.rollback()
            finally:
                conn.close()
    
    def invalidate(self, 
                  namespace: str, 
                  key_components: Optional[Dict[str, Any]] = None) -> int:
        """Invalidate cache entries.
        
        Args:
            namespace: Cache namespace
            key_components: Dictionary of key components (None to invalidate all entries in namespace)
            
        Returns:
            Number of invalidated entries
        """
        invalidated_count = 0
        
        if key_components:
            # Invalidate specific entry
            cache_key = self._generate_cache_key(namespace, key_components)
            
            # Remove from memory cache if enabled
            if self.enable_memory_cache:
                with self.memory_cache_lock:
                    if cache_key in self.memory_cache:
                        del self.memory_cache[cache_key]
                        invalidated_count += 1
            
            # Remove from disk cache if enabled
            if self.enable_disk_cache:
                try:
                    conn = self._get_db_connection()
                    cursor = conn.execute("DELETE FROM cache WHERE key = ?", (cache_key,))
                    invalidated_count += cursor.rowcount
                    conn.commit()
                except Exception as e:
                    logger.error(f"Error invalidating disk cache entry: {e}")
                    conn.rollback()
                finally:
                    conn.close()
        else:
            # Invalidate all entries in namespace
            prefix = f"{namespace}:"
            
            # Remove from memory cache if enabled
            if self.enable_memory_cache:
                with self.memory_cache_lock:
                    keys_to_remove = [k for k in self.memory_cache.keys() if k.startswith(prefix)]
                    for key in keys_to_remove:
                        del self.memory_cache[key]
                    invalidated_count += len(keys_to_remove)
            
            # Remove from disk cache if enabled
            if self.enable_disk_cache:
                try:
                    conn = self._get_db_connection()
                    cursor = conn.execute("DELETE FROM cache WHERE key LIKE ?", (f"{prefix}%",))
                    invalidated_count += cursor.rowcount
                    conn.commit()
                except Exception as e:
                    logger.error(f"Error invalidating disk cache namespace: {e}")
                    conn.rollback()
                finally:
                    conn.close()
        
        logger.info(f"Invalidated {invalidated_count} cache entries for namespace: {namespace}")
        return invalidated_count
    
    def clear(self, tier: Optional[str] = None) -> int:
        """Clear the cache.
        
        Args:
            tier: Cache tier to clear (None to clear all tiers)
            
        Returns:
            Number of cleared entries
        """
        cleared_count = 0
        
        # Clear memory cache if enabled
        if self.enable_memory_cache:
            with self.memory_cache_lock:
                if tier:
                    # Can't separate tiers in memory cache, so we have to clear all
                    # and update stats for the specified tier only
                    cleared_count += len(self.memory_cache)
                    self.memory_cache.clear()
                else:
                    cleared_count += len(self.memory_cache)
                    self.memory_cache.clear()
        
        # Clear disk cache if enabled
        if self.enable_disk_cache:
            try:
                conn = self._get_db_connection()
                if tier:
                    cursor = conn.execute("DELETE FROM cache WHERE tier = ?", (tier,))
                    cleared_count += cursor.rowcount
                    
                    # Reset stats for this tier
                    conn.execute("""
                    UPDATE cache_stats
                    SET hits = 0, misses = 0, inserts = 0, evictions = 0
                    WHERE tier = ?
                    """, (tier,))
                else:
                    cursor = conn.execute("DELETE FROM cache")
                    cleared_count += cursor.rowcount
                    
                    # Reset all stats
                    conn.execute("""
                    UPDATE cache_stats
                    SET hits = 0, misses = 0, inserts = 0, evictions = 0
                    """)
                
                conn.commit()
            except Exception as e:
                logger.error(f"Error clearing disk cache: {e}")
                conn.rollback()
            finally:
                conn.close()
        
        logger.info(f"Cleared {cleared_count} cache entries" + 
                    (f" for tier: {tier}" if tier else ""))
        return cleared_count
    
    def cleanup_expired(self) -> int:
        """Clean up expired cache entries.
        
        Returns:
            Number of expired entries removed
        """
        expired_count = 0
        current_time = time.time()
        
        # Clean up memory cache if enabled
        if self.enable_memory_cache:
            with self.memory_cache_lock:
                expired_keys = [
                    k for k, v in self.memory_cache.items() 
                    if v['expires_at'] <= current_time
                ]
                for key in expired_keys:
                    del self.memory_cache[key]
                    self.memory_cache_stats['evictions'] += 1
                expired_count += len(expired_keys)
        
        # Clean up disk cache if enabled
        if self.enable_disk_cache:
            try:
                conn = self._get_db_connection()
                current_time_int = int(current_time)
                
                # Count expired entries by tier for stats
                cursor = conn.execute("""
                SELECT tier, COUNT(*) as count
                FROM cache
                WHERE expires_at <= ?
                GROUP BY tier
                """, (current_time_int,))
                
                tier_counts = {row['tier']: row['count'] for row in cursor.fetchall()}
                
                # Update eviction stats for each tier
                for tier, count in tier_counts.items():
                    conn.execute("""
                    UPDATE cache_stats
                    SET evictions = evictions + ?
                    WHERE tier = ?
                    """, (count, tier))
                
                # Delete expired entries
                cursor = conn.execute("DELETE FROM cache WHERE expires_at <= ?", (current_time_int,))
                expired_count += cursor.rowcount
                
                conn.commit()
            except Exception as e:
                logger.error(f"Error cleaning up expired disk cache entries: {e}")
                conn.rollback()
            finally:
                conn.close()
        
        logger.info(f"Cleaned up {expired_count} expired cache entries")
        return expired_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary of cache statistics
        """
        stats = {
            'memory_cache': {
                'enabled': self.enable_memory_cache,
                'size': len(self.memory_cache) if self.enable_memory_cache else 0,
                'max_size': self.memory_cache_size,
                'hits': self.memory_cache_stats['hits'],
                'misses': self.memory_cache_stats['misses'],
                'hit_ratio': (
                    self.memory_cache_stats['hits'] / 
                    (self.memory_cache_stats['hits'] + self.memory_cache_stats['misses'])
                    if (self.memory_cache_stats['hits'] + self.memory_cache_stats['misses']) > 0
                    else 0
                ),
                'inserts': self.memory_cache_stats['inserts'],
                'evictions': self.memory_cache_stats['evictions']
            },
            'disk_cache': {
                'enabled': self.enable_disk_cache,
                'tiers': {}
            }
        }
        
        # Get disk cache stats if enabled
        if self.enable_disk_cache:
            try:
                conn = self._get_db_connection()
                
                # Get stats for each tier
                cursor = conn.execute("SELECT * FROM cache_stats")
                tier_stats = cursor.fetchall()
                
                for row in tier_stats:
                    tier = row['tier']
                    hits = row['hits']
                    misses = row['misses']
                    hit_ratio = hits / (hits + misses) if (hits + misses) > 0 else 0
                    
                    # Get count and size
                    cursor = conn.execute("""
                    SELECT COUNT(*) as count, SUM(LENGTH(value)) as size
                    FROM cache
                    WHERE tier = ?
                    """, (tier,))
                    
                    count_row = cursor.fetchone()
                    count = count_row['count'] if count_row else 0
                    size = count_row['size'] if count_row else 0
                    
                    stats['disk_cache']['tiers'][tier] = {
                        'count': count,
                        'size_bytes': size,
                        'hits': hits,
                        'misses': misses,
                        'hit_ratio': hit_ratio,
                        'inserts': row['inserts'],
                        'evictions': row['evictions'],
                        'ttl_seconds': self.cache_tiers[tier]['ttl'],
                        'description': self.cache_tiers[tier]['description']
                    }
                
                # Get total stats
                cursor = conn.execute("""
                SELECT COUNT(*) as count, SUM(LENGTH(value)) as size
                FROM cache
                """)
                
                total_row = cursor.fetchone()
                total_count = total_row['count'] if total_row else 0
                total_size = total_row['size'] if total_row else 0
                
                # Sum hits, misses, inserts, evictions across all tiers
                cursor = conn.execute("""
                SELECT 
                    SUM(hits) as total_hits,
                    SUM(misses) as total_misses,
                    SUM(inserts) as total_inserts,
                    SUM(evictions) as total_evictions
                FROM cache_stats
                """)
                
                totals_row = cursor.fetchone()
                total_hits = totals_row['total_hits'] if totals_row else 0
                total_misses = totals_row['total_misses'] if totals_row else 0
                total_hit_ratio = (
                    total_hits / (total_hits + total_misses)
                    if (total_hits + total_misses) > 0
                    else 0
                )
                
                stats['disk_cache']['total'] = {
                    'count': total_count,
                    'size_bytes': total_size,
                    'hits': total_hits,
                    'misses': total_misses,
                    'hit_ratio': total_hit_ratio,
                    'inserts': totals_row['total_inserts'] if totals_row else 0,
                    'evictions': totals_row['total_evictions'] if totals_row else 0
                }
            except Exception as e:
                logger.error(f"Error getting disk cache stats: {e}")
                stats['disk_cache']['error'] = str(e)
            finally:
                conn.close()
        
        return stats
    
    def cached(self, 
              namespace: str,
              tier: str = 'short',
              key_generator: Optional[Callable[[list, dict], Dict[str, Any]]] = None):
        """Decorator to cache function results.
        
        Args:
            namespace: Cache namespace
            tier: Cache tier
            key_generator: Function to generate key components from args and kwargs
                           (default: use all args and kwargs)
        
        Returns:
            Decorator function
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate key components
                if key_generator:
                    key_components = key_generator(args, kwargs)
                else:
                    # Create key from args and kwargs
                    key_components = {}
                    
                    # Add positional args
                    for i, arg in enumerate(args):
                        if isinstance(arg, (str, int, float, bool, type(None))):
                            key_components[f"arg_{i}"] = arg
                        else:
                            # For complex objects, use their string representation
                            key_components[f"arg_{i}"] = str(arg)
                    
                    # Add keyword args
                    for key, value in kwargs.items():
                        if isinstance(value, (str, int, float, bool, type(None))):
                            key_components[key] = value
                        else:
                            # For complex objects, use their string representation
                            key_components[key] = str(value)
                
                # Try to get from cache
                cached_result = self.get(namespace, key_components, tier)
                if cached_result is not None:
                    return cached_result
                
                # Call the function
                result = func(*args, **kwargs)
                
                # Cache the result
                self.set(namespace, key_components, result, tier)
                
                return result
            return wrapper
        return decorator

# Example usage
if __name__ == "__main__":
    # Create cache manager
    cache = CacheManager()
    
    # Set an item in the cache
    cache.set(
        namespace="solar_resource",
        key_components={"lat": 39.7392, "lon": -104.9903},
        value={"ghi": 5.5, "dni": 6.2},
        tier="long"
    )
    
    # Get the item from cache
    cached_value = cache.get(
        namespace="solar_resource",
        key_components={"lat": 39.7392, "lon": -104.9903},
        tier="long"
    )
    
    print("Cached value:", cached_value)
    
    # Example with decorator
    @cache.cached(namespace="test_function", tier="medium")
    def test_function(x, y):
        print(f"Calculating {x} + {y}...")
        return x + y
    
    # First call will calculate
    result1 = test_function(5, 10)
    print("Result 1:", result1)
    
    # Second call will use cache
    result2 = test_function(5, 10)
    print("Result 2:", result2)
    
    # Get cache stats
    stats = cache.get_stats()
    print("Cache stats:", json.dumps(stats, indent=2))