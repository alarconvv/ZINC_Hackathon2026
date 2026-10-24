export function elapsedSeconds(start:number,now:number,limit=30){return Math.max(0,Math.min(limit,Math.floor((now-start)/1000)));}
