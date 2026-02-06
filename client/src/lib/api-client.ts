import { API_BASE } from "./config"
import type { APIError } from "./types/common"

class APIClient {
  private getAuthToken(): string | null {
    if (typeof window === "undefined") return null
    return localStorage.getItem("authToken")
  }

  private async request<T>(url: string, options: RequestInit = {}): Promise<T> {
    const token = this.getAuthToken()
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers,
    }

    if (token) {
      headers["Authorization"] = `Token ${token}`
    }

    const response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error: APIError = await response.json().catch(() => ({
        detail: response.statusText,
      }))
      throw error
    }

    return response.json()
  }

  async get<T>(url: string, params?: Record<string, any>): Promise<T> {
    const searchParams = params ? `?${new URLSearchParams(params)}` : ""
    return this.request<T>(`${url}${searchParams}`, {
      method: "GET",
    })
  }

  async post<T>(url: string, data: any): Promise<T> {
    return this.request<T>(url, {
      method: "POST",
      body: JSON.stringify(data),
    })
  }

  async put<T>(url: string, data: any): Promise<T> {
    return this.request<T>(url, {
      method: "PUT",
      body: JSON.stringify(data),
    })
  }

  async patch<T>(url: string, data: any): Promise<T> {
    return this.request<T>(url, {
      method: "PATCH",
      body: JSON.stringify(data),
    })
  }

  async delete<T>(url: string): Promise<T> {
    return this.request<T>(url, {
      method: "DELETE",
    })
  }
}

export const apiClient = new APIClient()
