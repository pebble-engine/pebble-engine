"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Users, Folder, AlertTriangle, RefreshCw, ShieldAlert, Activity } from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";
import { useAuth } from "@/components/auth-provider";

type AdminUser = {
  id:            string;
  email:         string;
  created_at:    string;
  project_count: number;
};

type AdminProject = {
  slug:               string;
  business_name:      string;
  business_type:      string | null;
  user_id:            string;
  user_email:         string;
  built_at:           string | null;
  estimated_cost_usd: number;
  publish:            { kind: string; url: string; deployed_at: string } | null;
  domain:             { host: string; status: string } | null;
};

type AdminErrorLine = { file: string; line: string };

type AdminEngagementRow = {
  user_id:         string;
  email:           string;
  score:           "power" | "active" | "at_risk";
  distinct_events: number;
  total_events:    number;
};

type Tab = "users" | "projects" | "errors" | "engagement";

async function adminFetch<T>(path: string): Promise<T> {
  // Phase 58e (2026-05-22) — must send the Supabase access token; the
  // engine's _require_admin only reads `Authorization: Bearer <jwt>`
  // (and the legacy pebble_session cookie, which v3 never sets). Without
  // this header every admin tab was 401'ing for the v3 admin page even
  // when the caller's email was in PEBBLE_ADMIN_EMAIL.
  let authHeader: Record<string, string> = {};
  try {
    const { createClient } = await import("@/lib/supabase/client");
    const supabase = createClient();
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) authHeader = { "Authorization": `Bearer ${session.access_token}` };
  } catch { /* not authenticated — endpoint will 401 */ }
  const resp = await fetch(path, { headers: authHeader });
  const text = await resp.text();
  let json: unknown;
  try { json = JSON.parse(text); } catch { json = { error: text || "non-json response" }; }
  if (!resp.ok) {
    const err = (json as { error?: string }).error || `HTTP ${resp.status}`;
    throw new Error(err);
  }
  return json as T;
}

export default function AdminPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [tab, setTab] = useState<Tab>("users");
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [projects, setProjects] = useState<AdminProject[]>([]);
  const [errors, setErrors] = useState<AdminErrorLine[]>([]);
  const [engagement, setEngagement] = useState<AdminEngagementRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (authLoading) return;
    if (!user) {
      router.push("/login");
    }
  }, [authLoading, user, router]);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      if (tab === "users")      setUsers     ((await adminFetch<{ users:    AdminUser[] }>         ("/api/admin/users")).users);
      if (tab === "projects")   setProjects  ((await adminFetch<{ projects: AdminProject[] }>      ("/api/admin/projects")).projects);
      if (tab === "errors")     setErrors    ((await adminFetch<{ errors:   AdminErrorLine[] }>    ("/api/admin/errors")).errors);
      if (tab === "engagement") setEngagement((await adminFetch<{ users:    AdminEngagementRow[] }>("/api/admin/engagement")).users);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Admin fetch failed.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { if (user) void refresh(); /* eslint-disable-next-line */ }, [tab, user]);

  if (authLoading || !user) {
    return (
      <div className="min-h-screen-safe flex flex-col">
        <TopNav projectName="Admin" />
        <main className="flex-1 flex items-center justify-center text-muted-foreground">Loading…</main>
      </div>
    );
  }

  return (
    <div className="min-h-screen-safe flex flex-col">
      <TopNav projectName="Admin" />
      <main className="flex-1 px-6 py-10">
        <div className="max-w-5xl mx-auto space-y-6">
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <div>
              <h1 className={`${type.display.m} text-foreground`}>Support tooling</h1>
              <p className={`${type.body.s} text-muted-foreground mt-1`}>
                Read-only — to grant access add an email to <code className="font-mono text-xs">PEBBLE_ADMIN_EMAIL</code> in <code className="font-mono text-xs">.env</code>.
              </p>
            </div>
            <button
              onClick={refresh}
              className={`${interactions.chip} bg-card border border-border text-foreground px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2`}
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} /> Refresh
            </button>
          </div>

          <div className="flex gap-2 border-b border-border">
            <TabButton active={tab === "users"}      onClick={() => setTab("users")}      Icon={Users}         label="Users" />
            <TabButton active={tab === "projects"}   onClick={() => setTab("projects")}   Icon={Folder}        label="Projects" />
            <TabButton active={tab === "engagement"} onClick={() => setTab("engagement")} Icon={Activity}      label="Engagement" />
            <TabButton active={tab === "errors"}     onClick={() => setTab("errors")}     Icon={AlertTriangle} label="Errors" />
          </div>

          {error && (
            <div className="p-4 bg-destructive/10 border border-destructive/40 rounded-lg text-sm text-destructive flex items-center gap-2">
              <ShieldAlert className="w-4 h-4" /> {error}
            </div>
          )}

          {!error && tab === "users"      && <UsersTable      rows={users} />}
          {!error && tab === "projects"   && <ProjectsTable   rows={projects} />}
          {!error && tab === "engagement" && <EngagementTable rows={engagement} />}
          {!error && tab === "errors"     && <ErrorsList      rows={errors} />}

          <p className={`${type.caption} pt-6 text-center`}>
            <Link href="/dashboard" className={`${interactions.link}`}>← Back to dashboard</Link>
          </p>
        </div>
      </main>
    </div>
  );
}

