import React, {createContext, useContext, useEffect, useState} from 'react';
import {AccessibilityInfo} from 'react-native';
export const colors = {blue:'#126bc5', ocean:'#063774', surface:'#f4faff', ink:'#12365b', muted:'#526b84', rule:'#d6e7f5', pale:'#e8f3ff', danger:'#a51d25'};
export const fonts = {body:'DMSans_400Regular', medium:'DMSans_600SemiBold', heading:'Manrope_700Bold'};
const Preferences = createContext({large:false, contrast:false, setLarge:(_v:boolean)=>{}, setContrast:(_v:boolean)=>{}});
export const usePreferences = ()=>useContext(Preferences);
export function PreferencesProvider({children}:React.PropsWithChildren) {
 const [large,setLarge]=useState(false), [contrast,setContrast]=useState(false);
 return <Preferences.Provider value={{large,contrast,setLarge,setContrast}}>{children}</Preferences.Provider>;
}
export function useReducedMotion() {
 const [reduce,setReduce]=useState(true);
 useEffect(()=>{ AccessibilityInfo.isReduceMotionEnabled().then(setReduce); const listener=AccessibilityInfo.addEventListener('reduceMotionChanged',setReduce);return ()=>listener.remove(); },[]);
 return reduce;
}
