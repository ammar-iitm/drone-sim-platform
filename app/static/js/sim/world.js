// The 3D world: terrain, sky, lighting and contact silhouettes.
// Low-poly and instanced so a 12-drone swarm stays well inside 30 fps on integrated GPUs.
import * as THREE from '/static/vendor/three.module.js';
import { mulberry32 } from './rng.js';

const LOOKS = {
  day: { top: 0x3f74b8, bottom: 0xbcd3e6, fog: 0xc4d4e2, sun: 0xffffff, sunI: 2.0, sunDir: [0.4, 1.0, 0.3], amb: 0.9,
    ground: [0x5c7744, 0x7a8750, 0x8b7b59], urban: 0x6b6f73, building: 0xa9adb2, contact: 0x1a1c1f, stars: false },
  dusk: { top: 0x1c2a52, bottom: 0xe0894e, fog: 0x8e7468, sun: 0xffb27a, sunI: 1.2, sunDir: [-1.0, 0.18, 0.2], amb: 0.45,
    ground: [0x3d4c31, 0x535339, 0x5c4e3d], urban: 0x45474c, building: 0x5a5c62, contact: 0x0e0f11, stars: false },
  night: { top: 0x02040a, bottom: 0x0c1424, fog: 0x070a12, sun: 0x8fa6d8, sunI: 0.3, sunDir: [0.3, 0.8, -0.5], amb: 0.16,
    ground: [0x151b15, 0x1a1f16, 0x1d1b16], urban: 0x16181c, building: 0x1f2228, contact: 0x07080a, stars: true },
};

// Approximate real sizes, used to keep every contact at least 6 px on screen.
export const MODEL_SIZE = { quadcopter: 0.9, hexacopter: 1.6, fixed_wing: 3.0, balloon: 2.8, bird: 0.9, friendly_aircraft: 16 };
const WOBBLE = { quadcopter: 1.5, hexacopter: 1.0, fixed_wing: 0, balloon: 2.5, bird: 5, friendly_aircraft: 0 };

// ------------------------------------------------------------ noise for terrain

function valueNoise2D(seed) {
  const rand = mulberry32(seed);
  const N = 64;
  const grid = new Float32Array(N * N);
  for (let i = 0; i < grid.length; i++) grid[i] = rand();
  const at = (x, y) => grid[((y % N + N) % N) * N + ((x % N + N) % N)];
  const smooth = (t) => t * t * (3 - 2 * t);
  return (x, y) => {
    const xi = Math.floor(x), yi = Math.floor(y);
    const fx = smooth(x - xi), fy = smooth(y - yi);
    const a = at(xi, yi), b = at(xi + 1, yi), c = at(xi, yi + 1), d = at(xi + 1, yi + 1);
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy;
  };
}

function smoothstep(e0, e1, x) {
  const t = Math.min(1, Math.max(0, (x - e0) / (e1 - e0)));
  return t * t * (3 - 2 * t);
}

// ------------------------------------------------------------ geometry helpers

function merge(parts) {
  // parts: [geometry, matrix] pairs; returns one non-indexed geometry (one draw call).
  const pos = [], nor = [];
  for (const [g, m] of parts) {
    const geo = (g.index ? g.toNonIndexed() : g.clone()).applyMatrix4(m);
    pos.push(...geo.attributes.position.array);
    nor.push(...geo.attributes.normal.array);
  }
  const out = new THREE.BufferGeometry();
  out.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  out.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  out.computeBoundingSphere();
  return out;
}

const M = () => new THREE.Matrix4();
const at = (x, y, z, ry = 0, rx = 0, rz = 0) =>
  M().compose(new THREE.Vector3(x, y, z), new THREE.Quaternion().setFromEuler(new THREE.Euler(rx, ry, rz)), new THREE.Vector3(1, 1, 1));

function rotorParts(radius, positions) {
  return positions.map(([x, z]) => [new THREE.CylinderGeometry(radius, radius, 0.03, 10), at(x, 0.08, z)]);
}