function TabButton({ active, onClick, Icon, label }: { active: boolean; onClick: () => void; Icon: typeof Users; label: string }) {
  return (
    <button
      onClick={onClick}
      className={`${interactions.chip} flex items-center gap-2 px-4 py-2 text-sm font-semibold border-b-2 -mb-px ${
        active ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"
      }`}
    >
      <Icon className="w-4 h-4" /> {label}
    </button>
  );
}

function UsersTable({ rows }: { rows: AdminUser[] }) {
  if (!rows.length) return <p className="text-sm text-muted-foreground">No users yet.</p>;
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-card border border-border rounded-xl overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-accent text-muted-foreground">
          <tr>
            <th className="text-left px-4 py-2 font-semibold">Email</th>
            <th className="text-left px-4 py-2 font-semibold">Joined</th>
            <th className="text-right px-4 py-2 font-semibold">Projects</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((u) => (
            <tr key={u.id} className="border-t border-border">
              <td className="px-4 py-2 font-mono text-xs">{u.email}</td>
              <td className="px-4 py-2 text-xs text-muted-foreground">{u.created_at?.slice(0, 19).replace("T", " ")}</td>
              <td className="px-4 py-2 text-xs text-right">{u.project_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </motion.div>
  );
}

function ProjectsTable({ rows }: { rows: AdminProject[] }) {
  if (!rows.length) return <p className="text-sm text-muted-foreground">No projects yet.</p>;
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-card border border-border rounded-xl overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-accent text-muted-foreground">
          <tr>
            <th className="text-left px-4 py-2 font-semibold">Project</th>
            <th className="text-left px-4 py-2 font-semibold">Owner</th>
            <th className="text-left px-4 py-2 font-semibold">Built</th>
            <th className="text-left px-4 py-2 font-semibold">Status</th>
            <th className="text-right px-4 py-2 font-semibold">$ Cost</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((p) => (
            <tr key={p.slug} className="border-t border-border">
              <td className="px-4 py-2">
                <p className="font-semibold">{p.business_name}</p>
                <p className="text-[11px] font-mono text-muted-foreground">{p.slug}</p>
              </td>
              <td className="px-4 py-2 text-xs">{p.user_email || <span className="text-muted-foreground italic">unclaimed</span>}</td>
              <td className="px-4 py-2 text-xs text-muted-foreground">{(p.built_at || "").slice(0, 19).replace("T", " ")}</td>
              <td className="px-4 py-2 text-xs">
                {p.publish ? <span className="text-earth-deep">Published</span> : <span className="text-muted-foreground">Draft</span>}
                {p.domain && <span className="text-spark-deep ml-2">+ domain</span>}
              </td>
              <td className="px-4 py-2 text-xs text-right">${p.estimated_cost_usd.toFixed(4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </motion.div>
  );
}

function EngagementTable({ rows }: { rows: AdminEngagementRow[] }) {
  if (!rows.length) return <p className="text-sm text-muted-foreground">No engagement data yet — events appear after users start using refine / visual-edit / blocks / projects.</p>;
  const badge = (score: AdminEngagementRow["score"]) => {
    if (score === "power")   return <span className="text-earth-deep font-semibold">Power</span>;
    if (score === "active")  return <span className="text-spark-deep font-semibold">Active</span>;
    return <span className="text-muted-foreground">At-risk</span>;
  };
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-card border border-border rounded-xl overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-accent text-muted-foreground">
          <tr>
            <th className="text-left px-4 py-2 font-semibold">User</th>
            <th className="text-left px-4 py-2 font-semibold">Bucket</th>
            <th className="text-right px-4 py-2 font-semibold">Distinct (30d)</th>
            <th className="text-right px-4 py-2 font-semibold">Total events (30d)</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.user_id} className="border-t border-border">
              <td className="px-4 py-2">
                <p className="text-xs">{r.email || <span className="text-muted-foreground italic">no email</span>}</p>
                <p className="text-[11px] font-mono text-muted-foreground">{r.user_id.slice(0, 12)}…</p>
              </td>
              <td className="px-4 py-2 text-xs">{badge(r.score)}</td>
              <td className="px-4 py-2 text-xs text-right">{r.distinct_events}</td>
              <td className="px-4 py-2 text-xs text-right">{r.total_events}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </motion.div>
  );
}

function ErrorsList({ rows }: { rows: AdminErrorLine[] }) {
  if (!rows.length) return <p className="text-sm text-muted-foreground">No errors logged. Quiet is good.</p>;
  return (
    <motion.ul initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-1">
      {rows.map((r, i) => (
        <li key={i} className="font-mono text-xs p-2 bg-card border border-border rounded">
          <span className="text-muted-foreground mr-2">[{r.file}]</span>
          <span className="text-foreground break-words">{r.line}</span>
        </li>
      ))}
    </motion.ul>
  );
}
