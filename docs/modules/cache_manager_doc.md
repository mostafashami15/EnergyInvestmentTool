# Data Caching System Documentation

## Overview

The Data Caching System implemented in the Energy Investment Decision Support System provides a multi-tiered caching solution that optimizes performance by reducing redundant API calls and calculations. The system is designed to cache data at different levels based on the data's update frequency and access patterns.

## Key Features

1. **Multi-tiered caching**: Three-tier caching strategy with different expiration times
2. **Memory and disk caching**: Combines fast in-memory cache with persistent disk storage
3. **Namespace organization**: Logical grouping of cached data by functional area
4. **Cache invalidation**: Targeted or broad-based cache clearing capabilities
5. **Cache statistics**: Comprehensive metrics for cache performance analysis
6. **Decorator support**: Easy integration with existing functions via decorator pattern

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Cache Manager                        │
├────────────────┬───────────────────┬────────────────────┤
│  Memory Cache  │    Disk Cache     │  Cache Control     │
│  (Short-term)  │  (Medium/Long)    │     & Stats        │
├────────────────┼───────────────────┼────────────────────┤
│ Fast access    │ SQLite backing    │ Admin interface    │
│ Non-persistent │ Persistent store  │ Monitoring tools   │
│ Size limited   │ Larger capacity   │ Performance metrics│
└────────────────┴───────────────────┴────────────────────┘
                           │
          ┌────────────────┼─────────────────┐
          │                │                 │
┌─────────▼──────┐  ┌──────▼───────┐  ┌──────▼───────┐
│  Short-term    │  │  Medium-term │  │  Long-term   │
│  Cache Tier    │  │  Cache Tier  │  │  Cache Tier  │
├────────────────┤  ├──────────────┤  ├──────────────┤
│ TTL: 1 hour    │  │ TTL: 1 day   │  │ TTL: 30 days │
│ API responses  │  │ Location data│  │ Solar data   │
│ Session data   │  │ Utility rates│  │ Reference    │
└────────────────┘  └──────────────┘  └──────────────┘
```

## Core Components

### CacheManager Class

The `CacheManager` class is the main entry point for the caching system. It manages both memory and disk caches, handles cache tiers, and provides methods for cache operations.

```python
class CacheManager:
    """Manages multi-tiered caching for API responses and calculation results."""
    
    def __init__(self, 
                db_path=None,
                memory_cache_size=1000,
                enable_memory_cache=True,
                enable_disk_cache=True):
        """Initialize the cache manager.
        
        Args:
            db_path: Path to SQLite database for persistent cache
            memory_cache_size: Maximum number of items in memory cache
            enable_memory_cache: Whether to use memory caching
            enable_disk_cache: Whether to use disk caching
        """
        # Implementation...
```

### Cache Tiers

The system defines three cache tiers with different time-to-live (TTL) values:

```python
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
```

### Memory Cache Implementation

The memory cache provides fast access to frequently used data but is limited in size and not persistent:

```python
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
```

Memory cache entries have the following structure:
```python
memory_cache[cache_key] = {
    'value': actual_value,
    'expires_at': expiration_timestamp,
    'last_accessed_at': last_access_time,
    'access_count': access_count
}
```

### Disk Cache Implementation

The disk cache uses SQLite for persistent storage of cache entries:

```python
def _init_disk_cache(self) -> None:
    """Initialize the disk cache database."""
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
    finally:
        conn.close()
```

## Key Operations

### Cache Key Generation

Cache keys are generated from a namespace and key components:

```python
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
```

### Getting Cached Items

The `get` method retrieves items from the cache:

```python
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
        # Memory cache lookup implementation...
    
    # Check disk cache if enabled
    if self.enable_disk_cache:
        # Disk cache lookup implementation...
    
    return None  # Not found in any cache
```

### Setting Cached Items

The `set` method adds or updates items in the cache:

```python
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
        # Memory cache update implementation...
    
    # Set in disk cache if enabled
    if self.enable_disk_cache:
        # Disk cache update implementation...
```

### Cache Invalidation

The system provides methods for invalidating cache entries:

```python
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
        # Remove from disk cache if enabled
    else:
        # Invalidate all entries in namespace
        prefix = f"{namespace}:"
        
        # Remove from memory cache if enabled
        # Remove from disk cache if enabled
    
    return invalidated_count
```

### Cache Cleanup

The system provides a method for removing expired entries:

```python
def cleanup_expired(self) -> int:
    """Clean up expired cache entries.
    
    Returns:
        Number of expired entries removed
    """
    expired_count = 0
    current_time = time.time()
    
    # Clean up memory cache if enabled
    if self.enable_memory_cache:
        # Memory cache cleanup implementation...
    
    # Clean up disk cache if enabled
    if self.enable_disk_cache:
        # Disk cache cleanup implementation...
    
    return expired_count
