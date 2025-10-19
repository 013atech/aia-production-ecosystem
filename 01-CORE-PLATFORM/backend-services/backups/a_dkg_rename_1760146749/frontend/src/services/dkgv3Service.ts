/**
 * DKG v3 Professional API Service
 * ===============================
 *
 * Enterprise-grade service for DKG v3 knowledge graph API integration
 * Optimized for sub-30ms performance with intelligent caching and error handling
 *
 * Multi-Agent Team Coordination:
 * - Cryptography Agent: Authentication and security
 * - Analytics Agent: Performance monitoring and metrics
 * - Knowledge Orchestrator: Query optimization and routing
 * - Software Development Agent: Service architecture and patterns
 */

import {
  DKGv3Config,
  KnowledgeAtomRequest,
  KnowledgeAtomResponse,
  PersonalizationRequest,
  PersonalizationResponse,
  SemanticSearchRequest,
  SemanticSearchResponse,
  GraphTraversalRequest,
  GraphTraversalResponse,
  InsightsRequest,
  InsightsResponse,
  LearningPathRequest,
  LearningPathResponse,
  AnalyticsRequest,
  AnalyticsResponse,
  ExportRequest,
  ExportResponse,
  KnowledgeStatusResponse,
  DKGv3HealthResponse,
  WebSocketMessage,
  WebSocketResponse,
  PerformanceMetrics,
  APIError,
  BatchRequest,
  BatchResponse,
  CacheManager,
  PerformanceOptimizer
} from '../types/dkg-v3';

/**
 * Advanced cache manager with TTL and intelligent eviction
 */
class AdvancedCacheManager implements CacheManager {
  private cache = new Map<string, {
    data: any;
    timestamp: number;
    ttl: number;
    accessCount: number;
    lastAccessed: number;
  }>();
  private maxSize = 1000;
  private cleanupInterval: NodeJS.Timeout;

  constructor(maxSize = 1000, cleanupIntervalMs = 60000) {
    this.maxSize = maxSize;
    this.cleanupInterval = setInterval(() => this.cleanup(), cleanupIntervalMs);
  }

  async get<T>(key: string): Promise<T | null> {
    const entry = this.cache.get(key);
    if (!entry) return null;

    const now = Date.now();
    if (now > entry.timestamp + entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    // Update access statistics
    entry.accessCount++;
    entry.lastAccessed = now;

    return entry.data;
  }

  async set<T>(key: string, data: T, ttl = 300000): Promise<void> {
    const now = Date.now();

    // Evict least recently used entries if cache is full
    if (this.cache.size >= this.maxSize) {
      this.evictLRU();
    }

    this.cache.set(key, {
      data,
      timestamp: now,
      ttl,
      accessCount: 1,
      lastAccessed: now
    });
  }

  async invalidate(key: string): Promise<void> {
    this.cache.delete(key);
  }

  async clear(): Promise<void> {
    this.cache.clear();
  }

  private evictLRU(): void {
    let oldestKey = '';
    let oldestTime = Date.now();

    for (const [key, entry] of this.cache.entries()) {
      if (entry.lastAccessed < oldestTime) {
        oldestTime = entry.lastAccessed;
        oldestKey = key;
      }
    }

    if (oldestKey) {
      this.cache.delete(oldestKey);
    }
  }

  private cleanup(): void {
    const now = Date.now();
    const expiredKeys: string[] = [];

    for (const [key, entry] of this.cache.entries()) {
      if (now > entry.timestamp + entry.ttl) {
        expiredKeys.push(key);
      }
    }

    expiredKeys.forEach(key => this.cache.delete(key));
  }

  getStats() {
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      entries: Array.from(this.cache.entries()).map(([key, entry]) => ({
        key,
        accessCount: entry.accessCount,
        lastAccessed: new Date(entry.lastAccessed).toISOString(),
        ttl: entry.ttl
      }))
    };
  }

  destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
    }
    this.clear();
  }
}

/**
 * Performance optimizer for DKG v3 queries
 */
class DKGv3PerformanceOptimizer implements PerformanceOptimizer {
  private queryHistory: Map<string, PerformanceMetrics[]> = new Map();

  async optimize_query(query: any): Promise<any> {
    // Implement query optimization strategies
    const optimizedQuery = { ...query };

    // Limit result sets for performance
    if (optimizedQuery.limit && optimizedQuery.limit > 100) {
      optimizedQuery.limit = 100;
    }

    // Add performance hints
    optimizedQuery._performance_hint = 'sub_30ms_target';

    return optimizedQuery;
  }

