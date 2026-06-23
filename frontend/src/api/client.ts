const BASE_URL = '/api'

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.text()
    throw new ApiError(response.status, body || response.statusText)
  }
  if (response.status === 204) return undefined as T
  return response.json()
}

export const api = {
  get: <T>(path: string): Promise<T> =>
    fetch(`${BASE_URL}${path}`).then(handleResponse<T>),

  post: <T>(path: string, body?: unknown): Promise<T> =>
    fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    }).then(handleResponse<T>),

  upload: <T>(path: string, formData: FormData): Promise<T> =>
    fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      body: formData,
    }).then(handleResponse<T>),

  delete: <T>(path: string): Promise<T> =>
    fetch(`${BASE_URL}${path}`, { method: 'DELETE' }).then(handleResponse<T>),
}
