import React from 'react';
import { ThreeCanvas } from '@remotion/three';
import { useThree } from '@react-three/fiber';
import { EffectComposer, Bloom, Vignette, DepthOfField, HueSaturation } from '@react-three/postprocessing';
import * as THREE from 'three';
import { AbsoluteFill, Easing, Sequence, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { Toon, Face, Pose, STRIDE } from './Toon';
import { Rooftop, Dust } from './City';

/* ==================================================================
 * "What If You Could Pause Time?" — sample opening.
 * Each shot = one narration line, ~2.5s average shot length.
 * ================================================================== */

const MINT = '#3ccf9b'; // Kai (protagonist)
const TEAL = '#e0607e'; // Juni (friend)
const GOLD = '#f5ce62';
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const ease = { easing: Easing.inOut(Easing.cubic), ...clamp };
type V3 = [number, number, number];
const lerp3 = (a: V3, b: V3, t: number) => a.map((v, i) => v + (b[i] - v) * t) as V3;

type ShotDef = { id: string; frames: number; line: string; Shot: React.FC; frozen?: boolean };

const CameraRig: React.FC<{ pos: V3; target: V3; fov?: number }> = ({ pos, target, fov = 35 }) => {
  const camera = useThree((s) => s.camera) as THREE.PerspectiveCamera;
  camera.position.set(...pos);
  camera.lookAt(...target);
  if (camera.fov !== fov) {
    camera.fov = fov;
    camera.updateProjectionMatrix();
  }
  return null;
};

/** Shared stage: lights, set, atmosphere, post-processing. */
const Stage: React.FC<{ cam: V3; target: V3; focus: V3; fov?: number; frozen?: boolean; t: number; children: React.ReactNode }> = ({
  cam,
  target,
  focus,
  fov,
  frozen,
  t,
  children,
}) => {
  const { width, height } = useVideoConfig();
  return (
    <ThreeCanvas width={width} height={height} shadows camera={{ fov: 35, near: 0.1, far: 300 }}>
      <fog attach="fog" args={['#c08fb3', 14, 70]} />
      <hemisphereLight args={['#e2d4ff', '#7a4f6e', 1.3]} />
      {/* warm sunset key */}
      <directionalLight position={[-6, 5, 6]} intensity={1.5} color="#ffc9a3" castShadow shadow-mapSize={[1024, 1024]} shadow-camera-left={-8} shadow-camera-right={8} shadow-camera-top={8} shadow-camera-bottom={-8} shadow-bias={-0.0005} />
      {/* back rim light — the glowing edge around characters */}
      <directionalLight position={[2, 4, -8]} intensity={2.2} color="#ffd6b8" />
      {/* soft lilac front fill so faces read bright white */}
      <directionalLight position={[3, 2.5, 8]} intensity={1.1} color="#eadfff" />
      <CameraRig pos={cam} target={target} fov={fov} />
      <Rooftop />
      <Dust t={frozen ? 0.5 : t} />
      {children}
      <EffectComposer multisampling={0}>
        <DepthOfField target={focus} focalLength={0.012} bokehScale={7} height={480} />
        <Bloom mipmapBlur intensity={0.8} luminanceThreshold={0.85} />
        <HueSaturation saturation={frozen ? -0.55 : 0.05} />
        <Vignette offset={0.3} darkness={0.6} />
      </EffectComposer>
    </ThreeCanvas>
  );
};

const blinkAt = (f: number, o = 0) => (f + o) % 80 < 4;

/* ---------- Shot 1: establishing — Kai walks to the roof edge ---------- */
const Shot1: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / 30;
  const k = interpolate(f, [0, 80], [0, 1], ease);
  const kaiX = interpolate(f, [0, 66], [-2.4, 0], clamp);
  const walkAmp = interpolate(f, [0, 4, 60, 68], [0.4, 1, 1, 0], clamp);
  const kaiRot = interpolate(f, [0, 62, 74], [Math.PI / 2 - 0.25, Math.PI / 2 - 0.25, 0.35], ease);
  return (
    <Stage cam={lerp3([-3.5, 2.4, 7.5], [-1.4, 1.9, 6.2], k)} target={[kaiX * 0.5, 1.5, 0]} focus={[kaiX, 1.8, 0]} t={t}>
      <Toon position={[kaiX, 0, 0]} rotationY={kaiRot} hoodie={MINT} face={f > 70 ? 'happy' : 'open'} blink={blinkAt(f)} pose="idle" t={t} walk={(kaiX + 2.4) / STRIDE} walkAmp={walkAmp} />
      <Toon position={[2.2, 0, -1.2]} rotationY={-0.6} hoodie={TEAL} cap="#2e2e38" face="happy" pose="wave" t={t} />
    </Stage>
  );
};

