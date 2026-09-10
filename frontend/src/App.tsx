import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { AuthProvider } from "./lib/auth";
import { AdminPage } from "./pages/AdminPage";
import { BusinessPage } from "./pages/BusinessPage";
import { CollectorsPage } from "./pages/CollectorsPage";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { OffersPage } from "./pages/OffersPage";
import { PickupPage } from "./pages/PickupPage";
import { PricesPage } from "./pages/PricesPage";
import { SellPage } from "./pages/SellPage";
import { TraceabilityPage } from "./pages/TraceabilityPage";
import { TrackPage } from "./pages/TrackPage";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/sell" element={<SellPage />} />
            <Route path="/prices" element={<PricesPage />} />
            <Route path="/offers" element={<OffersPage />} />
            <Route path="/pickup" element={<PickupPage />} />
            <Route path="/track" element={<TrackPage />} />
            <Route path="/collectors" element={<CollectorsPage />} />
            <Route path="/traceability" element={<TraceabilityPage />} />
            <Route path="/business" element={<BusinessPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/admin" element={<AdminPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