```

### Cache Statistics

The system tracks cache performance statistics:

```python
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
        # Disk cache statistics collection implementation...
    
    return stats
```

## Cache Decorator

The system includes a decorator for easily caching function results:

```python
def cached(self, 
          namespace: str,
          tier: str = 'short',
          key_generator: Optional[Callable] = None):
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
```

## API Integration

The caching system is integrated with the API through middleware:

```python
def cache_middleware(namespace, tier='short'):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Check if path parameters are in kwargs
            params = {}
            for key, value in kwargs.items():
                if key != 'user_id' and key != 'username':  # Skip auth params
                    params[key] = value
                    
            # Add query parameters from request
            for key, value in request.args.items():
                params[key] = value
                
            # For POST/PUT requests, add a hash of the body
            if request.method in ['POST', 'PUT'] and request.is_json:
                body_hash = hashlib.md5(json.dumps(request.get_json(), sort_keys=True).encode()).hexdigest()
                params['body_hash'] = body_hash
            
            # Try to get cached response
            cached_response = cache_manager.get(namespace, params, tier)
            if cached_response:
                return jsonify(cached_response)
            
            # Call the original function
            result = f(*args, **kwargs)
            
            # Cache the result if it's a JSON response
            if isinstance(result, tuple):
                response, status_code = result
                if status_code == 200 and hasattr(response, 'get_json'):
                    cache_manager.set(namespace, params, response.get_json(), tier)
            else:
                if hasattr(result, 'get_json'):
                    cache_manager.set(namespace, params, result.get_json(), tier)
            
            return result
        return wrapped
    return decorator
```

## Admin Interface Endpoints

The system provides API endpoints for cache administration:

```python
@app.route('/api/admin/cache/stats', methods=['GET'])
@token_required
def get_cache_stats(user_id, username):
    """Get cache statistics."""
    # Check if user is admin
    is_admin = True  # Replace with actual admin check
    if not is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    stats = cache_manager.get_stats()
    return jsonify(stats)

@app.route('/api/admin/cache/clear', methods=['POST'])
@token_required
def clear_cache(user_id, username):
    """Clear the cache."""
    # Check if user is admin
    is_admin = True  # Replace with actual admin check
    if not is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    tier = data.get('tier') if data else None
    
    count = cache_manager.clear(tier)
    return jsonify({'success': True, 'count': count})

@app.route('/api/admin/cache/invalidate', methods=['POST'])
@token_required
def invalidate_cache(user_id, username):
    """Invalidate cache entries by namespace."""
    # Check if user is admin
    is_admin = True  # Replace with actual admin check
    if not is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    if not data or 'namespace' not in data:
        return jsonify({'error': 'Namespace is required'}), 400
    
    namespace = data['namespace']
    key_components = data.get('key_components')
    
    count = cache_manager.invalidate(namespace, key_components)
    return jsonify({'success': True, 'count': count})

@app.route('/api/admin/cache/cleanup', methods=['POST'])
@token_required
def cleanup_cache(user_id, username):
    """Clean up expired cache entries."""
    # Check if user is admin
    is_admin = True  # Replace with actual admin check
    if not is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    count = cache_manager.cleanup_expired()
    return jsonify({'success': True, 'count': count})
```

## Frontend Admin Interface

A `CacheMonitoring` component provides a visual interface for monitoring and managing the cache:

```jsx
const CacheMonitoring = ({ isAdmin = false }) => {
  const { authFetch, isAuthenticated } = useAuth();
  const [cacheStats, setCacheStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAction, setSelectedAction] = useState(null);
  const [actionTier, setActionTier] = useState('all');
  const [actionNamespace, setActionNamespace] = useState('');
  const [actionSuccess, setActionSuccess] = useState(null);
  const [refreshInterval, setRefreshInterval] = useState(0);
  const [refreshTimer, setRefreshTimer] = useState(null);

  // Colors for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];
  
  // Fetch cache statistics
  const fetchCacheStats = async () => {
    // Implementation...
  };
  
  // Handle cache actions (clear, invalidate, cleanup)
  const handleCacheAction = async () => {
    // Implementation...
  };
  
  // Toggle automatic refresh
  const toggleRefresh = (interval) => {
    // Implementation...
  };
  
  // Component UI implementation...
};
```

The component provides:
1. Visual statistics display with charts
2. Cache tier information
3. Cache management actions
4. Real-time monitoring capability

## Caching Strategy Guide

### What to Cache

1. **Short-term Cache (1 hour)**:
   - API responses during user sessions
   - Calculation results that may be repeated in a short time
   - Form input validation results

2. **Medium-term Cache (1 day)**:
   - Location-specific data that changes infrequently
   - Utility rate information
   - User preference data

3. **Long-term Cache (30 days)**:
   - Solar radiation data (changes seasonally, not daily)
   - Geographic information
   - Reference data (system components, etc.)

### Using Cache Tiers Appropriately

```python
# API data that changes frequently - short term
@cache_middleware('weather_data', 'short')
def get_weather_data():
    # Implementation...

