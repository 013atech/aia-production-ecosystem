/**
 * AIA Enterprise Platform - Performance Monitor
 * ===========================================
 *
 * Advanced performance monitoring system for 3D rendering with
 * real-time metrics, adaptive quality adjustment, and optimization suggestions.
 */

export interface PerformanceMetrics {
  fps: number;
  frameTime: number;
  renderTime: number;
  triangleCount: number;
  drawCalls: number;
  memoryUsage: number;
  gpuMemoryUsage: number;
  qualityLevel: string;
  bottleneck: string;
  suggestions: string[];
}

interface PerformanceThresholds {
  fps: {
    excellent: number;
    good: number;
    acceptable: number;
    poor: number;
  };
  frameTime: {
    excellent: number;
    good: number;
    acceptable: number;
    poor: number;
  };
  triangles: {
    low: number;
    medium: number;
    high: number;
    extreme: number;
  };
}

export class PerformanceMonitor {
  private gl: THREE.WebGLRenderer;
  private frameHistory: number[] = [];
  private renderTimeHistory: number[] = [];
  private lastFrameTime: number = performance.now();
  private frameCount: number = 0;
  private currentMetrics: PerformanceMetrics;
  private memoryInfo: any;
  private isWebGLMemoryExtensionAvailable: boolean = false;

  private readonly thresholds: PerformanceThresholds = {
    fps: {
      excellent: 58,
      good: 50,
      acceptable: 30,
      poor: 20
    },
    frameTime: {
      excellent: 16.67, // 60fps
      good: 20,          // 50fps
      acceptable: 33.33, // 30fps
      poor: 50          // 20fps
    },
    triangles: {
      low: 10000,
      medium: 50000,
      high: 100000,
      extreme: 500000
    }
  };

  private readonly maxHistorySize = 60; // Keep 60 frame history for 1-second average at 60fps

  constructor(gl: THREE.WebGLRenderer) {
    this.gl = gl;
    this.initializeMemoryMonitoring();
    this.currentMetrics = this.getDefaultMetrics();
  }

  private initializeMemoryMonitoring(): void {
    // Check for WebGL memory extension
    const glContext = this.gl.getContext();
    const memoryExtension = glContext.getExtension('WEBGL_debug_renderer_info');

    if (memoryExtension) {
      this.isWebGLMemoryExtensionAvailable = true;
    }

    // Check for performance.memory (Chrome)
    if ('memory' in performance) {
      this.memoryInfo = (performance as any).memory;
    }
  }

  private getDefaultMetrics(): PerformanceMetrics {
    return {
      fps: 60,
      frameTime: 16.67,
      renderTime: 0,
      triangleCount: 0,
      drawCalls: 0,
      memoryUsage: 0,
      gpuMemoryUsage: 0,
      qualityLevel: 'high',
      bottleneck: 'none',
      suggestions: []
    };
  }

  update(deltaTime: number): PerformanceMetrics {
    const currentTime = performance.now();
    const frameTime = currentTime - this.lastFrameTime;

    // Update frame history
    this.frameHistory.push(frameTime);
    if (this.frameHistory.length > this.maxHistorySize) {
      this.frameHistory.shift();
    }

    // Update render time (estimate based on GPU timer if available)
    const renderTime = this.estimateRenderTime(deltaTime);
    this.renderTimeHistory.push(renderTime);
    if (this.renderTimeHistory.length > this.maxHistorySize) {
      this.renderTimeHistory.shift();
    }

    this.frameCount++;
    this.lastFrameTime = currentTime;

    // Calculate metrics every frame but return smoothed values
    if (this.frameCount % 10 === 0) { // Update metrics every 10 frames
      this.currentMetrics = this.calculateMetrics();
    }

    return this.currentMetrics;
  }

  private estimateRenderTime(deltaTime: number): number {
    // Use delta time as a rough estimate of render time
    // In a real implementation, you might use WebGL timer queries
    const glInfo = this.gl.info;
    const complexity = glInfo.render.triangles / 1000 + glInfo.render.calls;

    // Rough estimation based on complexity
    return Math.min(deltaTime * 1000, 50); // Cap at 50ms
  }

