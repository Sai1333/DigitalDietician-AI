// src/types/pantry.ts
export interface PantryItemIn {
    name: string;
    quantity?: number;
    unit?: string;
    expiry_date?: string | null;
  }
  
  export interface PantryItemOut extends PantryItemIn {
    id: number;
  }
  