# Location-specific data that changes occasionally - medium term
@cache_middleware('utility_rates', 'medium')
def get_utility_rates():
    # Implementation...

# Solar resource data that rarely changes - long term
@cache_middleware('solar_resource', 'long')
def get_solar_resource():
    # Implementation...
```

### Using the Cached Decorator

Directly cache function results using the decorator:

```python
@cache_manager.cached(namespace="production_calculation", tier="medium")
def calculate_solar_production(lat, lon, system_capacity, module_type, losses, array_type, tilt, azimuth):
    # Expensive calculation implementation...
    return result
```

### Custom Key Generation

For complex functions, use custom key generation:

```python
def custom_key_generator(args, kwargs):
    # Extract only the parameters that affect the calculation result
    lat = kwargs.get('lat', args[0] if args else None)
    lon = kwargs.get('lon', args[1] if len(args) > 1 else None)
    capacity = kwargs.get('system_capacity', args[2] if len(args) > 2 else None)
    
    return {
        'lat': round(lat, 4),  # Round to reduce key variants
        'lon': round(lon, 4),
        'capacity': capacity
    }

@cache_manager.cached(
    namespace="solar_calculation", 
    tier="medium",
    key_generator=custom_key_generator
)
def calculate_solar_production(lat, lon, system_capacity, **kwargs):
    # Implementation...
```

## Performance Considerations

### Memory Usage

1. **Memory Cache Size**: Set an appropriate memory cache size based on available RAM.
2. **LRU Eviction**: Least Recently Used items are evicted when cache reaches capacity.
3. **Monitoring**: Track memory usage through cache statistics.

### Disk Usage

1. **Database Size**: Monitor the size of the SQLite database file.
2. **Regular Cleanup**: Schedule regular cleanup of expired entries.
3. **Value Serialization**: Large values are serialized to JSON for storage.

### Thread Safety

1. **Thread Locks**: Memory cache operations are protected by a reentrant lock.
2. **Database Transactions**: SQLite operations use transactions for consistency.
3. **Atomic Operations**: Cache updates are performed atomically.

## Best Practices

1. **Define Clear Namespaces**: Use descriptive namespaces for different data types.
2. **Choose Appropriate Tiers**: Select cache tiers based on data update frequency.
3. **Regular Maintenance**: Schedule regular cache cleanup to prevent bloat.
4. **Monitor Performance**: Track hit ratios and adjust caching strategy accordingly.
5. **Invalidate Selectively**: Target specific namespaces or entries for invalidation.

## Example Usage Patterns

### Caching API Responses

```python
@app.route('/api/solar-resource', methods=['GET'])
@cache_middleware('solar_resource', 'long')  # Cache solar resource data for 30 days
def get_solar_resource():
    # Get parameters from request
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid latitude or longitude parameters'}), 400
    
    try:
        # Use calculation engine to fetch solar resource data
        nrel_data = calculation_engine.nrel.get_solar_resource(lat, lon)
        
        # Return data
        return jsonify(nrel_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Caching Calculation Results

```python
@app.route('/api/calculate-production', methods=['POST'])
@cache_middleware('production_calculation', 'medium')  # Cache calculations for 1 day
def calculate_production():
    # Get JSON data from request
    try:
        data = request.get_json()
        
        # Extract required parameters
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        system_capacity = float(data.get('systemCapacity', 4.0))
        module_type = int(data.get('moduleType', 1))
        array_type = int(data.get('arrayType', 1))
        losses = float(data.get('losses', 14.0))
        tilt = float(data.get('tilt', 20.0))
        azimuth = float(data.get('azimuth', 180.0))
        data_source = data.get('dataSource', 'both')
        
    except (TypeError, ValueError) as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    
    try:
        # Use calculation engine to calculate production
        production_data = calculation_engine.calculate_solar_production(
            lat, lon, system_capacity, module_type, losses, 
            array_type, tilt, azimuth, data_source
        )
        
        # Return data
        return jsonify(production_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Directly Caching Function Results

```python
# Utility function to get solar data with caching
@cache_manager.cached(namespace="solar_data", tier="long")
def get_solar_data_for_location(lat, lon):
    # Make external API call to get solar data
    response = requests.get(f"{NREL_API_URL}?lat={lat}&lon={lon}&api_key={API_KEY}")
    
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}")
    
    return response.json()
```

## Conclusion

The Data Caching System provides a comprehensive solution for optimizing the performance of the Energy Investment Decision Support System. By implementing a multi-tiered approach with both memory and disk caching, the system reduces redundant API calls, speeds up calculations, and improves the overall user experience. The integration with the API through middleware and the decorator pattern makes it easy to apply caching to existing code with minimal changes.