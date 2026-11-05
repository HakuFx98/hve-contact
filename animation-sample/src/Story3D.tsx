import React, { useMemo } from 'react';
import { ThreeCanvas } from '@remotion/three';
import { useThree } from '@react-three/fiber';
import { Billboard } from '@react-three/drei';
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing';
import * as THREE from 'three';
import {
  AbsoluteFill,
  Easing,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { Character3D, Expr } from './Character3D';

const NEON = '#3dffa2';
const GOLD = '#f5c451';
const RED = '#ff5470';
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const ease = { easing: Easing.inOut(Easing.cubic), ...clamp };

/* =====================================================================
 * STORY SCRIPT
 * A long-form episode is just a longer list of these shots. Each shot
 * says which set to use, how long it lasts, and the narration line
 * (which later gets a voiceover and drives captions).
 * ===================================================================== */
type Shot = { id: string; frames: number; narration: string; render: React.FC };

export const SHOTS: Shot[] = [
  { id: 'walk-in', frames: 105, narration: 'You walk into school like any other Monday…', render: () => <HallwayShot part="walk" /> },
  { id: 'reveal', frames: 75, narration: 'but now there’s a number floating over every head.', render: () => <HallwayShot part="reveal" /> },
  { id: 'react', frames: 75, narration: 'And then you see it. Ninety-nine.', render: () => <HallwayShot part="react" /> },
];

export const storyLength = SHOTS.reduce((a, s) => a + s.frames, 0);

/* ===================== reusable 3D pieces ===================== */

// Text drawn onto a canvas texture: synchronous + deterministic for rendering.
const useLabel = (text: string, color: string) =>
  useMemo(() => {
    const c = document.createElement('canvas');
    c.width = 512;
    c.height = 224;
    const ctx = c.getContext('2d')!;
    ctx.fillStyle = 'rgba(12,6,34,0.85)';
    ctx.strokeStyle = color;
    ctx.lineWidth = 14;
    ctx.beginPath();
    ctx.roundRect(14, 14, 484, 196, 98);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = color;
    ctx.font = '900 120px Inter';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, 256, 120);
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }, [text, color]);

const LuckTag: React.FC<{ position: [number, number, number]; value: number; appear: number }> = ({ position, value, appear }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const color = value > 90 ? GOLD : value < 10 ? RED : NEON;
  const tex = useLabel(`${value}`, color);
  const s = spring({ frame: frame - appear, fps, config: { damping: 9, mass: 0.6 } });
  const float = Math.sin((frame + appear) / 10) * 0.04;
  if (s < 0.01) return null;
  return (
    <Billboard position={[position[0], position[1] + float, position[2]]}>
      <mesh scale={[0.75 * s, 0.33 * s, 1]}>
        <planeGeometry />
        {/* toneMapped=false + >1 colour makes bloom pick it up as a glow */}
        <meshBasicMaterial map={tex} transparent toneMapped={false} color={[1.6, 1.6, 1.6]} />
      </mesh>
    </Billboard>
  );
};

const Hallway: React.FC = () => {
  const lockers = Array.from({ length: 34 }, (_, i) => i);
  return (
    <group>
      {/* floor: slightly glossy */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[80, 20]} />
        <meshStandardMaterial color="#3a3170" roughness={0.35} metalness={0.15} />
      </mesh>
      {/* back wall */}
      <mesh position={[0, 3, -2.2]} receiveShadow>
        <planeGeometry args={[80, 6]} />
        <meshStandardMaterial color="#2a2066" roughness={0.9} />
      </mesh>
      {lockers.map((i) => (
        <group key={i} position={[-12 + i * 0.72, 1.05, -2.05]}>
          <mesh castShadow receiveShadow>
            <boxGeometry args={[0.68, 2.1, 0.3]} />
            <meshStandardMaterial color={i % 2 ? '#4247a3' : '#3c4198'} roughness={0.4} metalness={0.3} />
          </mesh>
          {[0.75, 0.65, 0.55].map((y) => (
            <mesh key={y} position={[0, y, 0.155]}>
              <boxGeometry args={[0.5, 0.03, 0.01]} />
              <meshStandardMaterial color="#262a6e" />
            </mesh>
          ))}
          <mesh position={[0.24, 0, 0.17]}>
            <boxGeometry args={[0.04, 0.18, 0.03]} />
            <meshStandardMaterial color="#b9bdf5" metalness={0.8} roughness={0.2} />
          </mesh>
        </group>
      ))}
      {/* glowing ceiling strips */}
      {Array.from({ length: 14 }, (_, i) => (
        <mesh key={i} position={[-12 + i * 2.6, 3.6, -0.6]}>
          <boxGeometry args={[1.4, 0.05, 0.25]} />
          <meshBasicMaterial color={[3, 3, 4]} toneMapped={false} />
        </mesh>
      ))}
    </group>
  );
};

