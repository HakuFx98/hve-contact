import React, { useMemo } from 'react';
import * as THREE from 'three';

/* Deterministic random so every render tab draws the same city. */
export const rng = (seed: number) => () => {
  seed = (seed * 16807) % 2147483647;
  return (seed - 1) / 2147483646;
};

/** Vertical sunset gradient painted on the inside of a big sphere. */
export const Sky: React.FC<{ top?: string; mid?: string; horizon?: string }> = ({
  top = '#5d4f9e',
  mid = '#9a7cc4',
  horizon = '#f0a9b4',
}) => {
  const tex = useMemo(() => {
    const c = document.createElement('canvas');
    c.width = 4;
    c.height = 512;
    const g = c.getContext('2d')!;
    const grd = g.createLinearGradient(0, 0, 0, 512);
    grd.addColorStop(0, top);
    grd.addColorStop(0.55, mid);
    grd.addColorStop(0.8, horizon);
    grd.addColorStop(1, horizon);
    g.fillStyle = grd;
    g.fillRect(0, 0, 4, 512);
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }, [top, mid, horizon]);
  return (
    <mesh>
      <sphereGeometry args={[120, 32, 32, 0, Math.PI * 2, 0, Math.PI / 2 + 0.15]} />
      <meshBasicMaterial map={tex} side={THREE.BackSide} fog={false} />
    </mesh>
  );
};

/** Window grid texture: wall colour + warm lit windows (+ matching emissive map). */
const useWindows = (seed: number, wall: string) =>
  useMemo(() => {
    const r = rng(seed);
    const make = (emissive: boolean) => {
      const c = document.createElement('canvas');
      c.width = 256;
      c.height = 512;
      const g = c.getContext('2d')!;
      g.fillStyle = emissive ? '#000' : wall;
      g.fillRect(0, 0, 256, 512);
      return { c, g };
    };
    const base = make(false);
    const glow = make(true);
    for (let y = 16; y < 500; y += 40) {
      for (let x = 14; x < 240; x += 40) {
        const lit = r() < 0.32;
        const warm = r() < 0.7 ? '#ffd28a' : '#ffb8a0';
        base.g.fillStyle = lit ? warm : '#3a2f5c';
        base.g.fillRect(x, y, 26, 26);
        if (lit) {
          glow.g.fillStyle = warm;
          glow.g.fillRect(x, y, 26, 26);
        }
      }
    }
    const tex = (c: HTMLCanvasElement) => {
      const t = new THREE.CanvasTexture(c);
      t.colorSpace = THREE.SRGBColorSpace;
      return t;
    };
    return { map: tex(base.c), emissive: tex(glow.c) };
  }, [seed, wall]);

export const Building: React.FC<{ position: [number, number, number]; size: [number, number, number]; seed: number; wall?: string }> = ({
  position,
  size,
  seed,
  wall = '#6c5a96',
}) => {
  const { map, emissive } = useWindows(seed, wall);
  return (
    <mesh position={[position[0], position[1] + size[1] / 2, position[2]]}>
      <boxGeometry args={size} />
      <meshStandardMaterial map={map} emissiveMap={emissive} emissive="#ffffff" emissiveIntensity={0.55} roughness={0.9} />
    </mesh>
  );
};

