export type Role = "CONSUMER" | "COLLECTOR" | "RECYCLER" | "BUSINESS" | "ADMIN";
export type DataType = "DEMO" | "LIVE" | "HISTORICAL";

export type TokenPair = { access_token: string; refresh_token: string; token_type: string };
export type User = { id: string; email: string; full_name: string; role: Role; phone?: string | null };

export type Price = {
  material: string;
  material_name: string;
  location: string;
  unit: string;
  low: number;
  high: number;
  average: number;
  recommended: number;
  currency: string;
  source: string;
  source_url: string | null;
  retrieved_at: string;
  data_type: DataType;
  is_live: boolean;
  confidence: number | null;
  chart_points: number[];
  neighborhoods: { area: string; price: number; data_type: DataType }[];
};

export type Scrap = {
  id: string;
  status: string;
  material_id: string | null;
  quantity: number | null;
  unit: string;
  location: string;
  area: string | null;
  estimated_low: number | null;
  estimated_high: number | null;
  identification_available: boolean | null;
  identification_message: string | null;
};

export type Offer = {
  id: string;
  listing_id: string;
  buyer_type: string;
  name: string;
  verification: string;
  distance_km: number | null;
  eta_label: string;
  price_per_unit: number;
  score: number;
  status: string;
  data_type: DataType;
};

export type Pickup = {
  id: string;
  listing_id: string;
  status: string;
  collector_name: string | null;
  vehicle_type: string | null;
  eta_minutes: number | null;
  area: string | null;
  lat: number | null;
  lng: number | null;
  route: number[][] | null;
  data_note: string;
};

export type MarketRequest = {
  id: string;
  seller_name: string;
  seller_type: string;
  area: string;
  location: string;
  quantity: number | null;
  unit: string;
  material_name: string;
  status: string;
  description: string | null;
  estimated_low: number | null;
  estimated_high: number | null;
  created_at: string | null;
  photo_count: number;
};

export type Collector = {
  id: string;
  name: string;
  vehicle_type: string | null;
  service_areas: string[];
  rating: number | null;
  completed_pickups: number;
  verification: string;
  lat: number | null;
  lng: number | null;
};

export type Recycler = {
  id: string;
  organization_name: string;
  location: string;
  pickup_available: boolean;
  materials: string[];
  verification: string;
  authority_name: string | null;
  verification_source: string | null;
};

export type Trace = {
  lot_id: string;
  current_status: string;
  initial_weight: number | null;
  current_weight: number | null;
  data_type: DataType;
  events: { event_type: string; timestamp: string; location: string | null; weight: number | null; notes: string | null }[];
};

export type Bulk = {
  id: string;
  status: string;
  pickup_location: string;
  materials: unknown[];
  estimated_low: number | null;
  estimated_high: number | null;
  data_type: DataType;
};

export type Notification = { id: string; title: string; body: string; is_read: boolean; created_at: string };
export type MapConfig = {
  tile_url: string;
  attribution: string;
  provider_configured: boolean;
  note: string;
  center: number[];
  zoom: number;
};
