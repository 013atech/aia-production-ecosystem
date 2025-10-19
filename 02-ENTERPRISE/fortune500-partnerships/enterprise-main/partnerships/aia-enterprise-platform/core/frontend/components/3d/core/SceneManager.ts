/**
 * AIA Enterprise Platform - Scene Manager
 * =====================================
 *
 * Central scene management system that consolidates and optimizes
 * all 3D scene operations for maximum performance and maintainability.
 */

import * as THREE from 'three';

interface LightingConfig {
  enableShadows: boolean;
  ambientIntensity: number;
  directionalIntensity: number;
}

interface QualityLevel {
  shadowMapSize: number;
  antialias: boolean;
  lodDistance: number;
  maxObjects: number;
}

export class SceneManager {
  private scene: THREE.Scene;
  private config: any;
  private qualitySettings: { [key: string]: QualityLevel };
  private currentQuality: string = 'high';
  private objects: Map<string, THREE.Object3D> = new Map();
  private lights: THREE.Light[] = [];
  private animationMixers: THREE.AnimationMixer[] = [];

  constructor(scene: THREE.Scene, config: any) {
    this.scene = scene;
    this.config = config;

    // Initialize quality settings
    this.qualitySettings = {
      low: {
        shadowMapSize: 512,
        antialias: false,
        lodDistance: 25,
        maxObjects: 50
      },
      medium: {
        shadowMapSize: 1024,
        antialias: true,
        lodDistance: 50,
        maxObjects: 100
      },
      high: {
        shadowMapSize: 2048,
        antialias: true,
        lodDistance: 75,
        maxObjects: 200
      },
      ultra: {
        shadowMapSize: 4096,
        antialias: true,
        lodDistance: 100,
        maxObjects: 500
      }
    };

    this.initializeScene();
  }

  private initializeScene(): void {
    // Set up scene background and fog
    this.scene.background = new THREE.Color(0x1a1a1a);
    this.scene.fog = new THREE.Fog(0x1a1a1a, 10, 200);

    // Enable shadows on renderer level
    if (this.config.lighting?.enableShadows) {
      this.scene.traverse((object) => {
        if (object instanceof THREE.Mesh) {
          object.castShadow = true;
          object.receiveShadow = true;
        }
      });
    }
  }

  setupLighting(lightingConfig: LightingConfig): void {
    // Clear existing lights
    this.lights.forEach(light => this.scene.remove(light));
    this.lights = [];

    // Ambient Light
    const ambientLight = new THREE.AmbientLight(0x404040, lightingConfig.ambientIntensity);
    this.scene.add(ambientLight);
    this.lights.push(ambientLight);

    // Directional Light (Main Sun)
    const directionalLight = new THREE.DirectionalLight(0xffffff, lightingConfig.directionalIntensity);
    directionalLight.position.set(50, 50, 25);
    directionalLight.castShadow = lightingConfig.enableShadows;

    if (lightingConfig.enableShadows) {
      const shadowQuality = this.qualitySettings[this.currentQuality];
      directionalLight.shadow.mapSize.width = shadowQuality.shadowMapSize;
      directionalLight.shadow.mapSize.height = shadowQuality.shadowMapSize;
      directionalLight.shadow.camera.near = 0.1;
      directionalLight.shadow.camera.far = 200;
      directionalLight.shadow.camera.left = -50;
      directionalLight.shadow.camera.right = 50;
      directionalLight.shadow.camera.top = 50;
      directionalLight.shadow.camera.bottom = -50;
      directionalLight.shadow.bias = -0.001;
    }

    this.scene.add(directionalLight);
    this.lights.push(directionalLight);

    // Point lights for accent lighting
    const pointLight1 = new THREE.PointLight(0x00ffff, 0.3, 50);
    pointLight1.position.set(-20, 20, 20);
    this.scene.add(pointLight1);
    this.lights.push(pointLight1);

    const pointLight2 = new THREE.PointLight(0xffff00, 0.3, 50);
    pointLight2.position.set(20, 20, -20);
    this.scene.add(pointLight2);
    this.lights.push(pointLight2);
  }

  addObject(id: string, object: THREE.Object3D): void {
    this.objects.set(id, object);
    this.scene.add(object);

    // Apply quality settings to new objects
    this.applyQualitySettings(object);
  }

  removeObject(id: string): boolean {
    const object = this.objects.get(id);
    if (object) {
      this.scene.remove(object);
      this.objects.delete(id);

      // Cleanup geometry and materials
      this.disposeObject(object);
      return true;
    }
    return false;
  }

  getObject(id: string): THREE.Object3D | undefined {
    return this.objects.get(id);
  }

