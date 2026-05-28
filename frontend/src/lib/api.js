const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function authHeaders() {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function handleResponse(res) {
  if (res.status === 401) {
    // Token missing / expired — wipe it and bounce to login.
    localStorage.removeItem('token')
    if (typeof window !== 'undefined' && !location.pathname.startsWith('/login')) {
      location.assign('/login')
    }
    throw new Error('Your session has expired. Please sign in again.')
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    const msg = err.detail || 'API request failed'
    const error = new Error(msg)
    error.status = res.status
    throw error
  }
  return res.json()
}

async function fetchAPI(path, params = {}) {
  const url = new URL(`${API_BASE}${path}`)
  Object.entries(params).forEach(([key, val]) => {
    if (val !== undefined && val !== null && val !== '') {
      url.searchParams.set(key, val)
    }
  })
  const res = await fetch(url.toString(), { headers: { ...authHeaders() } })
  return handleResponse(res)
}

async function sendJSON(path, method, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: body ? JSON.stringify(body) : undefined,
  })
  return handleResponse(res)
}

// ─── Dashboard ───
export const dashboardAPI = {
  getTableCounts: () => fetchAPI('/api/dashboard/table-counts'),
  getTableCount: (table) => fetchAPI(`/api/dashboard/table-count/${table}`),
  getTableData: (table, opts = {}) => fetchAPI(`/api/dashboard/table-data/${table}`, opts),
  getTableColumns: (table) => fetchAPI(`/api/dashboard/table-columns/${table}`),
  getExpiryAlerts: (table) => fetchAPI(`/api/dashboard/expiry-alerts/${table}`),
  getInventoryCharts: () => fetchAPI('/api/dashboard/inventory-charts'),
}

// ─── Platform ───
export const platformAPI = {
  getStats: (slug) => fetchAPI(`/api/platform/${slug}/stats`),
  getPOs: (slug, opts = {}) => fetchAPI(`/api/platform/${slug}/pos`, opts),
  getInventoryMatch: (slug, sku) => fetchAPI(`/api/platform/${slug}/inventory-match`, { sku }),
  listDispatches: (slug) => fetchAPI(`/api/platform/${slug}/dispatches`),
  createDispatch: (slug, data) => sendJSON(`/api/platform/${slug}/dispatches`, 'POST', data),
  deleteDispatch: (slug, id) => sendJSON(`/api/platform/${slug}/dispatches/${id}`, 'DELETE'),
  clearDispatches: (slug) => sendJSON(`/api/platform/${slug}/dispatches`, 'DELETE'),
}

// ─── SAP ───
export const sapAPI = {
  getDistributors: (opts = {}) => fetchAPI('/api/sap/distributors', opts),
  getDistributor: (cardCode) => fetchAPI(`/api/sap/distributors/${cardCode}`),
  getDistributorOrders: (cardCode, opts = {}) => fetchAPI(`/api/sap/distributor-orders/${cardCode}`, opts),
  getDistributorInvoices: (cardCode, opts = {}) => fetchAPI(`/api/sap/distributor-invoices/${cardCode}`, opts),
  getItems: (opts = {}) => fetchAPI('/api/sap/items', opts),
  getStockByWarehouse: (itemCode) => fetchAPI('/api/sap/stock-by-warehouse', { item_code: itemCode }),
  getSalesInvoices: (opts = {}) => fetchAPI('/api/sap/sales-invoices', opts),
  getCustomerSalesInvoices: (cardCode, opts = {}) => fetchAPI(`/api/sap/sales-invoices/${cardCode}`, opts),
  getSalesInvoiceLines: (docEntry) => fetchAPI(`/api/sap/sales-invoice-lines/${docEntry}`),
  getPlatformSalesInvoices: (slug, opts = {}) => fetchAPI(`/api/sap/platform-sales-invoices/${slug}`, opts),
  getPlatformDistributors: (slug, opts = {}) => fetchAPI(`/api/sap/platform-distributors/${slug}`, opts),
  getPlatformDistributorDetail: (slug, cardCode) => fetchAPI(`/api/sap/platform-distributors/${slug}/${cardCode}`),
}
