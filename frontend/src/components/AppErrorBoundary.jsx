import React from "react";
import { feLogger } from "../logging/logger";

export class AppErrorBoundary extends React.Component {
  constructor(props){ super(props); this.state = { hasError: false }; }
  static getDerivedStateFromError(){ return { hasError: true }; }
  componentDidCatch(error, info){
    feLogger.error("ui","render-error",{ message: error.message, stack: error.stack, componentStack: info.componentStack });
  }
  render(){
    if (this.state.hasError) {
      return <div style={{ padding: "2rem", color: "#b30000" }}>Ein unerwarteter UI-Fehler ist aufgetreten. Bitte neu laden.</div>;
    }
    return this.props.children;
  }
}