// Models face +z (Object3D.lookAt points +z at the target).
const BUILDERS = {
  quadcopter() {
    const d = 0.32;
    return merge([
      [new THREE.BoxGeometry(0.35, 0.12, 0.35), at(0, 0, 0)],
      [new THREE.BoxGeometry(0.95, 0.04, 0.06), at(0, 0, 0, Math.PI / 4)],
      [new THREE.BoxGeometry(0.95, 0.04, 0.06), at(0, 0, 0, -Math.PI / 4)],
      ...rotorParts(0.15, [[d, d], [-d, d], [d, -d], [-d, -d]]),
    ]);
  },
  hexacopter() {
    const parts = [[new THREE.BoxGeometry(0.6, 0.2, 0.6), at(0, 0, 0)],
      [new THREE.BoxGeometry(0.28, 0.32, 0.28), at(0, -0.26, 0)]];
    for (let i = 0; i < 3; i++) parts.push([new THREE.BoxGeometry(1.6, 0.05, 0.08), at(0, 0, 0, (i * Math.PI) / 3)]);
    const rotors = [];
    for (let i = 0; i < 6; i++) rotors.push([Math.cos((i * Math.PI) / 3) * 0.8, Math.sin((i * Math.PI) / 3) * 0.8]);
    return merge([...parts, ...rotorParts(0.22, rotors)]);
  },
  fixed_wing() {
    return merge([
      [new THREE.CylinderGeometry(0.1, 0.13, 2.2, 8), at(0, 0, 0, 0, Math.PI / 2)],
      [new THREE.BoxGeometry(1.6, 0.04, 0.45), at(0.75, 0, -0.1, -0.45)],
      [new THREE.BoxGeometry(1.6, 0.04, 0.45), at(-0.75, 0, -0.1, 0.45)],
      [new THREE.BoxGeometry(0.04, 0.4, 0.3), at(0, 0.2, -1.0)],
    ]);
  },
  balloon() {
    return merge([
      [new THREE.SphereGeometry(1.4, 10, 8), at(0, 0, 0)],
      [new THREE.BoxGeometry(0.03, 2.2, 0.03), at(0, -2.4, 0)],
    ]);
  },
  bird() {
    return merge([[new THREE.BoxGeometry(0.12, 0.1, 0.38), at(0, 0, 0)], [new THREE.BoxGeometry(0.06, 0.06, 0.1), at(0, 0.03, 0.22)]]);
  },
  friendly_aircraft() {
    return merge([
      [new THREE.CylinderGeometry(0.7, 0.9, 14, 10), at(0, 0, 0, 0, Math.PI / 2)],
      [new THREE.BoxGeometry(16, 0.25, 2.2), at(0, -0.2, 0.5)],
      [new THREE.BoxGeometry(5, 0.2, 1.2), at(0, 0.2, -6.2)],
      [new THREE.BoxGeometry(0.2, 2.6, 1.6), at(0, 1.4, -6.2)],
    ]);
  },
};

// ------------------------------------------------------------ world

