import { clsx, type ClassValue } from "clsx";
import { tailwindMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  // Try to use tailwindMerge and clsx if imported (clsx and tailwind-merge are in package.json dependencies!)
  try {
    return tailwindMerge(clsx(inputs));
  } catch (e) {
    return inputs.filter(Boolean).join(" ");
  }
}