  adjustQuality(currentFPS: number): void {
    let targetQuality = this.currentQuality;

    // Adaptive quality adjustment based on FPS
    if (currentFPS < 30 && this.currentQuality !== 'low') {
      targetQuality = 'low';
    } else if (currentFPS < 45 && this.currentQuality === 'ultra') {
      targetQuality = 'high';
    } else if (currentFPS < 50 && this.currentQuality === 'high') {
      targetQuality = 'medium';
    } else if (currentFPS > 55 && this.currentQuality === 'low') {
      targetQuality = 'medium';
    } else if (currentFPS > 58 && this.currentQuality === 'medium') {
      targetQuality = 'high';
    }

    if (targetQuality !== this.currentQuality) {
      this.setQuality(targetQuality);
    }
  }

  setQuality(qualityLevel: string): void {
    if (!this.qualitySettings[qualityLevel]) {
      console.warn(`Unknown quality level: ${qualityLevel}`);
      return;
    }

    this.currentQuality = qualityLevel;
    const settings = this.qualitySettings[qualityLevel];

    // Apply quality settings to existing objects
    this.scene.traverse((object) => {
      this.applyQualitySettings(object);
    });

    // Update shadow map size for lights
    this.lights.forEach(light => {
      if (light instanceof THREE.DirectionalLight && light.shadow) {
        light.shadow.mapSize.width = settings.shadowMapSize;
        light.shadow.mapSize.height = settings.shadowMapSize;
        light.shadow.needsUpdate = true;
      }
    });

    console.log(`Quality adjusted to: ${qualityLevel}`);
  }

  private applyQualitySettings(object: THREE.Object3D): void {
    const settings = this.qualitySettings[this.currentQuality];

    if (object instanceof THREE.Mesh) {
      // LOD based on distance and quality
      object.userData.originalPosition = object.userData.originalPosition || object.position.clone();

      // Material quality adjustments
      if (object.material) {
        const materials = Array.isArray(object.material) ? object.material : [object.material];

        materials.forEach(material => {
          if (material instanceof THREE.MeshStandardMaterial || material instanceof THREE.MeshPhysicalMaterial) {
            // Adjust material complexity based on quality
            switch (this.currentQuality) {
              case 'low':
                material.envMapIntensity = 0.5;
                material.roughness = 0.8;
                material.metalness = 0.2;
                break;
              case 'medium':
                material.envMapIntensity = 0.7;
                material.roughness = 0.6;
                material.metalness = 0.4;
                break;
              case 'high':
                material.envMapIntensity = 1.0;
                material.roughness = 0.4;
                material.metalness = 0.6;
                break;
              case 'ultra':
                material.envMapIntensity = 1.2;
                material.roughness = 0.3;
                material.metalness = 0.8;
                break;
            }
            material.needsUpdate = true;
          }
        });
      }
    }
  }

  update(deltaTime: number): void {
    // Update animation mixers
    this.animationMixers.forEach(mixer => {
      mixer.update(deltaTime);
    });

    // Update objects with custom update methods
    this.objects.forEach(object => {
      if (object.userData.update) {
        object.userData.update(deltaTime);
      }
    });

    // Frustum culling for performance
    this.performFrustumCulling();
  }

  private performFrustumCulling(): void {
    const settings = this.qualitySettings[this.currentQuality];

    this.objects.forEach(object => {
      if (object.userData.originalPosition) {
        const distance = object.userData.originalPosition.distanceTo(new THREE.Vector3(0, 0, 0));

        // Hide objects beyond LOD distance based on quality
        object.visible = distance <= settings.lodDistance;
      }
    });
  }

  addAnimationMixer(mixer: THREE.AnimationMixer): void {
    this.animationMixers.push(mixer);
  }

  removeAnimationMixer(mixer: THREE.AnimationMixer): void {
    const index = this.animationMixers.indexOf(mixer);
    if (index > -1) {
      this.animationMixers.splice(index, 1);
    }
  }

  private disposeObject(object: THREE.Object3D): void {
    object.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        if (child.geometry) {
          child.geometry.dispose();
        }

        if (child.material) {
          const materials = Array.isArray(child.material) ? child.material : [child.material];
          materials.forEach(material => {
            material.dispose();

            // Dispose textures
            Object.values(material).forEach(value => {
              if (value instanceof THREE.Texture) {
                value.dispose();
              }
            });
          });
        }
      }
    });
  }

  getPerformanceMetrics(): {
    objectCount: number;
    lightCount: number;
    animationCount: number;
    qualityLevel: string;
  } {
    return {
      objectCount: this.objects.size,
      lightCount: this.lights.length,
      animationCount: this.animationMixers.length,
      qualityLevel: this.currentQuality
    };
  }

  dispose(): void {
    // Clear all objects
    this.objects.forEach((object, id) => {
      this.removeObject(id);
    });

    // Clear lights
    this.lights.forEach(light => this.scene.remove(light));
    this.lights = [];

    // Clear animation mixers
    this.animationMixers = [];

    // Clear scene
    this.scene.clear();
  }
}