import { CircleMarker, MapContainer, Polyline, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import type { MapConfig } from "../api/types";

type Props = {
  config: MapConfig | null;
  points?: { lat: number; lng: number; label?: string }[];
  route?: number[][] | null;
  height?: number;
};

export function CityMap({ config, points = [], route, height = 360 }: Props) {
  const center = (config?.center as [number, number] | undefined) ?? [12.9716, 77.5946];
  const zoom = config?.zoom ?? 12;
  const url = config?.tile_url ?? "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
  const attribution = config?.attribution ?? "© OpenStreetMap contributors";

  return (
    <div className="overflow-hidden rounded-2xl border border-line" style={{ height }}>
      <MapContainer center={center} zoom={zoom} style={{ height: "100%", width: "100%" }} scrollWheelZoom={false}>
        <TileLayer url={url} attribution={attribution} />
        {route && route.length > 1 ? <Polyline positions={route as [number, number][]} color="#3D7A5F" weight={4} /> : null}
        {points.map((p) => (
          <CircleMarker key={`${p.lat}-${p.lng}`} center={[p.lat, p.lng]} radius={8} pathOptions={{ color: "#3D7A5F", fillColor: "#52A67A", fillOpacity: 0.9 }} />
        ))}
      </MapContainer>
    </div>
  );
}