const Lights: React.FC = () => (
  <>
    <color attach="background" args={['#120a33']} />
    <fog attach="fog" args={['#160c3d', 7, 22]} />
    <hemisphereLight args={['#b7a8ff', '#2a1250', 0.9]} />
    <directionalLight
      position={[3, 6, 5]}
      intensity={1.6}
      color="#ffe9f0"
      castShadow
      shadow-mapSize={[1024, 1024]}
      shadow-camera-left={-10}
      shadow-camera-right={10}
      shadow-camera-top={6}
      shadow-camera-bottom={-6}
    />
    {/* magenta rim light — gives the moody coloured edge */}
    <pointLight position={[-4, 2.5, 2]} intensity={6} color="#c44dff" distance={14} />
  </>
);

const CameraRig: React.FC<{ pos: [number, number, number]; target: [number, number, number]; fov?: number }> = ({ pos, target, fov = 40 }) => {
  const camera = useThree((s) => s.camera) as THREE.PerspectiveCamera;
  camera.position.set(...pos);
  camera.lookAt(...target);
  if (camera.fov !== fov) {
    camera.fov = fov;
    camera.updateProjectionMatrix();
  }
  return null;
};

const lerp3 = (a: number[], b: number[], t: number) => a.map((v, i) => v + (b[i] - v) * t) as [number, number, number];

/* ===================== shots ===================== */

const STUDENTS = [
  { x: 4.2, luck: 12, shirt: '#e0566f', hair: '#5a2a1a', style: 'long' as const, expr: 'neutral' as Expr, appear: 0 },
  { x: 5.6, luck: 99, shirt: '#ffb340', hair: '#ffd84a', style: 'spiky' as const, expr: 'happy' as Expr, appear: 18 },
  { x: 7.0, luck: 47, shirt: '#8a5cff', hair: '#111111', style: 'short' as const, expr: 'neutral' as Expr, appear: 30 },
  { x: 8.4, luck: 3, shirt: '#56c2e0', hair: '#6b4a2f', style: 'short' as const, expr: 'neutral' as Expr, appear: 40 },
];

