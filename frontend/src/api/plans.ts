import { apiFetch } from "./_base";

// These unions keep provider and plan values aligned with the backend seed data.
export type Provider = "fone" | "gap" | "flipper";
export type PlanType = "sim" | "phone";
export type PhoneBrand = "apple" | "samsung" | null;
export type PhoneModel =
  | "iPhone 14 Pro"
  | "iPhone 14"
  | "iPhone 13"
  | "Samsung S22"
  | "Samsung S21"
  | null;

// Plan is the frontend shape after the backend formats database rows for the UI.
export interface Plan  {
  id: string;
  provider: Provider;
  name: string;
  tier: "SIM Only" | "All-in" | "Just Phone";
  type: PlanType;
  data: number;
  dataLabel: string;
  callsTexts: "limited" | "unlimited";
  calls?: string;
  texts?: string;
  phoneBrand: PhoneBrand;
  phoneModel: PhoneModel;
  monthlyPrice: number;
  contractMonths: number;
  twoYearCost?: number;
}

// Load every plan for browse, provider, and homepage views.
export async function getAllPlans() : Promise<Plan[]> {
  return apiFetch<Plan[]>("/plans");
}

// Load one plan by id for pages that only know the selected plan id.
export async function getPlanById(id:string) : Promise<Plan | undefined > {
  return apiFetch<Plan>(`/plans/${id}`);
  
}



// Ask the backend recommendation endpoint for plans that match finder answers.
export async function getRecommendedPlans(params:{
  path?:string;
  justPhone?: string;
  brand?: string;
  data?: string;
  calls?: string;
  priority?: string;
  budget?: string;
}) : Promise<Plan[]> {
  // URLSearchParams avoids hand-building query strings and skips empty answers.
  const query = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if(v !== undefined) query.set(k,v);
  });
  return apiFetch<Plan[]> (`/plans/recommend?${query.toString()}`);
}


export interface PlanFilters {
  providers?: Provider[];
  type?: "all" | "sim" | "phone";
  budget?: number;
  data?: string[];
  brand?: "any" | "apple" | "samsung";
  calls?: "any" | "limited" | "unlimited";
}




export async function getFilteredPlans(filters:PlanFilters) : Promise<Plan[]> {
  const params = new URLSearchParams();
   console.log("Filters being sent:", filters);
  

  if (filters.providers && filters.providers.length > 0 && filters.providers.length < 3) {
    params.set("providers", filters.providers.join(","));
  }
  if(filters.type && filters.type !== "all")
    params.set("type", filters.type);
  if(filters.budget !== undefined)
    params.set("budget", filters.budget.toString());
  if(filters.data && filters.data.length > 0)
    params.set("data", filters.data.join(","));
  if(filters.brand && filters.brand !== "any")
    params.set("brand", filters.brand);
  if(filters.calls && filters.calls !== "any")
    params.set("calls", filters.calls);

   console.log("URL params:", params.toString());


  return apiFetch<Plan[]>(`/plans?${params.toString()}`)
}