  private calculateMetrics(): PerformanceMetrics {
    const glInfo = this.gl.info;

    // Calculate average FPS from frame history
    const avgFrameTime = this.frameHistory.reduce((sum, time) => sum + time, 0) / this.frameHistory.length;
    const fps = 1000 / avgFrameTime;

    // Calculate average render time
    const avgRenderTime = this.renderTimeHistory.reduce((sum, time) => sum + time, 0) / this.renderTimeHistory.length;

    // Memory usage
    const memoryUsage = this.getMemoryUsage();
    const gpuMemoryUsage = this.getGPUMemoryUsage();

    // Identify bottleneck
    const bottleneck = this.identifyBottleneck(fps, avgRenderTime, glInfo.render.triangles, glInfo.render.calls);

    // Generate optimization suggestions
    const suggestions = this.generateSuggestions(fps, avgRenderTime, glInfo.render.triangles, glInfo.render.calls, memoryUsage);

    // Determine quality level recommendation
    const qualityLevel = this.recommendQualityLevel(fps, avgRenderTime, glInfo.render.triangles);

    return {
      fps: Math.round(fps * 10) / 10,
      frameTime: Math.round(avgFrameTime * 100) / 100,
      renderTime: Math.round(avgRenderTime * 100) / 100,
      triangleCount: glInfo.render.triangles,
      drawCalls: glInfo.render.calls,
      memoryUsage: Math.round(memoryUsage * 100) / 100,
      gpuMemoryUsage: Math.round(gpuMemoryUsage * 100) / 100,
      qualityLevel,
      bottleneck,
      suggestions
    };
  }

  private getMemoryUsage(): number {
    if (this.memoryInfo) {
      // Chrome's performance.memory (in MB)
      return this.memoryInfo.usedJSHeapSize / (1024 * 1024);
    }

    // Fallback estimate based on renderer info
    const glInfo = this.gl.info;
    const estimatedUsage = (glInfo.memory.geometries * 0.1 + glInfo.memory.textures * 0.5) / 1024;
    return estimatedUsage;
  }

  private getGPUMemoryUsage(): number {
    const glInfo = this.gl.info;

    // Estimate GPU memory usage based on textures and geometries
    // This is a rough estimation since actual GPU memory is not directly accessible
    const textureMemory = glInfo.memory.textures * 0.001; // Rough estimate in MB
    const geometryMemory = glInfo.memory.geometries * 0.0001; // Rough estimate in MB

    return textureMemory + geometryMemory;
  }

  private identifyBottleneck(fps: number, renderTime: number, triangles: number, drawCalls: number): string {
    if (fps < this.thresholds.fps.poor) {
      if (triangles > this.thresholds.triangles.high) {
        return 'geometry-complexity';
      } else if (drawCalls > 100) {
        return 'draw-calls';
      } else if (renderTime > this.thresholds.frameTime.poor) {
        return 'gpu-rendering';
      } else {
        return 'cpu-bound';
      }
    } else if (fps < this.thresholds.fps.acceptable) {
      if (triangles > this.thresholds.triangles.medium) {
        return 'moderate-geometry';
      } else if (drawCalls > 50) {
        return 'moderate-draw-calls';
      } else {
        return 'minor-bottleneck';
      }
    }

    return 'none';
  }

  private generateSuggestions(fps: number, renderTime: number, triangles: number, drawCalls: number, memoryUsage: number): string[] {
    const suggestions: string[] = [];

    // FPS-based suggestions
    if (fps < this.thresholds.fps.acceptable) {
      suggestions.push('Consider reducing scene complexity or lowering quality settings');
    }

    // Triangle count suggestions
    if (triangles > this.thresholds.triangles.high) {
      suggestions.push('High triangle count detected - implement LOD (Level of Detail) system');
      suggestions.push('Consider using instanced rendering for repeated geometry');
    } else if (triangles > this.thresholds.triangles.medium) {
      suggestions.push('Moderate triangle count - consider optimizing geometry');
    }

    // Draw call suggestions
    if (drawCalls > 100) {
      suggestions.push('High draw call count - implement geometry batching');
      suggestions.push('Use texture atlases to reduce material switches');
    } else if (drawCalls > 50) {
      suggestions.push('Consider consolidating objects to reduce draw calls');
    }

    // Memory usage suggestions
    if (memoryUsage > 100) {
      suggestions.push('High memory usage detected - implement texture compression');
      suggestions.push('Consider disposing unused geometries and materials');
    } else if (memoryUsage > 50) {
      suggestions.push('Monitor memory usage and implement object pooling');
    }

    // Render time suggestions
    if (renderTime > this.thresholds.frameTime.poor) {
      suggestions.push('High render time - check shader complexity');
      suggestions.push('Disable expensive effects like shadows or post-processing');
    }

    // Quality level suggestions
    if (fps < this.thresholds.fps.good) {
      suggestions.push('Consider automatically lowering quality level for better performance');
    }

    return suggestions;
  }

