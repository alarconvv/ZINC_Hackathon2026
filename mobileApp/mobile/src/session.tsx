import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { request, ApiError, tokenStore } from "./api";
import { Snapshot } from "./types";
type Session = {
  token: string | null;
  data: Snapshot | null;
  ready: boolean;
  busy: boolean;
  error: string;
  clearError: () => void;
  refresh: () => Promise<void>;
  authenticate: (
    email: string,
    password: string,
    name?: string,
  ) => Promise<void>;
  act: <T = Snapshot>(
    path: string,
    body?: unknown,
    method?: string,
  ) => Promise<T>;
  run: (fn: () => Promise<void>) => Promise<void>;
  signOut: () => Promise<void>;
  stop: () => Promise<void>;
};
const Context = createContext<Session>(null!);
export const useSession = () => useContext(Context);
export function SessionProvider({ children }: React.PropsWithChildren) {
  const [token, setToken] = useState<string | null>(null),
    [data, setData] = useState<Snapshot | null>(null),
    [ready, setReady] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  const read = useCallback(async (t: string) => {
    const me = await request<Snapshot>("/me", t);
    const plan = me.consented ? await request<Snapshot>("/plan", t) : me;
    setData({ ...me, ...plan });
  }, []);
  useEffect(() => {
    let live = true;
    tokenStore
      .get()
      .then(async (t) => {
        if (!live) return;
        if (t) {
          setToken(t);
          try {
            await read(t);
          } catch (e) {
            if (e instanceof ApiError && e.status === 401) {
              await tokenStore.set(null);
              setToken(null);
            } else setError((e as Error).message);
          }
        }
      })
      .finally(() => setReady(true));
    return () => {
      live = false;
    };
  }, [read]);
  const refresh = useCallback(async () => {
    if (token) await read(token);
  }, [token, read]);
  async function signOut() {
    await tokenStore.set(null);
    setToken(null);
    setData(null);
    setError("");
  }
  async function authenticate(email: string, password: string, name?: string) {
    const result = await request<{ access_token: string }>(
      "/auth/" + (name !== undefined ? "register" : "login"),
      null,
      "POST",
      { email, password, ...(name !== undefined ? { name } : {}) },
    );
    await tokenStore.set(result.access_token);
    setToken(result.access_token);
    await read(result.access_token);
  }
  async function act<T = Snapshot>(
    path: string,
    body?: unknown,
    method = "POST",
  ): Promise<T> {
    try {
      const result = await request<T>(path, token, method, body, data?.version);
      if (
        result &&
        typeof result === "object" &&
        "state" in result &&
        "version" in result
      ) {
        setData((previous) => ({
          ...previous,
          ...(result as unknown as Snapshot),
        }));
      } else if (path === "/consent") await refresh();
      return result;
    } catch (e) {
      if (e instanceof ApiError && (e.status === 409 || e.status === 423))
        await refresh();
      if (e instanceof ApiError && e.status === 401) await signOut();
      throw e;
    }
  }
  async function run(fn: () => Promise<void>) {
    setBusy(true);
    setError("");
    try {
      await fn();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function stop() {
    try {
      await act("/stop");
      setError("");
    } catch (e) {
      setError((e as Error).message);
    }
  }
  return (
    <Context.Provider
      value={{
        token,
        data,
        ready,
        busy,
        error,
        clearError: () => setError(""),
        refresh,
        authenticate,
        act,
        run,
        signOut,
        stop,
      }}
    >
      {children}
    </Context.Provider>
  );
}
