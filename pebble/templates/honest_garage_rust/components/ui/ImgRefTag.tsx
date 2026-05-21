/**
 * Warm-amber IMG-REF corner tag for photos. Sits in the bottom-left of any
 * absolutely-positioned image container (parent must be `relative`). Per the
 * auto_honest_diag DNA — every photo on the site gets one.
 */
export function ImgRefTag({ code }: { code: string }) {
  return <span className="img-ref-tag">{code}</span>;
}
