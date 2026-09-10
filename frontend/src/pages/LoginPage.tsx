import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";

const demos = [
  ["Consumer", "ananya@kabadiwala.local"],
  ["Collector", "ravi@kabadiwala.local"],
  ["Business", "itpark@kabadiwala.local"],
  ["Admin", "admin@kabadiwala.local"],
];

export function LoginPage() {
  const { login, register, error } = useAuth();
  const nav = useNavigate();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("ananya@kabadiwala.local");
  const [password, setPassword] = useState("DemoPass123!");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("CONSUMER");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      if (mode === "login") await login(email, password);
      else await register({ email, password, full_name: fullName, role });
      nav("/");
    } catch {
      /* error shown from context */
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-md space-y-6">
      <h1 className="font-display text-3xl font-bold">{mode === "login" ? "Sign in" : "Create account"}</h1>
      <p className="text-sm text-muted">Demo password for seeded users: DemoPass123!</p>
      <form onSubmit={onSubmit} className="space-y-3 rounded-2xl border border-line bg-white/50 p-6">
        {mode === "register" ? (
          <>
            <label className="block text-sm">
              Full name
              <input className="mt-1 w-full rounded-lg border border-line bg-cream px-3 py-2" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
            </label>
            <label className="block text-sm">
              Role
              <select className="mt-1 w-full rounded-lg border border-line bg-cream px-3 py-2" value={role} onChange={(e) => setRole(e.target.value)}>
                <option>CONSUMER</option>
                <option>COLLECTOR</option>
                <option>BUSINESS</option>
              </select>
            </label>
          </>
        ) : null}
        <label className="block text-sm">
          Email
          <input className="mt-1 w-full rounded-lg border border-line bg-cream px-3 py-2" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label className="block text-sm">
          Password
          <input className="mt-1 w-full rounded-lg border border-line bg-cream px-3 py-2" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
        {error ? <p className="text-sm text-[#a0443a]">{error}</p> : null}
        <button disabled={busy} className="w-full rounded-full bg-emerald py-2 font-semibold text-cream disabled:opacity-60">
          {busy ? "Please wait…" : mode === "login" ? "Sign in" : "Register"}
        </button>
      </form>
      <button type="button" className="text-sm text-forest underline" onClick={() => setMode(mode === "login" ? "register" : "login")}>
        {mode === "login" ? "Need an account?" : "Already have an account?"}
      </button>
      <ul className="text-sm text-muted">
        {demos.map(([label, mail]) => (
          <li key={mail}>
            <button type="button" className="underline" onClick={() => setEmail(mail)}>
              {label}: {mail}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