  get_cache_strategy(query_type: any): string {
    const strategies = {
      knowledge_atoms: 'aggressive', // 5 minutes
      semantic_search: 'moderate', // 2 minutes
      personalization: 'conservative', // 10 minutes
      graph_traversal: 'moderate', // 3 minutes
      insights_generation: 'conservative', // 15 minutes
      learning_paths: 'conservative', // 30 minutes
      analytics: 'aggressive' // 1 hour
    };

    return strategies[query_type as keyof typeof strategies] || 'moderate';
  }

  estimate_response_time(query: any): number {
    // Estimate response time based on query complexity
    let estimatedTime = 20; // Base 20ms

    if (query.limit > 50) estimatedTime += 5;
    if (query.include_relationships) estimatedTime += 3;
    if (query.semantic_similarity_threshold < 0.8) estimatedTime += 7;

    return Math.min(estimatedTime, 30); // Cap at 30ms target
  }

  get_optimization_recommendations(): string[] {
    return [
      'Enable aggressive caching for frequent queries',
      'Use pagination for large result sets',
      'Implement query debouncing for search',
      'Pre-warm cache for popular content',
      'Use WebSocket for real-time updates'
    ];
  }

  recordQueryPerformance(queryType: string, metrics: PerformanceMetrics): void {
    if (!this.queryHistory.has(queryType)) {
      this.queryHistory.set(queryType, []);
    }

    const history = this.queryHistory.get(queryType)!;
    history.push(metrics);

    // Keep only last 100 entries per query type
    if (history.length > 100) {
      history.shift();
    }
  }

  getPerformanceStats(queryType?: string): any {
    if (queryType) {
      const history = this.queryHistory.get(queryType) || [];
      if (history.length === 0) return null;

      const avgResponseTime = history.reduce((sum, m) => sum + m.query_time_ms, 0) / history.length;
      const cacheHitRate = history.filter(m => m.cache_hit).length / history.length;

      return {
        queryType,
        avgResponseTime,
        cacheHitRate,
        totalQueries: history.length,
        sub30msAchievement: history.filter(m => m.query_time_ms < 30).length / history.length
      };
    }

    // Return stats for all query types
    const allStats: any = {};
    for (const [type, history] of this.queryHistory.entries()) {
      allStats[type] = this.getPerformanceStats(type);
    }
    return allStats;
  }
}

/**
 * WebSocket manager for real-time updates
 */
class DKGv3WebSocketManager {
  private connections = new Map<string, WebSocket>();
  private subscribers = new Map<string, Set<(data: WebSocketResponse) => void>>();
  private reconnectAttempts = new Map<string, number>();
  private maxReconnectAttempts = 5;

  connect(clientId: string, wsUrl: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const ws = new WebSocket(`${wsUrl}/${clientId}`);

        ws.onopen = () => {
          this.connections.set(clientId, ws);
          this.reconnectAttempts.set(clientId, 0);
          console.log(`DKG v3 WebSocket connected: ${clientId}`);
          resolve();
        };

        ws.onmessage = (event) => {
          try {
            const data: WebSocketResponse = JSON.parse(event.data);
            this.notifySubscribers(clientId, data);
          } catch (error) {
            console.error('WebSocket message parsing error:', error);
          }
        };

        ws.onclose = (event) => {
          console.log(`DKG v3 WebSocket closed: ${clientId}`, event.code, event.reason);
          this.connections.delete(clientId);

          // Attempt reconnection if not intentional
          if (event.code !== 1000) {
            this.attemptReconnection(clientId, wsUrl);
          }
        };

        ws.onerror = (error) => {
          console.error(`DKG v3 WebSocket error: ${clientId}`, error);
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect(clientId: string): void {
    const ws = this.connections.get(clientId);
    if (ws) {
      ws.close(1000, 'Client disconnect');
      this.connections.delete(clientId);
      this.subscribers.delete(clientId);
      this.reconnectAttempts.delete(clientId);
    }
  }

  subscribe(clientId: string, callback: (data: WebSocketResponse) => void): () => void {
    if (!this.subscribers.has(clientId)) {
      this.subscribers.set(clientId, new Set());
    }

    this.subscribers.get(clientId)!.add(callback);

    // Return unsubscribe function
    return () => {
      const callbacks = this.subscribers.get(clientId);
      if (callbacks) {
        callbacks.delete(callback);
        if (callbacks.size === 0) {
          this.subscribers.delete(clientId);
        }
      }
    };
  }

  send(clientId: string, message: WebSocketMessage): boolean {
    const ws = this.connections.get(clientId);
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
      return true;
    }
    return false;
  }

  isConnected(clientId: string): boolean {
    const ws = this.connections.get(clientId);
    return ws?.readyState === WebSocket.OPEN;
  }

  private notifySubscribers(clientId: string, data: WebSocketResponse): void {
    const callbacks = this.subscribers.get(clientId);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('WebSocket subscriber callback error:', error);
        }
      });
    }
  }

  private async attemptReconnection(clientId: string, wsUrl: string): Promise<void> {
    const attempts = this.reconnectAttempts.get(clientId) || 0;
    if (attempts >= this.maxReconnectAttempts) {
      console.error(`Max reconnection attempts reached for ${clientId}`);
      return;
    }

    const delay = Math.pow(2, attempts) * 1000; // Exponential backoff
    console.log(`Attempting to reconnect ${clientId} in ${delay}ms (attempt ${attempts + 1})`);

    setTimeout(async () => {
      try {
        this.reconnectAttempts.set(clientId, attempts + 1);
        await this.connect(clientId, wsUrl);
      } catch (error) {
        console.error(`Reconnection failed for ${clientId}:`, error);
      }
    }, delay);
  }

  getConnectionStats() {
    return {
      activeConnections: this.connections.size,
      totalSubscribers: Array.from(this.subscribers.values()).reduce((sum, set) => sum + set.size, 0),
      connectionDetails: Array.from(this.connections.entries()).map(([clientId, ws]) => ({
        clientId,
        readyState: ws.readyState,
        reconnectAttempts: this.reconnectAttempts.get(clientId) || 0
      }))
    };
  }
}

