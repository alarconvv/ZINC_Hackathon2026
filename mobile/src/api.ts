import Constants from 'expo-constants';
import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';
export const API_URL = process.env.EXPO_PUBLIC_API_URL || Constants.expoConfig?.extra?.apiUrl || 'http://127.0.0.1:8000';
const key = 'zinc-access-token';
export const tokenStore = {
  async get() { return Platform.OS === 'web' ? (typeof localStorage === 'undefined' ? null : localStorage.getItem(key)) : SecureStore.getItemAsync(key); },
  async set(token: string | null) {
    if (Platform.OS === 'web') { if (token) localStorage.setItem(key, token); else localStorage.removeItem(key); }
    else if (token) await SecureStore.setItemAsync(key, token); else await SecureStore.deleteItemAsync(key);
  }
};
export class ApiError extends Error { constructor(public status: number, message: string) { super(message); } }
export async function request<T>(path: string, token: string | null, method='GET', body?: unknown, version?: number): Promise<T> {
  let response: Response;
  try {
    response = await fetch(API_URL + path, {method, headers:{'Content-Type':'application/json', ...(token ? {Authorization:`Bearer ${token}`} : {}), ...(version !== undefined ? {'If-Match':String(version)} : {})}, ...(body !== undefined ? {body:JSON.stringify(body)} : {}), signal:AbortSignal.timeout(40000)});
  } catch { throw new ApiError(0, 'Cannot reach ZINC. Check your connection and try again.'); }
  if (response.status === 204) return undefined as T;
  const data = await response.json();
  if (!response.ok) throw new ApiError(response.status, typeof data.detail === 'string' ? data.detail : 'Check your entries and try again.');
  return data;
}