/** Rooftop: floor, parapet, water tower, vents + a skyline all around. */
export const Rooftop: React.FC = () => {
  const skyline = useMemo(() => {
    const r = rng(7);
    const out: { p: [number, number, number]; s: [number, number, number]; seed: number }[] = [];
    for (let i = 0; i < 26; i++) {
      const a = -Math.PI * 0.95 + (i / 26) * Math.PI * 0.9; // arc behind the camera's usual view
      const d = 16 + r() * 18;
      const h = 8 + r() * 16;
      out.push({ p: [Math.cos(a) * d, -6, Math.sin(a) * d], s: [3 + r() * 3, h, 3 + r() * 3], seed: i + 3 });
    }
    return out;
  }, []);

  return (
    <group>
      <Sky />
      {/* roof slab */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[16, 12]} />
        <meshStandardMaterial color="#6e5470" roughness={0.95} />
      </mesh>
      <mesh position={[0, -3.05, 0]}>
        <boxGeometry args={[16, 6, 12]} />
        <meshStandardMaterial color="#4a3b66" roughness={1} />
      </mesh>
      {/* parapet walls */}
      {[
        { p: [0, 0.35, -6], s: [16, 0.7, 0.3] },
        { p: [-8, 0.35, 0], s: [0.3, 0.7, 12] },
        { p: [8, 0.35, 0], s: [0.3, 0.7, 12] },
      ].map((w, i) => (
        <mesh key={i} position={w.p as [number, number, number]} castShadow receiveShadow>
          <boxGeometry args={w.s as [number, number, number]} />
          <meshStandardMaterial color="#5d4b78" roughness={0.9} />
        </mesh>
      ))}
      {/* water tower */}
      <group position={[4.5, 0, -4]}>
        <mesh position={[0, 3.3, 0]} castShadow>
          <cylinderGeometry args={[1.3, 1.3, 2.2, 32]} />
          <meshStandardMaterial color="#b8714a" roughness={0.7} />
        </mesh>
        <mesh position={[0, 4.65, 0]} castShadow>
          <coneGeometry args={[1.45, 0.6, 32]} />
          <meshStandardMaterial color="#8d5236" roughness={0.7} />
        </mesh>
        {[0, 1, 2, 3].map((i) => (
          <mesh key={i} position={[Math.cos((i * Math.PI) / 2 + 0.78) * 1.0, 1.1, Math.sin((i * Math.PI) / 2 + 0.78) * 1.0]} castShadow>
            <cylinderGeometry args={[0.06, 0.06, 2.2, 8]} />
            <meshStandardMaterial color="#2e2238" />
          </mesh>
        ))}
      </group>
      {/* vent boxes */}
      <mesh position={[-5, 0.4, -3.5]} castShadow>
        <boxGeometry args={[1.2, 0.8, 1]} />
        <meshStandardMaterial color="#7a6a93" roughness={0.6} metalness={0.3} />
      </mesh>
      <mesh position={[-3.6, 0.25, -4.6]} castShadow>
        <boxGeometry args={[0.8, 0.5, 0.8]} />
        <meshStandardMaterial color="#7a6a93" roughness={0.6} metalness={0.3} />
      </mesh>
      {/* nearby taller buildings framing the roof */}
      <Building position={[-6, -6, -12]} size={[5, 20, 4]} seed={101} />
      <Building position={[2, -6, -15]} size={[4, 22, 4]} seed={202} />
      <Building position={[9, -6, -11]} size={[5, 17, 5]} seed={303} wall="#7a6390" />
      {skyline.map((b, i) => (
        <Building key={i} position={b.p} size={b.s} seed={b.seed} />
      ))}
    </group>
  );
};

/** Floating dust motes — deterministic, drift with time. */
export const Dust: React.FC<{ t: number; count?: number }> = ({ t, count = 140 }) => {
  const base = useMemo(() => {
    const r = rng(42);
    return Array.from({ length: count }, () => [r() * 14 - 7, r() * 4, r() * 8 - 4, r() * 6.28] as const);
  }, [count]);
  const positions = useMemo(() => new Float32Array(count * 3), [count]);
  base.forEach(([x, y, z, ph], i) => {
    positions[i * 3] = x + Math.sin(t * 0.3 + ph) * 0.3;
    positions[i * 3 + 1] = (y + t * 0.08) % 4;
    positions[i * 3 + 2] = z + Math.cos(t * 0.25 + ph) * 0.3;
  });
  return (
    <points key={Math.floor(t * 1000)}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} count={count} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial color="#fff3e6" size={0.03} transparent opacity={0.7} toneMapped={false} />
    </points>
  );
};