/**
 * Main DKG v3 Professional Service
 */
export class DKGv3Service {
  private config: DKGv3Config;
  private cache: AdvancedCacheManager;
  private optimizer: DKGv3PerformanceOptimizer;
  private wsManager: DKGv3WebSocketManager;
  private requestInterceptors: Array<(config: RequestInit) => RequestInit> = [];
  private responseInterceptors: Array<(response: Response) => Response> = [];

  constructor(config: Partial<DKGv3Config> = {}) {
    this.config = {
      api_base_url: process.env.REACT_APP_DKG_API_URL || 'http://localhost:8000/api/v1/knowledge',
      websocket_url: process.env.REACT_APP_DKG_WS_URL || 'ws://localhost:8000/api/v1/knowledge/ws',
      auth_token: '',
      cache_ttl: 300000,
      retry_attempts: 3,
      timeout_ms: 30000,
      ...config
    };

    this.cache = new AdvancedCacheManager();
    this.optimizer = new DKGv3PerformanceOptimizer();
    this.wsManager = new DKGv3WebSocketManager();

    // Add default request interceptor for auth
    this.addRequestInterceptor((config) => {
      const headers = { ...config.headers } as Record<string, string>;

      if (this.config.auth_token) {
        headers['Authorization'] = `Bearer ${this.config.auth_token}`;
      }

      headers['Content-Type'] = 'application/json';

      return { ...config, headers };
    });
  }

  // Configuration management
  updateConfig(config: Partial<DKGv3Config>): void {
    this.config = { ...this.config, ...config };
  }

  getConfig(): DKGv3Config {
    return { ...this.config };
  }

  // Request/Response interceptors
  addRequestInterceptor(interceptor: (config: RequestInit) => RequestInit): void {
    this.requestInterceptors.push(interceptor);
  }

  addResponseInterceptor(interceptor: (response: Response) => Response): void {
    this.responseInterceptors.push(interceptor);
  }