const HallwayShot: React.FC<{ part: 'walk' | 'reveal' | 'react' }> = ({ part }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const blink = (o: number) => (frame + o) % 70 < 4;

  // where "you" are and what the camera does, per shot
  let youX = 2.4;
  let walk: number | undefined;
  let youRot = 0.5;
  let expr: Expr = 'neutral';
  let cam: [number, number, number];
  let tgt: [number, number, number];
  let fov = 40;

  if (part === 'walk') {
    youX = interpolate(frame, [0, 105], [-3, 2.4], clamp);
    walk = frame / 3.2;
    youRot = Math.PI / 2;
    const t = interpolate(frame, [0, 105], [0, 1], ease);
    cam = lerp3([youX - 1.5, 1.4, 5.2], [youX + 0.2, 1.7, 4.6], t);
    tgt = [youX + 1.2, 1.3, 0];
  } else if (part === 'reveal') {
    // low-angle dolly past the students
    const t = interpolate(frame, [0, 75], [0, 1], ease);
    cam = lerp3([3.4, 1.1, 4.6], [5.4, 1.2, 4.0], t);
    tgt = lerp3([5.6, 1.8, -0.4], [6.3, 1.9, -0.4], t);
    youRot = Math.PI / 2;
  } else {
    // snap zoom onto your shocked face
    const t = interpolate(frame, [0, 14], [0, 1], { easing: Easing.out(Easing.exp), ...clamp });
    cam = lerp3([4.6, 1.8, 4.0], [3.2, 1.75, 2.3], t);
    tgt = [2.4, 1.6, 0];
    fov = interpolate(frame, [0, 75], [38, 32], clamp);
    expr = frame > 6 ? 'shock' : 'neutral';
    youRot = interpolate(frame, [0, 6], [Math.PI / 2, 0.55], clamp);
  }
  const shake = part === 'react' && frame > 6 && frame < 16 ? Math.sin(frame * 4) * 0.03 : 0;

  return (
    <ThreeCanvas width={width} height={height} shadows gl={{ antialias: true }} camera={{ fov: 40 }}>
      <Lights />
      <CameraRig pos={[cam[0] + shake, cam[1], cam[2]]} target={tgt} fov={fov} />
      <Hallway />
      <Character3D position={[youX, 0, 0.3]} rotationY={youRot} walk={walk} expr={expr} blink={blink(0)} />
      {STUDENTS.map((s, i) => (
        <group key={i}>
          <Character3D position={[s.x, 0, -0.4]} rotationY={-0.35} shirt={s.shirt} hair={s.hair} hairStyle={s.style} expr={s.expr} blink={blink(i * 17)} />
          <LuckTag position={[s.x, 2.45, -0.4]} value={s.luck} appear={part === 'walk' ? 999 : part === 'reveal' ? s.appear : -30} />
        </group>
      ))}
      <EffectComposer multisampling={4}>
        <Bloom mipmapBlur intensity={1.1} luminanceThreshold={0.9} radius={0.7} />
        <Vignette offset={0.25} darkness={0.75} />
      </EffectComposer>
    </ThreeCanvas>
  );
};

/* ===================== 2D overlays (captions, HUD) ===================== */

const Captions: React.FC<{ text: string; frames: number }> = ({ text, frames }) => {
  const frame = useCurrentFrame();
  const words = text.split(' ');
  const per = (frames - 12) / words.length;
  return (
    <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 44 }}>
      <div style={{ maxWidth: 1000, textAlign: 'center', fontFamily: 'Inter, sans-serif', fontWeight: 900, fontSize: 38, lineHeight: 1.25 }}>
        {words.map((w, i) => {
          const on = frame >= i * per;
          const active = on && frame < (i + 1) * per;
          return (
            <span key={i} style={{ color: active ? NEON : '#fff', opacity: on ? 1 : 0, display: 'inline-block', margin: '0 7px', transform: `scale(${active ? 1.12 : 1})`, textShadow: '0 4px 0 #000, 0 0 12px rgba(0,0,0,0.8)' }}>
              {w}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const Hud: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - 110, fps, config: { damping: 10 } });
  return (
    <div style={{ position: 'absolute', top: 26, left: 26, opacity: s, transform: `scale(${0.6 + 0.4 * s})`, transformOrigin: 'left top', padding: '10px 22px', borderRadius: 40, background: 'rgba(10,6,30,0.6)', border: `3px solid ${NEON}`, boxShadow: `0 0 20px ${NEON}`, fontFamily: 'Inter, sans-serif', fontWeight: 900, fontSize: 30, color: '#fff' }}>
      🍀 YOUR LUCK: <span style={{ color: NEON }}>50</span>
    </div>
  );
};

/* ===================== composition ===================== */

export const Story3D: React.FC = () => {
  let at = 0;
  return (
    <AbsoluteFill style={{ background: '#000' }}>
      {SHOTS.map((s) => {
        const from = at;
        at += s.frames;
        const Shot = s.render;
        return (
          <Sequence key={s.id} from={from} durationInFrames={s.frames}>
            <Shot />
            <Captions text={s.narration} frames={s.frames} />
          </Sequence>
        );
      })}
      <Hud />
    </AbsoluteFill>
  );
};
