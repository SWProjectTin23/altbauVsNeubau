// Lightweight frontend logger
const LEVELS = ["silent","error","warn","info","debug"];
const MAP = { error: console.error, warn: console.warn, info: console.info, debug: console.debug };
const activeLevel = (process.env.REACT_APP_LOG_LEVEL || "warn").toLowerCase();
const activeIdx = Math.max(0, LEVELS.indexOf(activeLevel));

function should(level){ return LEVELS.indexOf(level) <= activeIdx && level !== "silent"; }
function fmt(sys, lvl, msg, meta){
  const base = `[FE][${lvl.toUpperCase()}][${sys}] ${msg}`;
  return meta && Object.keys(meta).length ? `${base} | ${JSON.stringify(meta)}` : base;
}

export function log(sys, lvl, msg, meta = {}) {
  if (!should(lvl)) return;
  (MAP[lvl] || console.log)(fmt(sys,lvl,msg,meta));
}

export const feLogger = {
  debug:(s,m,meta)=>log(s,"debug",m,meta),
  info:(s,m,meta)=>log(s,"info",m,meta),
  warn:(s,m,meta)=>log(s,"warn",m,meta),
  error:(s,m,meta)=>log(s,"error",m,meta)
};