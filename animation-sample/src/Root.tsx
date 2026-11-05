import React from 'react';
import { Composition } from 'remotion';
import { WhatIf } from './WhatIf';
import { Story3D, storyLength } from './Story3D';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Story3D" component={Story3D} durationInFrames={storyLength} fps={30} width={1280} height={720} />
    <Composition id="WhatIf" component={WhatIf} durationInFrames={770} fps={30} width={1280} height={720} />
  </>
);