export class World {
  constructor(canvas, scenario) {
    this.scenario = scenario;
    this.env = scenario.environment;
    this.look = LOOKS[this.env.time_of_day] || LOOKS.day;
    this.urban = this.env.terrain === 'urban';
    this.eyeHeight = this.urban ? 24 : 6;

    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'low-power' });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(60, 1, 0.5, 10000);
    this.camera.rotation.order = 'YXZ';
    this.camera.position.set(0, this.eyeHeight, 0);
    this.baseFov = 60;

    const far = this.env.visual_range_m * 1.05;
    this.scene.fog = new THREE.Fog(this.look.fog, far * (0.6 - 0.45 * this.env.fog), far);

    this.hemi = new THREE.HemisphereLight(this.look.top, this.urban ? this.look.urban : this.look.ground[0], this.look.amb);
    this.scene.add(this.hemi);
    this.sun = new THREE.DirectionalLight(this.look.sun, this.look.sunI);
    this.sun.position.set(...this.look.sunDir).multiplyScalar(1000);
    this.scene.add(this.sun);

    this.heightAt = () => 0;
    this.buildSky();
    if (this.urban) this.buildUrban(); else this.buildRural();
    this.occluders = this.scene.children.filter((o) => o.userData.occluder);

    this.contactMat = new THREE.MeshLambertMaterial({ color: this.look.contact, emissive: 0x000000 });
    this.navMat = new THREE.MeshBasicMaterial({ color: 0xff3030, fog: false });
    this.meshes = new Map();
    for (const c of scenario.contacts) this.meshes.set(c.id, this.buildContact(c));
    this.mode = 'eo';
  }

  buildSky() {
    const geo = new THREE.SphereGeometry(9000, 32, 16);
    const top = new THREE.Color(this.look.top), bottom = new THREE.Color(this.look.bottom);
    const colors = [];
    const p = geo.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const h = Math.max(0, p.getY(i) / 9000);
      const c = bottom.clone().lerp(top, Math.pow(h, 0.5));
      colors.push(c.r, c.g, c.b);
    }
    geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    this.sky = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.BackSide, fog: false, depthWrite: false }));
    this.scene.add(this.sky);
    if (this.look.stars) {
      const rand = mulberry32(this.env.terrain_seed ^ 0x51a5);
      const pts = [];
      for (let i = 0; i < 260; i++) {
        const az = rand() * Math.PI * 2, el = 0.05 + rand() * 1.4;
        pts.push(Math.cos(az) * Math.cos(el) * 8500, Math.sin(el) * 8500, Math.sin(az) * Math.cos(el) * 8500);
      }
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
      this.stars = new THREE.Points(g, new THREE.PointsMaterial({ color: 0x9aa6c8, size: 1.5, sizeAttenuation: false, fog: false }));
      this.scene.add(this.stars);
    }
  }

  buildRural() {
    const noise = valueNoise2D(this.env.terrain_seed);
    const height = (x, z) => {
      const r = Math.hypot(x, z);
      let h = 0, amp = 1, freq = 1 / 900;
      for (let o = 0; o < 4; o++) { h += amp * noise(x * freq + 17, z * freq + 31); amp *= 0.5; freq *= 2; }
      return (h - 0.9) * 70 * smoothstep(150, 700, r);
    };
    this.heightAt = height;
    const geo = new THREE.PlaneGeometry(9000, 9000, 150, 150);
    geo.rotateX(-Math.PI / 2);
    const p = geo.attributes.position;
    const cols = [];
    const [g0, g1, g2] = this.look.ground.map((c) => new THREE.Color(c));
    for (let i = 0; i < p.count; i++) {
      const h = height(p.getX(i), p.getZ(i));
      p.setY(i, h);
      const t = Math.min(1, Math.max(0, (h + 20) / 70));
      const c = t < 0.5 ? g0.clone().lerp(g1, t * 2) : g1.clone().lerp(g2, (t - 0.5) * 2);
      cols.push(c.r, c.g, c.b);
    }
    geo.setAttribute('color', new THREE.Float32BufferAttribute(cols, 3));
    geo.computeVertexNormals();
    const ground = new THREE.Mesh(geo, new THREE.MeshLambertMaterial({ vertexColors: true, flatShading: true }));
    ground.userData.occluder = true;
    this.scene.add(ground);

    const rand = mulberry32(this.env.terrain_seed ^ 0x7ee5);
    const count = 420;
    const trees = new THREE.InstancedMesh(new THREE.ConeGeometry(4, 13, 5), new THREE.MeshLambertMaterial({ color: this.look.ground[0], flatShading: true }), count);
    const m = new THREE.Matrix4();
    for (let i = 0; i < count; i++) {
      const a = rand() * Math.PI * 2, r = 220 + rand() * 3400, s = 0.7 + rand() * 0.8;
      const x = Math.cos(a) * r, z = Math.sin(a) * r;
      m.compose(new THREE.Vector3(x, height(x, z) + 6 * s, z), new THREE.Quaternion(), new THREE.Vector3(s, s, s));
      trees.setMatrixAt(i, m);
    }
    this.scene.add(trees);
  }

  buildUrban() {
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(9000, 9000).rotateX(-Math.PI / 2), new THREE.MeshLambertMaterial({ color: this.look.urban }));
    ground.userData.occluder = true;
    this.scene.add(ground);
    const rand = mulberry32(this.env.terrain_seed ^ 0xb10c);
    const cell = 60, block = 40, maxR = 2600, list = [];
    for (let gx = -Math.floor(maxR / cell); gx <= maxR / cell; gx++) {
      for (let gz = -Math.floor(maxR / cell); gz <= maxR / cell; gz++) {
        const x = gx * cell, z = gz * cell, r = Math.hypot(x, z);
        if (r > maxR || r < 130 || rand() < 0.14) continue;
        // Roofs near the post stay below eye level; the skyline rises with distance.
        const cap = 12 + 48 * smoothstep(150, 900, r);
        list.push([x, z, 6 + Math.pow(rand(), 1.4) * cap, 0.75 + rand() * 0.25]);
      }
    }
    const mesh = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshLambertMaterial({ color: 0xffffff }), list.length);
    const m = new THREE.Matrix4(), col = new THREE.Color(), base = new THREE.Color(this.look.building);
    list.forEach(([x, z, h, shade], i) => {
      m.compose(new THREE.Vector3(x, h / 2, z), new THREE.Quaternion(), new THREE.Vector3(block, h, block));
      mesh.setMatrixAt(i, m);
      mesh.setColorAt(i, col.copy(base).multiplyScalar(shade));
    });
    mesh.userData.occluder = true;
    this.scene.add(mesh);
  }

  buildContact(c) {
    const group = new THREE.Group();
    const body = new THREE.Mesh(BUILDERS[c.model](), this.contactMat);
    group.add(body);
    if (c.model === 'bird') {
      const wingGeo = new THREE.BoxGeometry(0.45, 0.02, 0.16).translate(0.24, 0, 0);
      group.userData.wings = [new THREE.Mesh(wingGeo, this.contactMat), new THREE.Mesh(wingGeo, this.contactMat)];
      group.userData.wings[1].scale.x = -1;
      group.userData.wings.forEach((w) => group.add(w));
    }
    if (c.model === 'friendly_aircraft') {
      const light = new THREE.Mesh(new THREE.SphereGeometry(0.6, 6, 4), this.navMat);
      light.position.set(8, 0, 0.5);
      group.add(light);
      group.userData.nav = light;
    }
    const rand = mulberry32(c.wobble_seed);
    group.userData.phase = [rand() * 6.28, rand() * 6.28, rand() * 6.28, 0.6 + rand() * 0.8];
    group.userData.size = MODEL_SIZE[c.model];
    group.visible = false;
    this.scene.add(group);
    return group;
  }

  /** Wobble offset (visual only) written into out. */
  wobble(c, t, out) {
    const [p1, p2, p3, f] = this.meshes.get(c.id).userData.phase;
    const a = WOBBLE[c.model];
    out[0] += a * Math.sin(t * f + p1);
    out[1] += a * 0.6 * Math.sin(t * f * 1.7 + p2);
    out[2] += a * Math.sin(t * f * 0.8 + p3);
  }

  setSensorMode(mode) {
    this.mode = mode;
    const thermal = mode === 'thermal';
    this.contactMat.color.set(thermal ? 0xffffff : this.look.contact);
    this.contactMat.emissive.set(thermal ? 0xffffff : mode === 'nv' ? 0x5a5a5a : 0x000000);
    // Heat cuts through haze better than visible light; fog still limits the other modes.
    this.contactMat.fog = !thermal;
    this.contactMat.needsUpdate = true;
    if (this.stars) this.stars.visible = !thermal;
    // White-hot thermal: cold sky reads dark, the ground a cool mid-grey, warm contacts bright.
    this.sky.visible = !thermal;
    this.scene.background = thermal ? new THREE.Color(0x161616) : null;
    this.scene.fog.color.set(thermal ? 0x303030 : this.look.fog);
    // Thermal shows the background as cool, even greys whatever the time of day.
    this.hemi.intensity = mode === 'nv' ? Math.max(1.4, this.look.amb * 3) : thermal ? 0.9 : this.look.amb;
    this.sun.intensity = thermal ? 0.3 : this.look.sunI;
  }

  resize(w, h) {
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.viewHeight = h;
  }

  setZoom(z) {
    this.camera.fov = this.baseFov / z;
    this.camera.updateProjectionMatrix();
  }

  /** World metres per screen pixel at a given distance. */
  metresPerPixel(d) {
    return (2 * d * Math.tan((this.camera.fov * Math.PI) / 360)) / (this.viewHeight || 1);
  }

  render() {
    this.renderer.render(this.scene, this.camera);
  }
}
