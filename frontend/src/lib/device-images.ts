import iphone14pro from "../assets/iphone-14-pro.png";   
import iphone14 from "../assets/iphone-14.png";           
import iphone13 from "../assets/iphone-13.png";           
import samsungS22 from "../assets/samsung-s22.png";       
import samsungS21 from "../assets/samsung-s21.png";       
import simCard from "../assets/sim-card.png";              
import type { Plan } from "../api/plans";                  

// Pick the right asset for a plan card or details view.
export function deviceImage(plan: Plan): string {
  if (plan.type === "sim") return simCard;
  switch (plan.phoneModel) {
    case "iPhone 14 Pro": return iphone14pro;
    case "iPhone 14":     return iphone14;
    case "iPhone 13":     return iphone13;
    case "Samsung S22":   return samsungS22;
    case "Samsung S21":   return samsungS21;
    default:              return simCard;
  }
}

// Exported separately for places that explicitly need the SIM artwork.
export const SIM_IMAGE = simCard;

// Model-to-image map for custom UI that already has a phone model string.
export const DEVICE_IMAGES = {
  "iPhone 14 Pro": iphone14pro,
  "iPhone 14":     iphone14,
  "iPhone 13":     iphone13,
  "Samsung S22":   samsungS22,
  "Samsung S21":   samsungS21,
} as const;