  // Core HTTP methods
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {},
    cacheKey?: string
  ): Promise<{ data: T; performance: PerformanceMetrics }> {
    const startTime = Date.now();

    // Check cache first
    if (cacheKey && (!options.method || options.method === 'GET')) {
      const cachedData = await this.cache.get<T>(cacheKey);
      if (cachedData) {
        const performance: PerformanceMetrics = {
          query_time_ms: Date.now() - startTime,
          cache_hit: true,
          atoms_processed: 0,
          relationships_traversed: 0,
          timestamp: new Date().toISOString()
        };
        return { data: cachedData, performance };
      }
    }

    // Apply request interceptors
    let processedOptions = options;
    for (const interceptor of this.requestInterceptors) {
      processedOptions = interceptor(processedOptions);
    }

    const url = `${this.config.api_base_url}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...processedOptions,
        signal: AbortSignal.timeout(this.config.timeout_ms)
      });

      // Apply response interceptors
      let processedResponse = response;
      for (const interceptor of this.responseInterceptors) {
        processedResponse = interceptor(processedResponse);
      }

      if (!processedResponse.ok) {
        const errorText = await processedResponse.text();
        const error: APIError = {
          detail: errorText,
          status_code: processedResponse.status,
          timestamp: new Date().toISOString()
        };
        throw error;
      }

      const data = await processedResponse.json();
      const responseTime = Date.now() - startTime;

      // Cache successful GET responses
      if (cacheKey && (!options.method || options.method === 'GET')) {
        const cacheStrategy = this.optimizer.get_cache_strategy(endpoint);
        const ttl = cacheStrategy === 'aggressive' ? 600000 :
                    cacheStrategy === 'conservative' ? 1800000 : 300000;
        await this.cache.set(cacheKey, data, ttl);
      }

      const performance: PerformanceMetrics = {
        query_time_ms: responseTime,
        cache_hit: false,
        atoms_processed: data.atoms?.length || data.results?.length || 0,
        relationships_traversed: data.traversal_results?.total_relationships || 0,
        timestamp: new Date().toISOString()
      };

      // Record performance metrics
      const queryType = endpoint.split('/').pop() || 'unknown';
      this.optimizer.recordQueryPerformance(queryType, performance);

      return { data, performance };

    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        throw {
          detail: 'Request timeout',
          status_code: 408,
          timestamp: new Date().toISOString()
        } as APIError;
      }
      throw error;
    }
  }

  private generateCacheKey(endpoint: string, data?: any): string {
    const dataStr = data ? JSON.stringify(data, Object.keys(data).sort()) : '';
    return `dkg_v3:${endpoint}:${btoa(dataStr).replace(/[+/=]/g, '')}`;
  }

  // API Methods

  async getHealth(): Promise<{ data: DKGv3HealthResponse; performance: PerformanceMetrics }> {
    return this.makeRequest<DKGv3HealthResponse>('/health', {}, 'health');
  }

  async getKnowledgeStatus(): Promise<{ data: KnowledgeStatusResponse; performance: PerformanceMetrics }> {
    return this.makeRequest<KnowledgeStatusResponse>('/status', {}, 'status');
  }

  async queryKnowledgeAtoms(
    request: KnowledgeAtomRequest
  ): Promise<{ data: KnowledgeAtomResponse; performance: PerformanceMetrics }> {
    const optimizedRequest = await this.optimizer.optimize_query(request);
    const cacheKey = this.generateCacheKey('atoms', optimizedRequest);

    return this.makeRequest<KnowledgeAtomResponse>(
      '/atoms',
      {
        method: 'POST',
        body: JSON.stringify(optimizedRequest)
      },
      cacheKey
    );
  }

  async generatePersonalization(
    request: PersonalizationRequest
  ): Promise<{ data: PersonalizationResponse; performance: PerformanceMetrics }> {
    const cacheKey = this.generateCacheKey('personalization', request);

    return this.makeRequest<PersonalizationResponse>(
      '/personalization',
      {
        method: 'POST',
        body: JSON.stringify(request)
      },
      cacheKey
    );
  }

  async semanticSearch(
    request: SemanticSearchRequest
  ): Promise<{ data: SemanticSearchResponse; performance: PerformanceMetrics }> {
    const optimizedRequest = await this.optimizer.optimize_query(request);
    const cacheKey = this.generateCacheKey('search/semantic', optimizedRequest);

    return this.makeRequest<SemanticSearchResponse>(
      '/search/semantic',
      {
        method: 'POST',
        body: JSON.stringify(optimizedRequest)
      },
      cacheKey
    );
  }

  async traverseGraph(
    request: GraphTraversalRequest
  ): Promise<{ data: GraphTraversalResponse; performance: PerformanceMetrics }> {
    const optimizedRequest = await this.optimizer.optimize_query(request);
    const cacheKey = this.generateCacheKey('graph/traverse', optimizedRequest);

    return this.makeRequest<GraphTraversalResponse>(
      '/graph/traverse',
      {
        method: 'POST',
        body: JSON.stringify(optimizedRequest)
      },
      cacheKey
    );
  }

  async generateInsights(
    request: InsightsRequest
  ): Promise<{ data: InsightsResponse; performance: PerformanceMetrics }> {
    const cacheKey = this.generateCacheKey('insights/generate', request);

    return this.makeRequest<InsightsResponse>(
      '/insights/generate',
      {
        method: 'POST',
        body: JSON.stringify(request)
      },
      cacheKey
    );
  }

  async recommendLearningPaths(
    request: LearningPathRequest
  ): Promise<{ data: LearningPathResponse; performance: PerformanceMetrics }> {
    const cacheKey = this.generateCacheKey('learning-paths', request);

    return this.makeRequest<LearningPathResponse>(
      '/learning-paths',
      {
        method: 'POST',
        body: JSON.stringify(request)
      },
      cacheKey
    );
  }

  async getAnalytics(
    request: AnalyticsRequest
  ): Promise<{ data: AnalyticsResponse; performance: PerformanceMetrics }> {
    const cacheKey = this.generateCacheKey('analytics/usage', request);

    return this.makeRequest<AnalyticsResponse>(
      '/analytics/usage',
      {
        method: 'POST',
        body: JSON.stringify(request)
      },
      cacheKey
    );
  }

  async exportKnowledge(
    request: ExportRequest
  ): Promise<{ data: ExportResponse; performance: PerformanceMetrics }> {
    // Don't cache export requests
    return this.makeRequest<ExportResponse>(
      '/export/formats',
      {
        method: 'POST',
        body: JSON.stringify(request)
      }
    );
  }

  // Batch operations
  async executeBatch(request: BatchRequest): Promise<BatchResponse> {
    const startTime = Date.now();
    const results: any[] = [];

    if (request.parallel_execution) {
      // Execute operations in parallel with concurrency limit
      const concurrency = request.max_concurrency || 5;
      const chunks: any[][] = [];

      for (let i = 0; i < request.operations.length; i += concurrency) {
        chunks.push(request.operations.slice(i, i + concurrency));
      }

      for (const chunk of chunks) {
        const chunkResults = await Promise.allSettled(
          chunk.map(op => this.executeSingleOperation(op))
        );
        results.push(...chunkResults);
      }
    } else {
      // Execute operations sequentially
      for (const operation of request.operations) {
        try {
          const result = await this.executeSingleOperation(operation);
          results.push({ status: 'fulfilled', value: result });
        } catch (error) {
          results.push({ status: 'rejected', reason: error });
        }
      }
    }

    const totalTime = Date.now() - startTime;
    const successfulResults = results.filter(r => r.status === 'fulfilled');
    const cacheHits = successfulResults.filter(r => r.value?.performance?.cache_hit).length;

    return {
      results: results.map((r, index) => ({
        id: request.operations[index].id,
        success: r.status === 'fulfilled',
        data: r.status === 'fulfilled' ? r.value.data : undefined,
        error: r.status === 'rejected' ? r.reason : undefined,
        performance: r.status === 'fulfilled' ? r.value.performance : undefined
      })),
      performance: {
        total_time_ms: totalTime,
        parallel_operations: request.parallel_execution ? request.max_concurrency || 5 : 1,
        cache_hits: cacheHits
      }
    };
  }

  private async executeSingleOperation(operation: any): Promise<any> {
    switch (operation.type) {
      case 'knowledge_atoms':
        return await this.queryKnowledgeAtoms(operation.request);
      case 'semantic_search':
        return await this.semanticSearch(operation.request);
      case 'personalization':
        return await this.generatePersonalization(operation.request);
      case 'graph_traversal':
        return await this.traverseGraph(operation.request);
      case 'insights_generation':
        return await this.generateInsights(operation.request);
      case 'learning_paths':
        return await this.recommendLearningPaths(operation.request);
      case 'analytics':
        return await this.getAnalytics(operation.request);
      default:
        throw new Error(`Unsupported operation type: ${operation.type}`);
    }
  }

  // WebSocket methods
  async connectWebSocket(clientId: string): Promise<void> {
    return this.wsManager.connect(clientId, this.config.websocket_url);
  }

  disconnectWebSocket(clientId: string): void {
    this.wsManager.disconnect(clientId);
  }

  subscribeWebSocket(clientId: string, callback: (data: WebSocketResponse) => void): () => void {
    return this.wsManager.subscribe(clientId, callback);
  }

  sendWebSocketMessage(clientId: string, message: WebSocketMessage): boolean {
    return this.wsManager.send(clientId, message);
  }

  isWebSocketConnected(clientId: string): boolean {
    return this.wsManager.isConnected(clientId);
  }

  // Performance and diagnostics
  getPerformanceStats(): any {
    return {
      optimizer: this.optimizer.getPerformanceStats(),
      cache: this.cache.getStats(),
      websockets: this.wsManager.getConnectionStats()
    };
  }

  getCacheManager(): AdvancedCacheManager {
    return this.cache;
  }

  getOptimizer(): DKGv3PerformanceOptimizer {
    return this.optimizer;
  }

  // Cleanup
  destroy(): void {
    this.cache.destroy();
    // Close all WebSocket connections
    const connectionStats = this.wsManager.getConnectionStats();
    connectionStats.connectionDetails.forEach(({ clientId }) => {
      this.wsManager.disconnect(clientId);
    });
  }
}

// Export singleton instance
export const dkgv3Service = new DKGv3Service();

// Export service class for custom instances
export default DKGv3Service;