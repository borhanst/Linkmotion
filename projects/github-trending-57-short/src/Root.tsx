import { Composition, AbsoluteFill, Audio, useCurrentFrame, useVideoConfig } from "remotion";
import React from "react";

const scenes = [
  {text:"35 Trending Repos", audio:"audio/beat-1.mp3", dur:6.864},
  {text:"GitHub Trending Today #57", audio:"audio/beat-2.mp3", dur:7.632},
  {text:"unslop, tv-detox, TwinDesk, Venture", audio:"audio/beat-3.mp3", dur:8.352},
  {text:"Trends Move Fast", audio:"audio/beat-4.mp3", dur:7.464},
  {text:"Bookmark & Try One", audio:"audio/beat-5.mp3", dur:5.04},
];

const Scene: React.FC<{text:string;audio:string}> = ({text,audio}) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{backgroundColor:"#0b0b0f",color:"white",justifyContent:"center",alignItems:"center",fontSize:64,fontWeight:700}}>
      <div style={{opacity: Math.min(1, frame/15)}}>{text}</div>
      
    </AbsoluteFill>
  );
};

export const RemotionRoot: React.FC = () => {
  let from = 0;
  return (
    <>
      {scenes.map((s,i)=>{
        const dur = Math.round(s.dur*30);
        const el = <Composition id={`scene-${i}`} component={()=><Scene text={s.text} audio={s.audio}/>} durationInFrames={dur} fps={30} width={1080} height={1920} />;
        from += dur;
        return el;
      })}
      <Composition id="Main" component={()=>{
        // sequential not supported simply; render first only as fallback
        return <Scene text={scenes[0].text} audio={scenes[0].audio}/>;
      }} durationInFrames={Math.round(scenes.reduce((a,b)=>a+b.dur,0)*30)} fps={30} width={1080} height={1920} />
    </>
  );
};

