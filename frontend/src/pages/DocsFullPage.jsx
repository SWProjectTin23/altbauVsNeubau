import React, { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function DocsFullPage() {
  const [content, setContent] = useState("");

  useEffect(() => {
    fetch("/docs/docs_full.md")
      .then(res => res.text())
      .then(setContent);
  }, []);

  return (
    <div className="markdown-body" style={{ padding: "2rem", maxWidth: "900px", margin: "auto" }}>
      <ReactMarkdown children={content} remarkPlugins={[remarkGfm]} />
    </div>
  );
}