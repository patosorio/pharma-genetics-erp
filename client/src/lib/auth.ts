"use client"

import { API_BASE } from "./config"
import type { User } from "./types/core"

export interface AuthResponse {
  token: string
}

export async function signIn(email: string, password: string): Promise<{ token: string; user: User }> {
  // Call Django Token Auth endpoint
  const response = await fetch(`${API_BASE.replace('/api/v1', '')}/api/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: email, password }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Invalid credentials" }))
    throw new Error(error.detail || error.non_field_errors?.[0] || "Failed to sign in")
  }

  const { token } = await response.json()
  
  // Store token
  localStorage.setItem("authToken", token)
  
  // Fetch user profile
  const userResponse = await fetch(`${API_BASE}/me/`, {
    headers: { Authorization: `Token ${token}` },
  })
  
  if (!userResponse.ok) {
    throw new Error("Failed to fetch user profile")
  }
  
  const user = await userResponse.json()
  
  return { token, user }
}

export async function signUp(data: {
  email: string
  password: string
  first_name: string
  last_name: string
}): Promise<{ detail: string; email: string }> {
  const response = await fetch(`${API_BASE}/register/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Registration failed" }))
    throw error
  }

  return response.json()
}

export async function signOut() {
  const token = localStorage.getItem("authToken")
  
  if (token) {
    // Call logout endpoint (optional, just deletes token)
    try {
      await fetch(`${API_BASE}/logout/`, {
        method: "POST",
        headers: { Authorization: `Token ${token}` },
      })
    } catch {
      // Ignore errors on logout
    }
  }
  
  localStorage.removeItem("authToken")
}

export async function getCurrentUser(): Promise<User | null> {
  const token = localStorage.getItem("authToken")
  
  if (!token) return null
  
  try {
    const response = await fetch(`${API_BASE}/me/`, {
      headers: { Authorization: `Token ${token}` },
    })
    
    if (!response.ok) {
      localStorage.removeItem("authToken")
      return null
    }
    
    return response.json()
  } catch {
    return null
  }
}
