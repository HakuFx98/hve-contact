import React from 'react';
import { Composition } from 'remotion';
import { WhatIf } from './WhatIf';

export const RemotionRoot: React.FC = () => (
  <Composition id="WhatIf" component={WhatIf} durationInFrames={770} fps={30} width={1280} height={720} />
);
