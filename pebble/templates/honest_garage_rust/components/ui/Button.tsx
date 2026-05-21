import Link from "next/link";
import { cn } from "@/lib/cn";
import type { ComponentProps, ReactNode } from "react";

type Variant = "primary" | "ghost";

const VARIANT_STYLES: Record<Variant, string> = {
  primary: "btn-primary",
  ghost: "btn-ghost",
};

type CommonProps = {
  variant?: Variant;
  className?: string;
  children: ReactNode;
};

type LinkProps = CommonProps & { href: string } & Omit<
  ComponentProps<typeof Link>,
  "href" | "className" | "children"
>;
type ButtonProps = CommonProps & { href?: undefined } & Omit<
  ComponentProps<"button">,
  "className" | "children"
>;

/**
 * Primary = filled rust + physical-button depress on :active.
 * Ghost = outlined bone on dark; hover flips to rust.
 *
 * Both reuse the same `.btn-primary` / `.btn-ghost` utilities defined in
 * globals.css so they stay consistent across the site.
 */
export function Button(props: LinkProps | ButtonProps) {
  const { variant = "primary", className, children, ...rest } = props;
  const classes = cn(VARIANT_STYLES[variant], className);

  if ("href" in props && props.href) {
    const { href, ...linkRest } = rest as LinkProps;
    return (
      <Link href={href} className={classes} {...linkRest}>
        {children}
      </Link>
    );
  }

  return (
    <button className={classes} {...(rest as ComponentProps<"button">)}>
      {children}
    </button>
  );
}