  private recommendQualityLevel(fps: number, renderTime: number, triangles: number): string {
    if (fps >= this.thresholds.fps.excellent && renderTime <= this.thresholds.frameTime.excellent) {
      return 'ultra';
    } else if (fps >= this.thresholds.fps.good && renderTime <= this.thresholds.frameTime.good) {
      return 'high';
    } else if (fps >= this.thresholds.fps.acceptable && renderTime <= this.thresholds.frameTime.acceptable) {
      return 'medium';
    } else {
      return 'low';
    }
  }

  getDetailedReport(): {
    metrics: PerformanceMetrics;
    history: {
      frameHistory: number[];
      renderTimeHistory: number[];
    };
    recommendations: {
      immediate: string[];
      longTerm: string[];
    };
    systemInfo: any;
  } {
    const glContext = this.gl.getContext();
    const systemInfo = {
      renderer: glContext.getParameter(glContext.RENDERER),
      vendor: glContext.getParameter(glContext.VENDOR),
      version: glContext.getParameter(glContext.VERSION),
      maxTextureSize: glContext.getParameter(glContext.MAX_TEXTURE_SIZE),
      maxViewportDims: glContext.getParameter(glContext.MAX_VIEWPORT_DIMS),
      maxVertexAttribs: glContext.getParameter(glContext.MAX_VERTEX_ATTRIBS),
      extensions: glContext.getSupportedExtensions()
    };

    const immediate = this.currentMetrics.suggestions.slice(0, 3);
    const longTerm = [
      'Implement progressive loading for large scenes',
      'Consider using Web Workers for heavy computations',
      'Implement adaptive rendering based on device capabilities',
      'Use occlusion culling for complex scenes',
      'Consider WebGPU migration for better performance'
    ];

    return {
      metrics: this.currentMetrics,
      history: {
        frameHistory: [...this.frameHistory],
        renderTimeHistory: [...this.renderTimeHistory]
      },
      recommendations: {
        immediate,
        longTerm
      },
      systemInfo
    };
  }

  reset(): void {
    this.frameHistory = [];
    this.renderTimeHistory = [];
    this.frameCount = 0;
    this.lastFrameTime = performance.now();
    this.currentMetrics = this.getDefaultMetrics();
  }

  // Static utility methods for performance analysis
  static analyzeFramePattern(frameHistory: number[]): {
    isStable: boolean;
    variance: number;
    spikes: number[];
  } {
    if (frameHistory.length < 10) {
      return { isStable: true, variance: 0, spikes: [] };
    }

    const avg = frameHistory.reduce((sum, time) => sum + time, 0) / frameHistory.length;
    const variance = frameHistory.reduce((sum, time) => sum + Math.pow(time - avg, 2), 0) / frameHistory.length;

    const spikes = frameHistory
      .map((time, index) => ({ time, index }))
      .filter(({ time }) => time > avg + (variance * 2))
      .map(({ index }) => index);

    const isStable = variance < 5 && spikes.length < frameHistory.length * 0.1; // Less than 10% spikes

    return { isStable, variance, spikes };
  }

  static getPerformanceGrade(metrics: PerformanceMetrics): {
    grade: 'A' | 'B' | 'C' | 'D' | 'F';
    score: number;
    breakdown: { [key: string]: number };
  } {
    const fpsScore = Math.min(100, (metrics.fps / 60) * 100);
    const frameTimeScore = Math.min(100, (16.67 / metrics.frameTime) * 100);
    const memoryScore = Math.max(0, 100 - (metrics.memoryUsage / 100) * 100);
    const triangleScore = Math.max(0, 100 - (metrics.triangleCount / 100000) * 100);

    const breakdown = {
      fps: fpsScore,
      frameTime: frameTimeScore,
      memory: memoryScore,
      geometry: triangleScore
    };

    const totalScore = (fpsScore + frameTimeScore + memoryScore + triangleScore) / 4;

    let grade: 'A' | 'B' | 'C' | 'D' | 'F';
    if (totalScore >= 90) grade = 'A';
    else if (totalScore >= 80) grade = 'B';
    else if (totalScore >= 70) grade = 'C';
    else if (totalScore >= 60) grade = 'D';
    else grade = 'F';

    return { grade, score: Math.round(totalScore), breakdown };
  }
}