/* ---------- Shot 2: close-up — smug grin, finger snap ---------- */
const Shot2: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / 30;
  const snap = 40;
  const push = interpolate(f, [0, 75], [0, 1], ease);
  const shake = f > snap && f < snap + 8 ? Math.sin(f * 5) * 0.03 : 0;
  const ring = interpolate(f, [snap, snap + 25], [0.2, 9], clamp);
  const ringO = interpolate(f, [snap, snap + 25], [1, 0], clamp);
  const pose: Pose = f > snap - 12 ? 'wave' : 'idle';
  const face: Face = f > snap ? 'smug' : 'open';
  return (
    <Stage cam={lerp3([1.1 + shake, 2.0, 4.2], [0.8 + shake, 1.95, 3.4], push)} target={[0, 1.85, 0]} focus={[0, 2.0, 0.3]} fov={30} t={t} frozen={f > snap}>
      <Toon position={[0, 0, 0]} rotationY={0.25} hoodie={MINT} face={face} blink={f < snap && blinkAt(f, 30)} pose={pose} t={f > snap ? 0 : t} />
      {f > snap && (
        <mesh position={[0, 1.4, 0]} rotation={[Math.PI / 2, 0, 0]} scale={ring}>
          <torusGeometry args={[1, 0.02, 8, 64]} />
          <meshBasicMaterial color={[3, 3, 3.5]} transparent opacity={ringO} toneMapped={false} />
        </mesh>
      )}
    </Stage>
  );
};

/* ---------- Shot 3: frozen world — Juni stuck mid-jump, soda frozen in air ---------- */
const Shot3: React.FC = () => {
  const f = useCurrentFrame();
  const k = interpolate(f, [0, 90], [0, 1], ease);
  // slow orbit around the frozen moment
  const a = -0.5 + k * 0.7;
  const cam: V3 = [Math.sin(a) * 6 + 1.0, 1.9, Math.cos(a) * 6];
  return (
    <Stage cam={cam} target={[1.0, 1.9, 0]} focus={[1.5, 1.8, 0]} t={0} frozen>
      <Toon position={[1.5, 0.55, 0]} rotationY={-0.2} hoodie={TEAL} cap="#2e2e38" face="happy" pose="cheer" t={0.11} />
      {/* soda can + frozen droplets */}
      <group position={[2.3, 2.7, 0.6]} rotation={[0.6, 0.3, 0.9]}>
        <mesh>
          <cylinderGeometry args={[0.09, 0.09, 0.3, 24]} />
          <meshStandardMaterial color="#e2483d" metalness={0.6} roughness={0.3} />
        </mesh>
      </group>
      {Array.from({ length: 9 }, (_, i) => (
        <mesh key={i} position={[2.35 + Math.cos(i) * 0.3, 2.55 + Math.sin(i * 2.1) * 0.25, 0.6 + Math.sin(i) * 0.2]}>
          <sphereGeometry args={[0.025 + (i % 3) * 0.01, 10, 8]} />
          <meshStandardMaterial color="#ffd9b8" transparent opacity={0.85} roughness={0.1} />
        </mesh>
      ))}
      <Toon position={[interpolate(f, [0, 90], [4.6, 2.9], clamp), 0, -1.4]} rotationY={-Math.PI / 2 + 0.3} hoodie={MINT} face="happy" pose="idle" t={f / 30} blink={blinkAt(f, 10)} walk={(4.6 - interpolate(f, [0, 90], [4.6, 2.9], clamp)) / STRIDE} walkAmp={1} />
    </Stage>
  );
};

/* ---------- Shot 4: low-angle hero — Kai looks up at a frozen sky ---------- */
const Shot4: React.FC = () => {
  const f = useCurrentFrame();
  const k = interpolate(f, [0, 75], [0, 1], ease);
  return (
    <Stage cam={lerp3([0.5, 0.45, 4.6], [0.35, 0.7, 3.9], k)} target={[0, 2.1, 0]} focus={[0, 2.0, 0]} fov={42} t={0} frozen>
      <Toon position={[0, 0, 0]} rotationY={0.1} hoodie={MINT} face={f > 25 ? 'happy' : 'shock'} pose={f > 25 ? 'fists' : 'idle'} t={f / 30} />
    </Stage>
  );
};

export const SHOTS: ShotDef[] = [
  { id: 'roof', frames: 85, line: 'It’s Friday. You’re on the roof with Juni, like always.', Shot: Shot1 },
  { id: 'snap', frames: 80, line: 'You snap your fingers… and the whole world just stops.', Shot: Shot2 },
  { id: 'frozen', frames: 90, line: 'Juni is frozen mid-jump. Her soda hangs in the air.', Shot: Shot3, frozen: true },
  { id: 'hero', frames: 75, line: 'Nothing moves. Nothing… except you.', Shot: Shot4, frozen: true },
];
export const episodeLength = SHOTS.reduce((a, s) => a + s.frames, 0);

/* ======================= 2D overlays ======================= */

