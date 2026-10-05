"use client";

import { useEffect, useRef, useState } from "react";
import { PLACEHOLDER_IMAGE } from "@/lib/constants";

// Shows the product photo, or a placeholder when there is none / it fails to load.
// Plain <img> is used because images will come from Supabase Storage URLs.
export default function ProductImage({ src, alt, className, priority = false }) {
  const [failed, setFailed] = useState(false);
  const imgRef = useRef(null);
  const url = !src || failed ? PLACEHOLDER_IMAGE : src;

  // The server-rendered <img> may fail before React hydrates and attaches
  // onError, so check its state once after mount as well.
  useEffect(() => {
    const img = imgRef.current;
    if (img && img.complete && img.naturalWidth === 0) setFailed(true);
  }, []);

  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      ref={imgRef}
      src={url}
      alt={alt}
      className={className}
      loading={priority ? "eager" : "lazy"}
      onError={() => setFailed(true)}
    />
  );
}