const Captions: React.FC<{ text: string; frames: number }> = ({ text, frames }) => {
  const frame = useCurrentFrame();
  const words = text.split(' ');
  const per = (frames - 14) / words.length;
  return (
    <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 40 }}>
      <div style={{ maxWidth: 980, textAlign: 'center', fontFamily: 'Inter, sans-serif', fontWeight: 900, fontSize: 36, lineHeight: 1.25 }}>
        {words.map((w, i) => {
          const on = frame >= i * per;
          const active = on && frame < (i + 1) * per;
          return (
            <span key={i} style={{ color: active ? GOLD : '#fff', opacity: on ? 1 : 0, display: 'inline-block', margin: '0 6px', transform: `scale(${active ? 1.1 : 1})`, textShadow: '0 3px 0 #1d1430, 0 0 14px rgba(29,20,48,0.9)' }}>
              {w}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/** Game-style ability pills, top-right. */
const Abilities: React.FC<{ start: number }> = ({ start }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const items: [React.ReactNode, string][] = [
    [<svg width="20" height="20" viewBox="0 0 20 20"><rect x="3" y="2" width="5" height="16" rx="2" fill="#7fd6ff" /><rect x="12" y="2" width="5" height="16" rx="2" fill="#7fd6ff" /></svg>, 'TIME PAUSED'],
    [<svg width="20" height="20" viewBox="0 0 20 20"><circle cx="10" cy="5" r="4" fill={MINT} /><rect x="5" y="10" width="10" height="9" rx="4" fill={MINT} /></svg>, 'ONLY YOU MOVE'],
    [<svg width="20" height="20" viewBox="0 0 20 20"><path d="M4 2h12M4 18h12M5 2c0 6 10 6 10 16M15 2c0 6-10 6-10 16" stroke="#ff8f8f" strokeWidth="2.4" fill="none" strokeLinecap="round" /></svg>, `${Math.max(0, 600 - Math.floor((frame - start) / 3))}s REMAINING`],
  ];
  return (
    <div style={{ position: 'absolute', top: 24, right: 24, display: 'flex', flexDirection: 'column', gap: 8 }}>
      {items.map(([icon, label], i) => {
        const s = spring({ frame: frame - start - i * 8, fps, config: { damping: 13 } });
        return (
          <div key={i} style={{ opacity: s, transform: `translateX(${(1 - s) * 60}px)`, display: 'flex', alignItems: 'center', gap: 12, padding: '8px 22px 8px 14px', borderRadius: 30, background: 'rgba(29,21,40,0.82)', border: '2px solid #3a2d50', fontFamily: 'Inter, sans-serif', fontWeight: 900, fontSize: 22, letterSpacing: 2, color: GOLD }}>
            <span style={{ display: 'flex' }}>{icon}</span>
            {label}
          </div>
        );
      })}
    </div>
  );
};

/** "RULE 1" card on frosted/steamed glass. */
const RuleCard: React.FC<{ n: number; text: string }> = ({ n, text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - 18, fps, config: { damping: 14 } });
  const wipe = interpolate(frame, [18, 40], [0, 100], clamp);
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'flex-start', paddingLeft: 70 }}>
      <div
        style={{
          opacity: s,
          transform: `translateY(${(1 - s) * 30}px)`,
          padding: '22px 36px',
          borderRadius: 22,
          background: 'rgba(30,20,55,0.45)',
          backdropFilter: 'blur(14px)',
          border: '2px solid rgba(255,255,255,0.35)',
          boxShadow: '0 10px 40px rgba(20,10,40,0.35)',
          clipPath: `inset(0 ${100 - wipe}% 0 0 round 22px)`,
        }}
      >
        <div style={{ fontFamily: 'Inter, sans-serif', fontWeight: 900, fontSize: 22, letterSpacing: 6, color: GOLD }}>RULE {n}</div>
        <div style={{ fontFamily: 'Inter, sans-serif', fontWeight: 800, fontSize: 46, color: '#fff', textShadow: '0 2px 10px rgba(29,20,48,0.6)' }}>{text}</div>
      </div>
    </AbsoluteFill>
  );
};

export const Episode: React.FC = () => {
  const frame = useCurrentFrame();
  let at = 0;
  const snapAt = SHOTS[0].frames + 40;
  return (
    <AbsoluteFill style={{ background: '#000' }}>
      {SHOTS.map((s) => {
        const from = at;
        at += s.frames;
        return (
          <Sequence key={s.id} from={from} durationInFrames={s.frames}>
            <s.Shot />
            {s.id === 'frozen' && <RuleCard n={1} text="Only you can move." />}
            <Captions text={s.line} frames={s.frames} />
          </Sequence>
        );
      })}
      <Sequence from={snapAt}>
        <Abilities start={8} />
      </Sequence>
      {/* white flash on the snap */}
      <AbsoluteFill style={{ background: '#fff', pointerEvents: 'none', opacity: frame - snapAt >= 0 && frame - snapAt < 6 ? (6 - (frame - snapAt)) / 7 : 0 }} />
    </AbsoluteFill>
  );
};
